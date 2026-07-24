import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { FolderOpen, FileText, ArrowRight } from 'lucide-react'
import { api } from '../api'

export default function Dashboard() {
  const [stats, setStats] = useState({ documents: 0, proposals: 0 })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([api.documents.list(), api.proposals.list()])
      .then(([d, pr]) => setStats({ documents: d.length, proposals: pr.length }))
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 mb-1">Dashboard</h1>
        <p className="text-sm text-gray-500">AI-powered enterprise sales proposals with multi-format Document RAG</p>
      </div>

      {error && <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">{error}</div>}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {[{ l: 'RAG Knowledge Documents', v: stats.documents, ic: FolderOpen, c: 'bg-indigo-600', link: '/documents' },
          { l: 'Generated Proposals', v: stats.proposals, ic: FileText, c: 'bg-emerald-600', link: '/proposals' }].map(({ l, v, ic: I, c, link }) => (
          <Link key={l} to={link} className="bg-white rounded-xl border border-gray-100 p-6 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-wider text-gray-500">{l}</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  {loading ? <span className="inline-block w-12 h-8 bg-gray-200 animate-pulse rounded" /> : v}
                </p>
              </div>
              <div className={`${c} p-3 rounded-xl`}><I className="w-6 h-6 text-white" /></div>
            </div>
          </Link>
        ))}
      </div>

      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-xl p-8 text-white shadow-sm space-y-3">
        <h2 className="text-xl font-bold">Generate a RAG Proposal</h2>
        <p className="text-indigo-100 text-sm max-w-xl">
          Enter customer demands. ProposalPilot retrieves your company knowledge context and generates professional proposals with live AI chatbot editing.
        </p>
        <div>
          <Link to="/generate" className="inline-flex items-center gap-2 bg-white text-indigo-600 px-4 py-2.5 rounded-lg font-medium text-sm hover:bg-indigo-50 transition-colors shadow-sm">
            Generate Proposal <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>
    </div>
  )
}
