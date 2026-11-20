// =====================================================
// src/pages/admin/Dashboard.jsx — Admin Dashboard
// =====================================================

import { useState, useEffect } from "react";
import { adminAPI, documentAPI } from "../../api/client";
import { Users, FileText, CheckCircle, MessageSquare, Clock, TrendingUp } from "lucide-react";

// Stats card component
function StatCard({ label, value, icon: Icon, color }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <div className="flex items-center justify-between mb-3">
        <span className="text-gray-400 text-sm">{label}</span>
        <div className={`w-9 h-9 ${color} rounded-lg flex items-center justify-center`}>
          <Icon className="w-4 h-4 text-white" />
        </div>
      </div>
      <p className="text-3xl font-bold text-white">{value ?? "—"}</p>
    </div>
  );
}

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [docs, setDocs] = useState([]);
  const [activity, setActivity] = useState([]);

  useEffect(() => {
    // Sab data ek saath load karo
    adminAPI.stats().then((r) => setStats(r.data));
    documentAPI.list().then((r) => setDocs(r.data.slice(0, 5)));  // latest 5
    adminAPI.activity().then((r) => setActivity(r.data.slice(0, 10)));
  }, []);

  // Status color
  const statusColor = {
    done: "text-green-400",
    processing: "text-yellow-400",
    pending: "text-gray-400",
    failed: "text-red-400",
  };

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold text-white mb-6">Dashboard</h1>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard label="Total Users" value={stats?.total_users} icon={Users} color="bg-blue-600" />
        <StatCard label="Total Documents" value={stats?.total_documents} icon={FileText} color="bg-purple-600" />
        <StatCard label="Processed" value={stats?.processed_documents} icon={CheckCircle} color="bg-green-600" />
        <StatCard label="Conversations" value={stats?.total_conversations} icon={MessageSquare} color="bg-orange-600" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Documents */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <h2 className="text-white font-semibold mb-4 flex items-center gap-2">
            <FileText className="w-4 h-4 text-blue-400" /> Recent Documents
          </h2>
          <div className="space-y-3">
            {docs.map((doc) => (
              <div key={doc.id} className="flex items-center justify-between py-2 border-b border-gray-800">
                <div>
                  <p className="text-sm text-white">{doc.original_name}</p>
                  <p className="text-xs text-gray-500">{doc.file_type.toUpperCase()} • {(doc.file_size / 1024).toFixed(1)} KB</p>
                </div>
                <span className={`text-xs font-medium ${statusColor[doc.status]}`}>
                  {doc.status}
                </span>
              </div>
            ))}
            {docs.length === 0 && <p className="text-gray-500 text-sm">No documents yet</p>}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <h2 className="text-white font-semibold mb-4 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-green-400" /> Recent Activity
          </h2>
          <div className="space-y-3">
            {activity.map((log) => (
              <div key={log.id} className="flex items-start gap-3 py-2 border-b border-gray-800">
                <Clock className="w-3 h-3 text-gray-500 mt-1 flex-shrink-0" />
                <div>
                  <p className="text-sm text-white">{log.action.replace(/_/g, " ")}</p>
                  <p className="text-xs text-gray-500">{new Date(log.created_at).toLocaleString()}</p>
                </div>
              </div>
            ))}
            {activity.length === 0 && <p className="text-gray-500 text-sm">No activity yet</p>}
          </div>
        </div>
      </div>
    </div>
  );
}
