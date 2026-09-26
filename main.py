from fastmcp import FastMCP
import os
from contextlib import asynccontextmanager
from collections import defaultdict
from fastmcp.server.auth.providers.workos import AuthKitProvider
from fastmcp.server.auth.providers.jwt import JWTVerifier
import sys

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
    EditExpenseNoteRequest,
    EditExpenseResponse,
    DeleteExpenseRequest,
    DeleteExpenseResponse,
)

@asynccontextmanager
async def lifespan(app: FastMCP):
    import core.db as core_db
    # Startup: initialize Supabase client (if not already done)
    await init_supabase_client()

    yield  # App runs here

    # Shutdown: close the HTTP session
    await core_db.supabase_client.postgrest.session.aclose()

class DebugJWTVerifier(JWTVerifier):
    async def verify_token(self, token: str):
        access_token = await super().verify_token(token)
        print("\n" + "="*40)
        print(f"[DEBUG] AccessToken attributes: {dir(access_token)}")
        # Agar .claims hai
        if hasattr(access_token, "claims") and isinstance(access_token.claims, dict):
            for k, v in access_token.claims.items():
                print(f"[DEBUG] {k} = {v}")
        print("="*40 + "\n")
        return access_token

auth = AuthKitProvider(
    authkit_domain=os.environ["AUTHKIT_DOMAIN"],
    base_url=os.environ["BASE_URL"],   # Dhyan dena: yahan tumhara port 8003 hai, /mcp nahi
    token_verifier=DebugJWTVerifier(
        jwks_uri=f"{os.environ['AUTHKIT_DOMAIN']}/oauth2/jwks",
        issuer=os.environ["AUTHKIT_DOMAIN"],
        audience=f'{os.environ["BASE_URL"]}/mcp', # Yahan /mcp aayega
    ),
)

mcp = FastMCP("ExpenseTracker", lifespan=lifespan, auth=auth)


@mcp.tool()
async def add_expense(request: AddExpenseRequest) -> AddExpenseResponse:
    """Add a new expense entry to the database."""
    import core.db as core_db
    try:
        user_id = await core_db.get_or_create_user()
        response = await core_db.supabase_client.table("expenses").insert({
            "user_id": user_id,
            "date": request.date,
            "amount": request.amount,
            "category": request.category.value,
            "note": request.note
        }).execute()
        return AddExpenseResponse(status="ok", message="Expense has been added successfully")
    except Exception as e:
        return AddExpenseResponse(status="error", message=str(e))


@mcp.tool()
async def list_expenses(request: ListExpensesRequest) -> ListExpensesResponse:
    """List expenses with optional filters for date range, category, and amount."""
    import core.db as core_db
    try:
        user_id = await core_db.get_or_create_user()
        query = core_db.supabase_client.table("expenses").select("*").eq("user_id", user_id)

        if request.start_date:
            query = query.gte("date", request.start_date)
        if request.end_date:
            query = query.lte("date", request.end_date)
        if request.category:
            query = query.eq("category", request.category.value.value)
        if request.amount:
            query = query.eq("amount", request.amount)

        response = await query.execute()
        items = [ExpenseItem(**row) for row in response.data]
        return ListExpensesResponse(status="ok", expenses=items)
    except Exception as e:
        return ListExpensesResponse(status="error", message=str(e))


@mcp.tool()
async def summarize(request: SummarizeRequest) -> SummarizeResponse:
    """Summarize expenses by category within an inclusive date range."""
    import core.db as core_db
    try:
        user_id = await core_db.get_or_create_user()
        query = core_db.supabase_client.table("expenses") \
            .select("category, amount") \
            .eq("user_id", user_id) \
            .gte("date", request.start_date) \
            .lte("date", request.end_date)

        if request.category:
            query = query.eq("category", request.category.value)

        response = await query.execute()
        totals = defaultdict(float)
        for row in response.data:
            totals[row["category"]] += row["amount"]
        summary = [SummaryItem(category=cat, total_amount=total) for cat, total in sorted(totals.items())]
        return SummarizeResponse(status="ok", summary=summary)
    except Exception as e:
        return SummarizeResponse(status="error", message=str(e))
            

@mcp.tool()
async def edit_expense_amount(request: EditExpenseAmountRequest) -> EditExpenseResponse:
    """Update the amount of an expense by its ID."""
    import core.db as core_db
    try:
        user_id = await core_db.get_or_create_user()
        response = await core_db.supabase_client.table("expenses") \
            .update({"amount": request.amount}) \
            .eq("id", request.id) \
            .eq("user_id", user_id) \
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
        user_id = await core_db.get_or_create_user()
        response = await core_db.supabase_client.table("expenses") \
            .update({"date": request.new_date}) \
            .eq("id", request.id) \
            .eq("user_id", user_id) \
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
        user_id = await core_db.get_or_create_user()
        response = await core_db.supabase_client.table("expenses") \
            .update({"category": request.new_category}) \
            .eq("id", request.id) \
            .eq("user_id", user_id) \
            .execute()

        if not response.data:
            return EditExpenseResponse(status="error", message="Expense not found.")
        return EditExpenseResponse(status="ok", message="Category updated successfully.")
    except Exception as e:
        return EditExpenseResponse(status="error", message=str(e))


@mcp.tool()
async def edit_expense_note(request: EditExpenseNoteRequest) -> EditExpenseResponse:
    """Edit the note of a particular expense."""
    import core.db as core_db
    try:
        user_id = await core_db.get_or_create_user()
        response = await core_db.supabase_client.table("expenses") \
            .update({"note": request.new_note}) \
            .eq("id", request.id) \
            .eq("user_id", user_id) \
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
        user_id = await core_db.get_or_create_user()
        response = await core_db.supabase_client.table("expenses") \
            .delete() \
            .eq("id", request.id) \
            .eq("user_id", user_id) \
            .execute()

        if not response.data:
            return DeleteExpenseResponse(status="error", message="Expense not found.")
        return DeleteExpenseResponse(status="ok", message="Row deleted successfully.")
    except Exception as e:
        return DeleteExpenseResponse(status="error", message=str(e))


# if __name__ == "__main__":
#     mcp.run()

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)