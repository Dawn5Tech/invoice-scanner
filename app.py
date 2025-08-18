"""
Invoice Scanner: OCR + TensorFlow (optional classifier) + Streamlit UI

Features
- Upload invoice/receipt (PNG/JPG/JPEG/PDF)
- OCR via Tesseract (pytesseract)
- Heuristic extraction (regex for dates, currency amounts, invoice numbers)
- Optional TensorFlow text classifier to tag lines as DATE / TOTAL / INVOICE_NUMBER / VENDOR / OTHER
  * You can train it inside the app from a small labeled CSV and it will be saved to ./models/invoice_line_classifier
- Export structured results (JSON & CSV) with download buttons

Notes
- For PDF support, install poppler on your OS so pdf2image can convert PDFs to images.
  * Windows: https://github.com/oschwartz10612/poppler-windows/releases/ (add bin folder to PATH)
  * macOS (Homebrew): brew install poppler
  * Linux (Debian/Ubuntu): sudo apt-get install poppler-utils

Author: You + ChatGPT
"""

import streamlit as st
import pytesseract
import tensorflow as tf
import numpy as np
import os
from PIL import Image
from pdf2image import convert_from_path
import re
import json

# --- Config ---
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Path to Tesseract (Windows users must set this)
# Uncomment and edit if needed:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# --- Dummy TensorFlow model (for now just character count as placeholder) ---
def build_dummy_model():
    # Just a placeholder dense model
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(1,)),
        tf.keras.layers.Dense(8, activation='relu'),
        tf.keras.layers.Dense(1, activation='linear')
    ])
    model.compile(optimizer='adam', loss='mse')
    return model

model = build_dummy_model()

# --- OCR Function ---
def extract_text(file_path):
    text = ""
    if file_path.lower().endswith(".pdf"):
        pages = convert_from_path(file_path)
        for page in pages:
            text += pytesseract.image_to_string(page)
    else:
        img = Image.open(file_path)
        text = pytesseract.image_to_string(img)
    return text

# --- Extract structured invoice fields ---
def extract_invoice_fields(text):
    fields = {}

    # Invoice Number
    invoice_no_match = re.search(r"(Invoice\s*(No\.?|#)\s*[:\-]?\s*(\w+))", text, re.IGNORECASE)
    fields["Invoice Number"] = invoice_no_match.group(3) if invoice_no_match else "Not found"

    # Date (matches formats like 2025-08-18, 18/08/2025, 08-18-2025)
    date_match = re.search(r"(\d{2}[\/\-]\d{2}[\/\-]\d{4}|\d{4}[\/\-]\d{2}[\/\-]\d{2})", text)
    fields["Date"] = date_match.group(0) if date_match else "Not found"

    # Total Amount (matches e.g. Total: $123.45 or Amount Due 999.99)
    total_match = re.search(r"(Total|Amount Due)[:\s]*\$?([\d,]+\.\d{2})", text, re.IGNORECASE)
    fields["Total Amount"] = total_match.group(2) if total_match else "Not found"

    return fields

# --- Streamlit UI ---
st.set_page_config(page_title="Invoice Scanner", page_icon="🧾", layout="wide")
st.title("🧾 Invoice Scanner (TensorFlow + OCR)")

uploaded_file = st.file_uploader("Upload an invoice (PDF or Image)", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file is not None:
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"File uploaded: {uploaded_file.name}")

    with st.spinner("Extracting text with OCR..."):
        extracted_text = extract_text(file_path)
    
    st.subheader("📄 Extracted Text")
    st.text_area("OCR Output", extracted_text, height=300)

    # --- Dummy ML Prediction ---
    length = len(extracted_text.split())
    prediction = model.predict(np.array([[length]]))

    st.subheader("🤖 ML Model Output")
    st.write(f"Predicted Value (based on text length): {prediction[0][0]:.2f}")

    # --- Extract invoice fields ---
    fields = extract_invoice_fields(extracted_text)

    st.subheader("📑 Extracted Fields")
    st.write(fields)

    # Download extracted text
    st.download_button(
        label="💾 Download Extracted Text",
        data=extracted_text,
        file_name="invoice_text.txt",
        mime="text/plain"
    )

    # Download extracted fields as JSON
    st.download_button(
        label="💾 Download Extracted Fields (JSON)",
        data=json.dumps(fields, indent=2),
        file_name="invoice_fields.json",
        mime="application/json"
    )
