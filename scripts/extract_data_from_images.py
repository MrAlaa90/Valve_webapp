import os
import csv
import re
import sys
from PIL import Image
import pytesseract

# You might need to point to your tesseract executable if it's not in your PATH
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_value(text, pattern):
    """
    Extracts a value based on a regex pattern.
    """
    match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
    if match:
        return match.group(1).strip()
    return ""

def process_images(root_dir, output_csv):
    """
    Walks through the directory structure, OCRs images, and extracts data.
    """
    
    headers = [
        'tag_number',
        'Shut-off Pressures P1 / P2',
        'Power Failure Pos.',
        'Manufacturer / Model',
        'Body Style',
        'Required Travel / Angle',
        'Bench Range'
    ]

    extracted_data = []
    
    # Walk through the directory
    # Expected: root_dir/TAG_NUMBER/Valves_Specs/image.jpg
    
    print(f"Scanning directory: {root_dir}")
    
    for tag_folder in os.listdir(root_dir):
        tag_path = os.path.join(root_dir, tag_folder)
        
        if not os.path.isdir(tag_path):
            continue
            
        # The tag number is the folder name
        tag_number = tag_folder
        
        specs_dir = os.path.join(tag_path, "Valves_Specs")
        if not os.path.exists(specs_dir):
            continue
            
        for file in os.listdir(specs_dir):
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_path = os.path.join(specs_dir, file)
                print(f"Processing {tag_number} - {file}...")
                
                try:
                    text = pytesseract.image_to_string(Image.open(image_path))
                    
                    # Normalize text for easier matching (optional)
                    # text = text.replace('\n', ' ')
                    
                    # Extract fields using Regex
                    # Note: These regexes assume the format is roughly "Label: Value" or "Label Value"
                    # We might need to adjust based on actual OCR output.
                    
                    row = {'tag_number': tag_number}
                    
                    # 1. Shut-off Pressures P1 / P2
                    # Patterns can be tricky. Looking for "Shut-off Pressures" then some value until newline or next label
                    row['Shut-off Pressures P1 / P2'] = extract_value(text, r"Shut-off Pressures.*?[:\s]+(.*?)(?:\n|$)")
                    
                    # 2. Power Failure Pos.
                    row['Power Failure Pos.'] = extract_value(text, r"Power Failure Pos.*?[:\s]+(.*?)(?:\n|$)")
                    
                    # 3. Manufacturer / Model
                    row['Manufacturer / Model'] = extract_value(text, r"Manufacturer.*?Model.*?[:\s]+(.*?)(?:\n|$)")
                    
                    # 4. Body Style
                    row['Body Style'] = extract_value(text, r"Body Style.*?[:\s]+(.*?)(?:\n|$)")
                    
                    # 5. Required Travel / Angle
                    row['Required Travel / Angle'] = extract_value(text, r"Required Travel.*?Angle.*?[:\s]+(.*?)(?:\n|$)")
                    
                    # 6. Bench Range
                    row['Bench Range'] = extract_value(text, r"Bench Range.*?[:\s]+(.*?)(?:\n|$)")
                    
                    extracted_data.append(row)
                    
                    # Assuming one spec sheet per tag, we can break after finding one.
                    # If there are multiple pages, we might need to concat text.
                    # For now, let's assume the first image has the data or we just process all and take the last (or merge).
                    # Let's break for now to avoid duplicates if there are multiple images for the same thing.
                    break 
                    
                except Exception as e:
                    print(f"Error processing {image_path}: {e}")

    # Write to CSV
    print(f"Writing results to {output_csv}...")
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(extracted_data)

    print("Done.")

if __name__ == "__main__":
    # Adjust paths relative to where the script is run
    base_dir = os.getcwd()
    media_root = os.path.join(base_dir, "media", "AFC 3", "Valves Specs")
    output_file = os.path.join(base_dir, "extracted_data_afc3.csv")
    
    if not os.path.exists(media_root):
        print(f"Error: Directory not found: {media_root}")
        sys.exit(1)
        
    process_images(media_root, output_file)
