# Fin-Assistant

Financial Assistant: upload bank statements (CSV/PDF/Image), get expense breakdowns, tailored suggestions, and credit-card comparisons.

Tech stack:
- Backend: FastAPI
- Frontend: Streamlit
- DB: SQLite (only for non-PI example data)
- OCR: pytesseract (optional)
- Charts: Matplotlib

## Quick start (local)

1. Clone repo
2. Start backend:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

cd frontend
pip install -r requirements.txt
streamlit run streamlit_app.py



docker-compose up --build
