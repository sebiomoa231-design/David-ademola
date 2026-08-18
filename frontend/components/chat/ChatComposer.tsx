'use client';

import { useState } from 'react';
import { useChat } from '@/hooks/useChat';

export function ChatComposer() {
  const [message, setMessage] = useState('');
  const { send, loading } = useChat();

  async function submit() {
    if (!message.trim() || loading) return;
    await send(message);
    setMessage('');
  }

  return (
    <div className="border-t border-white/10 p-4">
      <div className="flex gap-2 rounded-2xl border border-white/10 bg-slate-900 p-2">
        <input
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter') void submit();
          }}
          className="min-w-0 flex-1 bg-transparent px-3 py-3 outline-none"
          placeholder="Message David..."
          aria-label="Message David"
        />
        <button onClick={() => void submit()} disabled={loading} className="rounded-xl bg-red-600 px-5 py-3">
          {loading ? 'Thinking...' : 'Send'}
        </button>
      </div>
    </div>
  );
}
