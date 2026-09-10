from fastmcp import FastMCP
import os
from contextlib import asynccontextmanager
from collections import defaultdict

# Import the initialized Supabase client
from core.db import init_supabase_client

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
async def add_expense(date: str, amount: float, category: str, subcategory: str = "", note: str = ""):
    """Add a new expense entry to the database."""
    import core.db as core_db
    try:
        response = await core_db.supabase_client.table("expenses").insert({
            "date": date,
            "amount": amount,
            "category": category,
            "subcategory": subcategory,
            "note": note,
        }).execute()

        return {"status": "ok", "id": response.data[0]["id"]}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
async def list_expenses(start_date: str, end_date: str):
    """List expense entries within an inclusive date range."""
    import core.db as core_db
    try:
        response = await core_db.supabase_client.table("expenses") \
            .select("*") \
            .gte("date", start_date) \
            .lte("date", end_date) \
            .order("id") \
            .execute()

        return response.data
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
async def summarize(start_date: str, end_date: str, category: str = None):
    """Summarize expenses by category within an inclusive date range."""
    import core.db as core_db
    try:
        query = core_db.supabase_client.table("expenses") \
            .select("category, amount") \
            .gte("date", start_date) \
            .lte("date", end_date)

        if category:
            query = query.eq("category", category)

        response = await query.execute()

        totals = defaultdict(float)
        for row in response.data:
            totals[row["category"]] += row["amount"]

        result = [{"category": cat, "total_amount": total} for cat, total in sorted(totals.items())]
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
async def edit_expense_amount(date: str, category: str, subcategory: str, amount: float):
    """Edit the amount of a particular expense (or multiple if matching)."""
    import core.db as core_db
    try:
        response = await core_db.supabase_client.table("expenses") \
            .update({"amount": amount}) \
            .eq("date", date) \
            .eq("category", category) \
            .eq("subcategory", subcategory) \
            .execute()

        if not response.data:
            return "Expense not found."
        return "Row updated successfully."
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
async def edit_expense_date(date: str, category: str, subcategory: str, new_date: str):
    """Edit the expense date of a particular expense."""
    import core.db as core_db
    try:
        response = await core_db.supabase_client.table("expenses") \
            .update({"date": new_date}) \
            .eq("date", date) \
            .eq("category", category) \
            .eq("subcategory", subcategory) \
            .execute()

        if not response.data:
            return "Expense not found."
        return "Date updated successfully."
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
async def edit_expense_category(date: str, category: str, subcategory: str, new_category: str):
    """Edit the category of a particular expense."""
    import core.db as core_db
    try:
        response = await core_db.supabase_client.table("expenses") \
            .update({"category": new_category}) \
            .eq("date", date) \
            .eq("category", category) \
            .eq("subcategory", subcategory) \
            .execute()

        if not response.data:
            return "Expense not found."
        return "Category updated successfully."
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
async def edit_expense_sub_category(date: str, category: str, subcategory: str, new_subcategory: str):
    """Edit the subcategory of a particular expense."""
    import core.db as core_db
    try:
        response = await core_db.supabase_client.table("expenses") \
            .update({"subcategory": new_subcategory}) \
            .eq("date", date) \
            .eq("category", category) \
            .eq("subcategory", subcategory) \
            .execute()

        if not response.data:
            return "Expense not found."
        return "Subcategory updated successfully."
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
async def edit_expense_note(date: str, category: str, subcategory: str, new_note: str):
    """Edit the note of a particular expense."""
    import core.db as core_db
    try:
        response = await core_db.supabase_client.table("expenses") \
            .update({"note": new_note}) \
            .eq("date", date) \
            .eq("category", category) \
            .eq("subcategory", subcategory) \
            .execute()

        if not response.data:
            return "Expense not found."
        return "Note updated successfully."
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
async def delete_expense(date: str, category: str, subcategory: str):
    """Delete a particular expense (or multiple if matching)."""
    import core.db as core_db
    try:
        response = await core_db.supabase_client.table("expenses") \
            .delete() \
            .eq("date", date) \
            .eq("category", category) \
            .eq("subcategory", subcategory) \
            .execute()

        if not response.data:
            return "Expense not found."
        return "Row deleted successfully."
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.resource("expense://categories", mime_type="application/json")
def categories():
    with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
        return f.read()


if __name__ == "__main__":
    mcp.run()