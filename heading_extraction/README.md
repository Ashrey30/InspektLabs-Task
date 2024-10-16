# **OCR Document Heading Extraction Task**

This repository contains a Python script for extracting the headings from documents (PDFs and images) using Google Vision API.

## **Prerequisites**

### **1. Install Python Dependencies**

Create a virtual environment and install the required dependencies using `requirements.txt`:

```bash
python -m venv venv
venv/bin/activate
pip install -r requirements.txt
```

### **3. Install poppler**

```bash
sudo apt-get install poppler-utils
```
OR download from Poppler's website and edit the poppler path in the code.

### Notes:
1. Make sure `Poppler` is installed on your system for `pdf2image` to work properly. Instructions are available [here](https://github.com/Belval/pdf2image#installing-poppler).

2. Modify the `prompt` in the code as needed, especially with the fields you need to extract.

### **3. Run the Script**

```bash
python ./heading_extraction.py
```