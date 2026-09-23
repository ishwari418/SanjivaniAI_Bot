const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";

export type Source = {
  document_name: string;
  page_number: number;
  score: number;
};

export type ChatResponse = {
  answer: string;
  sources: Source[];
  mode: "rag" | "general";
  retrieved_chunks: {
    document_name: string;
    page_number: number;
    score: number;
    text_preview: string;
  }[];
};

export async function sendChatMessage(question: string): Promise<ChatResponse> {
  const res = await fetch(`${API_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || `Request failed (${res.status})`);
  }
  return res.json();
}

export type DocumentRecord = {
  id: number;
  filename: string;
  doc_type: string;
  status: "uploaded" | "processing" | "processed" | "failed";
  num_chunks: number;
  error_message: string | null;
  uploaded_at: string | null;
  processed_at: string | null;
};

function adminHeaders(token: string) {
  return { "X-Admin-Token": token };
}

export async function listDocuments(token: string): Promise<DocumentRecord[]> {
  const res = await fetch(`${API_URL}/api/documents`, { headers: adminHeaders(token) });
  if (!res.ok) throw new Error("Failed to load documents (check admin token)");
  return res.json();
}

export async function uploadDocument(
  token: string,
  file: File,
  docType: string
): Promise<DocumentRecord> {
  const form = new FormData();
  form.append("file", file);
  form.append("doc_type", docType);
  const res = await fetch(`${API_URL}/api/documents/upload`, {
    method: "POST",
    headers: adminHeaders(token),
    body: form,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || "Upload failed");
  }
  return res.json();
}

export async function deleteDocument(token: string, id: number): Promise<void> {
  const res = await fetch(`${API_URL}/api/documents/${id}`, {
    method: "DELETE",
    headers: adminHeaders(token),
  });
  if (!res.ok) throw new Error("Delete failed");
}

export async function reindexDocument(token: string, id: number): Promise<DocumentRecord> {
  const res = await fetch(`${API_URL}/api/documents/${id}/reindex`, {
    method: "POST",
    headers: adminHeaders(token),
  });
  if (!res.ok) throw new Error("Reindex failed");
  return res.json();
}
