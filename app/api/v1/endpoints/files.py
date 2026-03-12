import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from app.api import deps
from app.models.user import User

router = APIRouter()

# Paths to the PDF files
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
SAMPLE1_PATH = os.path.join(BASE_DIR, "sample1.pdf")
SAMPLE2_PATH = os.path.join(BASE_DIR, "sample2.pdf")

@router.get("/public-pdf")
def get_public_pdf():
    """
    Publicly available PDF endpoint.
    """
    if not os.path.exists(SAMPLE1_PATH):
        raise HTTPException(status_code=404, detail="Sample 1 PDF not found")
    
    return FileResponse(
        path=SAMPLE1_PATH,
        media_type="application/pdf",
        filename="sample1.pdf"
    )

@router.get("/private-pdf")
def get_private_pdf(current_user: User = Depends(deps.get_current_user)):
    """
    Private PDF endpoint that requires authentication.
    """
    if not os.path.exists(SAMPLE2_PATH):
        raise HTTPException(status_code=404, detail="Sample 2 PDF not found")
    
    return FileResponse(
        path=SAMPLE2_PATH,
        media_type="application/pdf",
        filename="sample2.pdf"
    )
