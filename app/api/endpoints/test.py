from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter()

@router.get("/test")
async def test_endpoint():
    return {"message": "Test endpoint works"}

@router.get("/test-db")
async def test_db(db: Session = Depends(get_db)):
    try:
        # Tester une requête simple
        result = db.execute("SELECT COUNT(*) as count FROM bornes").fetchone()
        return {
            "status": "success",
            "database": "connected",
            "bornes_count": result[0] if result else 0
        }
    except Exception as e:
        return {
            "status": "error",
            "database": "disconnected",
            "error": str(e)
        }
