"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import AdminDocumentList from "@/components/AdminDocumentList";
import {
  DocumentRecord,
  listDocuments,
  uploadDocument,
  deleteDocument,
  reindexDocument,
} from "@/lib/api";

const DOC_TYPES = [
  "attendance",
  "examination",
  "academic_calendar",
  "placement",
  "scholarship",
  "hostel",
  "student_handbook",
  "regulations",
  "general",
];

export default function AdminPage() {
  const [token, setToken] = useState("");
  const [unlocked, setUnlocked] = useState(false);
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [docType, setDocType] = useState("general");
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = async (t: string) => {
    try {
      const docs = await listDocuments(t);
      setDocuments(docs);
      setError(null);
    } catch (e: any) {
      setError(e.message);
      setUnlocked(false);
    }
  };

  useEffect(() => {
    const saved = typeof window !== "undefined" ? sessionStorage.getItem("admin_token") : null;
    if (saved) {
      setToken(saved);
      setUnlocked(true);
      refresh(saved);
    }
  }, []);

  const handleUnlock = async () => {
    if (!token.trim()) return;
    await refresh(token);
    if (!error) {
      setUnlocked(true);
      sessionStorage.setItem("admin_token", token);
    }
  };

  const handleUpload = async (file: File) => {
    setUploading(true);
    setError(null);
    try {
      await uploadDocument(token, file, docType);
      await refresh(token);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id: number) => {
    await deleteDocument(token, id);
    await refresh(token);
  };

  const handleReindex = async (id: number) => {
    await reindexDocument(token, id);
    await refresh(token);
  };

  if (!unlocked) {
    return (
      <div className="flex h-screen items-center justify-center bg-paper">
        <div className="w-full max-w-sm rounded-xl border border-navy/10 bg-white p-6 shadow-sm">
          <h1 className="font-serif text-lg font-semibold text-navy-dark">Admin access</h1>
          <p className="mt-1 text-sm text-navy/50">Enter the admin token to continue.</p>
          <input
            type="password"
            value={token}
            onChange={(e) => setToken(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleUnlock()}
            placeholder="Admin token"
            className="mt-4 w-full rounded-lg border border-navy/15 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gold/50"
          />
          {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
          <button
            onClick={handleUnlock}
            className="mt-4 w-full rounded-lg bg-navy px-4 py-2 text-sm font-medium text-white hover:bg-navy-light"
          >
            Continue
          </button>
          <Link href="/" className="mt-3 block text-center text-xs text-navy/40 hover:text-navy/60">
            ← Back to chat
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-paper">
      <header className="border-b border-navy/10 bg-white px-8 py-5">
        <div className="mx-auto flex max-w-4xl items-center justify-between">
          <div>
            <h1 className="font-serif text-lg font-semibold text-navy-dark">Admin Dashboard</h1>
            <p className="text-sm text-navy/50">Manage the Sanjivani knowledge base</p>
          </div>
          <Link href="/" className="text-sm text-navy/50 hover:text-navy">
            ← Back to chat
          </Link>
        </div>
      </header>

      <main className="mx-auto max-w-4xl px-8 py-8">
        <div className="mb-8 rounded-xl border border-navy/10 bg-white p-5">
          <h2 className="font-medium text-navy-dark">Upload document</h2>
          <div className="mt-3 flex flex-wrap items-center gap-3">
            <select
              value={docType}
              onChange={(e) => setDocType(e.target.value)}
              className="rounded-lg border border-navy/15 px-3 py-2 text-sm"
            >
              {DOC_TYPES.map((t) => (
                <option key={t} value={t}>
                  {t.replace("_", " ")}
                </option>
              ))}
            </select>
            <label className="cursor-pointer rounded-lg bg-navy px-4 py-2 text-sm font-medium text-white hover:bg-navy-light">
              {uploading ? "Uploading…" : "+ Upload Document"}
              <input
                type="file"
                accept="application/pdf"
                className="hidden"
                disabled={uploading}
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) handleUpload(file);
                  e.target.value = "";
                }}
              />
            </label>
          </div>
          {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
        </div>

        <h2 className="mb-3 font-medium text-navy-dark">Documents</h2>
        <AdminDocumentList documents={documents} onDelete={handleDelete} onReindex={handleReindex} />
      </main>
    </div>
  );
}
