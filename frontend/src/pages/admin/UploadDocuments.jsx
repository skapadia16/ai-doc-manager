// =====================================================
// src/pages/admin/UploadDocuments.jsx — File Upload
// =====================================================

import { useState, useRef } from "react";
import { documentAPI } from "../../api/client";
import { Upload, File, CheckCircle, XCircle, Loader, X } from "lucide-react";

export default function UploadDocuments() {
  const [files, setFiles] = useState([]);       // selected files
  const [uploading, setUploading] = useState(false);
  const [results, setResults] = useState([]);   // upload results
  const fileInputRef = useRef(null);

  const ALLOWED = ["pdf", "docx", "txt", "csv", "xlsx"];

  // File select hone par
  const handleFileSelect = (e) => {
    const selected = Array.from(e.target.files);
    const valid = selected.filter((f) => {
      const ext = f.name.split(".").pop().toLowerCase();
      return ALLOWED.includes(ext);
    });
    setFiles(valid);
  };

  // Drag & Drop
  const handleDrop = (e) => {
    e.preventDefault();
    const dropped = Array.from(e.dataTransfer.files);
    setFiles(dropped);
  };

  // Upload karo
  const handleUpload = async () => {
    if (files.length === 0) return;
    setUploading(true);
    setResults([]);

    const uploadResults = [];
    for (const file of files) {
      const formData = new FormData();
      formData.append("file", file);
      try {
        await documentAPI.upload(formData);
        uploadResults.push({ name: file.name, success: true });
      } catch (err) {
        uploadResults.push({ name: file.name, success: false, error: err.response?.data?.detail });
      }
    }

    setResults(uploadResults);
    setFiles([]);
    setUploading(false);
  };

  return (
    <div className="p-8 max-w-2xl">
      <h1 className="text-2xl font-bold text-white mb-6">Upload Documents</h1>

      {/* Drop Zone */}
      <div
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
        onClick={() => fileInputRef.current?.click()}
        className="border-2 border-dashed border-gray-700 rounded-xl p-12 text-center cursor-pointer hover:border-blue-500 transition-colors"
      >
        <Upload className="w-10 h-10 text-gray-500 mx-auto mb-3" />
        <p className="text-white font-medium">Drop files here or click to browse</p>
        <p className="text-gray-500 text-sm mt-1">PDF, DOCX, TXT, CSV, Excel (max 50MB)</p>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.docx,.txt,.csv,.xlsx,.xls"
          onChange={handleFileSelect}
          className="hidden"
        />
      </div>

      {/* Selected Files */}
      {files.length > 0 && (
        <div className="mt-4 space-y-2">
          {files.map((file, i) => (
            <div key={i} className="flex items-center gap-3 bg-gray-900 p-3 rounded-lg border border-gray-800">
              <File className="w-4 h-4 text-blue-400 flex-shrink-0" />
              <span className="text-sm text-white flex-1 truncate">{file.name}</span>
              <span className="text-xs text-gray-500">{(file.size / 1024).toFixed(1)} KB</span>
              <button onClick={() => setFiles(files.filter((_, idx) => idx !== i))}>
                <X className="w-4 h-4 text-gray-500 hover:text-red-400" />
              </button>
            </div>
          ))}

          <button
            onClick={handleUpload}
            disabled={uploading}
            className="w-full mt-3 bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-lg font-medium flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
          >
            {uploading ? <Loader className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
            {uploading ? "Uploading..." : `Upload ${files.length} file(s)`}
          </button>
        </div>
      )}

      {/* Results */}
      {results.length > 0 && (
        <div className="mt-6 space-y-2">
          <h3 className="text-white font-medium mb-3">Upload Results</h3>
          {results.map((r, i) => (
            <div key={i} className={`flex items-center gap-3 p-3 rounded-lg border ${r.success ? "border-green-800 bg-green-900/20" : "border-red-800 bg-red-900/20"}`}>
              {r.success
                ? <CheckCircle className="w-4 h-4 text-green-400" />
                : <XCircle className="w-4 h-4 text-red-400" />}
              <span className="text-sm text-white flex-1">{r.name}</span>
              {r.error && <span className="text-xs text-red-400">{r.error}</span>}
              {r.success && <span className="text-xs text-green-400">Processing...</span>}
            </div>
          ))}
        </div>
      )}

      <div className="mt-6 bg-blue-900/20 border border-blue-800 rounded-lg p-4">
        <p className="text-blue-300 text-sm">
          📌 After upload, documents will be automatically processed through the RAG pipeline.
          This may take a minute. Check Documents page for status.
        </p>
      </div>
    </div>
  );
}
