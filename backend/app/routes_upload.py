from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from .utils_parser import parse_file
from .utils_categorizer import categorize_transactions
from typing import List

router = APIRouter()

@router.post("/file")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")
    transactions = parse_file(file.filename, content)
    if not transactions:
        return JSONResponse({"transactions": [], "message": "No transactions parsed. Try CSV or higher-quality PDF/image."})
    categorized = categorize_transactions(transactions)
    return {"transactions": categorized}
