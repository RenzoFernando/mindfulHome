"""
LLM integration with Groq API.
Formats the math engine output and returns structured natural-language analysis.
"""
import json
from groq import Groq
from app.core.config import settings
from app.schemas.analysis import MortgageResult, CashflowResult, RatiosResult

RESPONSE_SCHEMA = {
    "summary": {"status": "string", "message": "string"},
    "global_analysis": {
        "financial_health_score": "number 0-100",
        "main_problem": "string",
        "secondary_problems": ["string"],
    },
    "insights": [
        {
            "id": "string",
            "label": "string",
            "severity": "low | medium | high | critical",
            "interpretation": {
                "what_it_means": "string",
                "why_it_matters": "string",
                "context": "string",
                "real_world_example": "string",
            },
            "impact": {"short_term": "string", "long_term": "string"},
        }
    ],
    "risks": [
        {"type": "string", "explanation": "string", "urgency": "low | medium | high"}
    ],
    "recommendations": [{"priority": "number", "action": "string", "reason": "string"}],
    "uiHints": {"primaryMetric": "string", "attentionAreas": ["string"]},
}

SYSTEM_PROMPT = """Eres un analista financiero que explica información compleja de forma simple.

Recibirás datos financieros ya calculados. NO debes recalcular nada.

Tu tarea es generar una interpretación clara y estructurada para una persona que entiende poco de finanzas.

REGLAS:
- NO hagas escenarios futuros
- NO hagas simulaciones
- NO recalcules métricas
- SOLO interpreta lo que ya existe
- Usa lenguaje simple, entendible para cualquier persona
- Cada explicación debe ser corta (máx 2 frases)
- Usa ejemplos cuando ayuden a entender
- Devuelve SOLO JSON válido, sin markdown, sin backticks
- SIEMPRE responde en español

El análisis debe ser profundo, pero claro para cualquier persona.

Cada insight debe incluir:
- qué significa
- por qué importa
- contexto financiero
- ejemplo simple de la vida real
- impacto corto y largo plazo"""


def build_prompt(
    mortgage: MortgageResult,
    cashflow: CashflowResult,
    ratios: RatiosResult,
) -> str:
    data = {
        "input": {
            "loan": {
                "loanAmount": mortgage.loan_amount,
                "monthlyPayment": mortgage.monthly_payment,
                "totalPaid": mortgage.total_paid,
                "totalInterest": mortgage.total_interest,
            },
            "cashflow": {
                "income": cashflow.income,
                "expenses": cashflow.expenses,
                "debt": cashflow.debt,
                "housingCost": cashflow.housing_cost,
                "liquidity": cashflow.liquidity,
                "liquidityAfterSavings": cashflow.liquidity_after_savings,
                "status": cashflow.status.value,
            },
            "ratios": {
                "mortgageRatio": ratios.mortgage_ratio,
                "debtRatio": ratios.debt_ratio,
                "housingRatio": ratios.housing_ratio,
                "emergencyMonths": ratios.emergency_months,
                "freeCashFlowRatio": ratios.free_cash_flow_ratio,
                "discretionaryIncomeRatio": ratios.discretionary_income_ratio,
            },
        }
    }
    return f"FORMATO OBLIGATORIO:\n{json.dumps(RESPONSE_SCHEMA, ensure_ascii=False, indent=2)}\n\nDATOS:\n{json.dumps(data, ensure_ascii=False, indent=2)}"


def analyze_with_llm(
    mortgage: MortgageResult,
    cashflow: CashflowResult,
    ratios: RatiosResult,
) -> dict:
    if not settings.GROQ_API_KEY:
        return {"error": "GROQ_API_KEY no configurada", "raw": None}

    # Crear cliente de Groq
    client = Groq(api_key=settings.GROQ_API_KEY)
    prompt = build_prompt(mortgage, cashflow, ratios)

    # Llamada a Groq (usando el endpoint de chat completions)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        model="llama-3.3-70b-versatile",  # Puedes usar otros modelos como "mixtral-8x7b-32768", "llama3-70b-8192", etc.
        temperature=0.7,
        max_tokens=4096,
        response_format={"type": "json_object"},  # Forzar respuesta JSON
    )

    # Extraer el contenido de la respuesta
    raw_text = chat_completion.choices[0].message.content.strip()
    
    # Limpiar markdown si existe
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
        raw_text = raw_text.strip()
    
    return json.loads(raw_text)