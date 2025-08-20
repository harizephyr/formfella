# pip install boto3 pdf2image pillow
import boto3, time, json
from pdf2image import convert_from_path
import os
from dotenv import load_dotenv
from PIL import ImageDraw

load_dotenv(dotenv_path=".env.local")

textract = boto3.client('textract', region_name='us-east-1', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'), aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))
s3_bucket = "formfella-dev"
s3_key = "uploads/sample.pdf"

def start_analysis(bucket, key):
    resp = textract.start_document_analysis(
        DocumentLocation={'S3Object': {'Bucket': bucket, 'Name': key}},
        FeatureTypes=['FORMS','TABLES']
    )
    return resp['JobId']

def is_job_complete(job_id):
    resp = textract.get_document_analysis(JobId=job_id)
    status = resp['JobStatus']
    return status, resp

def poll_job(job_id, wait=5):
    while True:
        status, resp = is_job_complete(job_id)
        print("Status:", status)
        if status in ('SUCCEEDED','FAILED'):
            return resp
        time.sleep(wait)

def normalized_to_pixels(box, img_w, img_h):
    left = box['Left']; top = box['Top']; w = box['Width']; h = box['Height']
    x = int(left * img_w)
    y = int(top  * img_h)
    wpx = int(w * img_w)
    hpx = int(h * img_h)
    return x, y, wpx, hpx

if __name__ == "__main__":
    job_id = start_analysis(s3_bucket, s3_key)
    print("Started Textract job:", job_id)
    # poll
    result = poll_job(job_id)
    blocks = result.get('Blocks', [])
    # render first PDF page to image to know img_w/img_h (pick DPI you want)
    s3 = boto3.client('s3')
    s3.download_file(s3_bucket, s3_key, 'sample.pdf')
    
    pages = convert_from_path('sample.pdf', dpi=300)  # local copy of the same S3 pdf
    img_w, img_h = pages[0].size
    # Create a drawing context
    draw = ImageDraw.Draw(pages[0])
    for b in blocks:
        if b['BlockType'] in ('LINE','WORD','KEY_VALUE_SET','CELL'):
            geom = b.get('Geometry',{})
            bbox = geom.get('BoundingBox')
            if bbox:
                x,y,wpx,hpx = normalized_to_pixels(bbox, img_w, img_h)
                print(f"Page {b.get('Page',1)} BlockType={b['BlockType']} text={b.get('Text')} bbox_px={(x,y,wpx,hpx)}")
                if b['BlockType'] == 'KEY_VALUE_SET':                
                    # render the bbox on image using the drawing context
                    draw.line([(x, y), (x + wpx, y)], fill='red', width=2)  # top
                    draw.line([(x, y), (x, y + hpx)], fill='red', width=2)  # left
                    draw.line([(x + wpx, y), (x + wpx, y + hpx)], fill='red', width=2)  # right
                    draw.line([(x, y + hpx), (x + wpx, y + hpx)], fill='red', width=2)  # bottom
    
    pages[0].save("output.pdf")
    os.remove('sample.pdf')
    print("Done")



# # pip install boto3 pdf2image pillow
# import boto3, time, json
# from pdf2image import convert_from_path
# import os
# from dotenv import load_dotenv

# load_dotenv(dotenv_path=".env.local")

# textract = boto3.client('textract', 
#                        region_name='us-east-1',
#                        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
#                        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))

# s3_bucket = "formfella-dev"
# s3_key = "uploads/ForeignLLC.pdf"

# def start_analysis(bucket, key):
#     resp = textract.start_document_analysis(
#         DocumentLocation={'S3Object': {'Bucket': bucket, 'Name': key}},
#         FeatureTypes=['FORMS','TABLES']
#     )
#     return resp['JobId']

# def is_job_complete(job_id):
#     resp = textract.get_document_analysis(JobId=job_id)
#     status = resp['JobStatus']
#     return status, resp

# def poll_job(job_id, wait=5):
#     while True:
#         status, resp = is_job_complete(job_id)
#         print("Status:", status)
#         if status in ('SUCCEEDED','FAILED'):
#             return resp
#         time.sleep(wait)

# def normalized_to_pixels(box, img_w, img_h):
#     left = box['Left']; top = box['Top']; w = box['Width']; h = box['Height']
#     x = int(left * img_w)
#     y = int(top * img_h)
#     wpx = int(w * img_w)
#     hpx = int(h * img_h)
#     return x, y, wpx, hpx

# def extract_fillable_fields(blocks, img_w, img_h):
#     """Extract coordinates of fillable form fields (VALUE parts of key-value pairs)"""
    
#     # Create a map of block IDs to blocks for easy lookup
#     block_map = {block['Id']: block for block in blocks}
#     fillable_fields = []
    
#     for block in blocks:
#         if block['BlockType'] == 'KEY_VALUE_SET':
#             entity_type = block.get('EntityTypes', [])
            
#             # We want VALUE blocks (the fillable parts)
#             if 'VALUE' in entity_type:
#                 geom = block.get('Geometry', {})
#                 bbox = geom.get('BoundingBox')
                
#                 if bbox:
#                     x, y, wpx, hpx = normalized_to_pixels(bbox, img_w, img_h)
                    
#                     # Get the text content if any
#                     text_content = ""
#                     relationships = block.get('Relationships', [])
                    
#                     for relationship in relationships:
#                         if relationship['Type'] == 'CHILD':
#                             for child_id in relationship['Ids']:
#                                 child_block = block_map.get(child_id)
#                                 if child_block and child_block.get('Text'):
#                                     text_content += child_block['Text'] + " "
                    
#                     text_content = text_content.strip()
                    
#                     # Find the corresponding KEY for context
#                     key_text = ""
#                     for relationship in relationships:
#                         if relationship['Type'] == 'VALUE':
#                             # This VALUE is connected to some KEY
#                             for parent_block in blocks:
#                                 if (parent_block['BlockType'] == 'KEY_VALUE_SET' and 
#                                     'KEY' in parent_block.get('EntityTypes', [])):
                                    
#                                     parent_relationships = parent_block.get('Relationships', [])
#                                     for parent_rel in parent_relationships:
#                                         if (parent_rel['Type'] == 'VALUE' and 
#                                             block['Id'] in parent_rel.get('Ids', [])):
#                                             # Found the parent KEY
#                                             key_relationships = parent_block.get('Relationships', [])
#                                             for key_rel in key_relationships:
#                                                 if key_rel['Type'] == 'CHILD':
#                                                     for key_child_id in key_rel['Ids']:
#                                                         key_child = block_map.get(key_child_id)
#                                                         if key_child and key_child.get('Text'):
#                                                             key_text += key_child['Text'] + " "
#                                             break
                    
#                     key_text = key_text.strip()
                    
#                     fillable_fields.append({
#                         'page': block.get('Page', 1),
#                         'field_label': key_text,
#                         'current_value': text_content,
#                         'coordinates': (x, y, wpx, hpx),
#                         'is_empty': len(text_content) == 0
#                     })
    
#     return fillable_fields

# def detect_empty_checkboxes_and_fields(blocks, img_w, img_h):
#     """Additional method to detect likely empty form fields based on size and position"""
    
#     potential_fields = []
    
#     for block in blocks:
#         if block['BlockType'] == 'SELECTION_ELEMENT':
#             # These are checkboxes/radio buttons
#             geom = block.get('Geometry', {})
#             bbox = geom.get('BoundingBox')
            
#             if bbox:
#                 x, y, wpx, hpx = normalized_to_pixels(bbox, img_w, img_h)
#                 selection_status = block.get('SelectionStatus', 'NOT_SELECTED')
                
#                 potential_fields.append({
#                     'page': block.get('Page', 1),
#                     'type': 'checkbox/radio',
#                     'status': selection_status,
#                     'coordinates': (x, y, wpx, hpx),
#                     'confidence': block.get('Confidence', 0)
#                 })
    
#     return potential_fields

# if __name__ == "__main__":
#     job_id = start_analysis(s3_bucket, s3_key)
#     print("Started Textract job:", job_id)
    
#     # Poll for completion
#     result = poll_job(job_id)
#     blocks = result.get('Blocks', [])
    
#     # Render first PDF page to image to know dimensions
#     pages = convert_from_path('ForeignLLC.pdf', dpi=300)  # local copy of the same S3 pdf
#     img_w, img_h = pages[0].size
    
#     # Extract fillable form fields
#     fillable_fields = extract_fillable_fields(blocks, img_w, img_h)
    
#     print("\n=== FILLABLE FORM FIELDS ===")
#     for field in fillable_fields:
#         print(f"Page {field['page']}: '{field['field_label']}' -> '{field['current_value']}' at {field['coordinates']} {'(EMPTY)' if field['is_empty'] else ''}")
    
#     # Also detect checkboxes/selection elements
#     selection_elements = detect_empty_checkboxes_and_fields(blocks, img_w, img_h)
    
#     print("\n=== CHECKBOXES/SELECTION ELEMENTS ===")
#     for element in selection_elements:
#         print(f"Page {element['page']}: {element['type']} - {element['status']} at {element['coordinates']}")
    
#     # If you want only empty fields (likely what users need to fill):
#     empty_fields = [field for field in fillable_fields if field['is_empty']]
#     unselected_checkboxes = [elem for elem in selection_elements if elem['status'] == 'NOT_SELECTED']
    
#     print(f"\n=== SUMMARY ===")
#     print(f"Total fillable text fields found: {len(fillable_fields)}")
#     print(f"Empty text fields: {len(empty_fields)}")
#     print(f"Unselected checkboxes: {len(unselected_checkboxes)}")
    
#     # Export coordinates for empty/unfilled fields only
#     user_fillable_coordinates = []
    
#     for field in empty_fields:
#         user_fillable_coordinates.append({
#             'type': 'text_field',
#             'label': field['field_label'],
#             'page': field['page'],
#             'coordinates': field['coordinates']
#         })
    
#     for element in unselected_checkboxes:
#         user_fillable_coordinates.append({
#             'type': 'checkbox',
#             'page': element['page'],
#             'coordinates': element['coordinates']
#         })
    
#     print(f"\nCoordinates for user to fill: {len(user_fillable_coordinates)} fields")
    
#     # Save to JSON file for easy use
#     with open('fillable_coordinates.json', 'w') as f:
#         json.dump(user_fillable_coordinates, f, indent=2)
    
#     print("Saved fillable coordinates to 'fillable_coordinates.json'")



# # pip install boto3 pdf2image pillow reportlab PyPDF2
# import boto3, time, json
# from pdf2image import convert_from_path
# import os
# from dotenv import load_dotenv
# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import letter
# from PyPDF2 import PdfReader, PdfWriter
# import io

# load_dotenv(dotenv_path=".env.local")

# textract = boto3.client('textract', 
#                        region_name='us-east-1',
#                        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
#                        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))

# s3_bucket = "formfella-dev"
# s3_key = "uploads/sample.pdf"

# def start_analysis(bucket, key):
#     resp = textract.start_document_analysis(
#         DocumentLocation={'S3Object': {'Bucket': bucket, 'Name': key}},
#         FeatureTypes=['FORMS','TABLES']
#     )
#     return resp['JobId']

# def is_job_complete(job_id):
#     resp = textract.get_document_analysis(JobId=job_id)
#     status = resp['JobStatus']
#     return status, resp

# def poll_job(job_id, wait=5):
#     while True:
#         status, resp = is_job_complete(job_id)
#         print("Status:", status)
#         if status in ('SUCCEEDED','FAILED'):
#             return resp
#         time.sleep(wait)

# def normalized_to_pixels(box, img_w, img_h):
#     left = box['Left']; top = box['Top']; w = box['Width']; h = box['Height']
#     x = int(left * img_w)
#     y = int(top * img_h)
#     wpx = int(w * img_w)
#     hpx = int(h * img_h)
#     return x, y, wpx, hpx

# def get_context_lines(target_block, blocks, block_map, context_range=3):
#     """Get text from lines above and below the target block for context"""
#     target_page = target_block.get('Page', 1)
#     target_bbox = target_block.get('Geometry', {}).get('BoundingBox', {})
#     target_top = target_bbox.get('Top', 0)
    
#     # Get all LINE blocks from the same page
#     page_lines = []
#     for block in blocks:
#         if (block['BlockType'] == 'LINE' and 
#             block.get('Page', 1) == target_page):
#             line_bbox = block.get('Geometry', {}).get('BoundingBox', {})
#             line_top = line_bbox.get('Top', 0)
#             line_text = block.get('Text', '').strip()
#             if line_text:  # Only include non-empty lines
#                 page_lines.append({
#                     'text': line_text,
#                     'top': line_top,
#                     'block': block
#                 })
    
#     # Sort lines by their vertical position (top to bottom)
#     page_lines.sort(key=lambda x: x['top'])
    
#     # Find lines around the target position
#     context_lines = []
#     for i, line in enumerate(page_lines):
#         # If this line is close to our target area
#         if abs(line['top'] - target_top) < 0.1:  # Within 10% of page height
#             # Get context lines before and after
#             start_idx = max(0, i - context_range)
#             end_idx = min(len(page_lines), i + context_range + 1)
            
#             for j in range(start_idx, end_idx):
#                 if j < len(page_lines):
#                     context_lines.append(page_lines[j]['text'])
#             break
    
#     return context_lines

# def extract_fillable_fields(blocks, img_w, img_h):
#     """Extract coordinates of fillable form fields (VALUE parts of key-value pairs)"""
    
#     # Create a map of block IDs to blocks for easy lookup
#     block_map = {block['Id']: block for block in blocks}
#     fillable_fields = []
    
#     for block in blocks:
#         if block['BlockType'] == 'KEY_VALUE_SET':
#             entity_type = block.get('EntityTypes', [])
            
#             # We want VALUE blocks (the fillable parts)
#             if 'VALUE' in entity_type:
#                 geom = block.get('Geometry', {})
#                 bbox = geom.get('BoundingBox')
                
#                 if bbox:
#                     x, y, wpx, hpx = normalized_to_pixels(bbox, img_w, img_h)
                    
#                     # Get the text content if any
#                     text_content = ""
#                     relationships = block.get('Relationships', [])
                    
#                     for relationship in relationships:
#                         if relationship['Type'] == 'CHILD':
#                             for child_id in relationship['Ids']:
#                                 child_block = block_map.get(child_id)
#                                 if child_block and child_block.get('Text'):
#                                     text_content += child_block['Text'] + " "
                    
#                     text_content = text_content.strip()
                    
#                     # Find the corresponding KEY for context
#                     key_text = ""
#                     for relationship in relationships:
#                         if relationship['Type'] == 'VALUE':
#                             # This VALUE is connected to some KEY
#                             for parent_block in blocks:
#                                 if (parent_block['BlockType'] == 'KEY_VALUE_SET' and 
#                                     'KEY' in parent_block.get('EntityTypes', [])):
                                    
#                                     parent_relationships = parent_block.get('Relationships', [])
#                                     for parent_rel in parent_relationships:
#                                         if (parent_rel['Type'] == 'VALUE' and 
#                                             block['Id'] in parent_rel.get('Ids', [])):
#                                             # Found the parent KEY
#                                             key_relationships = parent_block.get('Relationships', [])
#                                             for key_rel in key_relationships:
#                                                 if key_rel['Type'] == 'CHILD':
#                                                     for key_child_id in key_rel['Ids']:
#                                                         key_child = block_map.get(key_child_id)
#                                                         if key_child and key_child.get('Text'):
#                                                             key_text += key_child['Text'] + " "
#                                             break
                    
#                     key_text = key_text.strip()
                    
#                     # Get context lines around this field
#                     context_lines = get_context_lines(block, blocks, block_map)
                    
#                     fillable_fields.append({
#                         'page': block.get('Page', 1),
#                         'field_label': key_text,
#                         'current_value': text_content,
#                         'coordinates': (x, y, wpx, hpx),
#                         'is_empty': len(text_content) == 0,
#                         'context_lines': context_lines,
#                         'block': block
#                     })
    
#     return fillable_fields

# def detect_empty_checkboxes_and_fields(blocks, img_w, img_h):
#     """Additional method to detect likely empty form fields based on size and position"""
    
#     potential_fields = []
    
#     for block in blocks:
#         if block['BlockType'] == 'SELECTION_ELEMENT':
#             # These are checkboxes/radio buttons
#             geom = block.get('Geometry', {})
#             bbox = geom.get('BoundingBox')
            
#             if bbox:
#                 x, y, wpx, hpx = normalized_to_pixels(bbox, img_w, img_h)
#                 selection_status = block.get('SelectionStatus', 'NOT_SELECTED')
                
#                 potential_fields.append({
#                     'page': block.get('Page', 1),
#                     'type': 'checkbox/radio',
#                     'status': selection_status,
#                     'coordinates': (x, y, wpx, hpx),
#                     'confidence': block.get('Confidence', 0)
#                 })
    
#     return potential_fields

# def interactive_form_filling(fillable_fields, selection_elements):
#     """Interactively ask user to fill form fields with context"""
    
#     filled_data = []
    
#     print("\n" + "="*60)
#     print("INTERACTIVE FORM FILLING")
#     print("="*60)
#     print("I'll show you each empty field with context to help you understand what to fill.")
#     print("Press Enter to skip a field, or type 'quit' to stop.\n")
    
#     # Process empty text fields
#     empty_fields = [field for field in fillable_fields if field['is_empty']]
    
#     for i, field in enumerate(empty_fields, 1):
#         print(f"\n--- Field {i}/{len(empty_fields)} (Page {field['page']}) ---")
        
#         # Show context lines
#         if field['context_lines']:
#             print("📄 Context from document:")
#             for j, line in enumerate(field['context_lines']):
#                 # Highlight the line that likely contains our field label
#                 if field['field_label'].lower() in line.lower():
#                     print(f"  ➤ {line}")
#                 else:
#                     print(f"    {line}")
        
#         # Show field label if available
#         if field['field_label']:
#             print(f"\n🏷️  Field Label: '{field['field_label']}'")
        
#         print(f"📍 Location: {field['coordinates']} (x, y, width, height)")
        
#         # Ask for input
#         user_input = input(f"\n✏️  Enter value for this field (or press Enter to skip): ").strip()
        
#         if user_input.lower() == 'quit':
#             print("Stopping form filling...")
#             break
        
#         if user_input:
#             filled_data.append({
#                 'type': 'text_field',
#                 'field_label': field['field_label'],
#                 'page': field['page'],
#                 'coordinates': field['coordinates'],
#                 'user_value': user_input,
#                 'context_lines': field['context_lines']
#             })
#             print(f"✅ Saved: '{user_input}'")
#         else:
#             print("⏭️  Skipped")
    
#     # Process unselected checkboxes if any
#     unselected_checkboxes = [elem for elem in selection_elements if elem['status'] == 'NOT_SELECTED']
    
#     if unselected_checkboxes:
#         print(f"\n--- CHECKBOXES/SELECTION ELEMENTS ---")
#         print(f"Found {len(unselected_checkboxes)} unselected checkboxes.")
        
#         for i, element in enumerate(unselected_checkboxes, 1):
#             print(f"\nCheckbox {i} (Page {element['page']}) at {element['coordinates']}")
            
#             should_select = input("Select this checkbox? (y/n or Enter to skip): ").strip().lower()
            
#             if should_select == 'quit':
#                 break
#             elif should_select in ['y', 'yes']:
#                 filled_data.append({
#                     'type': 'checkbox',
#                     'page': element['page'],
#                     'coordinates': element['coordinates'],
#                     'user_value': True
#                 })
#                 print("✅ Checkbox will be selected")
#             else:
#                 print("⏭️  Checkbox skipped")
    
# def create_filled_pdf(original_pdf_path, filled_data, output_path):
#     """Create a new PDF with filled form data overlaid on the original"""
    
#     # Read the original PDF
#     reader = PdfReader(original_pdf_path)
#     writer = PdfWriter()
    
#     # Get page dimensions from the first page
#     first_page = reader.pages[0]
#     page_width = float(first_page.mediabox.width)
#     page_height = float(first_page.mediabox.height)
    
#     # Group filled data by page
#     data_by_page = {}
#     for item in filled_data:
#         page_num = item['page']
#         if page_num not in data_by_page:
#             data_by_page[page_num] = []
#         data_by_page[page_num].append(item)
    
#     # Process each page
#     for page_num in range(len(reader.pages)):
#         original_page = reader.pages[page_num]
        
#         # Check if this page has any filled data
#         current_page_num = page_num + 1  # PDF pages are 1-indexed in our data
#         if current_page_num in data_by_page:
#             # Create overlay with text
#             overlay_buffer = io.BytesIO()
#             overlay_canvas = canvas.Canvas(overlay_buffer, pagesize=(page_width, page_height))
            
#             # Add filled text to overlay
#             for item in data_by_page[current_page_num]:
#                 if item['type'] == 'text_field' and 'user_value' in item:
#                     x, y, width, height = item['coordinates']
                    
#                     # Convert coordinates - PDF coordinate system has origin at bottom-left
#                     pdf_x = x
#                     pdf_y = page_height - y - height
                    
#                     # Set font and size
#                     font_size = min(height * 0.8, 12)  # Scale font to fit field height
#                     overlay_canvas.setFont("Helvetica", font_size)
                    
#                     # Draw the text
#                     overlay_canvas.drawString(pdf_x + 2, pdf_y + height/2 - font_size/2, 
#                                             str(item['user_value']))
                
#                 elif item['type'] == 'checkbox' and item.get('user_value'):
#                     x, y, width, height = item['coordinates']
#                     pdf_x = x
#                     pdf_y = page_height - y - height
                    
#                     # Draw checkmark
#                     overlay_canvas.setFont("Helvetica", min(height * 0.8, 12))
#                     overlay_canvas.drawString(pdf_x + width/4, pdf_y + height/4, "✓")
            
#             overlay_canvas.save()
#             overlay_buffer.seek(0)
            
#             # Create overlay PDF
#             overlay_pdf = PdfReader(overlay_buffer)
#             overlay_page = overlay_pdf.pages[0]
            
#             # Merge overlay with original page
#             original_page.merge_page(overlay_page)
        
#         # Add page to writer
#         writer.add_page(original_page)
    
#     # Write the final PDF
#     with open(output_path, 'wb') as output_file:
#         writer.write(output_file)
    
#     print(f"📄 Filled PDF saved as: {output_path}")
#     return output_path

# def create_filled_pdf_advanced(original_pdf_path, filled_data, pages_info, output_path):
#     """Create filled PDF with better coordinate mapping using page dimensions from pdf2image"""
    
#     reader = PdfReader(original_pdf_path)
#     writer = PdfWriter()
    
#     # Group filled data by page
#     data_by_page = {}
#     for item in filled_data:
#         page_num = item['page']
#         if page_num not in data_by_page:
#             data_by_page[page_num] = []
#         data_by_page[page_num].append(item)
    
#     # Process each page
#     for page_num in range(len(reader.pages)):
#         original_page = reader.pages[page_num]
#         pdf_page_width = float(original_page.mediabox.width)
#         pdf_page_height = float(original_page.mediabox.height)
        
#         current_page_num = page_num + 1
        
#         if current_page_num in data_by_page and current_page_num <= len(pages_info):
#             # Get image dimensions for coordinate conversion
#             img_width, img_height = pages_info[page_num].size
            
#             overlay_buffer = io.BytesIO()
#             overlay_canvas = canvas.Canvas(overlay_buffer, pagesize=(pdf_page_width, pdf_page_height))
            
#             for item in data_by_page[current_page_num]:
#                 if item['type'] == 'text_field' and 'user_value' in item:
#                     img_x, img_y, img_w, img_h = item['coordinates']
                    
#                     # Convert from image coordinates to PDF coordinates
#                     pdf_x = (img_x / img_width) * pdf_page_width
#                     pdf_y = pdf_page_height - ((img_y + img_h) / img_height) * pdf_page_height
#                     pdf_w = (img_w / img_width) * pdf_page_width
#                     pdf_h = (img_h / img_height) * pdf_page_height
                    
#                     # Set appropriate font size
#                     font_size = min(pdf_h * 0.7, 12)
#                     overlay_canvas.setFont("Helvetica", font_size)
                    
#                     # Draw text with proper positioning
#                     text_y = pdf_y + (pdf_h - font_size) / 2
#                     overlay_canvas.drawString(pdf_x + 2, text_y, str(item['user_value']))
                
#                 elif item['type'] == 'checkbox' and item.get('user_value'):
#                     img_x, img_y, img_w, img_h = item['coordinates']
                    
#                     pdf_x = (img_x / img_width) * pdf_page_width
#                     pdf_y = pdf_page_height - ((img_y + img_h) / img_height) * pdf_page_height
#                     pdf_w = (img_w / img_width) * pdf_page_width
#                     pdf_h = (img_h / img_height) * pdf_page_height
                    
#                     # Draw checkmark
#                     check_size = min(pdf_h * 0.8, 10)
#                     overlay_canvas.setFont("Helvetica-Bold", check_size)
#                     overlay_canvas.drawString(pdf_x + pdf_w/4, pdf_y + pdf_h/4, "✓")
            
#             overlay_canvas.save()
#             overlay_buffer.seek(0)
            
#             # Merge overlay
#             overlay_pdf = PdfReader(overlay_buffer)
#             original_page.merge_page(overlay_pdf.pages[0])
        
#         writer.add_page(original_page)
    
#     # Save final PDF
#     with open(output_path, 'wb') as output_file:
#         writer.write(output_file)
    
#     return output_path

# if __name__ == "__main__":
#     job_id = start_analysis(s3_bucket, s3_key)
#     print("Started Textract job:", job_id)
    
#     # Poll for completion
#     result = poll_job(job_id)
#     blocks = result.get('Blocks', [])
    
#     # Render first PDF page to image to know dimensions
#     pages = convert_from_path('sample.pdf', dpi=300)  # local copy of the same S3 pdf
#     img_w, img_h = pages[0].size
    
#     # Extract fillable form fields
#     fillable_fields = extract_fillable_fields(blocks, img_w, img_h)
    
#     # Also detect checkboxes/selection elements
#     selection_elements = detect_empty_checkboxes_and_fields(blocks, img_w, img_h)
    
#     # Show summary
#     empty_fields = [field for field in fillable_fields if field['is_empty']]
#     unselected_checkboxes = [elem for elem in selection_elements if elem['status'] == 'NOT_SELECTED']
    
#     print(f"\n=== FORM ANALYSIS SUMMARY ===")
#     print(f"📊 Total fillable text fields found: {len(fillable_fields)}")
#     print(f"📝 Empty text fields: {len(empty_fields)}")
#     print(f"☐  Unselected checkboxes: {len(unselected_checkboxes)}")
    
#     if len(empty_fields) == 0 and len(unselected_checkboxes) == 0:
#         print("\n🎉 No empty fields found! The form appears to be already filled.")
#         exit()
    
#     # Interactive form filling
#     user_data = interactive_form_filling(fillable_fields, selection_elements)
    
#     # Save results
#     if user_data:
#         print(f"\n🎉 Form filling complete! Collected {len(user_data)} field values.")
        
#         # Save to JSON file
#         output_data = {
#             'filled_fields': user_data,
#             'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
#             'source_document': s3_key
#         }
        
#         with open('filled_form_data.json', 'w') as f:
#             json.dump(output_data, f, indent=2)
        
#         print("💾 Saved filled form data to 'filled_form_data.json'")
        
#         # CREATE THE FILLED PDF
#         try:
#             output_pdf_path = 'sample_FILLED.pdf'
#             create_filled_pdf_advanced('sample.pdf', user_data, pages, output_pdf_path)
#             print(f"✅ Created filled PDF: {output_pdf_path}")
#         except Exception as e:
#             print(f"❌ Error creating filled PDF: {e}")
#             print("📋 But your form data is saved in the JSON file.")
        
#         # Print summary
#         print("\n📋 FILLED DATA SUMMARY:")
#         for item in user_data:
#             if item['type'] == 'text_field':
#                 print(f"  📝 '{item['field_label']}' = '{item['user_value']}'")
#             elif item['type'] == 'checkbox':
#                 print(f"  ☑️  Checkbox at page {item['page']} = Selected")
#     else:
#         print("\n🤷 No data was entered.")
    
#     print("\n✨ Done!")
