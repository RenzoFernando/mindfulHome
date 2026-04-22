"""Unit tests for key financial ratios."""
import pytest
from unittest.mock import MagicMock
from app.services.ratios import calculate_ratios
from app.schemas.analysis import MortgageResult, CashflowResult
from app.models.analysis import RiskStatus


def make_user(**kwargs):
    user = MagicMock()
    user.monthly_income = kwargs.get("monthly_income", 5_000_000)
    user.fixed_expenses = kwargs.get("fixed_expenses", 500_000)
    user.variable_expenses = kwargs.get("variable_expenses", 300_000)
    user.monthly_debt_payments = kwargs.get("monthly_debt_payments", 200_000)
    user.emergency_fund = kwargs.get("emergency_fund", 5_000_000)
    return user


def make_mortgage(monthly_payment=1_500_000):
    return MortgageResult(
        loan_amount=180_000_000,
        monthly_rate=0.01,
        num_payments=240,
        monthly_payment=monthly_payment,
        total_paid=360_000_000,
        total_interest=180_000_000,
    )


def make_cashflow(housing_cost=1_500_000, expenses=1_000_000):
    return CashflowResult(
        income=5_000_000,
        expenses=expenses,
        debt=200_000,
        housing_cost=housing_cost,
        liquidity=2_300_000,
        liquidity_after_savings=2_000_000,
        status=RiskStatus.SAFE,
    )


class TestCalculateRatios:
    def test_mortgage_ratio(self):
        result = calculate_ratios(make_user(), make_mortgage(1_000_000), make_cashflow(1_000_000))
        assert result.mortgage_ratio == round(1_000_000 / 5_000_000, 4)

    def test_debt_ratio(self):
        result = calculate_ratios(
            make_user(monthly_debt_payments=500_000),
            make_mortgage(),
            make_cashflow(),
        )
        assert result.debt_ratio == round(500_000 / 5_000_000, 4)

    def test_housing_ratio(self):
        result = calculate_ratios(make_user(), make_mortgage(), make_cashflow(housing_cost=2_000_000))
        assert result.housing_ratio == round(2_000_000 / 5_000_000, 4)

    def test_emergency_months_positive(self):
        result = calculate_ratios(make_user(emergency_fund=6_000_000), make_mortgage(), make_cashflow())
        assert result.emergency_months > 0

    def test_zero_income_returns_zero_ratios(self):
        result = calculate_ratios(
            make_user(monthly_income=0),
            make_mortgage(),
            make_cashflow(),
        )
        assert result.mortgage_ratio == 0
        assert result.debt_ratio == 0
        assert result.housing_ratio == 0

    def test_free_cash_flow_ratio_range(self):
        result = calculate_ratios(make_user(), make_mortgage(), make_cashflow())
        assert -1 <= result.free_cash_flow_ratio <= 1

    def test_discretionary_less_than_free_cash_flow(self):
        result = calculate_ratios(make_user(), make_mortgage(), make_cashflow())
        # discretionary subtracts variable expenses too, so it must be <= FCF
        assert result.discretionary_income_ratio <= result.free_cash_flow_ratio

    def test_all_fields_present(self):
        result = calculate_ratios(make_user(), make_mortgage(), make_cashflow())
        assert hasattr(result, "mortgage_ratio")
        assert hasattr(result, "debt_ratio")
        assert hasattr(result, "housing_ratio")
        assert hasattr(result, "emergency_months")
        assert hasattr(result, "free_cash_flow_ratio")
        assert hasattr(result, "discretionary_income_ratio")
