# PDF & Image Processing and Information Extraction

This project processes PDFs and images in a directory structure, converts PDFs to images, extracts information using GPT-4 API, and stores the results in a CSV file.

## Features
- Convert each page of a PDF to an image.
- Maintain the original folder structure in the output directory.
- Extract information from images using OpenAI GPT-4 API.
- Store the results in a CSV file with the first column as the file name and subsequent columns as extracted fields.

## Setup Instructions

1. **Install dependencies**:
   Run the following command to install the required libraries:

```bash
   pip install -r requirements.txt
   ```

### Notes:
1. Make sure `Poppler` is installed on your system for `pdf2image` to work properly. Instructions are available [here](https://github.com/Belval/pdf2image#installing-poppler).

2. Modify the `prompt` in the code as needed, especially with the fields you need to extract.
