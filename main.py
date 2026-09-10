from fastmcp import FastMCP
import os
from contextlib import asynccontextmanager
from collections import defaultdict

# Import the initialized Supabase client
from core.db import init_supabase_client

# Import the Pydantic request/response models
from models import (
    AddExpenseRequest, AddExpenseResponse,
    ListExpensesRequest, ListExpensesResponse, ExpenseItem,
    SummarizeRequest, SummarizeResponse, SummaryItem,
    EditExpenseAmountRequest,
    EditExpenseDateRequest,
    EditExpenseCategoryRequest,
    EditExpenseSubCategoryRequest,
    EditExpenseNoteRequest,
    EditExpenseResponse,
    DeleteExpenseRequest,
    DeleteExpenseResponse,
)

CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")


@asynccontextmanager
async def lifespan(app: FastMCP):
    import core.db as core_db
    # Startup: initialize Supabase client (if not already done)
    await init_supabase_client()

    yield  # App runs here

    # Shutdown: close the HTTP session
    await core_db.supabase_client.postgrest.session.aclose()


mcp = FastMCP("ExpenseTracker", lifespan=lifespan)


@mcp.tool()
async def add_expense(request: AddExpenseRequest) -> AddExpenseResponse:
    """Add a new expense entry to the database."""
    import core.db as core_db
    try:
        response = await core_db.supabase_client.table("expenses").insert({
            "date": request.date,
            "amount": request.amount,
            "category": request.category,
            "subcategory": request.subcategory,
            "note": request.note,
        }).execute()

        return AddExpenseResponse(status="ok", id=response.data[0]["id"])
    except Exception as e:
        return AddExpenseResponse(status="error", message=str(e))


@mcp.tool()
async def list_expenses(request: ListExpensesRequest) -> ListExpensesResponse:
    """List expense entries within an inclusive date range."""
    import core.db as core_db
    try:
        response = await core_db.supabase_client.table("expenses") \
            .select("*") \
            .gte("date", request.start_date) \
            .lte("date", request.end_date) \
            .order("id") \
            .execute()

        items = [ExpenseItem(**row) for row in response.data]
        return ListExpensesResponse(status="ok", expenses=items)
    except Exception as e:
        return ListExpensesResponse(status="error", message=str(e))


@mcp.tool()
async def summarize(request: SummarizeRequest) -> SummarizeResponse:
    """Summarize expenses by category within an inclusive date range."""
    import core.db as core_db
    try:
        query = core_db.supabase_client.table("expenses") \
            .select("category, amount") \
            .gte("date", request.start_date) \
            .lte("date", request.end_date)

        if request.category:
            query = query.eq("category", request.category)

        response = await query.execute()

        totals = defaultdict(float)
        for row in response.data:
            totals[row["category"]] += row["amount"]

        summary = [
            SummaryItem(category=cat, total_amount=total)
            for cat, total in sorted(totals.items())
        ]
        return SummarizeResponse(status="ok", summary=summary)
    except Exception as e:
        return SummarizeResponse(status="error", message=str(e))


@mcp.tool()
async def edit_expense_amount(request: EditExpenseAmountRequest) -> EditExpenseResponse:
    """Edit the amount of a particular expense (or multiple if matching)."""
    import core.db as core_db
    try:
        response = await core_db.supabase_client.table("expenses") \
            .update({"amount": request.amount}) \
            .eq("date", request.date) \
            .eq("category", request.category) \
            .eq("subcategory", request.subcategory) \
            .execute()

        if not response.data:
            return EditExpenseResponse(status="error", message="Expense not found.")
        return EditExpenseResponse(status="ok", message="Row updated successfully.")
    except Exception as e:
        return EditExpenseResponse(status="error", message=str(e))


@mcp.tool()
async def edit_expense_date(request: EditExpenseDateRequest) -> EditExpenseResponse:
    """Edit the expense date of a particular expense."""
    import core.db as core_db
    try:
        response = await core_db.supabase_client.table("expenses") \
            .update({"date": request.new_date}) \
            .eq("date", request.date) \
            .eq("category", request.category) \
            .eq("subcategory", request.subcategory) \
            .execute()

        if not response.data:
            return EditExpenseResponse(status="error", message="Expense not found.")
        return EditExpenseResponse(status="ok", message="Date updated successfully.")
    except Exception as e:
        return EditExpenseResponse(status="error", message=str(e))


@mcp.tool()
async def edit_expense_category(request: EditExpenseCategoryRequest) -> EditExpenseResponse:
    """Edit the category of a particular expense."""
    import core.db as core_db
    try:
        response = await core_db.supabase_client.table("expenses") \
            .update({"category": request.new_category}) \
            .eq("date", request.date) \
            .eq("category", request.category) \
            .eq("subcategory", request.subcategory) \
            .execute()

        if not response.data:
            return EditExpenseResponse(status="error", message="Expense not found.")
        return EditExpenseResponse(status="ok", message="Category updated successfully.")
    except Exception as e:
        return EditExpenseResponse(status="error", message=str(e))


@mcp.tool()
async def edit_expense_sub_category(request: EditExpenseSubCategoryRequest) -> EditExpenseResponse:
    """Edit the subcategory of a particular expense."""
    import core.db as core_db
    try:
        response = await core_db.supabase_client.table("expenses") \
            .update({"subcategory": request.new_subcategory}) \
            .eq("date", request.date) \
            .eq("category", request.category) \
            .eq("subcategory", request.subcategory) \
            .execute()

        if not response.data:
            return EditExpenseResponse(status="error", message="Expense not found.")
        return EditExpenseResponse(status="ok", message="Subcategory updated successfully.")
    except Exception as e:
        return EditExpenseResponse(status="error", message=str(e))


@mcp.tool()
async def edit_expense_note(request: EditExpenseNoteRequest) -> EditExpenseResponse:
    """Edit the note of a particular expense."""
    import core.db as core_db
    try:
        response = await core_db.supabase_client.table("expenses") \
            .update({"note": request.new_note}) \
            .eq("date", request.date) \
            .eq("category", request.category) \
            .eq("subcategory", request.subcategory) \
            .execute()

        if not response.data:
            return EditExpenseResponse(status="error", message="Expense not found.")
        return EditExpenseResponse(status="ok", message="Note updated successfully.")
    except Exception as e:
        return EditExpenseResponse(status="error", message=str(e))


@mcp.tool()
async def delete_expense(request: DeleteExpenseRequest) -> DeleteExpenseResponse:
    """Delete a particular expense (or multiple if matching)."""
    import core.db as core_db
    try:
        response = await core_db.supabase_client.table("expenses") \
            .delete() \
            .eq("date", request.date) \
            .eq("category", request.category) \
            .eq("subcategory", request.subcategory) \
            .execute()

        if not response.data:
            return DeleteExpenseResponse(status="error", message="Expense not found.")
        return DeleteExpenseResponse(status="ok", message="Row deleted successfully.")
    except Exception as e:
        return DeleteExpenseResponse(status="error", message=str(e))


@mcp.resource("expense://categories", mime_type="application/json")
def categories():
    with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
        return f.read()


if __name__ == "__main__":
    mcp.run()