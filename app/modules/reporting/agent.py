from langchain_core.tools import tool
from app.modules.storage.database import SessionLocal
from . import service as reporting_service


@tool
def reporting_overview_tool() -> dict:
    """Retourne les métriques globales: nombre de documents, nombre de chunks,
    moyenne de chunks par document, date du dernier ingest."""
    session = SessionLocal()
    try:
        return reporting_service.overview(session)
    finally:
        session.close()


@tool
def document_report_tool(document_id: int, sample_limit: int = 3) -> dict:
    """Retourne un rapport détaillé pour un document: nombre de chunks,
    longueur moyenne des chunks, extraits d'exemple."""
    session = SessionLocal()
    try:
        return reporting_service.doc_report(session, document_id, sample_limit=sample_limit)
    finally:
        session.close()


@tool
def export_documents_tool(limit: int = 1000, offset: int = 0) -> dict:
    """Exporte la liste des documents (id, titre, date de création), avec pagination."""
    session = SessionLocal()
    try:
        rows, total = reporting_service.export_documents(session, limit=limit, offset=offset)
        return {"documents": rows, "total": total}
    finally:
        session.close()


REPORTING_TOOLS = [reporting_overview_tool, document_report_tool, export_documents_tool]