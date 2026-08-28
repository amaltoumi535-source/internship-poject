import { apiClient } from "./client";

export interface ReportOverview {
  total_documents: number;
  total_chunks: number;
  avg_chunks_per_document: number;
  last_ingest_at: string | null;
}

export interface DocReport {
  document_id: number;
  title: string | null;
  chunk_count: number;
  avg_chunk_length: number;
  sample_snippets: string[];
}

export interface DocumentRow {
  id: number;
  title: string | null;
  created_at: string | null;
}

export interface ExportDocumentsResponse {
  total: number;
  rows: DocumentRow[];
}

export const getReportsOverview = () => apiClient.get<ReportOverview>("/reports/overview");
export const getDocReport = (documentId: number, sampleLimit = 3) =>
  apiClient.get<DocReport>(`/reports/doc/${documentId}?sample_limit=${sampleLimit}`);
export const exportDocuments = (format: "json" | "csv" = "json", limit = 1000, offset = 0) =>
  apiClient.get<ExportDocumentsResponse>(`/reports/export?format=${format}&limit=${limit}&offset=${offset}`);