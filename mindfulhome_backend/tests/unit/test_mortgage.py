"""Unit tests for mortgage calculation engine."""
import pytest
from app.schemas.analysis import PropertyInput
from app.models.analysis import InterestRateType
from app.services.mortgage import calculate_mortgage


def make_property(**kwargs):
    defaults = dict(
        property_price=300_000_000,
        down_payment=60_000_000,
        annual_interest_rate=12.0,
        interest_rate_type=InterestRateType.FIJA,
        loan_term_years=20,
    )
    defaults.update(kwargs)
    return PropertyInput(**defaults)


class TestCalculateMortgage:
    def test_loan_amount_is_price_minus_down_payment(self):
        result = calculate_mortgage(make_property(property_price=300_000_000, down_payment=60_000_000))
        assert result.loan_amount == 240_000_000

    def test_num_payments_equals_years_times_12(self):
        result = calculate_mortgage(make_property(loan_term_years=20))
        assert result.num_payments == 240

    def test_total_paid_equals_payment_times_num_payments(self):
        result = calculate_mortgage(make_property())
        assert abs(result.total_paid - result.monthly_payment * result.num_payments) < 1

    def test_total_interest_is_positive(self):
        result = calculate_mortgage(make_property())
        assert result.total_interest > 0

    def test_total_interest_equals_total_paid_minus_loan(self):
        result = calculate_mortgage(make_property())
        assert abs(result.total_interest - (result.total_paid - result.loan_amount)) < 1

    def test_monthly_payment_is_positive(self):
        result = calculate_mortgage(make_property())
        assert result.monthly_payment > 0

    def test_higher_rate_means_higher_payment(self):
        low = calculate_mortgage(make_property(annual_interest_rate=8.0))
        high = calculate_mortgage(make_property(annual_interest_rate=15.0))
        assert high.monthly_payment > low.monthly_payment

    def test_longer_term_means_lower_payment(self):
        short = calculate_mortgage(make_property(loan_term_years=10))
        long_ = calculate_mortgage(make_property(loan_term_years=20))
        assert long_.monthly_payment < short.monthly_payment

    def test_monthly_rate_calculation(self):
        result = calculate_mortgage(make_property(annual_interest_rate=12.0))
        assert abs(result.monthly_rate - 0.01) < 0.0001
