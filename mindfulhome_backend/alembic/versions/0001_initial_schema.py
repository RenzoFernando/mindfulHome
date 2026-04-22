"""initial schema

Revision ID: 0001
Revises: 
Create Date: 2025-01-01 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        # Financial profile
        sa.Column("monthly_income", sa.Float(), nullable=True),
        sa.Column("fixed_expenses", sa.Float(), nullable=True),
        sa.Column("variable_expenses", sa.Float(), nullable=True),
        sa.Column("total_savings", sa.Float(), nullable=True),
        sa.Column("emergency_fund", sa.Float(), nullable=True),
        sa.Column("monthly_savings_goal", sa.Float(), nullable=True),
        # Labor profile
        sa.Column("income_type", sa.Enum("EMPLEADO", "INDEPENDIENTE", "EMPRESARIO", "PENSIONADO",
                                          name="incometype"), nullable=True),
        sa.Column("income_variability", sa.Enum("FIJO", "VARIABLE", "MIXTO",
                                                  name="incomevariability"), nullable=True),
        sa.Column("contract_type", sa.Enum("INDEFINIDO", "FIJO", "PRESTACION_SERVICIOS", "NINGUNO",
                                            name="contracttype"), nullable=True),
        sa.Column("job_seniority_months", sa.Integer(), nullable=True),
        # Debt profile
        sa.Column("monthly_debt_payments", sa.Float(), nullable=True),
        sa.Column("total_debt", sa.Float(), nullable=True),
        # Housing profile
        sa.Column("is_renting", sa.Boolean(), nullable=True),
        sa.Column("monthly_rent", sa.Float(), nullable=True),
        sa.Column("rent_mortgage_overlap_months", sa.Integer(), nullable=True),
        # Household
        sa.Column("dependents", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    op.create_table(
        "property_analyses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("property_price", sa.Float(), nullable=False),
        sa.Column("down_payment", sa.Float(), nullable=False),
        sa.Column("annual_interest_rate", sa.Float(), nullable=False),
        sa.Column("interest_rate_type", sa.Enum("FIJA", "VARIABLE", name="interestratetype"), nullable=False),
        sa.Column("loan_term_years", sa.Integer(), nullable=False),
        sa.Column("mortgage_result", sa.JSON(), nullable=True),
        sa.Column("cashflow_result", sa.JSON(), nullable=True),
        sa.Column("ratios_result", sa.JSON(), nullable=True),
        sa.Column("llm_analysis", sa.JSON(), nullable=True),
        sa.Column("status", sa.Enum("SAFE", "MODERATE", "RISKY", "CRITICAL", name="riskstatus"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_property_analyses_id", "property_analyses", ["id"])


def downgrade() -> None:
    op.drop_table("property_analyses")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS incometype")
    op.execute("DROP TYPE IF EXISTS incomevariability")
    op.execute("DROP TYPE IF EXISTS contracttype")
    op.execute("DROP TYPE IF EXISTS interestratetype")
    op.execute("DROP TYPE IF EXISTS riskstatus")
