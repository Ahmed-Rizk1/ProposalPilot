import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'
import { Zap, Download, Loader2, Edit3, FileText } from 'lucide-react'

export default function Generate() {
  const navigate = useNavigate()
  const [clientName, setClientName] = useState('')
  const [clientRequest, setClientRequest] = useState('')
  const [language, setLanguage] = useState('en')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState('')
  const [docCount, setDocCount] = useState<number>(0)

  useEffect(() => {
    api.documents.list().then(docs => setDocCount(docs.length)).catch(() => {})
  }, [])

  const generate = async () => {
    if (!clientName || !clientRequest) return
    setLoading(true); setError(''); setResult(null)
    try {
      const res = await api.proposals.generate({ client_name: clientName, client_request: clientRequest, language })
      setResult(res)
    } catch (e: any) { setError(e.message) }
    finally { setLoading(false) }
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 mb-1">Generate Sales Proposal</h1>
        <p className="text-sm text-gray-500">
          Enter customer demands. Proposal Pilot uses RAG to retrieve relevant context from your uploaded company documents.
        </p>
      </div>

      {docCount === 0 && (
        <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl flex items-center justify-between text-sm text-amber-800">
          <div className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-amber-600" />
            <span>No company documents uploaded yet. Proposals will use general AI knowledge.</span>
          </div>
          <button
            onClick={() => navigate('/documents')}
            className="px-3 py-1.5 bg-amber-600 hover:bg-amber-700 text-white font-medium text-xs rounded-lg transition-colors"
          >
            Upload Documents Now
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Left Input Form */}
        <div className="bg-white rounded-xl border border-gray-100 p-6 shadow-sm space-y-4">
          <h2 className="font-semibold text-gray-800">Client Demands</h2>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Client / Customer Name</label>
            <input
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline-none"
              placeholder="e.g. Acme Global Logistics"
              value={clientName}
              onChange={e => setClientName(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Proposal Language</label>
            <select
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline-none bg-white"
              value={language}
              onChange={e => setLanguage(e.target.value)}
            >
              <option value="en">English (Professional Enterprise)</option>
              <option value="ar">Arabic (العربية - رسمي وتجاري)</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Customer Needs & Specific Demands</label>
            <textarea
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm h-40 resize-none focus:ring-2 focus:ring-indigo-500 outline-none"
              placeholder="e.g. Client needs 500 cloud seats, 24/7 SLA support, enterprise data encryption, and delivery within 30 days. Budget around $45,000..."
              value={clientRequest}
              onChange={e => setClientRequest(e.target.value)}
            />
          </div>

          <button
            onClick={generate}
            disabled={loading || !clientName || !clientRequest}
            className="w-full flex items-center justify-center gap-2 bg-indigo-600 text-white px-4 py-3 rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50 transition-colors shadow-sm"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                RAG Searching & Generating Proposal...
              </>
            ) : (
              <>
                <Zap className="w-5 h-5" />
                Generate RAG Proposal
              </>
            )}
          </button>
        </div>

        {/* Right Output Box */}
        <div className="bg-white rounded-xl border border-gray-100 p-6 shadow-sm flex flex-col justify-between">
          <div>
            <h2 className="font-semibold text-gray-800 mb-4">Generated Proposal Draft</h2>
            {error && <div className="bg-red-50 text-red-700 p-4 rounded-lg text-sm">{error}</div>}
            
            {result && (
              <div className="space-y-4">
                <div className="flex items-center justify-between bg-emerald-50 p-3 rounded-lg border border-emerald-100 text-xs">
                  <span className="text-emerald-800 font-medium">Status: {result.status}</span>
                  <div className="flex gap-2">
                    <button
                      onClick={() => navigate(`/proposals/${result.id}`)}
                      className="flex items-center gap-1.5 bg-indigo-600 text-white px-3 py-1.5 rounded-lg font-medium hover:bg-indigo-700"
                    >
                      <Edit3 className="w-3.5 h-3.5" /> Edit with AI
                    </button>
                    <a
                      href={api.proposals.downloadUrl(result.id)}
                      className="flex items-center gap-1.5 bg-emerald-600 text-white px-3 py-1.5 rounded-lg font-medium hover:bg-emerald-700"
                    >
                      <Download className="w-3.5 h-3.5" /> PDF
                    </a>
                  </div>
                </div>

                <div className="bg-gray-50 rounded-lg p-4 text-xs font-mono text-gray-800 whitespace-pre-wrap max-h-[420px] overflow-auto border border-gray-200">
                  {result.proposal_content}
                </div>
              </div>
            )}

            {!result && !error && (
              <div className="text-center py-20 text-gray-400">
                <Zap className="w-12 h-12 mx-auto mb-3 opacity-40 text-indigo-500" />
                <p className="font-medium text-gray-600">No Proposal Generated Yet</p>
                <p className="text-xs text-gray-400 mt-1">Fill out customer demands and click Generate to retrieve context & create proposal.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
