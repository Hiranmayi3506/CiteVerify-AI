
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="CiteVerify AI Verification API",
    description="Research claim verification backend",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "message": "CiteVerify Verification Backend is running"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "AI Verification Backend"
    }

@app.post("/verify")
async def verify_pdf(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        return {"error": "Please upload a PDF file"}

    pdf_content = await file.read()

    return {
        "message": "PDF received successfully",
        "filename": file.filename,
        "file_size": len(pdf_content),
        "claims": [],
        "citations": [],
        "verdicts": []
    }
