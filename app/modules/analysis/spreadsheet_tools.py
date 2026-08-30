"""Pandas-based descriptive analysis for spreadsheet documents (xlsx/xls).
Computes real numbers directly from the stored file — no embeddings, no chunking.
"""

from langchain_core.tools import tool
from app.modules.storage.repository import StorageRepository
import logging

logger = logging.getLogger(__name__)
_repo = StorageRepository()

# Common column-name aliases we try to detect automatically
_QUANTITY_COLS = ["quantity", "qty", "units", "units sold"]
_PRICE_COLS = ["unitprice", "unit_price", "price", "unit price"]
_DATE_COLS = ["invoicedate", "invoice_date", "date", "order date", "orderdate"]
_PRODUCT_COLS = ["description", "product", "product name", "item", "stockcode", "stock_code"]
_COUNTRY_COLS = ["country", "region", "location"]


def _find_column(columns, candidates):
    lower_map = {c.lower().strip(): c for c in columns}
    for cand in candidates:
        if cand in lower_map:
            return lower_map[cand]
    return None


@tool
def analyze_spreadsheet_tool(document_id: int) -> dict:
    """Compute real descriptive statistics (totals, top products, revenue by month,
    top countries) from a stored Excel/spreadsheet document. Only works on .xlsx/.xls
    documents. Use this for questions about sales totals, top-selling items, revenue,
    or trends within a spreadsheet — NOT for text search, which won't see the full dataset."""
    try:
        import pandas as pd
    except ImportError:
        return {"error": "pandas not installed. Install with: pip install pandas"}

    doc = _repo.get_document(document_id)
    if not doc or not doc.stored_path:
        return {"error": f"document {document_id} not found or has no stored file"}

    if not doc.stored_path.lower().endswith((".xlsx", ".xls")):
        return {"error": f"document {document_id} ({doc.filename}) is not a spreadsheet file"}

    try:
        df = pd.read_excel(doc.stored_path)
    except Exception as e:
        logger.error("Failed to read spreadsheet %s: %s", doc.stored_path, e)
        return {"error": f"failed to read spreadsheet: {e}"}

    result = {
        "document_id": document_id,
        "filename": doc.filename,
        "row_count": int(len(df)),
        "columns": list(df.columns),
    }

    qty_col = _find_column(df.columns, _QUANTITY_COLS)
    price_col = _find_column(df.columns, _PRICE_COLS)
    date_col = _find_column(df.columns, _DATE_COLS)
    product_col = _find_column(df.columns, _PRODUCT_COLS)
    country_col = _find_column(df.columns, _COUNTRY_COLS)

    # Total revenue (only if we can compute quantity * price)
    if qty_col and price_col:
        try:
            df["_revenue"] = df[qty_col] * df[price_col]
            result["total_revenue"] = round(float(df["_revenue"].sum()), 2)
            result["total_units_sold"] = round(float(df[qty_col].sum()), 2)
        except Exception:
            logger.exception("Revenue computation failed")

    # Top products by revenue (or quantity if no price available)
    if product_col:
        try:
            if "_revenue" in df.columns:
                top = df.groupby(product_col)["_revenue"].sum().sort_values(ascending=False).head(10)
                result["top_products_by_revenue"] = [
                    {"product": str(k), "revenue": round(float(v), 2)} for k, v in top.items()
                ]
            elif qty_col:
                top = df.groupby(product_col)[qty_col].sum().sort_values(ascending=False).head(10)
                result["top_products_by_quantity"] = [
                    {"product": str(k), "quantity": round(float(v), 2)} for k, v in top.items()
                ]
        except Exception:
            logger.exception("Top products computation failed")

    # Revenue/orders by month
    if date_col and ("_revenue" in df.columns or True):
        try:
            df["_month"] = pd.to_datetime(df[date_col], errors="coerce").dt.to_period("M").astype(str)
            if "_revenue" in df.columns:
                by_month = df.groupby("_month")["_revenue"].sum().sort_index()
                result["revenue_by_month"] = [
                    {"month": k, "revenue": round(float(v), 2)} for k, v in by_month.items()
                ]
            else:
                by_month = df.groupby("_month").size().sort_index()
                result["orders_by_month"] = [
                    {"month": k, "count": int(v)} for k, v in by_month.items()
                ]
        except Exception:
            logger.exception("Monthly breakdown computation failed")

    # Top countries
    if country_col:
        try:
            top_countries = df[country_col].value_counts().head(10)
            result["top_countries_by_order_count"] = [
                {"country": str(k), "orders": int(v)} for k, v in top_countries.items()
            ]
        except Exception:
            logger.exception("Top countries computation failed")

    return result


SPREADSHEET_TOOLS = [analyze_spreadsheet_tool]