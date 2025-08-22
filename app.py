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

Author: Dawn
"""

import streamlit as st
import pytesseract
import fitz  # PyMuPDF
import re
import json
import os
import pandas as pd
from datetime import datetime
from PIL import Image

# --- Ensure directories exist ---
os.makedirs("uploads", exist_ok=True)
os.makedirs("processed", exist_ok=True)

# --- Invoice field extraction function ---
def extract_invoice_fields(text):
    fields = {
        "Invoice Number": None,
        "Invoice Date": None,
        "Total Amount": None,
    }

    # Invoice Number (e.g. Invoice #12345)
    invoice_number_match = re.search(r"(Invoice\s*#?:?\s*)([A-Za-z0-9\-]+)", text, re.IGNORECASE)

    # Dates (DD-MM-YYYY, YYYY-MM-DD, DD/MM/YYYY, 18 Aug 2025, etc.)
    date_match = re.search(
        r"(\d{2}[/-]\d{2}[/-]\d{4}|\d{4}[/-]\d{2}[/-]\d{2}|\d{1,2}\s+\w+\s+\d{4})",
        text
    )

    # Totals (Total, Grand Total, Amount Due, Balance)
    total_match = re.search(
        r"(Total\s*Amount\s*:?|Grand\s*Total|Amount\s*Due|Balance)\s*\$?([\d,]+\.\d{2})",
        text,
        re.IGNORECASE
    )

    if invoice_number_match:
        fields["Invoice Number"] = invoice_number_match.group(2)
    if date_match:
        fields["Invoice Date"] = date_match.group(1)
    if total_match:
        fields["Total Amount"] = total_match.group(2)

    return fields


# --- Streamlit App ---
st.title("📄 AI Invoice Scanner (Freelance-Ready + Cloud-Safe)")
st.write("Upload an invoice (PDF or image), extract details, and download results.")

uploaded_file = st.file_uploader("Upload Invoice", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file:
    # Save uploaded file
    file_path = os.path.join("uploads", uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    text = ""
    images = []

    if uploaded_file.type == "application/pdf":
        # Open PDF with PyMuPDF
        doc = fitz.open(stream=open(file_path, "rb").read(), filetype="pdf")
        for page in doc:
            text += page.get_text("text")  # Extract text
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            images.append(img)

        # OCR fallback if no text
        if not text.strip():
            st.warning("No embedded text found. Running OCR...")
            for img in images:
                try:
                    text += pytesseract.image_to_string(img)
                except Exception:
                    st.error("⚠️ OCR not available here. Use PDF with embedded text or deploy with OCR API.")
                    break

    else:
        # Handle image upload
        image = Image.open(file_path)
        st.image(image, caption="Uploaded Invoice", use_column_width=True)

        try:
            text = pytesseract.image_to_string(image)
        except Exception:
            st.error("⚠️ OCR not available in this environment.")
            text = ""

    # --- Display Results ---
    st.subheader("📝 Extracted Text")
    st.text(text if text else "⚠️ No text could be extracted.")

    fields = extract_invoice_fields(text)

    st.subheader("📌 Extracted Fields")
    st.json(fields)

    # --- Save extracted fields ---
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = f"processed/invoice_{timestamp}.json"
    csv_path = f"processed/invoice_{timestamp}.csv"

    with open(json_path, "w") as f:
        json.dump(fields, f, indent=2)

    pd.DataFrame([fields]).to_csv(csv_path, index=False)

    # --- Downloads ---
    st.download_button(
        "💾 Download Extracted Fields (JSON)",
        data=json.dumps(fields, indent=2),
        file_name="invoice_fields.json",
        mime="application/json",
    )

    st.download_button(
        "📊 Download Extracted Fields (CSV)",
        data=pd.DataFrame([fields]).to_csv(index=False),
        file_name="invoice_fields.csv",
        mime="text/csv",
    )

    # --- Show Preview ---
    if images:
        st.subheader("🖼️ Invoice Preview")
        st.image(images, caption=[f"Page {i+1}" for i in range(len(images))])