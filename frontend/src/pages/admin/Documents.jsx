// =====================================================
// src/pages/admin/Documents.jsx — Document Management
// =====================================================

import { useState, useEffect } from "react";
import { documentAPI, adminAPI } from "../../api/client";
import {
  FileText, Trash2, RefreshCw, CheckCircle, Clock,
  AlertCircle, Loader, UserPlus, X, ShieldCheck
} from "lucide-react";

const STATUS_CONFIG = {
  done:       { icon: CheckCircle, color: "text-green-400",  bg: "bg-green-900/20" },
  processing: { icon: Loader,      color: "text-yellow-400", bg: "bg-yellow-900/20" },
  pending:    { icon: Clock,       color: "text-gray-400",   bg: "bg-gray-800" },
  failed:     { icon: AlertCircle, color: "text-red-400",    bg: "bg-red-900/20" },
};

export default function Documents() {
  const [docs, setDocs] = useState([]);
  const [loading, setLoading] = useState(true);

  // Permission Modal State
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [users, setUsers] = useState([]);
  const [permissions, setPermissions] = useState([]);
  const [selectedUserId, setSelectedUserId] = useState("");
  const [modalLoading, setModalLoading] = useState(false);

  const fetchDocs = () => {
    setLoading(true);
    documentAPI.list()
      .then((r) => setDocs(r.data))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchDocs();
    adminAPI.users().then((r) => setUsers(r.data));
  }, []);

  const handleDelete = async (id, name) => {
    if (!confirm(`Delete "${name}"?`)) return;
    await documentAPI.delete(id);
    fetchDocs();
  };

  const handleReprocess = async (id) => {
    await documentAPI.reprocess(id);
    fetchDocs();
  };

  // Open Permission Modal
  const openPermissionModal = async (doc) => {
    setSelectedDoc(doc);
    setSelectedUserId("");
    setModalLoading(true);
    try {
      const res = await documentAPI.getPermissions(doc.id);
      setPermissions(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setModalLoading(false);
    }
  };

  // Grant Access to User
  const handleGrantAccess = async (e) => {
    e.preventDefault();
    if (!selectedUserId || !selectedDoc) return;
    try {
      await documentAPI.assignPermission({
        document_id: selectedDoc.id,
        user_id: parseInt(selectedUserId),
      });
      setSelectedUserId("");
      // Refresh permissions
      const res = await documentAPI.getPermissions(selectedDoc.id);
      setPermissions(res.data);
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to grant access");
    }
  };

  // Revoke Access
  const handleRevoke = async (permId) => {
    try {
      await documentAPI.revokePermission(permId);
      setPermissions((prev) => prev.filter((p) => p.id !== permId));
    } catch (err) {
      alert("Failed to revoke access");
    }
  };

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-white">Documents</h1>
          <p className="text-gray-400 text-sm mt-1">Manage documents & grant user access permissions</p>
        </div>
        <button onClick={fetchDocs} className="flex items-center gap-2 text-sm text-gray-400 hover:text-white">
          <RefreshCw className="w-4 h-4" /> Refresh
        </button>
      </div>

      {loading ? (
        <div className="text-center py-12 text-gray-500">Loading...</div>
      ) : docs.length === 0 ? (
        <div className="text-center py-12">
          <FileText className="w-12 h-12 text-gray-700 mx-auto mb-3" />
          <p className="text-gray-500">No documents uploaded yet</p>
        </div>
      ) : (
        <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-800">
                {["Document", "Type", "Size", "Status", "Uploaded", "Access & Actions"].map((h) => (
                  <th key={h} className="text-left text-xs text-gray-500 uppercase px-4 py-3">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {docs.map((doc) => {
                const cfg = STATUS_CONFIG[doc.status] || STATUS_CONFIG.pending;
                const Icon = cfg.icon;
                return (
                  <tr key={doc.id} className="border-b border-gray-800 hover:bg-gray-800/50">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <FileText className="w-4 h-4 text-blue-400 flex-shrink-0" />
                        <span className="text-sm text-white truncate max-w-[200px]" title={doc.original_name}>
                          {doc.original_name}
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-xs bg-gray-800 text-gray-300 px-2 py-1 rounded">
                        {doc.file_type.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-400">
                      {(doc.file_size / 1024).toFixed(1)} KB
                    </td>
                    <td className="px-4 py-3">
                      <span className={`flex items-center gap-1.5 text-xs ${cfg.color}`}>
                        <Icon className={`w-3 h-3 ${doc.status === "processing" ? "animate-spin" : ""}`} />
                        {doc.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-xs text-gray-500">
                      {new Date(doc.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        {/* Grant Access / Permissions Button */}
                        <button
                          onClick={() => openPermissionModal(doc)}
                          title="Manage User Access"
                          className="flex items-center gap-1 px-2.5 py-1.5 bg-blue-600/20 text-blue-400 hover:bg-blue-600 hover:text-white rounded text-xs transition-colors"
                        >
                          <UserPlus className="w-3.5 h-3.5" />
                          Access
                        </button>

                        <button
                          onClick={() => handleReprocess(doc.id)}
                          title="Reprocess"
                          className="p-1.5 text-gray-400 hover:text-blue-400 hover:bg-blue-900/20 rounded"
                        >
                          <RefreshCw className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => handleDelete(doc.id, doc.original_name)}
                          title="Delete"
                          className="p-1.5 text-gray-400 hover:text-red-400 hover:bg-red-900/20 rounded"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Access Permission Modal */}
      {selectedDoc && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50">
          <div className="bg-gray-900 border border-gray-800 rounded-2xl w-full max-w-md p-6">
            <div className="flex items-center justify-between mb-4 pb-3 border-b border-gray-800">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-blue-400" />
                <h2 className="text-white font-semibold text-lg">Document Access</h2>
              </div>
              <button
                onClick={() => setSelectedDoc(null)}
                className="text-gray-400 hover:text-white p-1 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <p className="text-xs text-gray-400 mb-4 truncate">
              Document: <span className="text-white font-medium">{selectedDoc.original_name}</span>
            </p>

            {/* Grant Form */}
            <form onSubmit={handleGrantAccess} className="mb-6 space-y-3">
              <label className="text-xs text-gray-400 block font-medium">Select User to Grant Access:</label>
              <div className="flex gap-2">
                <select
                  value={selectedUserId}
                  onChange={(e) => setSelectedUserId(e.target.value)}
                  className="flex-1 bg-gray-800 text-white text-sm px-3 py-2 rounded-lg border border-gray-700 focus:outline-none focus:border-blue-500"
                  required
                >
                  <option value="">-- Choose User --</option>
                  {users
                    .filter((u) => u.role !== "admin")
                    .map((u) => (
                      <option key={u.id} value={u.id}>
                        {u.name} ({u.email})
                      </option>
                    ))}
                </select>
                <button
                  type="submit"
                  disabled={!selectedUserId}
                  className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-sm px-4 py-2 rounded-lg font-medium transition-colors"
                >
                  Grant
                </button>
              </div>
            </form>

            {/* List of Users with Access */}
            <div>
              <h3 className="text-xs font-semibold uppercase text-gray-400 mb-2">Users with Access:</h3>
              {modalLoading ? (
                <p className="text-xs text-gray-500">Loading access list...</p>
              ) : permissions.length === 0 ? (
                <div className="bg-gray-800/40 border border-gray-800 rounded-lg p-3 text-center">
                  <p className="text-xs text-gray-500">No regular users assigned yet. (Admin has full access)</p>
                </div>
              ) : (
                <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                  {permissions.map((p) => (
                    <div
                      key={p.id}
                      className="flex items-center justify-between bg-gray-800 px-3 py-2 rounded-lg text-sm"
                    >
                      <div>
                        <p className="text-white text-xs font-medium">{p.user_name || "User"}</p>
                        <p className="text-gray-400 text-[11px]">{p.user_email}</p>
                      </div>
                      <button
                        onClick={() => handleRevoke(p.id)}
                        className="text-xs text-red-400 hover:text-red-300 hover:bg-red-500/10 px-2 py-1 rounded"
                      >
                        Revoke
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="mt-6 pt-4 border-t border-gray-800 flex justify-end">
              <button
                onClick={() => setSelectedDoc(null)}
                className="bg-gray-800 hover:bg-gray-700 text-white text-sm px-4 py-2 rounded-lg"
              >
                Done
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
