# 📄 AI Invoice Scanner (Freelance-Ready)

A lightweight invoice scanning app built with **Streamlit**, **PyMuPDF**, and **Tesseract OCR**.  
Upload an invoice (PDF or image) → extract key fields → download results in **CSV/JSON**.

---

## 🚀 Features
- Upload **PDFs or Images** (JPG, PNG).
- Extract key invoice fields:
  - Invoice Number
  - Invoice Date
  - Total Amount
- Save processed data to `processed/` folder.
- Download results as **JSON or CSV**.
- Works on **local machine** and **Streamlit Cloud**.

---

## ⚠️ Local vs. Cloud OCR

- **Local Machine** → Full OCR (PDFs & images work).
- **Streamlit Cloud** → PDFs with embedded text work fine ✅  
  But **OCR may not run** (images / scanned PDFs may not extract text).  

👉 For freelance projects, you can:
- Run it locally with Tesseract installed.
- Or upgrade to an **OCR API service** (like Google Vision / AWS Textract / Mindee) for full cloud support.

---

## 🛠️ Installation (Local)

```bash
# Clone repo
git clone https://github.com/YOUR-USERNAME/invoice-scanner.git
cd invoice-scanner

# Create virtual environment
python -m venv venv
source venv/bin/activate   # (Mac/Linux)
venv\Scripts\activate      # (Windows)

# Install dependencies
pip install -r requirements.txt

# Run app
streamlit run app.py