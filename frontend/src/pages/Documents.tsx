import React, { useState, useEffect } from 'react'
import { api } from '../api'
import { FileText, Trash2, Eye, X, UploadCloud, Search, CheckCircle } from 'lucide-react'

interface DocumentItem {
  id: number
  filename: string
  file_type: string
  file_size: number
  chunk_count: number
  created_at: string
}

export default function Documents() {
  const [docs, setDocs] = useState<DocumentItem[]>([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<any[]>([])
  const [isSearching, setIsSearching] = useState(false)

  // Document Viewer Modal State
  const [selectedDoc, setSelectedDoc] = useState<any>(null)
  const [docLoading, setDocLoading] = useState(false)

  const loadDocs = async () => {
    try {
      setLoading(true)
      const data = await api.documents.list()
      setDocs(data)
    } catch (err: any) {
      setError(err.message || 'Failed to load documents')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadDocs()
  }, [])

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (!files || files.length === 0) return
    setError('')
    setUploading(true)
    try {
      for (let i = 0; i < files.length; i++) {
        await api.documents.upload(files[i])
      }
      await loadDocs()
    } catch (err: any) {
      setError(err.message || 'Upload failed')
    } finally {
      setUploading(false)
      e.target.value = ''
    }
  }

  const handleDelete = async (id: number, name: string, e: React.MouseEvent) => {
    e.stopPropagation()
    if (!confirm(`Are you sure you want to delete "${name}"?`)) return
    try {
      await api.documents.delete(id)
      setDocs(docs.filter((d) => d.id !== id))
      if (selectedDoc?.id === id) setSelectedDoc(null)
    } catch (err: any) {
      alert(err.message || 'Failed to delete document')
    }
  }

  const handleViewDoc = async (id: number) => {
    try {
      setDocLoading(true)
      const data = await api.documents.get(id)
      setSelectedDoc(data)
    } catch (err: any) {
      alert(err.message || 'Failed to view document content')
    } finally {
      setDocLoading(false)
    }
  }

  const handleTestSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!searchQuery.trim()) return
    setIsSearching(true)
    try {
      const res = await api.documents.search(searchQuery)
      setSearchResults(res.results || [])
    } catch (err: any) {
      alert(err.message || 'Search failed')
    } finally {
      setIsSearching(false)
    }
  }

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Company Knowledge Base (RAG)</h1>
          <p className="text-sm text-gray-500 mt-1">
            Upload company documentation, proposals, CSV data, or PDFs. Click any file row to view its parsed content.
          </p>
        </div>
        <div>
          <label className={`cursor-pointer inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-white font-medium shadow-sm transition-all ${uploading ? 'bg-indigo-400' : 'bg-indigo-600 hover:bg-indigo-700'}`}>
            <UploadCloud className="w-5 h-5" />
            <span>{uploading ? 'Parsing & Indexing...' : 'Upload Document(s)'}</span>
            <input type="file" multiple onChange={handleFileUpload} className="hidden" disabled={uploading} />
          </label>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-50 text-red-700 rounded-lg border border-red-200 text-sm">
          {error}
        </div>
      )}

      {/* Document List */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
        <div className="p-6 border-b border-gray-100 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-800">Uploaded Files ({docs.length})</h2>
          <span className="text-xs bg-indigo-50 text-indigo-700 font-medium px-2.5 py-1 rounded-full flex items-center gap-1">
            <CheckCircle className="w-3.5 h-3.5" /> RAG Vector Indexed
          </span>
        </div>

        {loading ? (
          <div className="p-12 text-center text-gray-400">Loading document catalog...</div>
        ) : docs.length === 0 ? (
          <div className="p-12 text-center text-gray-500">
            <FileText className="w-12 h-12 mx-auto text-gray-300 mb-3" />
            <p className="font-medium text-gray-700">No documents uploaded yet.</p>
            <p className="text-sm text-gray-400 mt-1">Upload company PDFs, CSVs, or DOCX files to enable intelligent RAG proposals.</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {docs.map((doc) => (
              <div
                key={doc.id}
                onClick={() => handleViewDoc(doc.id)}
                className="p-4 sm:px-6 flex items-center justify-between hover:bg-indigo-50/50 cursor-pointer transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div className="p-2.5 bg-indigo-50 text-indigo-600 rounded-lg font-bold text-xs uppercase">
                    {doc.file_type}
                  </div>
                  <div>
                    <div className="font-medium text-gray-900 flex items-center gap-2">
                      {doc.filename}
                      <span className="text-[10px] bg-gray-100 text-gray-600 px-2 py-0.5 rounded font-normal">Click to View</span>
                    </div>
                    <div className="text-xs text-gray-400 flex items-center gap-3 mt-0.5">
                      <span>{formatBytes(doc.file_size)}</span>
                      <span>•</span>
                      <span>{doc.chunk_count} RAG chunks</span>
                      <span>•</span>
                      <span>Uploaded {new Date(doc.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleViewDoc(doc.id)}
                    className="p-2 text-indigo-600 hover:bg-indigo-100 rounded-lg transition-colors text-xs flex items-center gap-1 font-medium"
                    title="View Content"
                  >
                    <Eye className="w-4 h-4" /> View Text
                  </button>

                  <button
                    onClick={(e) => handleDelete(doc.id, doc.filename, e)}
                    className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    title="Delete Document"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Document Content Viewer Modal */}
      {selectedDoc && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl border border-gray-100 shadow-2xl max-w-3xl w-full p-6 space-y-4 max-h-[85vh] flex flex-col">
            <div className="flex items-center justify-between border-b border-gray-100 pb-3">
              <div>
                <h3 className="font-bold text-gray-900 text-lg">{selectedDoc.filename}</h3>
                <p className="text-xs text-gray-400">File Type: {selectedDoc.file_type?.toUpperCase()} • {selectedDoc.chunk_count} RAG Chunks</p>
              </div>
              <button onClick={() => setSelectedDoc(null)} className="p-1 text-gray-400 hover:text-gray-600">
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="flex-1 bg-gray-50 p-4 rounded-lg border border-gray-200 overflow-y-auto font-mono text-xs text-gray-800 whitespace-pre-wrap">
              {docLoading ? 'Loading document text...' : selectedDoc.parsed_text || 'No text extracted.'}
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setSelectedDoc(null)}
                className="px-4 py-2 bg-gray-900 text-white text-xs font-medium rounded-lg hover:bg-black transition-colors"
              >
                Close Viewer
              </button>
            </div>
          </div>
        </div>
      )}

      {/* RAG Context Tester */}
      <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm space-y-4">
        <h2 className="text-lg font-semibold text-gray-800">RAG Context Inspector</h2>
        <form onSubmit={handleTestSearch} className="flex gap-2">
          <input
            type="text"
            placeholder="Search your knowledge base (e.g., 'Cloud hosting pricing', 'SLA guarantees')..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 outline-none"
          />
          <button
            type="submit"
            disabled={isSearching}
            className="px-4 py-2 bg-gray-900 hover:bg-black text-white text-sm font-medium rounded-lg transition-colors flex items-center gap-1.5"
          >
            <Search className="w-4 h-4" />
            {isSearching ? 'Searching...' : 'Test RAG'}
          </button>
        </form>

        {searchResults.length > 0 && (
          <div className="space-y-3 mt-4">
            <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Top Matching Chunks</h3>
            {searchResults.map((r, i) => (
              <div key={i} className="p-3 bg-gray-50 border border-gray-200 rounded-lg text-xs space-y-1">
                <div className="flex items-center justify-between text-indigo-600 font-semibold">
                  <span>Source: {r.filename}</span>
                  <span>Match Score: {(r.score * 100).toFixed(1)}%</span>
                </div>
                <p className="text-gray-700 whitespace-pre-wrap">{r.content}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
