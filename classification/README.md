# **OCR Document Classification Task**

This repository contains a Python script for classifying documents (PDFs and images) using Google Vision API. The classification is based on keywords, and the final output is a CSV file containing the image name, actual category, and classified category.

## **Prerequisites**

### **1. Install Python Dependencies**

Create a virtual environment and install the required dependencies using `requirements.txt`:

```bash
python -m venv venv
venv/bin/activate
pip install -r requirements.txt
```

### **2. Run the Script**

```bash
python ./classification_task.py
```

### Notes:
1. Make sure `Poppler` is installed on your system for `pdf2image` to work properly. Instructions are available [here](https://github.com/Belval/pdf2image#installing-poppler).

2. Modify the `prompt` in the code as needed, especially with the fields you need to extract.
