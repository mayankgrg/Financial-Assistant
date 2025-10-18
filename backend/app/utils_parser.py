import io
import pandas as pd
import re
from pdfminer.high_level import extract_text
from PIL import Image
import pytesseract
from typing import List, Dict

def parse_csv(file_bytes: bytes):
    df = pd.read_csv(io.BytesIO(file_bytes))
    cols = {c.lower(): c for c in df.columns}
    date_col = next((cols[c] for c in cols if 'date' in c), None)
    desc_col = next((cols[c] for c in cols if 'desc' in c or 'description' in c), None)
    amt_col = next((cols[c] for c in cols if 'amount' in c or 'amt' in c or 'debit' in c or 'credit' in c), None)
    transactions = []
    if desc_col and amt_col:
        for _, r in df.iterrows():
            try:
                amt = float(r[amt_col])
            except:
                # try to clean
                amt = float(str(r[amt_col]).replace(',', '').replace('$', ''))
            transactions.append({
                "date": str(r[date_col]) if date_col else None,
                "description": str(r[desc_col]),
                "amount": float(amt)
            })
    else:
        transactions = parse_text(df.to_csv(index=False))
    return transactions

def parse_pdf(file_bytes: bytes):
    text = extract_text(io.BytesIO(file_bytes))
    return parse_text(text)

def parse_image(file_bytes: bytes):
    image = Image.open(io.BytesIO(file_bytes))
    text = pytesseract.image_to_string(image)
    return parse_text(text)

def parse_text(text: str):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    transactions = []
    amt_re = re.compile(r'(-?\$?\(?\d{1,3}(?:[,]\d{3})*(?:\.\d{1,2})?\)?)')
    for line in lines:
        matches = amt_re.findall(line)
        if matches:
            raw_amt = matches[-1]
            amt = raw_amt.replace('(', '-').replace(')', '').replace('$', '').replace(',', '')
            try:
                amt_f = float(amt)
            except:
                continue
            desc = line.replace(matches[-1], '').strip(' -\t')
            transactions.append({
                "date": None,
                "description": desc[:200],
                "amount": amt_f
            })
    return transactions

def parse_file(filename: str, file_bytes: bytes):
    fname = filename.lower()
    if fname.endswith('.csv'):
        return parse_csv(file_bytes)
    elif fname.endswith('.pdf'):
        return parse_pdf(file_bytes)
    elif any(fname.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']):
        return parse_image(file_bytes)
    else:
        try:
            text = file_bytes.decode('utf-8')
            return parse_text(text)
        except:
            return []
