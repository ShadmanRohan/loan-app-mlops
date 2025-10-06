"""Pydantic schemas for loan approval API."""

from pydantic import BaseModel, Field
from typing import Optional

class LoanApplication(BaseModel):
    """Loan application input schema."""
    age: float = Field(..., ge=18, le=100, description="Applicant age")
    annual_income: float = Field(..., ge=0, description="Annual income in USD")
    credit_score: float = Field(..., ge=300, le=850, description="Credit score")
    experience: float = Field(..., ge=0, le=50, description="Years of work experience")
    loan_amount: float = Field(..., ge=1000, description="Requested loan amount")
    loan_duration: float = Field(..., ge=1, le=30, description="Loan duration in years")
    number_of_dependents: float = Field(..., ge=0, le=10, description="Number of dependents")
    monthly_debt_payments: float = Field(..., ge=0, description="Monthly debt payments")
    credit_card_utilization_rate: float = Field(..., ge=0, le=1, description="Credit card utilization rate")
    number_of_open_credit_lines: float = Field(..., ge=0, description="Number of open credit lines")
    number_of_credit_inquiries: float = Field(..., ge=0, description="Number of credit inquiries")
    debt_to_income_ratio: float = Field(..., ge=0, le=1, description="Debt to income ratio")
    bankruptcy_history: float = Field(..., ge=0, le=1, description="Bankruptcy history (0=no, 1=yes)")
    previous_loan_defaults: float = Field(..., ge=0, le=1, description="Previous loan defaults (0=no, 1=yes)")
    payment_history: float = Field(..., ge=0, le=1, description="Payment history score")
    length_of_credit_history: float = Field(..., ge=0, description="Length of credit history in years")
    savings_account_balance: float = Field(..., ge=0, description="Savings account balance")
    checking_account_balance: float = Field(..., ge=0, description="Checking account balance")
    total_assets: float = Field(..., ge=0, description="Total assets value")
    total_liabilities: float = Field(..., ge=0, description="Total liabilities value")
    monthly_income: float = Field(..., ge=0, description="Monthly income")
    job_tenure: float = Field(..., ge=0, description="Job tenure in years")
    net_worth: float = Field(..., description="Net worth (assets - liabilities)")
    employment_status: str = Field(default="Employed", description="Employment status")
    education_level: str = Field(default="Bachelor", description="Education level")
    marital_status: str = Field(default="Married", description="Marital status")
    home_ownership_status: str = Field(default="Own", description="Home ownership status")
    loan_purpose: str = Field(default="Home", description="Loan purpose")

class LoanPrediction(BaseModel):
    """Loan prediction response schema."""
    approved: bool = Field(..., description="Whether the loan is approved")
    probability: float = Field(..., ge=0, le=1, description="Approval probability")
    risk_score: float = Field(..., ge=0, le=100, description="Risk score (0-100)")
    confidence: str = Field(..., description="Confidence level (High/Medium/Low)")

class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str = Field(..., description="Service status")
    model_loaded: bool = Field(..., description="Whether model is loaded")
    shap_available: bool = Field(default=False, description="Whether SHAP explainer is available")

class LoanPredictionWithExplanation(BaseModel):
    """Loan prediction with SHAP explanation."""
    prediction: dict = Field(..., description="Prediction result")
    shap_explanation: dict = Field(..., description="SHAP explanation")

class ErrorResponse(BaseModel):
    """Error response schema."""
    detail: str = Field(..., description="Error message")
