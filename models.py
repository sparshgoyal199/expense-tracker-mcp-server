from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class Category(str, Enum):
    FOOD = "food"
    TRANSPORT = "transport"
    HOUSING = "housing"
    UTILITIES = "utilities"
    HEALTH = "health"
    EDUCATION = "education"
    FAMILY_KIDS = "family_kids"
    ENTERTAINMENT = "entertainment"
    SHOPPING = "shopping"
    SUBSCRIPTIONS = "subscriptions"
    PERSONAL_CARE = "personal_care"
    GIFTS_DONATIONS = "gifts_donations"
    FINANCE_FEES = "finance_fees"
    BUSINESS = "business"
    TRAVEL = "travel"
    HOME = "home"
    PET = "pet"
    TAXES = "taxes"
    INVESTMENTS = "investments"
    MISC = "misc"


# ---------- add_expense ----------

class AddExpenseRequest(BaseModel):
    date: str = Field(
        ...,
        description="Expense date in ISO format (YYYY-MM-DD).",
        examples=["2026-09-10"]
    )
    amount: float = Field(
        ...,
        description="Amount spent."
    )
    category: Category = Field(
        ...,
        description="Category of the expense."
    )
    note: str = Field(
        ...,
        description="Free-form note describing the expense."
    )


class AddExpenseResponse(BaseModel):
    status: str = "ok"
    message: Optional[str] = None


# ---------- list_expenses ----------

class ListExpensesRequest(BaseModel):
    start_date: Optional[str] = Field(
        default=None,
        description="Start date for the filter in ISO format (YYYY-MM-DD).",
        examples=["2026-09-10"]
    )
    end_date: Optional[str] = Field(
        default=None,
        description="End date for the filter in ISO format (YYYY-MM-DD).",
        examples=["2026-09-10"]
    )
    category: Optional[Category] = Field(
        default=None,
        description="Filter expenses by category."
    )
    amount: Optional[float] = Field(
        default=None,
        description="Filter expenses by exact amount."
    )


class ExpenseItem(BaseModel):
    id: int = Field(
        ...,
        description="Unique identifier of the expense record in the database table."
    )
    date: str = Field(
        ...,
        description="Expense date in ISO format (YYYY-MM-DD).",
        examples=["2026-09-10"]
    )
    amount: float
    category: Category
    note: str


class ListExpensesResponse(BaseModel):
    status: str = "ok"
    expenses: List[ExpenseItem] = Field(default_factory=list)
    message: Optional[str] = None


# ---------- summarize ----------

class SummarizeRequest(BaseModel):
    start_date: str = Field(
        ...,
        description="Start date for the summary in ISO format (YYYY-MM-DD).",
        examples=["2026-09-10"]
    )
    end_date: str = Field(
        ...,
        description="End date for the summary in ISO format (YYYY-MM-DD).",
        examples=["2026-09-10"]
    )
    category: Optional[Category] = Field(
        default=None,
        description="Category to summarize. If omitted, summarize all categories."
    )


class SummaryItem(BaseModel):
    category: Category
    total_amount: float


class SummarizeResponse(BaseModel):
    status: str = "ok"
    summary: List[SummaryItem] = Field(default_factory=list)
    message: Optional[str] = None


# ---------- edit_expense_* ----------

class EditExpenseAmountRequest(BaseModel):
    id: int = Field(
        ...,
        description="Unique identifier of the expense record in the database table."
    )
    amount: float = Field(
        ...,
        description="New amount for the expense."
    )


class EditExpenseDateRequest(BaseModel):
    id: int = Field(
        ...,
        description="Unique identifier of the expense record in the database table."
    )
    new_date: str = Field(
        ...,
        description="New expense date in ISO format (YYYY-MM-DD).",
        examples=["2026-09-10"]
    )


class EditExpenseCategoryRequest(BaseModel):
    id: int = Field(
        ...,
        description="Unique identifier of the expense record in the database table."
    )
    new_category: Category = Field(
        ...,
        description="New category for the expense."
    )


class EditExpenseNoteRequest(BaseModel):
    id: int = Field(
        ...,
        description="Unique identifier of the expense record in the database table."
    )
    new_note: str = Field(
        ...,
        description="New note for the expense."
    )


class EditExpenseResponse(BaseModel):
    status: str
    message: str


# ---------- delete_expense ----------

class DeleteExpenseRequest(BaseModel):
    id: int = Field(
        ...,
        description="Unique identifier of the expense record in the database table."
    )


class DeleteExpenseResponse(BaseModel):
    status: str
    message: str

