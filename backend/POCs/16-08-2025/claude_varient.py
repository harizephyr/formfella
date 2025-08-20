import boto3
import os
import json
from dotenv import load_dotenv
import fitz  # PyMuPDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from llm import get_llm_response

# Load environment variables
load_dotenv(dotenv_path="../.env.local")

# Initialize Textract client
textract = boto3.client("textract")

class InteractivePDFFormFiller:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.doc = None
        self.results = []
        self.user_responses = {}
        
    def process_pdf_form(self):
        """Process a PDF form and extract key-value pairs with interactive filling."""
        print("🔍 Analyzing PDF form with AWS Textract...")
        
        # Analyze the document with Textract
        with open(self.pdf_path, "rb") as f:
            response = textract.analyze_document(
                Document={"Bytes": f.read()},
                FeatureTypes=["FORMS"]
            )
        
        # Process blocks to find key-value pairs
        key_map, value_map, block_map = self.get_kv_map(response["Blocks"])
        
        # Open the PDF with PyMuPDF for visualization and cropping
        self.doc = fitz.open(self.pdf_path)
        page = self.doc[0]
        
        # Create output directory if it doesn't exist
        os.makedirs("output", exist_ok=True)
        
        print(f"📋 Found {len(key_map)} form fields to fill")
        print("=" * 60)
        
        # Process each key-value pair interactively
        for i, (key_id, key_block) in enumerate(key_map.items(), 1):
            value_block = self.find_value_block(key_block, value_map)
            if not value_block:
                continue
                
            # Get key and value text
            key_text = self.get_text_from_block(key_block, block_map)
            original_value = self.get_text_from_block(value_block, block_map)
            
            print(f"\n📝 Field {i}/{len(key_map)}")
            print(f"Field: {key_text}")
            if original_value.strip():
                print(f"Current value: {original_value}")
            
            # Save cropped images for LLM analysis
            key_img_path = f"output/key_{key_id}.png"
            value_img_path = f"output/value_{key_id}.png"
            
            self.save_cropped_image(page, key_block["Geometry"]["BoundingBox"], key_img_path)
            self.save_cropped_image(page, value_block["Geometry"]["BoundingBox"], value_img_path)

            # Get LLM-generated question based on the field
            try:
                llm_question = get_llm_response(
                    key_img_path, 
                    "Look at this form field image and generate a clear, specific question to ask the user to fill this field. Be concise and direct. For example, if the field says 'Email', ask 'What is your email address?'"
                )
                print(f"🤖 AI Question: {llm_question}")
            except Exception as e:
                print(f"⚠️ Could not generate AI question: {e}")
                llm_question = f"Please provide a value for '{key_text}'"
            
            # Get user input
            user_input = input("📝 Your answer: ").strip()
            
            # Store the response
            self.user_responses[key_id] = {
                "key": key_text,
                "original_value": original_value,
                "new_value": user_input,
                "key_bbox": key_block["Geometry"]["BoundingBox"],
                "value_bbox": value_block["Geometry"]["BoundingBox"]
            }
            
            self.results.append({
                "key": key_text,
                "original_value": original_value,
                "new_value": user_input,
                "key_image": key_img_path,
                "value_image": value_img_path,
                "llm_question": llm_question
            })
            
            print("✅ Response saved!")
        
        print("\n🎉 All fields completed!")
        return self.results

    def create_filled_pdf(self, output_path="output/filled_form.pdf"):
        """Create a new PDF with user responses filled in."""
        print("\n📄 Creating filled PDF...")
        
        if not self.doc:
            raise ValueError("PDF not processed yet. Run process_pdf_form() first.")
        
        # Create a copy of the original document
        filled_doc = fitz.open(self.pdf_path)
        page = filled_doc[0]
        
        # Add text overlays for user responses
        for key_id, response_data in self.user_responses.items():
            if response_data["new_value"]:
                # Calculate position for the new text
                bbox = response_data["value_bbox"]
                x = bbox["Left"] * page.rect.width
                y = bbox["Top"] * page.rect.height
                width = bbox["Width"] * page.rect.width
                height = bbox["Height"] * page.rect.height
                
                # Create a white rectangle to cover the original value
                rect = fitz.Rect(x, y, x + width, y + height)
                page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
                
                # Add the new text
                font_size = min(12, height * 0.7)  # Adjust font size based on field height
                text_rect = fitz.Rect(x + 2, y, x + width - 2, y + height)
                
                page.insert_text(
                    (x + 2, y + height * 0.7),
                    response_data["new_value"],
                    fontsize=font_size,
                    color=(0, 0, 0)
                )
        
        # Save the filled PDF
        filled_doc.save(output_path)
        filled_doc.close()
        print(f"✅ Filled PDF saved to: {output_path}")
        return output_path

    def create_summary_report(self, output_path="output/form_summary.json"):
        """Create a JSON summary of all form data."""
        summary = {
            "original_pdf": self.pdf_path,
            "processed_fields": len(self.results),
            "form_data": {}
        }
        
        for result in self.results:
            summary["form_data"][result["key"]] = {
                "original_value": result["original_value"],
                "new_value": result["new_value"],
                "ai_question": result["llm_question"]
            }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Summary report saved to: {output_path}")
        return output_path

    def get_kv_map(self, blocks):
        """Extract key-value pairs from Textract blocks."""
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
        """Find the value block associated with a key block."""
        for rel in key_block.get("Relationships", []):
            if rel["Type"] == "VALUE":
                for value_id in rel["Ids"]:
                    if value_id in value_map:
                        return value_map[value_id]
        return None

    def get_text_from_block(self, block, block_map):
        """Extract text from a block and its children."""
        text = ""
        for rel in block.get("Relationships", []):
            if rel["Type"] == "CHILD":
                for child_id in rel["Ids"]:
                    child = block_map.get(child_id, {})
                    if child.get("BlockType") == "WORD":
                        text += child.get("Text", "") + " "
        return text.strip()

    def save_cropped_image(self, page, bbox, output_path):
        """Save a cropped portion of the PDF page as an image."""
        rect = fitz.Rect(
            bbox["Left"] * page.rect.width,
            bbox["Top"] * page.rect.height,
            (bbox["Left"] + bbox["Width"]) * page.rect.width,
            (bbox["Top"] + bbox["Height"]) * page.rect.height
        )
        
        # Get the pixmap of the cropped area
        pix = page.get_pixmap(clip=rect)
        pix.save(output_path)

    def create_visual_overlay(self, output_path="output/analyzed_form.pdf"):
        """Create a visual representation of the form with bounding boxes."""
        if not self.doc:
            return
            
        page = self.doc[0]
        
        # Create a new PDF with the overlay
        packet = BytesIO()
        c = canvas.Canvas(packet, pagesize=(page.rect.width, page.rect.height))
        
        # Draw bounding boxes for each field
        for key_id, response_data in self.user_responses.items():
            # Draw key box in red
            self.draw_bbox(c, response_data["key_bbox"], (1, 0, 0), page.rect, "Field")
            # Draw value box in blue
            self.draw_bbox(c, response_data["value_bbox"], (0, 0, 1), page.rect, "Value")
        
        c.save()
        
        # Merge with original PDF
        packet.seek(0)
        overlay = fitz.open("pdf", packet.getvalue())
        page.show_pdf_page(page.rect, overlay, 0)
        self.doc.save(output_path)
        print(f"📋 Visual analysis saved to: {output_path}")

    def draw_bbox(self, canvas, bbox, color, page_rect, label):
        """Draw a bounding box on the canvas."""
        x1 = bbox["Left"] * page_rect.width
        y1 = (1 - bbox["Top"]) * page_rect.height  # Invert Y coordinate
        x2 = (bbox["Left"] + bbox["Width"]) * page_rect.width
        y2 = (1 - bbox["Top"] - bbox["Height"]) * page_rect.height
        
        r, g, b = color
        canvas.setStrokeColorRGB(r, g, b)
        canvas.setLineWidth(2)
        canvas.rect(x1, y2, x2 - x1, y1 - y2, stroke=1, fill=0)
        
        # Add label
        canvas.setFont("Helvetica-Bold", 8)
        canvas.setFillColorRGB(r, g, b)
        canvas.drawString(x1, y1 + 5, label)

