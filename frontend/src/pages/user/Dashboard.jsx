// =====================================================
// src/pages/user/Dashboard.jsx — User Dashboard
// =====================================================

import { useState, useEffect } from "react";
import { documentAPI, chatAPI } from "../../api/client";
import { useAuth } from "../../context/AuthContext";
import { Link } from "react-router-dom";
import { FolderOpen, MessageSquare, Bot, ArrowRight } from "lucide-react";

export default function UserDashboard() {
  const { user } = useAuth();
  const [docs, setDocs] = useState([]);
  const [conversations, setConversations] = useState([]);

  useEffect(() => {
    documentAPI.list().then((r) => setDocs(r.data));
    chatAPI.conversations().then((r) => setConversations(r.data));
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold text-white mb-2">Welcome, {user?.name}! 👋</h1>
      <p className="text-gray-400 mb-8">Ask questions about your documents using AI</p>

      {/* Quick action */}
      <Link
        to="/user/chat"
        className="block bg-gradient-to-r from-blue-600 to-blue-700 rounded-xl p-6 mb-8 hover:from-blue-700 hover:to-blue-800 transition-all"
      >
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Bot className="w-5 h-5 text-blue-200" />
              <span className="text-blue-200 text-sm">AI Assistant</span>
            </div>
            <h2 className="text-white text-xl font-semibold">Start a New Conversation</h2>
            <p className="text-blue-200 text-sm mt-1">Ask questions about your documents</p>
          </div>
          <ArrowRight className="w-6 h-6 text-blue-300" />
        </div>
      </Link>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* My Documents */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-white font-semibold flex items-center gap-2">
              <FolderOpen className="w-4 h-4 text-blue-400" /> My Documents
            </h2>
            <span className="text-xs text-gray-500">{docs.length} docs</span>
          </div>
          <div className="space-y-2">
            {docs.slice(0, 5).map((doc) => (
              <div key={doc.id} className="flex items-center gap-3 py-2 border-b border-gray-800">
                <div className="w-8 h-8 bg-gray-800 rounded-lg flex items-center justify-center text-xs text-gray-400">
                  {doc.file_type.toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-white truncate">{doc.original_name}</p>
                  <p className={`text-xs ${doc.status === "done" ? "text-green-400" : "text-gray-500"}`}>
                    {doc.status}
                  </p>
                </div>
              </div>
            ))}
            {docs.length === 0 && <p className="text-gray-500 text-sm">No documents available</p>}
          </div>
        </div>

        {/* Recent Chats */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-white font-semibold flex items-center gap-2">
              <MessageSquare className="w-4 h-4 text-green-400" /> Recent Chats
            </h2>
            <span className="text-xs text-gray-500">{conversations.length} total</span>
          </div>
          <div className="space-y-2">
            {conversations.slice(0, 5).map((conv) => (
              <Link
                key={conv.id}
                to="/user/chat"
                className="flex items-center gap-3 py-2 border-b border-gray-800 hover:bg-gray-800/50 -mx-2 px-2 rounded"
              >
                <Bot className="w-4 h-4 text-gray-500" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-white truncate">{conv.title}</p>
                  <p className="text-xs text-gray-500">{new Date(conv.created_at).toLocaleDateString()}</p>
                </div>
              </Link>
            ))}
            {conversations.length === 0 && <p className="text-gray-500 text-sm">No conversations yet</p>}
          </div>
        </div>
      </div>
    </div>
  );
}
