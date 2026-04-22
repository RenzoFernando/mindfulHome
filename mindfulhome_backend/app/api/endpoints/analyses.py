from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.base import get_db
from app.models.user import User
from app.models.analysis import PropertyAnalysis
from app.schemas.analysis import PropertyInput, AnalysisResponse
from app.services.analysis import run_analysis
from app.api import deps

router = APIRouter(prefix="/analyses", tags=["analyses"])


def _to_response(record: PropertyAnalysis) -> dict:
    return {
        "id": record.id,
        "status": record.status,
        "property_price": record.property_price,
        "down_payment": record.down_payment,
        "annual_interest_rate": record.annual_interest_rate,
        "loan_term_years": record.loan_term_years,
        "mortgage": record.mortgage_result,
        "cashflow": record.cashflow_result,
        "ratios": record.ratios_result,
        "llm_analysis": record.llm_analysis,
    }


@router.post("", status_code=status.HTTP_201_CREATED)
def create_analysis(
    payload: PropertyInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    # Validate that the user has a complete financial profile
    required = ["monthly_income", "fixed_expenses", "variable_expenses"]
    missing = [f for f in required if getattr(current_user, f) is None]
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"Perfil incompleto. Faltan: {', '.join(missing)}",
        )

    record = run_analysis(db, current_user, payload)
    return _to_response(record)


@router.get("", response_model=List[dict])
def list_analyses(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    records = (
        db.query(PropertyAnalysis)
        .filter(PropertyAnalysis.user_id == current_user.id)
        .order_by(PropertyAnalysis.id.desc())
        .all()
    )
    return [_to_response(r) for r in records]


@router.get("/{analysis_id}")
def get_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    record = (
        db.query(PropertyAnalysis)
        .filter(
            PropertyAnalysis.id == analysis_id,
            PropertyAnalysis.user_id == current_user.id,
        )
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")
    return _to_response(record)


@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    record = (
        db.query(PropertyAnalysis)
        .filter(
            PropertyAnalysis.id == analysis_id,
            PropertyAnalysis.user_id == current_user.id,
        )
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")
    db.delete(record)
    db.commit()
