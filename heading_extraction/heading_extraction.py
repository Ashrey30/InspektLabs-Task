import os
import shutil
import csv
import cv2
from google.cloud import vision
from pdf2image import convert_from_path
import pandas as pd
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Google Vision client
api_key = os.getenv('GOOGLE_API_KEY')
client = vision.ImageAnnotatorClient(client_options={"api_key": api_key})

# Define a regular expression to match only Turkish alphabet characters
turkish_alphabet_regex = re.compile(r'^[A-Za-zÇçĞğİıÖöŞşÜü]+')

# Helper function to perform OCR and extract heading
def extract_heading(image_path):
    with open(image_path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)

    response = client.document_text_detection(image=image)
    texts = response.text_annotations

    if texts:
        full_text = texts[0].description.split('\n')
        for line in full_text:
            clean_line = line.strip()
            if clean_line and turkish_alphabet_regex.match(clean_line):
                return clean_line
    return None

# Convert PDF to images and store them
def convert_pdf_to_images(pdf_path, output_dir):
    images = convert_from_path(pdf_path, poppler_path=r'C:\poppler-24.07.0\Library\bin')
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]

    image_paths = []
    for i, image in enumerate(images):
        image_path = os.path.join(output_dir, f"{base_name}_page_{i + 1}.jpg")
        image.save(image_path, 'JPEG')
        image_paths.append(image_path)

    return image_paths

# Copy folder structure and convert PDFs to images
def copy_structure_and_process_pdfs(input_dir, output_dir):
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    os.makedirs(output_dir, exist_ok=True)

    image_files = []

    for root, dirs, files in os.walk(input_dir):
        relative_path = os.path.relpath(root, input_dir)
        target_dir = os.path.join(output_dir, relative_path)

        os.makedirs(target_dir, exist_ok=True)

        for file in files:
            file_path = os.path.join(root, file)
            if file.lower().endswith(('png', 'jpg', 'jpeg')):
                target_file_path = os.path.join(target_dir, file)
                cv2.imwrite(target_file_path, cv2.imread(file_path))
                image_files.append((target_file_path, relative_path))
            elif file.lower().endswith('pdf'):
                pdf_images = convert_pdf_to_images(file_path, target_dir)
                for img in pdf_images:
                    image_files.append((img, relative_path))

    return image_files

# Main processing function
def process_images_and_extract_headings(input_dir, output_dir, csv_output):
    image_files = copy_structure_and_process_pdfs(input_dir, output_dir)

    extracted_data = []
    for image_file, subfolder in image_files:
        heading = extract_heading(image_file)
        extracted_data.append([os.path.basename(image_file), subfolder, heading])

    df = pd.DataFrame(extracted_data, columns=['File Name', 'Sub-folder', 'Extracted Heading'])
    df.to_csv(csv_output, index=False)
    print(f"Results saved to {csv_output}")

if __name__ == "__main__":
    input_directory = '../OCR_Project_Turkey_2024'
    output_directory = './output'
    csv_output_file = 'extracted_headings.csv'

    process_images_and_extract_headings(input_directory, output_directory, csv_output_file)
