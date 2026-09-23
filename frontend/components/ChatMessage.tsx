"use client";

import { useState } from "react";
import SourceCitation from "./SourceCitation";
import { Source } from "@/lib/api";

export type Message = {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  mode?: "rag" | "general";
  isError?: boolean;
};

export default function ChatMessage({ message }: { message: Message }) {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === "user";

  const handleCopy = async () => {
    await navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  if (isUser) {
    return (
      <div className="flex justify-end">
        <div className="max-w-[75%] rounded-2xl rounded-tr-sm bg-navy px-4 py-2.5 text-white">
          <p className="whitespace-pre-wrap text-[15px] leading-relaxed">{message.content}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start">
      <div
        className={`group relative max-w-[85%] rounded-2xl rounded-tl-sm border px-4 py-3 ${
          message.isError
            ? "border-red-200 bg-red-50 text-red-800"
            : "border-navy/10 bg-white text-navy-dark"
        }`}
      >
        <p className="whitespace-pre-wrap text-[15px] leading-relaxed">{message.content}</p>

        {!message.isError && message.sources && message.sources.length > 0 && (
          <SourceCitation sources={message.sources} />
        )}

        {!message.isError && message.mode === "general" && (
          <p className="mt-2 text-xs italic text-navy/40">
            General knowledge — not from Sanjivani University documents.
          </p>
        )}

        {!message.isError && (
          <button
            onClick={handleCopy}
            className="absolute -bottom-2 right-2 rounded-full border border-navy/10 bg-paper px-2 py-0.5 text-[11px] text-navy/50 opacity-0 shadow-sm transition-opacity group-hover:opacity-100 hover:text-navy"
          >
            {copied ? "Copied" : "Copy"}
          </button>
        )}
      </div>
    </div>
  );
}
