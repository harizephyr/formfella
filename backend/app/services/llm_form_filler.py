from fastapi import FastAPI, File, UploadFile, HTTPException, APIRouter, Depends, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import boto3
import os
import uuid
import shutil
from pathlib import Path
from datetime import datetime
import fitz  # PyMuPDF
from services.llm import get_llm_response
from core.config.settings import settings
from db.base import get_db
from db.crud.credits import update_credits,get_credits
from sqlalchemy.orm import Session
router = APIRouter()
from api.v1.endpoints.auth import get_email
from fastapi import BackgroundTasks
from time import sleep
# Initialize AWS Textract client
textract = boto3.client("textract", region_name=settings.AWS_DEFAULT_REGION, aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

# Create directories
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("output")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Pydantic models
class FormQuestion(BaseModel):
    field_id: str
    question: str
    field_name: str
    current_value: str

class QuestionResponse(BaseModel):
    field_id: str
    answer: str

class FormSubmission(BaseModel):
    responses: List[QuestionResponse]

class ProcessResponse(BaseModel):
    form_id: str
    questions: List[FormQuestion]
    total_questions: int

# In-memory storage for form data
form_storage: Dict[str, Dict] = {}

class PDFFormProcessor:
    def __init__(self, form_id: str, pdf_path: str):
        self.form_id = form_id
        self.pdf_path = pdf_path
        self.doc = None
        
    def process_and_get_questions(self) -> List[FormQuestion]:
        """Process PDF and return list of questions."""
        try:
            # Analyze document with Textract
            with open(self.pdf_path, "rb") as f:
                response = textract.analyze_document(
                    Document={"Bytes": f.read()},
                    FeatureTypes=["FORMS"]
                )
            
            # Process blocks
            key_map, value_map, block_map = self.get_kv_map(response["Blocks"])
            
            # Open PDF
            self.doc = fitz.open(self.pdf_path)
            page = self.doc[0]
            
            # Create output directory for images
            form_output_dir = OUTPUT_DIR / self.form_id
            form_output_dir.mkdir(exist_ok=True)
            
            questions = []
            field_data = {}
            
            # Process each field
            for key_id, key_block in key_map.items():
                value_block = self.find_value_block(key_block, value_map)
                if not value_block:
                    continue
                
                # Extract text
                key_text = self.get_text_from_block(key_block, block_map)
                original_value = self.get_text_from_block(value_block, block_map)
                
                # Save field image for LLM
                key_img_path = form_output_dir / f"key_{key_id}.png"
                self.save_cropped_image(page, key_block["Geometry"]["BoundingBox"], str(key_img_path))
                
                # Generate AI question
                try:
                    ai_question = get_llm_response(
                        str(key_img_path),
                        "Look at this form field image and generate a clear, specific question to ask the user. Be concise and direct. For example, if the field says 'Email', ask 'What is your email address?'"
                    )
                except Exception as e:
                    ai_question = f"Please provide a value for '{key_text}'"
                
                # Store field data for later use
                field_data[key_id] = {
                    "key_text": key_text,
                    "original_value": original_value,
                    "key_bbox": key_block["Geometry"]["BoundingBox"],
                    "value_bbox": value_block["Geometry"]["BoundingBox"]
                }
                
                # Create question
                question = FormQuestion(
                    field_id=key_id,
                    question=ai_question,
                    field_name=key_text,
                    current_value=original_value
                )
                questions.append(question)
            
            # Store form data for later use
            form_storage[self.form_id] = {
                "pdf_path": self.pdf_path,
                "field_data": field_data,
                "processed_at": datetime.now()
            }
            
            self.doc.close()
            return questions
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

    def create_filled_pdf(self, responses: Dict[str, str]) -> str:
        """Create filled PDF with answers."""
        try:
            # Get stored field data
            if self.form_id not in form_storage:
                raise HTTPException(status_code=404, detail="Form data not found")
            
            field_data = form_storage[self.form_id]["field_data"]
            
            # Open PDF
            filled_doc = fitz.open(self.pdf_path)
            page = filled_doc[0]
            
            # Fill each field with user responses
            for field_id, answer in responses.items():
                if field_id in field_data and answer.strip():
                    bbox = field_data[field_id]["value_bbox"]
                    
                    # Calculate position
                    x = bbox["Left"] * page.rect.width
                    y = bbox["Top"] * page.rect.height
                    width = bbox["Width"] * page.rect.width
                    height = bbox["Height"] * page.rect.height
                    
                    # Cover original text with white rectangle
                    rect = fitz.Rect(x, y, x + width, y + height)
                    page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
                    
                    # Add new text
                    font_size = min(12, height * 0.7)
                    page.insert_text(
                        (x + 2, y + height * 0.7),
                        answer,
                        fontsize=font_size,
                        color=(0, 0, 0)
                    )
            
            # Save filled PDF
            output_path = OUTPUT_DIR / f"filled_{self.form_id}.pdf"
            filled_doc.save(str(output_path))
            filled_doc.close()
            
            return str(output_path)
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"PDF creation failed: {str(e)}")

    def get_kv_map(self, blocks):
        key_map, value_map, block_map = {}, {}, {}
        for block in blocks:
            block_id = block["Id"]
            block_map[block_id] = block
            if block["BlockType"] == "KEY_VALUE_SET":
                if "KEY" in block.get("EntityTypes", []):
                    key_map[block_id] = block
                else:
                    value_map[block_id] = block
        return key_map, value_map, block_map

    def find_value_block(self, key_block, value_map):
        for rel in key_block.get("Relationships", []):
            if rel["Type"] == "VALUE":
                for value_id in rel["Ids"]:
                    if value_id in value_map:
                        return value_map[value_id]
        return None

    def get_text_from_block(self, block, block_map):
        text = ""
        for rel in block.get("Relationships", []):
            if rel["Type"] == "CHILD":
                for child_id in rel["Ids"]:
                    child = block_map.get(child_id, {})
                    if child.get("BlockType") == "WORD":
                        text += child.get("Text", "") + " "
        return text.strip()

    def save_cropped_image(self, page, bbox, output_path):
        rect = fitz.Rect(
            bbox["Left"] * page.rect.width,
            bbox["Top"] * page.rect.height,
            (bbox["Left"] + bbox["Width"]) * page.rect.width,
            (bbox["Top"] + bbox["Height"]) * page.rect.height
        )
        pix = page.get_pixmap(clip=rect)
        pix.save(output_path)

