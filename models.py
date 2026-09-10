from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


# ---------- Shared ----------
class ErrorResponse(BaseModel):
    status: str = "error"
    message: str


# ---------- add_expense ----------
class AddExpenseRequest(BaseModel):
    date: str = Field(..., description="Expense date, ISO format (YYYY-MM-DD)")
    amount: float = Field(..., description="Expense amount")
    category: str = Field(..., description="Expense category")
    subcategory: str = Field("", description="Expense subcategory")
    note: str = Field("", description="Free-form note")


class AddExpenseResponse(BaseModel):
    status: str = "ok"
    id: Optional[int] = None
    message: Optional[str] = None


# ---------- list_expenses ----------
class ListExpensesRequest(BaseModel):
    start_date: str = Field(..., description="Inclusive start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="Inclusive end date (YYYY-MM-DD)")


class ExpenseItem(BaseModel):
    id: int
    date: str
    amount: float
    category: str
    subcategory: Optional[str] = ""
    note: Optional[str] = ""


class ListExpensesResponse(BaseModel):
    status: str = "ok"
    expenses: List[ExpenseItem] = Field(default_factory=list)
    message: Optional[str] = None


# ---------- summarize ----------
class SummarizeRequest(BaseModel):
    start_date: str
    end_date: str
    category: Optional[str] = None


class SummaryItem(BaseModel):
    category: str
    total_amount: float


class SummarizeResponse(BaseModel):
    status: str = "ok"
    summary: List[SummaryItem] = Field(default_factory=list)
    message: Optional[str] = None


# ---------- edit_expense_* ----------
class EditExpenseAmountRequest(BaseModel):
    date: str
    category: str
    subcategory: str
    amount: float


class EditExpenseDateRequest(BaseModel):
    date: str
    category: str
    subcategory: str
    new_date: str


class EditExpenseCategoryRequest(BaseModel):
    date: str
    category: str
    subcategory: str
    new_category: str


class EditExpenseSubCategoryRequest(BaseModel):
    date: str
    category: str
    subcategory: str
    new_subcategory: str


class EditExpenseNoteRequest(BaseModel):
    date: str
    category: str
    subcategory: str
    new_note: str


class EditExpenseResponse(BaseModel):
    status: str
    message: str


# ---------- delete_expense ----------
class DeleteExpenseRequest(BaseModel):
    date: str
    category: str
    subcategory: str


class DeleteExpenseResponse(BaseModel):
    status: str
    message: str