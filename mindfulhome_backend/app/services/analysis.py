"""
Orchestrates the full analysis pipeline:
  1. Mortgage calculation
  2. Post-purchase cashflow
  3. Key ratios
  4. LLM interpretation
"""
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.analysis import PropertyAnalysis, RiskStatus
from app.schemas.analysis import PropertyInput, AnalysisResponse
from app.services.mortgage import calculate_mortgage
from app.services.cashflow import calculate_cashflow
from app.services.ratios import calculate_ratios
from app.services import llm as llm_service


def run_analysis(db: Session, user: User, prop: PropertyInput) -> PropertyAnalysis:
    mortgage = calculate_mortgage(prop)
    cashflow = calculate_cashflow(user, mortgage)
    ratios = calculate_ratios(user, mortgage, cashflow)
    llm_result = llm_service.analyze_with_llm(mortgage, cashflow, ratios)

    record = PropertyAnalysis(
        user_id=user.id,
        property_price=prop.property_price,
        down_payment=prop.down_payment,
        annual_interest_rate=prop.annual_interest_rate,
        interest_rate_type=prop.interest_rate_type,
        loan_term_years=prop.loan_term_years,
        mortgage_result=mortgage.model_dump(),
        cashflow_result=cashflow.model_dump(),
        ratios_result=ratios.model_dump(),
        llm_analysis=llm_result,
        status=RiskStatus(cashflow.status.value),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
