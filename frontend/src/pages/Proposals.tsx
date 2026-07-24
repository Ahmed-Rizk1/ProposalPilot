import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'
import { Download, Trash2, Bot, Eye, FileText, X } from 'lucide-react'

export default function Proposals() {
  const navigate = useNavigate()
  const [items, setItems] = useState<any[]>([])
  const [selected, setSelected] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [viewMode, setViewMode] = useState<'pdf' | 'text'>('pdf')

  const load = () => {
    api.proposals.list()
      .then(setItems)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const del = async (id: number) => {
    if (!confirm('Delete this proposal?')) return
    try {
      await api.proposals.delete(id)
      if (selected?.id === id) setSelected(null)
      load()
    } catch (e: any) { setError(e.message) }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 mb-1">Proposals</h1>
        <p className="text-sm text-gray-500">View generated proposals, view in-page PDFs, and chat live with AI co-pilot.</p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex justify-between text-sm">
          {error} <button onClick={() => setError('')}><X className="w-4 h-4" /></button>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Table list */}
        <div className={selected ? 'lg:col-span-5' : 'lg:col-span-12'}>
          <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
            {loading ? (
              <div className="p-12 text-center text-gray-400">
                <div className="animate-spin w-6 h-6 border-2 border-indigo-600 border-t-transparent rounded-full mx-auto mb-3" />
                Loading proposals...
              </div>
            ) : (
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b bg-gray-50 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    <th className="px-4 py-3">Client</th>
                    <th className="px-4 py-3">Lang</th>
                    <th className="px-4 py-3">Date</th>
                    <th className="px-4 py-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {items.length === 0 ? (
                    <tr>
                      <td colSpan={4} className="px-4 py-12 text-center text-gray-400">
                        No proposals generated yet.
                      </td>
                    </tr>
                  ) : (
                    items.map(p => (
                      <tr
                        key={p.id}
                        onClick={() => { setSelected(p); setViewMode('pdf') }}
                        className={`cursor-pointer transition-colors hover:bg-gray-50 ${selected?.id === p.id ? 'bg-indigo-50/70 font-medium' : ''}`}
                      >
                        <td className="px-4 py-3 font-semibold text-gray-900">{p.client_name}</td>
                        <td className="px-4 py-3 text-xs uppercase text-gray-500">{p.language}</td>
                        <td className="px-4 py-3 text-xs text-gray-400">
                          {p.created_at ? new Date(p.created_at).toLocaleDateString() : '-'}
                        </td>
                        <td className="px-4 py-3 text-right space-x-2">
                          <button
                            onClick={(e) => { e.stopPropagation(); navigate(`/proposals/${p.id}`) }}
                            className="p-1.5 text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                            title="Open AI Chat Workspace"
                          >
                            <Bot className="w-4 h-4" />
                          </button>
                          <a
                            href={api.proposals.downloadUrl(p.id)}
                            onClick={(e) => e.stopPropagation()}
                            download
                            className="p-1.5 text-gray-400 hover:text-emerald-600 rounded-lg transition-colors inline-block"
                            title="Download PDF"
                          >
                            <Download className="w-4 h-4" />
                          </a>
                          <button
                            onClick={(e) => { e.stopPropagation(); del(p.id) }}
                            className="p-1.5 text-gray-400 hover:text-red-600 rounded-lg transition-colors"
                            title="Delete Proposal"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            )}
          </div>
        </div>

        {/* Selected proposal viewer panel */}
        {selected && (
          <div className="lg:col-span-7">
            <div className="bg-white rounded-xl border border-gray-100 p-6 shadow-sm space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-gray-100 pb-4">
                <div>
                  <h2 className="text-lg font-bold text-gray-900">{selected.client_name}</h2>
                  <span className="text-xs text-gray-400">Created: {new Date(selected.created_at).toLocaleString()}</span>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => navigate(`/proposals/${selected.id}`)}
                    className="flex items-center gap-1.5 text-xs bg-indigo-600 text-white font-medium px-3 py-2 rounded-lg hover:bg-indigo-700 transition-colors shadow-sm"
                  >
                    <Bot className="w-3.5 h-3.5" /> Chat & Edit with AI
                  </button>

                  <div className="flex bg-gray-100 p-1 rounded-lg text-xs">
                    <button
                      onClick={() => setViewMode('pdf')}
                      className={`px-2.5 py-1 rounded font-semibold transition-colors ${viewMode === 'pdf' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500'}`}
                    >
                      <Eye className="w-3.5 h-3.5 inline mr-1" /> PDF
                    </button>
                    <button
                      onClick={() => setViewMode('text')}
                      className={`px-2.5 py-1 rounded font-semibold transition-colors ${viewMode === 'text' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500'}`}
                    >
                      <FileText className="w-3.5 h-3.5 inline mr-1" /> Text
                    </button>
                  </div>

                  <button onClick={() => setSelected(null)} className="text-gray-400 hover:text-gray-600 text-xs p-1">
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </div>

              {/* View Content Canvas */}
              {viewMode === 'pdf' ? (
                <iframe
                  src={`${api.proposals.pdfUrl(selected.id)}#toolbar=1`}
                  title="PDF Viewer"
                  className="w-full h-[600px] rounded-lg border border-gray-200 shadow-inner bg-white"
                />
              ) : (
                <div className="bg-gray-50 rounded-lg p-4 text-xs font-mono whitespace-pre-wrap max-h-[600px] overflow-auto border border-gray-200">
                  {selected.proposal_content}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
