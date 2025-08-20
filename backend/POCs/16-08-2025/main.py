import boto3
import os
import json
from dotenv import load_dotenv
import fitz  # PyMuPDF
from reportlab.pdfgen import canvas
from io import BytesIO
from llm import get_llm_response

# Load environment variables
load_dotenv(dotenv_path="../.env.local")

# Initialize Textract client
textract = boto3.client("textract")

def process_pdf_form(pdf_path):
    """Process a PDF form and extract key-value pairs with visual feedback."""
    # Analyze the document with Textract
    with open(pdf_path, "rb") as f:
        response = textract.analyze_document(
            Document={"Bytes": f.read()},
            FeatureTypes=["FORMS"]
        )
    
    # Process blocks to find key-value pairs
    key_map, value_map, block_map = get_kv_map(response["Blocks"])
    
    # Open the PDF with PyMuPDF for visualization and cropping
    doc = fitz.open(pdf_path)
    page = doc[0]
    
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    
    # Process each key-value pair
    results = []
    for key_id, key_block in key_map.items():
        value_block = find_value_block(key_block, value_map)
        if not value_block:
            continue
            
        # Get key and value text
        key_text = get_text_from_block(key_block, block_map)
        value_text = get_text_from_block(value_block, block_map)
        
        # Save cropped images
        key_img_path = f"output/key_{key_id}.png"
        value_img_path = f"output/value_{key_id}.png"
        
        save_cropped_image(page, key_block["Geometry"]["BoundingBox"], key_img_path)
        save_cropped_image(page, value_block["Geometry"]["BoundingBox"], value_img_path)

        # # get llm response

        # llm_response = get_llm_response(key_img_path, "based on this image, ask question about it? example: text is email, then ask what this your email")
        # # print("llm_response",input(llm_response))
        # user_input = input("Enter your answer: "+llm_response)
        
        results.append({
            "key": key_text,
            "value": value_text,
            "key_image": key_img_path,
            "value_image": value_img_path
        })

    print("key_map",key_map)
    print("value_map",value_map)
    
    # Create a visual representation of the form with bounding boxes
    create_visual_overlay(doc, key_map, value_map, "output/analyzed_form.pdf")
    
    return results

def get_kv_map(blocks):
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

def find_value_block(key_block, value_map):
    """Find the value block associated with a key block."""
    for rel in key_block.get("Relationships", []):
        if rel["Type"] == "VALUE":
            for value_id in rel["Ids"]:
                if value_id in value_map:
                    return value_map[value_id]
    return None

def get_text_from_block(block, block_map):
    """Extract text from a block and its children."""
    text = ""
    for rel in block.get("Relationships", []):
        if rel["Type"] == "CHILD":
            for child_id in rel["Ids"]:
                child = block_map.get(child_id, {})
                if child.get("BlockType") == "WORD":
                    text += child.get("Text", "") + " "
    return text.strip()

def save_cropped_image(page, bbox, output_path):
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

def create_visual_overlay(doc, key_map, value_map, output_path):
    """Create a visual representation of the form with bounding boxes."""
    page = doc[0]
    
    # Create a new PDF with the overlay
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=(page.rect.width, page.rect.height))
    
    # Draw key boxes in red
    for block in key_map.values():
        draw_bbox(c, block["Geometry"]["BoundingBox"], (1, 0, 0), page.rect, "Key")

    question = "what is email?"
    
    # Draw value boxes in blue
    for block in value_map.values():
        draw_bbox(c, block["Geometry"]["BoundingBox"], (0, 0, 1), page.rect, question)
    
    c.save()
    
    # Merge with original PDF
    packet.seek(0)
    overlay = fitz.open("pdf", packet.getvalue())
    page.show_pdf_page(page.rect, overlay, 0)
    doc.save(output_path)
    doc.close()

def draw_bbox(canvas, bbox, color, page_rect, text):
    """Draw a bounding box on the canvas."""
    x1 = bbox["Left"] * page_rect.width
    y1 = (1 - bbox["Top"]) * page_rect.height  # Invert Y coordinate
    x2 = (bbox["Left"] + bbox["Width"]) * page_rect.width
    y2 = (1 - bbox["Top"] - bbox["Height"]) * page_rect.height
    
    r, g, b = color
    canvas.setStrokeColorRGB(r, g, b)
    canvas.setLineWidth(2)
    canvas.rect(x1, y2, x2 - x1, y1 - y2, stroke=1, fill=0)

    # Set font and size
    canvas.setFont("Helvetica-Bold", 8)
    # canvas.drawString(x1, y2, "Key")
    # if text == "Key":
    #     canvas.drawString(x1, y2, "Key")
    if text != "Key":
        canvas.drawString(x1, y1-7, input(f"{text} : "))

if __name__ == "__main__":
    # Process the form and get results
    results = process_pdf_form("form.pdf")
    
    # Print extracted key-value pairs
    print("\nExtracted Form Data:")
    print("-" * 50)
    for item in results:
        print(f"{item['key']}: {item['value']}")
        print(f"  - Key image saved to: {item['key_image']}")
        print(f"  - Value image saved to: {item['value_image']}")
        print("-" * 50)
    
    print("\nAnalysis complete! Check the 'output' directory for results.")
