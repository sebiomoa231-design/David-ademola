"use client";

import { useState } from "react";
import { api } from "@/lib/api";

type Message = {
  role: "user" | "assistant";
  content: string;
};

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  async function send(text: string) {
    const message = text.trim();
    if (!message) return;

    setLoading(true);
    setMessages((prev) => [...prev, { role: "user", content: message }]);

    try {
      const response = await api.chat(message);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: response.reply },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return { messages, loading, send };
}
