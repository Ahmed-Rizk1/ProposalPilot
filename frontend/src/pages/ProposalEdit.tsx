import React, { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../api'
import { Download, Sparkles, Save, ArrowLeft, Loader2, Send, Eye, FileText, Bot, User as UserIcon } from 'lucide-react'

interface ChatMessage {
  id?: number
  sender: 'user' | 'assistant'
  message: string
  created_at?: string
}

export default function ProposalEdit() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const [proposal, setProposal] = useState<any>(null)
  const [content, setContent] = useState('')
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [chatInput, setChatInput] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [chatLoading, setChatLoading] = useState(false)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState<'pdf' | 'edit' | 'markdown'>('pdf')

  const chatEndRef = useRef<HTMLDivElement>(null)
  const proposalId = Number(id)

  const loadProposal = async () => {
    try {
      setLoading(true)
      const data = await api.proposals.get(proposalId)
      setProposal(data)
      setContent(data.proposal_content || '')
      setMessages(data.messages || [])
    } catch (err: any) {
      setError(err.message || 'Failed to load proposal workspace')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (proposalId) loadProposal()
  }, [proposalId])

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, chatLoading])

  const handleSave = async () => {
    try {
      setSaving(true)
      const updated = await api.proposals.update(proposalId, { proposal_content: content })
      setProposal(updated)
      alert('Proposal manually saved and PDF regenerated!')
    } catch (err: any) {
      alert(err.message || 'Failed to save proposal')
    } finally {
      setSaving(false)
    }
  }

  const handleSendChatMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    const text = chatInput.trim()
    if (!text || chatLoading) return

    setChatInput('')
    const tempUserMsg: ChatMessage = { sender: 'user', message: text }
    setMessages((prev) => [...prev, tempUserMsg])

    try {
      setChatLoading(true)
      const updated = await api.proposals.chat(proposalId, text)
      setProposal(updated)
      setContent(updated.proposal_content || '')
      setMessages(updated.messages || [])
    } catch (err: any) {
      alert(err.message || 'AI Chat Edit failed')
    } finally {
      setChatLoading(false)
    }
  }

  if (loading) return <div className="p-12 text-center text-gray-500">Loading proposal workspace...</div>
  if (error) return <div className="p-6 bg-red-50 text-red-700 rounded-lg">{error}</div>

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-4 sm:px-6 rounded-xl border border-gray-100 shadow-sm">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/proposals')}
            className="p-2 hover:bg-gray-100 rounded-lg text-gray-600 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-xl font-bold text-gray-900">
              Proposal: {proposal?.client_name}
            </h1>
            <p className="text-xs text-gray-500">
              Language: {proposal?.language?.toUpperCase()} • Real-time AI Chatbot Active
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleSave}
            disabled={saving}
            className="inline-flex items-center gap-2 px-4 py-2 border border-gray-300 hover:bg-gray-50 text-gray-700 rounded-lg text-sm font-medium transition-colors"
          >
            {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
            Save Draft
          </button>

          <a
            href={api.proposals.downloadUrl(proposalId)}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm font-medium transition-colors shadow-sm"
          >
            <Download className="w-4 h-4" />
            Download PDF
          </a>
        </div>
      </div>

      {/* Main Split Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Column: Conversational AI Chatbot Sidebar (5 Cols) */}
        <div className="lg:col-span-5 bg-white rounded-xl border border-gray-100 shadow-sm flex flex-col h-[720px] overflow-hidden">
          {/* Chat Header */}
          <div className="p-4 border-b border-gray-100 bg-indigo-50/50 flex items-center gap-2.5">
            <div className="p-2 bg-indigo-600 text-white rounded-lg">
              <Bot className="w-5 h-5" />
            </div>
            <div>
              <h2 className="font-semibold text-gray-900 text-sm">AI Proposal Co-Pilot Chat</h2>
              <p className="text-[11px] text-gray-500">Ask the AI to change pricing, add sections, or translate live</p>
            </div>
          </div>

          {/* Messages Stream */}
          <div className="flex-1 p-4 overflow-y-auto space-y-3.5 bg-gray-50/50">
            {messages.map((m, idx) => (
              <div
                key={idx}
                className={`flex gap-2.5 ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {m.sender === 'assistant' && (
                  <div className="p-1.5 bg-indigo-600 text-white rounded-full h-fit mt-0.5">
                    <Bot className="w-3.5 h-3.5" />
                  </div>
                )}

                <div
                  className={`max-w-[82%] p-3 rounded-xl text-xs leading-relaxed ${
                    m.sender === 'user'
                      ? 'bg-indigo-600 text-white rounded-tr-none shadow-sm'
                      : 'bg-white text-gray-800 border border-gray-200 shadow-sm rounded-tl-none'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{m.message}</p>
                </div>

                {m.sender === 'user' && (
                  <div className="p-1.5 bg-gray-800 text-white rounded-full h-fit mt-0.5">
                    <UserIcon className="w-3.5 h-3.5" />
                  </div>
                )}
              </div>
            ))}

            {chatLoading && (
              <div className="flex items-center gap-2 text-indigo-600 text-xs bg-white p-3 rounded-xl border border-gray-200 w-fit shadow-sm">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>AI is thinking & updating proposal live...</span>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Quick Conversation Presets */}
          <div className="p-2 border-t border-gray-100 bg-white overflow-x-auto flex gap-1.5 text-[11px] whitespace-nowrap">
            {[
              "Add 10% volume discount",
              "Add 24/7 SLA section",
              "Translate to Arabic",
              "Make tone formal enterprise"
            ].map((preset, i) => (
              <button
                key={i}
                onClick={() => setChatInput(preset)}
                className="px-2.5 py-1 bg-gray-100 hover:bg-indigo-50 hover:text-indigo-600 text-gray-600 rounded-full transition-colors"
              >
                ✨ {preset}
              </button>
            ))}
          </div>

          {/* Chat Input Bar */}
          <form onSubmit={handleSendChatMessage} className="p-3 border-t border-gray-100 bg-white flex gap-2">
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              placeholder="Chat with AI to edit proposal (e.g., 'Add payment schedule')..."
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-xs focus:ring-2 focus:ring-indigo-500 outline-none"
            />
            <button
              type="submit"
              disabled={chatLoading || !chatInput.trim()}
              className="px-3.5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-medium flex items-center gap-1.5 transition-colors disabled:opacity-50"
            >
              <Send className="w-3.5 h-3.5" />
            </button>
          </form>
        </div>

        {/* Right Column: In-Page View (PDF View | Interactive Editor | Markdown View) (7 Cols) */}
        <div className="lg:col-span-7 bg-white rounded-xl border border-gray-100 shadow-sm flex flex-col h-[720px] overflow-hidden">
          {/* View Toggle Bar */}
          <div className="flex items-center justify-between p-3 border-b border-gray-100 bg-gray-50">
            <div className="flex gap-1.5">
              <button
                onClick={() => setActiveTab('pdf')}
                className={`flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-semibold rounded-lg transition-colors ${
                  activeTab === 'pdf' ? 'bg-indigo-600 text-white shadow-sm' : 'text-gray-600 hover:bg-gray-200'
                }`}
              >
                <Eye className="w-3.5 h-3.5" />
                📄 Live PDF View
              </button>

              <button
                onClick={() => setActiveTab('edit')}
                className={`flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-semibold rounded-lg transition-colors ${
                  activeTab === 'edit' ? 'bg-indigo-600 text-white shadow-sm' : 'text-gray-600 hover:bg-gray-200'
                }`}
              >
                <FileText className="w-3.5 h-3.5" />
                Markdown Editor
              </button>

              <button
                onClick={() => setActiveTab('markdown')}
                className={`flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-semibold rounded-lg transition-colors ${
                  activeTab === 'markdown' ? 'bg-indigo-600 text-white shadow-sm' : 'text-gray-600 hover:bg-gray-200'
                }`}
              >
                <Sparkles className="w-3.5 h-3.5" />
                Rendered Preview
              </button>
            </div>

            <span className="text-[11px] text-gray-400 font-mono">Real-time Sync</span>
          </div>

          {/* View Content Canvas */}
          <div className="flex-1 p-2 bg-gray-100 overflow-hidden">
            {activeTab === 'pdf' && (
              <iframe
                key={proposal?.updated_at || proposal?.created_at}
                src={`${api.proposals.pdfUrl(proposalId)}#toolbar=1`}
                title="Proposal PDF Document Preview"
                className="w-full h-full rounded-lg border border-gray-200 shadow-inner bg-white"
              />
            )}

            {activeTab === 'edit' && (
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                className="w-full h-full p-4 font-mono text-xs text-gray-800 bg-white rounded-lg border border-gray-200 focus:ring-2 focus:ring-indigo-500 outline-none resize-none"
              />
            )}

            {activeTab === 'markdown' && (
              <div className="w-full h-full p-6 bg-white rounded-lg border border-gray-200 overflow-y-auto text-xs leading-relaxed text-gray-800 whitespace-pre-wrap font-sans">
                {content}
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  )
}
