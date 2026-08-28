import { apiClient} from "./client";

export interface ChunkResult {
  id: number;
  document_id: number;
  chunk_index: number | null;
  snippet: string;
  score: number;
}

export interface SearchResponse {
  total: number;
  results: ChunkResult[];
}

export const searchChunks = (q: string, limit = 10, offset = 0) =>
  api.get<SearchResponse>(`/search/?q=${encodeURIComponent(q)}&limit=${limit}&offset=${offset}`);
export const searchInDocument = (documentId: number, q: string, limit = 10, offset = 0) =>
  api.get<SearchResponse>(`/search/doc/${documentId}?q=${encodeURIComponent(q)}&limit=${limit}&offset=${offset}`);