# API Endpoints

@router.post("/api/process", response_model=List[ProcessResponse])
async def process_pdf_and_get_questions(request: Request,files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    """
    Upload multiple PDFs, process them, and return list of AI-generated questions for each.
    """
    responses = []
    
    # validate user credits
    email = get_email(request)
    credits = get_credits(email, db)["credits"]

    if credits < 5:
        raise HTTPException(status_code=400, detail="Not enough credits")


    
    for file in files:
        # Validate file
        if not file.filename.lower().endswith('.pdf'):
            continue  # Skip non-PDF files or return error
        
        # Generate unique form ID for each file
        form_id = str(uuid.uuid4())
        
        # Save uploaded file
        file_path = UPLOAD_DIR / f"{form_id}.pdf"
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            print(f"Failed to save file {file.filename}: {str(e)}")
            continue
        
        try:
            # Process PDF and get questions
            processor = PDFFormProcessor(form_id, str(file_path))
            questions = processor.process_and_get_questions()
            
            responses.append(ProcessResponse(
                form_id=form_id,
                questions=questions,
                total_questions=len(questions)
            ))
        except Exception as e:
            print(f"Error processing {file.filename}: {str(e)}")
            continue
    
    if not responses:
        raise HTTPException(status_code=400, detail="No valid PDF files were processed")


    # reduce 5 credits for each pdf processed
    reduce_credits(5, credits, email, db)

    #remove formid folder
    shutil.rmtree(OUTPUT_DIR / form_id)
        
    return responses

@router.post("/api/submit/{form_id}")
async def submit_answers_and_get_pdf(form_id: str, background_tasks: BackgroundTasks, submission: FormSubmission):
    """
    Submit answers and get the filled PDF for download.
    """
    # Check if form exists
    if form_id not in form_storage:
        raise HTTPException(status_code=404, detail="Form not found")
    
    # Convert responses to dict
    responses = {resp.field_id: resp.answer for resp in submission.responses}
    
    # Get PDF path
    pdf_path = form_storage[form_id]["pdf_path"]
    
    # Create filled PDF
    processor = PDFFormProcessor(form_id, pdf_path)
    output_path = processor.create_filled_pdf(responses)
    

    # add background task to remove this file after 2 mins
    background_tasks.add_task(remove_file, OUTPUT_DIR / f"filled_{form_id}.pdf")
    
    # Return filled PDF
    return FileResponse(
        path=output_path,
        filename=f"filled_form_{form_id}.pdf",
        media_type="application/pdf"
    )

def remove_file(file_path):
    try:
        sleep(10)
        os.remove(file_path)
    except Exception as e:
        print(f"Failed to remove file {file_path}: {str(e)}")

@router.get("/")
async def health_check():
    """Health check endpoint."""
    return {
        "message": "PDF Form Filler API is running",
        "version": "1.0.0",
        "endpoints": {
            "process": "POST /api/process - Upload PDF and get questions",
            "submit": "POST /api/submit/{form_id} - Submit answers and download PDF"
        }
    }


def reduce_credits(amount: int,credits: int, email: str, db):
    """Reduce credits for processing PDF."""
    
    # Reduce credits
    new_credits = max(0, credits - amount)
    
    # Save updated credits
    update_credits(new_credits, email, db)