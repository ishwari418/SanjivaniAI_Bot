"use client";

import { DocumentRecord } from "@/lib/api";

const STATUS_STYLES: Record<string, string> = {
  processed: "bg-green-50 text-green-700 border-green-200",
  processing: "bg-gold/10 text-gold-dark border-gold/40",
  uploaded: "bg-navy/5 text-navy/60 border-navy/15",
  failed: "bg-red-50 text-red-700 border-red-200",
};

export default function AdminDocumentList({
  documents,
  onDelete,
  onReindex,
}: {
  documents: DocumentRecord[];
  onDelete: (id: number) => void;
  onReindex: (id: number) => void;
}) {
  if (documents.length === 0) {
    return (
      <p className="py-10 text-center text-sm text-navy/40">
        No documents uploaded yet. Upload a PDF to build the knowledge base.
      </p>
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-navy/10">
      <table className="w-full text-left text-sm">
        <thead className="bg-navy/5 text-xs uppercase tracking-wide text-navy/50">
          <tr>
            <th className="px-4 py-2.5 font-medium">Document</th>
            <th className="px-4 py-2.5 font-medium">Type</th>
            <th className="px-4 py-2.5 font-medium">Status</th>
            <th className="px-4 py-2.5 font-medium">Chunks</th>
            <th className="px-4 py-2.5 font-medium">Uploaded</th>
            <th className="px-4 py-2.5 font-medium text-right">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-navy/10">
          {documents.map((doc) => (
            <tr key={doc.id} className="bg-white">
              <td className="px-4 py-3 font-medium text-navy-dark">{doc.filename}</td>
              <td className="px-4 py-3 text-navy/60">{doc.doc_type}</td>
              <td className="px-4 py-3">
                <span
                  className={`rounded-full border px-2 py-0.5 text-xs ${
                    STATUS_STYLES[doc.status] || STATUS_STYLES.uploaded
                  }`}
                  title={doc.error_message || undefined}
                >
                  {doc.status}
                </span>
              </td>
              <td className="px-4 py-3 text-navy/60">{doc.num_chunks}</td>
              <td className="px-4 py-3 text-navy/50">
                {doc.uploaded_at ? new Date(doc.uploaded_at).toLocaleDateString() : "—"}
              </td>
              <td className="px-4 py-3">
                <div className="flex justify-end gap-3">
                  <button
                    onClick={() => onReindex(doc.id)}
                    className="text-navy/60 hover:text-navy"
                  >
                    Re-index
                  </button>
                  <button
                    onClick={() => onDelete(doc.id)}
                    className="text-red-500 hover:text-red-700"
                  >
                    Delete
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
