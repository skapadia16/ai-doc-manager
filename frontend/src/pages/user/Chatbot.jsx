// =====================================================
// src/pages/user/Chatbot.jsx — AI Chatbot Interface
// =====================================================
// ChatGPT jaisi interface — left mein conversations, right mein chat

import { useState, useEffect, useRef } from "react";
import { chatAPI } from "../../api/client";
import { Send, Bot, User, Loader, Plus, Trash2, FileText } from "lucide-react";

// Ek message ka UI
function Message({ msg }) {
  const isUser = msg.role === "user";
  return (
    <div className={`flex gap-3 ${isUser ? "flex-row-reverse" : ""}`}>
      {/* Avatar */}
      <div
        className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${isUser ? "bg-blue-600" : "bg-gray-700"}`}
      >
        {isUser ? (
          <User className="w-4 h-4 text-white" />
        ) : (
          <Bot className="w-4 h-4 text-white" />
        )}
      </div>

      {/* Message bubble */}
      <div
        className={`max-w-[75%] ${isUser ? "items-end" : "items-start"} flex flex-col gap-1`}
      >
        <div
          className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${isUser ? "bg-blue-600 text-white" : "bg-gray-800 text-gray-100"}`}
        >
          {msg.content}
        </div>

        {/* Sources (AI message ke liye) */}
        {!isUser && msg.sources && msg.sources.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-1">
            {msg.sources.map((s, i) => (
              <span
                key={i}
                className="flex items-center gap-1 text-xs bg-gray-800 text-gray-400 px-2 py-1 rounded-full border border-gray-700"
              >
                <FileText className="w-3 h-3" />
                {s.document_name}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default function Chatbot() {
  const [conversations, setConversations] = useState([]);
  const [activeConvId, setActiveConvId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  // Conversations load karo
  useEffect(() => {
    chatAPI.conversations().then((r) => setConversations(r.data));
  }, []);

  // Conversation select karne par messages load karo
  useEffect(() => {
    if (activeConvId) {
      chatAPI.messages(activeConvId).then((r) => setMessages(r.data));
    } else {
      setMessages([]);
    }
  }, [activeConvId]);

  // Naya message aane par scroll down
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!question.trim() || loading) return;

    const userQuestion = question;
    setQuestion("");
    setLoading(true);

    // User message instantly dikhao
    setMessages((prev) => [
      ...prev,
      { role: "user", content: userQuestion, id: Date.now() },
    ]);

    try {
      const res = await chatAPI.ask({
        conversation_id: activeConvId,
        question: userQuestion,
      });
      const data = res.data;

      // Naya conversation ho toh list update karo
      if (!activeConvId) {
        setActiveConvId(data.conversation_id);
        chatAPI.conversations().then((r) => setConversations(r.data));
      }

      // AI ka jawab add karo
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer,
          sources: data.sources,
          id: Date.now() + 1,
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, something went wrong. Please try again.",
          id: Date.now() + 1,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleNewChat = () => {
    setActiveConvId(null);
    setMessages([]);
  };

  const handleDelete = async (id) => {
    await chatAPI.deleteConversation(id);
    if (activeConvId === id) handleNewChat();
    chatAPI.conversations().then((r) => setConversations(r.data));
  };

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Left: Conversation list */}
      <div className="w-64 bg-gray-900 border-r border-gray-800 flex flex-col">
        <div className="p-4 border-b border-gray-800">
          <button
            onClick={handleNewChat}
            className="w-full flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-3 py-2.5 rounded-lg text-sm"
          >
            <Plus className="w-4 h-4" /> New Chat
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {conversations.map((conv) => (
            <div
              key={conv.id}
              onClick={() => setActiveConvId(conv.id)}
              className={`flex items-center gap-2 px-3 py-2.5 rounded-lg cursor-pointer group ${activeConvId === conv.id ? "bg-gray-800" : "hover:bg-gray-800/50"}`}
            >
              <Bot className="w-3.5 h-3.5 text-gray-500 flex-shrink-0" />
              <span className="text-sm text-gray-300 flex-1 truncate">
                {conv.title}
              </span>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleDelete(conv.id);
                }}
                className="opacity-0 group-hover:opacity-100 p-1 text-gray-500 hover:text-red-400"
              >
                <Trash2 className="w-3 h-3" />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Right: Chat area */}
      <div className="flex-1 flex flex-col bg-gray-950">
        {/* Header */}
        <div className="p-4 border-b border-gray-800">
          <div className="flex items-center gap-2">
            <Bot className="w-5 h-5 text-blue-400" />
            <span className="text-white font-medium">DocuGenius</span>
          </div>
          <p className="text-xs text-gray-500 mt-0.5">
            Ask questions about your documents
          </p>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.length === 0 && (
            <div className="text-center py-16">
              <Bot className="w-12 h-12 text-gray-700 mx-auto mb-3" />
              <p className="text-gray-500">
                Ask me anything about your documents
              </p>
            </div>
          )}
          {messages.map((msg, i) => (
            <Message key={msg.id || i} msg={msg} />
          ))}

          {/* Loading indicator */}
          {loading && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center">
                <Bot className="w-4 h-4 text-white" />
              </div>
              <div className="bg-gray-800 rounded-2xl px-4 py-3">
                <Loader className="w-4 h-4 text-gray-400 animate-spin" />
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input box */}
        <div className="p-4 border-t border-gray-800">
          <div className="flex items-end gap-3 bg-gray-900 border border-gray-700 rounded-xl p-3">
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              placeholder="Ask a question about your documents..."
              rows={1}
              className="flex-1 bg-transparent text-white placeholder-gray-500 resize-none focus:outline-none text-sm"
            />
            <button
              onClick={handleSend}
              disabled={!question.trim() || loading}
              className="w-8 h-8 bg-blue-600 hover:bg-blue-700 rounded-lg flex items-center justify-center flex-shrink-0 disabled:opacity-40 transition-colors"
            >
              <Send className="w-3.5 h-3.5 text-white" />
            </button>
          </div>
          <p className="text-xs text-gray-600 mt-2 text-center">
            Answers are based only on uploaded documents
          </p>
        </div>
      </div>
    </div>
  );
}
