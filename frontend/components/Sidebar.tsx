import Link from "next/link";

export default function Sidebar({
  onNewConversation,
  onClearChat,
}: {
  onNewConversation: () => void;
  onClearChat: () => void;
}) {
  return (
    <aside className="flex h-full w-64 flex-col border-r border-navy/10 bg-navy text-white">
      <div className="px-5 py-6">
        <h1 className="font-serif text-xl font-semibold tracking-tight">SanjivaniAI</h1>
        <p className="mt-1 text-xs text-white/60">
          Your AI Assistant for Sanjivani University
        </p>
      </div>

      <div className="flex flex-col gap-1 px-3">
        <button
          onClick={onNewConversation}
          className="rounded-lg px-3 py-2 text-left text-sm text-white/90 transition-colors hover:bg-white/10"
        >
          + New conversation
        </button>
        <button
          onClick={onClearChat}
          className="rounded-lg px-3 py-2 text-left text-sm text-white/70 transition-colors hover:bg-white/10"
        >
          Clear chat
        </button>
      </div>

      <div className="mt-auto px-3 pb-5">
        <Link
          href="/admin"
          className="block rounded-lg px-3 py-2 text-sm text-gold/90 transition-colors hover:bg-white/10"
        >
          Admin dashboard →
        </Link>
      </div>
    </aside>
  );
}
