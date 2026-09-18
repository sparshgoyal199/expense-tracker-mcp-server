from __future__ import annotations

from typing import Annotated, List, Optional
from pydantic import BaseModel, Field
import datetime

DateStr = Annotated[
    datetime.date,
    Field(
        description="Date in ISO format (YYYY-MM-DD)",
        examples=["2026-09-10"],
    ),
]


# class ErrorResponse(BaseModel):
#     status: str = "error"
#     message: str


class AddExpenseRequest(BaseModel):
    date: DateStr
    amount: float = Field(..., description="Expense amount")
    category: str = Field(..., description="Expense category")
    subcategory: str = Field("", description="Expense subcategory")
    note: str = Field("", description="Free-form note")

class AddExpenseResponse(BaseModel):
    status: str = "ok"
    message: Optional[str] = None


class ListExpensesRequest(BaseModel):
    start_date: DateStr
    end_date: DateStr


class ExpenseItem(BaseModel):
    id: int
    date: DateStr
    amount: float
    category: str
    subcategory: str
    note: Optional[str] = ""


class ListExpensesResponse(BaseModel):
    status: str = "ok"
    expenses: List[ExpenseItem] = Field(default_factory=list)
    message: Optional[str] = None


# ---------- summarize ----------
class SummarizeRequest(BaseModel):
    start_date: DateStr
    end_date: DateStr
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
    date: DateStr
    category: str
    subcategory: str
    amount: float


class EditExpenseDateRequest(BaseModel):
    date: DateStr
    category: str
    subcategory: str
    new_date: DateStr


class EditExpenseCategoryRequest(BaseModel):
    date: DateStr
    category: str
    subcategory: str
    new_category: str


class EditExpenseSubCategoryRequest(BaseModel):
    date: DateStr
    category: str
    subcategory: str
    new_subcategory: str


class EditExpenseNoteRequest(BaseModel):
    date: DateStr
    category: str
    subcategory: str
    new_note: str


class EditExpenseResponse(BaseModel):
    status: str
    message: str


# ---------- delete_expense ----------
class DeleteExpenseRequest(BaseModel):
    date: DateStr
    category: str
    subcategory: str


class DeleteExpenseResponse(BaseModel):
    status: str
    message: str