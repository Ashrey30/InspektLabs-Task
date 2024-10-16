import shutil
import os
import csv
from pdf2image import convert_from_path
from google.cloud import vision
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')

# Define keyword-based categories
keyword_categories = {
    "accident_report": ["TESPIT", "TUTANAGI", "DİKKAT"],
    "alcohol_report": ["Alkol", "Alcovisor"],
    "commitment": ["TAAHHUT", "TESLIM"],
    "declaration": ["MÜDÜRLÜĞÜNE"],
    "driving_licence": ["SÜRÜCÜ BELGESİ", "KİMLİK KARTI", "Rh+"],
    "national_id": ["SÜRÜCÜ BELGESİ", "KİMLİK KARTI", "Rh+"],
    "invoice": ["Fatura"],
    "passport": ["PASSPORT"],
    "police_report": ["KAZANIN", "KAZAYA"],
    "policy": ["Sigorta", "SİGORTA", "SİGORTA POLİÇESİ", "SİGORTALI"],
    "vehicle_id": ["PLAKA", "VERİLDİĞİ"]
}

# Directory for storing images for OCR
image_processing_folder = 'processed_images'

# Google Vision API setup using API key
def get_vision_client(api_key):
    return vision.ImageAnnotatorClient(client_options={"api_key": api_key})

# Function to clean and create a new folder for storing images
def renew_image_folder(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)  # Remove existing folder and its contents
    os.makedirs(folder_path)  # Create a new, empty folder

# Function to convert PDF to images and store them in the specified folder (maintaining folder structure)
def convert_pdf_to_images(pdf_path, output_folder, relative_folder):
    images = convert_from_path(pdf_path, poppler_path=r'C:\poppler-24.07.0\Library\bin')
    image_paths = []
    
    # Create the relative folder structure in the output folder
    output_sub_folder = os.path.join(output_folder, relative_folder)
    if not os.path.exists(output_sub_folder):
        os.makedirs(output_sub_folder)
    
    for i, image in enumerate(images):
        image_name = f'{os.path.splitext(os.path.basename(pdf_path))[0]}_page_{i + 1}.png'
        image_path = os.path.join(output_sub_folder, image_name)
        image.save(image_path, 'PNG')
        image_paths.append(image_path)
    
    return image_paths

# Function to copy original images into the separate folder (maintaining folder structure)
def copy_image_to_folder(image_path, output_folder, relative_folder):
    # Create the relative folder structure in the output folder
    output_sub_folder = os.path.join(output_folder, relative_folder)
    if not os.path.exists(output_sub_folder):
        os.makedirs(output_sub_folder)

    destination = os.path.join(output_sub_folder, os.path.basename(image_path))
    shutil.copy(image_path, destination)

# Function to perform OCR on an image
def ocr_image(image_path, client):
    with open(image_path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    return response.text_annotations[0].description if response.text_annotations else ''

# Function to determine category based on keywords
def determine_category_by_keywords(text):
    for category, keywords in keyword_categories.items():
        if any(keyword.lower() in text.lower() for keyword in keywords):
            return category
    return "Unknown"

# Function to process a folder (images and PDFs)
def process_folder(folder_path, client):
    extracted_data = []

    # Renew the image processing folder to avoid leftover files
    renew_image_folder(image_processing_folder)

    for root, _, files in os.walk(folder_path):
        relative_path = os.path.relpath(root, folder_path)
        folder_name = relative_path.replace(os.sep, '_')

        for file in files:
            file_path = os.path.join(root, file)

            # Convert PDFs to images and store in the image processing folder
            if file.lower().endswith('.pdf'):
                images = convert_pdf_to_images(file_path, image_processing_folder, relative_path)
            # Copy original images (PNG, JPG, JPEG) to the image processing folder
            elif file.lower().endswith(('.png', '.jpg', '.jpeg')):
                copy_image_to_folder(file_path, image_processing_folder, relative_path)

    # Now process the images in the renewed image processing folder for OCR
    for root, _, files in os.walk(image_processing_folder):
        relative_path = os.path.relpath(root, image_processing_folder)
        folder_name = relative_path.replace(os.sep, '_')

        for file in files:
            image_path = os.path.join(root, file)
            text = ocr_image(image_path, client)

            # Classify based on the OCR text
            classified_category = determine_category_by_keywords(text)

            # Add data to the extracted list
            extracted_data.append({
                'Image Name': os.path.basename(file),
                'Original Category': folder_name,
                'Classified Category': classified_category
            })

    return extracted_data

# Write the extracted data to a CSV file
def write_to_csv(data, csv_file):
    fieldnames = ['Image Name', 'Original Category', 'Classified Category']
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for entry in data:
            writer.writerow(entry)

# Main Execution
if __name__ == '__main__':
    client = get_vision_client(api_key)

    # Process folder and write to CSV
    main_folder = '../OCR_Project_Turkey_2024'
    output_csv = 'classification_data.csv'

    classified_data = process_folder(main_folder, client)
    write_to_csv(classified_data, output_csv)
    print(f'Classification complete. Check {output_csv} for results.')
