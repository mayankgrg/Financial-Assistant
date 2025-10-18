from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes_upload import router as upload_router
from .routes_analysis import router as analysis_router

app = FastAPI(title="Fin Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router, prefix="/upload", tags=["upload"])
app.include_router(analysis_router, prefix="/analysis", tags=["analysis"])

@app.get("/")
def root():
    return {"message": "Fin Assistant API running"}
