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
- Cada explicación debe ser clara, detallada y completa
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


def _fallback_analysis(
    cashflow: CashflowResult,
    ratios: RatiosResult,
) -> dict:
    status = cashflow.status.value
    score_by_status = {
        "SAFE": 85,
        "MODERATE": 65,
        "RISKY": 40,
        "CRITICAL": 20,
    }
    score = score_by_status.get(status, 50)

    secondary_problems = []
    attention_areas = []
    risks = []
    recommendations = []

    if ratios.housing_ratio > 0.4:
        secondary_problems.append("El costo de vivienda consume una parte alta del ingreso")
        attention_areas.append("housingRatio")
        risks.append({
            "type": "Carga de vivienda elevada",
            "explanation": "Una parte alta del ingreso mensual queda comprometida con la vivienda.",
            "urgency": "high",
        })
        recommendations.append({
            "priority": 1,
            "action": "Aumentar la cuota inicial o ampliar el plazo antes de comprar",
            "reason": "Esto puede reducir la cuota mensual y liberar liquidez.",
        })
        score -= 10

    if ratios.emergency_months < 3:
        secondary_problems.append("El fondo de emergencia cubre menos de tres meses")
        attention_areas.append("emergencyMonths")
        risks.append({
            "type": "Respaldo de emergencia limitado",
            "explanation": "Un gasto inesperado podría afectar rápidamente la capacidad de pago.",
            "urgency": "high",
        })
        recommendations.append({
            "priority": 2,
            "action": "Fortalecer el fondo de emergencia antes de asumir la hipoteca",
            "reason": "Un fondo mayor protege los pagos ante gastos inesperados o pérdida de ingresos.",
        })
        score -= 10

    if cashflow.liquidity_after_savings < 0:
        secondary_problems.append("La liquidez después del ahorro mensual queda en negativo")
        attention_areas.append("liquidityAfterSavings")
        risks.append({
            "type": "Déficit mensual",
            "explanation": "Después de cubrir gastos y ahorro, el flujo mensual no alcanza.",
            "urgency": "high",
        })
        recommendations.append({
            "priority": 3,
            "action": "Reducir gastos o ajustar la meta de ahorro antes de comprar",
            "reason": "El flujo mensual debe mantenerse positivo para evitar depender de los ahorros.",
        })
        score -= 10

    if ratios.debt_ratio > 0.3:
        secondary_problems.append("Los pagos de deuda actuales son elevados")
        attention_areas.append("debtRatio")
        risks.append({
            "type": "Endeudamiento elevado",
            "explanation": "Las deudas actuales reducen el margen disponible para la hipoteca.",
            "urgency": "medium",
        })
        recommendations.append({
            "priority": 4,
            "action": "Reducir deudas antes de adquirir la vivienda",
            "reason": "Menos obligaciones mensuales mejoran la capacidad de pago.",
        })
        score -= 10

    if cashflow.liquidity_after_savings < 0:
        main_problem = "Falta de liquidez después de cubrir gastos y ahorro"
    elif ratios.housing_ratio > 0.4:
        main_problem = "Gastos de vivienda elevados"
    elif ratios.emergency_months < 3:
        main_problem = "Fondo de emergencia insuficiente"
    else:
        main_problem = "La compra mantiene un margen financiero manejable"

    if not secondary_problems:
        secondary_problems.append("Conviene mantener seguimiento mensual de gastos y ahorros")

    if not risks:
        risks.append({
            "type": "Cambios en el flujo mensual",
            "explanation": "La estabilidad depende de conservar ingresos y gastos similares a los actuales.",
            "urgency": "low",
        })

    if not recommendations:
        recommendations.append({
            "priority": 1,
            "action": "Mantener el fondo de emergencia y revisar el presupuesto periódicamente",
            "reason": "Esto ayuda a conservar la estabilidad después de la compra.",
        })

    score = max(0, min(100, score))

    return {
        "summary": {
            "status": status,
            "message": "El cálculo financiero se completó. La interpretación automática avanzada no estuvo disponible temporalmente.",
        },
        "global_analysis": {
            "financial_health_score": score,
            "main_problem": main_problem,
            "secondary_problems": secondary_problems,
        },
        "insights": [
            {
                "id": "liquidity",
                "label": "Liquidez mensual",
                "severity": "high" if cashflow.liquidity_after_savings < 0 else "medium",
                "interpretation": {
                    "what_it_means": f"Después de gastos y ahorro quedan {cashflow.liquidity_after_savings:,.0f} COP al mes.",
                    "why_it_matters": "Este valor muestra el margen disponible para imprevistos.",
                    "context": "Un margen positivo reduce la necesidad de usar ahorros o deuda adicional.",
                    "real_world_example": "Es el dinero que quedaría disponible al terminar el mes.",
                },
                "impact": {
                    "short_term": "Define qué tan cómodo será cubrir gastos inesperados.",
                    "long_term": "Influye en la capacidad de sostener la hipoteca sin deteriorar los ahorros.",
                },
            },
            {
                "id": "housing_ratio",
                "label": "Carga de vivienda",
                "severity": "high" if ratios.housing_ratio > 0.4 else "medium",
                "interpretation": {
                    "what_it_means": f"La vivienda representa aproximadamente {ratios.housing_ratio * 100:.1f}% del ingreso mensual.",
                    "why_it_matters": "Una carga alta deja menos dinero para otros gastos y metas.",
                    "context": "Mientras mayor sea el porcentaje, menor será la flexibilidad financiera.",
                    "real_world_example": "Es la parte del salario que quedaría comprometida con la vivienda.",
                },
                "impact": {
                    "short_term": "Reduce el dinero disponible cada mes.",
                    "long_term": "Puede aumentar el riesgo ante cambios de ingreso o gastos inesperados.",
                },
            },
        ],
        "risks": risks,
        "recommendations": recommendations,
        "uiHints": {
            "primaryMetric": "housingRatio",
            "attentionAreas": attention_areas,
        },
    }


def analyze_with_llm(
    mortgage: MortgageResult,
    cashflow: CashflowResult,
    ratios: RatiosResult,
) -> dict:
    if not settings.GROQ_API_KEY:
        return _fallback_analysis(cashflow, ratios)

    try:
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

        parsed = json.loads(raw_text)
        required = {"summary", "global_analysis", "insights", "risks", "recommendations", "uiHints"}
        if not required.issubset(parsed):
            return _fallback_analysis(cashflow, ratios)
        return parsed
    except Exception:
        return _fallback_analysis(cashflow, ratios)
