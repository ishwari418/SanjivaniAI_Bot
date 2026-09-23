import { Source } from "@/lib/api";

export default function SourceCitation({ sources }: { sources: Source[] }) {
  if (!sources || sources.length === 0) return null;

  return (
    <div className="mt-3 border-t border-navy/10 pt-3">
      <p className="text-xs font-medium text-navy/60 mb-1.5">Sources</p>
      <div className="flex flex-wrap gap-2">
        {sources.map((s, i) => (
          <div
            key={i}
            className="flex items-center gap-1.5 rounded-md border border-gold/40 bg-gold/10 px-2.5 py-1 text-xs text-navy-dark"
          >
            <span className="font-medium">{s.document_name}</span>
            <span className="text-navy/50">· Page {s.page_number}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
