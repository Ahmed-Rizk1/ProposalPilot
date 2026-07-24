import React from 'react'
import { Routes, Route, NavLink, Navigate } from 'react-router-dom'
import { LayoutDashboard, FolderOpen, Zap, FileText, Settings, LogOut } from 'lucide-react'
import { isLoggedIn, clearToken } from './api'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Documents from './pages/Documents'
import Generate from './pages/Generate'
import Proposals from './pages/Proposals'
import ProposalEdit from './pages/ProposalEdit'
import SettingsPage from './pages/Settings'

function Protected({ children }: { children: React.ReactNode }) {
  if (!isLoggedIn()) return <Navigate to="/login" replace />
  return <>{children}</>
}

const nav = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/documents', label: 'Documents (RAG)', icon: FolderOpen },
  { to: '/generate', label: 'Generate Proposal', icon: Zap },
  { to: '/proposals', label: 'All Proposals', icon: FileText },
  { to: '/settings', label: 'Settings', icon: Settings },
]

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="*" element={
        <Protected>
          <div className="flex min-h-screen bg-gray-50">
            <aside className="w-60 bg-white border-r border-gray-200 p-4 flex flex-col">
              <div className="mb-6 px-2">
                <h1 className="text-xl font-bold text-indigo-600">ProposalPilot</h1>
                <span className="text-[10px] uppercase font-semibold text-indigo-500 tracking-wider">Enterprise RAG Edition</span>
              </div>
              
              <nav className="space-y-1 flex-1">
                {nav.map(({ to, label, icon: Icon }) => (
                  <NavLink key={to} to={to} end={to === '/'}
                    className={({ isActive }) =>
                      `flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                        isActive ? 'bg-indigo-50 text-indigo-700 font-semibold' : 'text-gray-600 hover:bg-gray-100'
                      }`
                    }>
                    <Icon className="w-4 h-4" /> {label}
                  </NavLink>
                ))}
              </nav>

              <button onClick={() => { clearToken(); window.location.href = '/login' }}
                className="flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-500 hover:bg-red-50 hover:text-red-600 transition-colors">
                <LogOut className="w-4 h-4" /> Sign Out
              </button>
            </aside>

            <main className="flex-1 p-8 overflow-auto">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/documents" element={<Documents />} />
                <Route path="/generate" element={<Generate />} />
                <Route path="/proposals" element={<Proposals />} />
                <Route path="/proposals/:id" element={<ProposalEdit />} />
                <Route path="/settings" element={<SettingsPage />} />
              </Routes>
            </main>
          </div>
        </Protected>
      } />
    </Routes>
  )
}
