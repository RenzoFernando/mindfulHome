export interface PropertyInput {
    property_price: number;
    down_payment: number;
    annual_interest_rate: number;
    loan_term_years: number;
}

export interface Analysis {
    id: number;
    status: string;
    property_price: number;
    down_payment: number;
    annual_interest_rate: number;
    loan_term_years: number;
    mortgage: any;
    cashflow: any;
    ratios: any;
    llm_analysis: any;
}