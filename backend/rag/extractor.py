# =====================================================
# rag/extractor.py — Document se text nikalna
# =====================================================
# Har file type ke liye alag tarika hai text nikalne ka
# PDF, DOCX, TXT, CSV, Excel — sab support hai

import io
import csv
import PyPDF2
import docx
import openpyxl

def extract_text(file_bytes: bytes, file_type: str) -> str:
    """
    File bytes leke text return karo.
    file_type: "pdf", "docx", "txt", "csv", "xlsx"
    """
    
    if file_type == "pdf":
        return _extract_from_pdf(file_bytes)
    
    elif file_type == "docx":
        return _extract_from_docx(file_bytes)
    
    elif file_type == "txt":
        return _extract_from_txt(file_bytes)
    
    elif file_type == "csv":
        return _extract_from_csv(file_bytes)
    
    elif file_type in ("xlsx", "xls"):
        return _extract_from_excel(file_bytes)
    
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

# ---- PDF ----
def _extract_from_pdf(file_bytes: bytes) -> str:
    reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    pages_text = []
    
    for page_num, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        pages_text.append(f"[Page {page_num + 1}]\n{text}")
    
    return "\n\n".join(pages_text)

# ---- DOCX ----
def _extract_from_docx(file_bytes: bytes) -> str:
    doc = docx.Document(io.BytesIO(file_bytes))
    
    # Har paragraph ka text lo
    paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
    return "\n".join(paragraphs)

# ---- TXT ----
def _extract_from_txt(file_bytes: bytes) -> str:
    return file_bytes.decode("utf-8", errors="ignore")

# ---- CSV ----
def _extract_from_csv(file_bytes: bytes) -> str:
    text = file_bytes.decode("utf-8", errors="ignore")
    reader = csv.reader(io.StringIO(text))
    
    rows = []
    for row in reader:
        rows.append(", ".join(row))  # har row ko comma se join karo
    
    return "\n".join(rows)

# ---- Excel ----
def _extract_from_excel(file_bytes: bytes) -> str:
    wb = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
    
    all_sheets = []
    for sheet_name in wb.sheetnames:
        sheet = wb[sheet_name]
        rows = []
        
        for row in sheet.iter_rows(values_only=True):
            # None values ko empty string karo
            row_text = ", ".join([str(cell) if cell is not None else "" for cell in row])
            rows.append(row_text)
        
        all_sheets.append(f"[Sheet: {sheet_name}]\n" + "\n".join(rows))
    
    return "\n\n".join(all_sheets)
