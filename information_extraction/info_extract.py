import os
import shutil
import csv
from dotenv import load_dotenv
import openai
from pdf2image import convert_from_path
from PIL import Image

# Load API key from .env file
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# Function to create output directory structure
def create_output_directory_structure(input_dir, output_dir):
    if not os.path.exists(output_dir):
        shutil.copytree(input_dir, output_dir, ignore=shutil.ignore_patterns('*.pdf', '*.jpg', '*.png'))

# Function to convert PDFs to images
def convert_pdf_to_images(pdf_path, output_dir):
    images = convert_from_path(pdf_path)
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    pdf_output_dir = os.path.join(output_dir, pdf_name)
    os.makedirs(pdf_output_dir, exist_ok=True)
    image_paths = []
    for i, image in enumerate(images):
        image_path = os.path.join(pdf_output_dir, f"{pdf_name}_page_{i+1}.png")
        image.save(image_path, 'PNG')
        image_paths.append(image_path)
    return image_paths

# Function to process images using GPT-4 API
def extract_information_from_image(image_path):
    with open(image_path, 'rb') as image_file:
        image_data = image_file.read()

    # Replace the below completion call with GPT-4 multimodal if supported
    prompt = '''
    You are an information extractor. Your task is to extract information from the provided image.
    Given below is a list of fields that you are supposed to extract information for:
    
    fields = ["Poliçe No", "Başlangıç Tarihi", "Bitiş Tarihi", "Sigortalının Adı Soyadı", "Marka", "Marka Tipi", "Model", "Plaka No", "Model Yılı", "Şasi No", "Adı Soyadı", "Adı", "Soyadı", "Şase No", "T.C. KİMLİK NO", "Acente No", "Belge No", "Tedarikçi Unvan", "Tedarikçi Adres", "Tedarikçi Tel", "Tedarikçi Vergi Dairesi", "Tedarikçi VKN", "Tedarikçi SICIL NO", "Tedarikçi MERSIS NO", "Müşteri UNVAN/ AD SOYAD", "TC.KN/ VKN", "Senaryo", "Fatura Tipi", "Fatura No", "Tarihi", "Fatura Saati", "Vade Tarihi", "Ürün Kodu", "Mal Hizmet", "Miktar", "Birim Fiyat", "İsk % İskonto Tutarı", "KDV %", "KDV Tutarı", "Mal Hizmet Tutarı", "Mal Hizmet Toplam Tutarı", "Toplam İskonto", "Matrah", "KDV %20", "Vergiler Dahil Toplam Tutar", "Ödenecek Tutar", "Açıklama"]

    The images provided to you are for Turkish Documents. So work accordingly.
    All these fields may or may not be present in the provided image.
    Carefully analyze the image to extract the correct information.

    OUTPUT FORMAT:
    {
    Poliçe No : <value>,
    Başlangıç Tarihi : <value>,
    Adi : <value>,
    .... and so on.
    }

    Strictly follow the output format.
    '''
    
    # Call GPT with both the image and the prompt
    response = openai.Image.create_completion(
        prompt=prompt,
        file=image_data,
        max_tokens=1000
    )
    
    return response['choices'][0]['text'].strip()

# Function to write data to CSV
def write_to_csv(file_name, extracted_data, csv_writer, fields):
    row = [file_name] + [extracted_data.get(field, '') for field in fields]
    csv_writer.writerow(row)

# Main function to process folder and extract data
def process_folder(input_folder, output_folder, csv_file):
    fields = ["Poliçe No", "Başlangıç Tarihi", "Bitiş Tarihi", "Sigortalının Adı Soyadı", "Marka", "Marka Tipi", "Model", "Plaka No", "Model Yılı", "Şasi No", "Adı Soyadı", "Adı", "Soyadı", "Şase No", "T.C. KİMLİK NO", "Acente No", "Belge No", "Tedarikçi Unvan", "Tedarikçi Adres", "Tedarikçi Tel", "Tedarikçi Vergi Dairesi", "Tedarikçi VKN", "Tedarikçi SICIL NO", "Tedarikçi MERSIS NO", "Müşteri UNVAN/ AD SOYAD", "TC.KN/ VKN", "Senaryo", "Fatura Tipi", "Fatura No", "Tarihi", "Fatura Saati", "Vade Tarihi", "Ürün Kodu", "Mal Hizmet", "Miktar", "Birim Fiyat", "İsk % İskonto Tutarı", "KDV %", "KDV Tutarı", "Mal Hizmet Tutarı", "Mal Hizmet Toplam Tutarı", "Toplam İskonto", "Matrah", "KDV %20", "Vergiler Dahil Toplam Tutar", "Ödenecek Tutar", "Açıklama"]

    # Create directory structure
    create_output_directory_structure(input_folder, output_folder)

    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(['File Name'] + fields)

        for root, _, files in os.walk(input_folder):
            for file in files:
                file_path = os.path.join(root, file)
                # Process PDFs
                if file.lower().endswith('.pdf'):
                    pdf_images = convert_pdf_to_images(file_path, output_folder)
                    for image in pdf_images:
                        extracted_data = extract_information_from_image(image)
                        write_to_csv(os.path.basename(image), extracted_data, csv_writer)

                # Process images
                elif file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    output_image_path = os.path.join(output_folder, os.path.relpath(file_path, input_folder))
                    shutil.copy(file_path, output_image_path)
                    extracted_data = extract_information_from_image(output_image_path)
                    write_to_csv(os.path.basename(output_image_path), extracted_data, csv_writer, fields)

if __name__ == "__main__":
    input_folder = "../OCR_Project_Turkey_2024"
    output_folder = "./processed_data"
    csv_file = "extracted_data.csv"
    process_folder(input_folder, output_folder, csv_file)
