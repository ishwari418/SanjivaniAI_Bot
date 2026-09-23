"use client";

import { useEffect, useRef, useState } from "react";
import Sidebar from "@/components/Sidebar";
import ChatMessage, { Message } from "@/components/ChatMessage";
import ChatInput from "@/components/ChatInput";
import { sendChatMessage } from "@/lib/api";

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = async (text: string) => {
    const userMessage: Message = { role: "user", content: text };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      const res = await sendChatMessage(text);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: res.answer, sources: res.sources, mode: res.mode },
      ]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: err.message || "Something went wrong. Please try again.",
          isError: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleNewConversation = () => setMessages([]);
  const handleClearChat = () => setMessages([]);

  return (
    <div className="flex h-screen bg-paper">
      <Sidebar onNewConversation={handleNewConversation} onClearChat={handleClearChat} />

      <main className="flex flex-1 flex-col">
        <header className="border-b border-navy/10 bg-white px-6 py-4">
          <h2 className="font-serif text-lg font-semibold text-navy-dark">SanjivaniAI</h2>
          <p className="text-sm text-navy/50">
            Ask about attendance, exams, hostel rules, scholarships, placements, and more.
          </p>
        </header>

        <div className="flex-1 overflow-y-auto px-6 py-6">
          <div className="mx-auto flex max-w-2xl flex-col gap-4">
            {messages.length === 0 && (
              <div className="mt-16 text-center">
                <p className="font-serif text-lg text-navy-dark">
                  What would you like to know?
                </p>
                <p className="mt-1 text-sm text-navy/45">
                  Answers about Sanjivani University are grounded in official documents,
                  with sources cited.
                </p>
              </div>
            )}

            {messages.map((m, i) => (
              <ChatMessage key={i} message={m} />
            ))}

            {loading && (
              <div className="flex justify-start">
                <div className="flex items-center gap-1.5 rounded-2xl rounded-tl-sm border border-navy/10 bg-white px-4 py-3">
                  <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-navy/40 [animation-delay:-0.3s]" />
                  <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-navy/40 [animation-delay:-0.15s]" />
                  <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-navy/40" />
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        </div>

        <div className="border-t border-navy/10 bg-paper px-6 py-4">
          <div className="mx-auto max-w-2xl">
            <ChatInput onSend={handleSend} disabled={loading} />
          </div>
        </div>
      </main>
    </div>
  );
}