def main():
    """Main function to run the interactive PDF form filler."""
    try:
        print("🚀 Interactive PDF Form Filler")
        print("=" * 50)
        
        # Initialize the form filler
        form_filler = InteractivePDFFormFiller("generated_form.pdf")
        
        # Process the form interactively
        results = form_filler.process_pdf_form()
        
        # Create outputs
        print("\n📂 Creating output files...")
        
        # Create filled PDF
        filled_pdf_path = form_filler.create_filled_pdf()
        
        # Create visual overlay
        form_filler.create_visual_overlay()
        
        # Create summary report
        summary_path = form_filler.create_summary_report()
        
        # Display final summary
        print("\n" + "=" * 60)
        print("📊 FORM FILLING COMPLETE!")
        print("=" * 60)
        print(f"📋 Fields processed: {len(results)}")
        print(f"📄 Filled PDF: {filled_pdf_path}")
        print(f"📊 Summary report: {summary_path}")
        print(f"🔍 Visual analysis: output/analyzed_form.pdf")
        print("\n📝 Form Data Summary:")
        print("-" * 40)
        
        for result in results:
            print(f"• {result['key']}: {result['new_value'] or '(empty)'}")
        
        print("\n✅ All files saved in the 'output' directory!")
        
    except FileNotFoundError:
        print("❌ Error: 'form.pdf' not found in the current directory.")
        print("Please make sure the PDF file exists and try again.")
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")
        print("Please check your AWS credentials and try again.")

if __name__ == "__main__":
    main()