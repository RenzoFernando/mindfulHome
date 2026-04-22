"""Unit tests for post-purchase cashflow analysis."""
import pytest
from unittest.mock import MagicMock
from app.services.cashflow import calculate_cashflow, _classify_liquidity
from app.schemas.analysis import MortgageResult
from app.models.analysis import RiskStatus


def make_user(**kwargs):
    user = MagicMock()
    user.monthly_income = kwargs.get("monthly_income", 5_000_000)
    user.fixed_expenses = kwargs.get("fixed_expenses", 800_000)
    user.variable_expenses = kwargs.get("variable_expenses", 500_000)
    user.monthly_debt_payments = kwargs.get("monthly_debt_payments", 0)
    user.dependents = kwargs.get("dependents", 0)
    user.monthly_savings_goal = kwargs.get("monthly_savings_goal", 0)
    user.is_renting = kwargs.get("is_renting", False)
    user.monthly_rent = kwargs.get("monthly_rent", None)
    user.rent_mortgage_overlap_months = kwargs.get("rent_mortgage_overlap_months", 0)
    return user


def make_mortgage(monthly_payment=1_500_000):
    return MortgageResult(
        loan_amount=240_000_000,
        monthly_rate=0.01,
        num_payments=240,
        monthly_payment=monthly_payment,
        total_paid=360_000_000,
        total_interest=120_000_000,
    )


class TestClassifyLiquidity:
    def test_critical_when_negative(self):
        assert _classify_liquidity(-100_000, 5_000_000) == RiskStatus.CRITICAL

    def test_critical_when_zero_income(self):
        assert _classify_liquidity(0, 0) == RiskStatus.CRITICAL

    def test_risky_when_small_positive(self):
        # 2% of income
        assert _classify_liquidity(100_000, 5_000_000) == RiskStatus.RISKY

    def test_moderate_when_medium(self):
        # ~10% of income
        assert _classify_liquidity(500_000, 5_000_000) == RiskStatus.MODERATE

    def test_safe_when_above_20_percent(self):
        # 25% of income
        assert _classify_liquidity(1_250_000, 5_000_000) == RiskStatus.SAFE


class TestCalculateCashflow:
    def test_income_preserved(self):
        result = calculate_cashflow(make_user(monthly_income=4_000_000), make_mortgage())
        assert result.income == 4_000_000

    def test_liquidity_formula(self):
        user = make_user(
            monthly_income=5_000_000,
            fixed_expenses=800_000,
            variable_expenses=500_000,
            monthly_debt_payments=0,
            dependents=0,
        )
        mortgage = make_mortgage(monthly_payment=1_500_000)
        result = calculate_cashflow(user, mortgage)
        # expenses = 800k + 500k = 1300k, housing = 1500k, liquidity = 5000k - 2800k = 2200k
        assert result.liquidity == 2_200_000

    def test_dependents_increase_expenses(self):
        no_dep = calculate_cashflow(make_user(dependents=0), make_mortgage())
        with_dep = calculate_cashflow(make_user(dependents=2), make_mortgage())
        assert with_dep.expenses > no_dep.expenses

    def test_savings_goal_reduces_liquidity_after_savings(self):
        result = calculate_cashflow(
            make_user(monthly_savings_goal=300_000), make_mortgage()
        )
        assert result.liquidity_after_savings == result.liquidity - 300_000

    def test_rent_overlap_increases_housing_cost(self):
        no_overlap = calculate_cashflow(make_user(is_renting=False), make_mortgage())
        with_overlap = calculate_cashflow(
            make_user(is_renting=True, monthly_rent=1_200_000, rent_mortgage_overlap_months=3),
            make_mortgage(),
        )
        assert with_overlap.housing_cost > no_overlap.housing_cost

    def test_status_critical_when_income_insufficient(self):
        user = make_user(
            monthly_income=2_000_000,
            fixed_expenses=1_000_000,
            variable_expenses=500_000,
        )
        result = calculate_cashflow(user, make_mortgage(monthly_payment=2_000_000))
        assert result.status == RiskStatus.CRITICAL

    def test_status_safe_when_income_high(self):
        user = make_user(
            monthly_income=10_000_000,
            fixed_expenses=500_000,
            variable_expenses=300_000,
        )
        result = calculate_cashflow(user, make_mortgage(monthly_payment=1_000_000))
        assert result.status == RiskStatus.SAFE
