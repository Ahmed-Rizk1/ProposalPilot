import { useEffect, useState } from 'react'
import { api } from '../api'
import { Palette, Image, Type } from 'lucide-react'

export default function Settings() {
  const [org, setOrg] = useState<any>(null)
  const [color, setColor] = useState('#4F46E5')
  const [name, setName] = useState('')
  const [logoUrl, setLogoUrl] = useState('')
  const [fontFamily, setFontFamily] = useState('Helvetica')
  const [loading, setLoading] = useState(true)
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    api.org.get()
      .then(o => {
        setOrg(o)
        setName(o.name)
        setColor(o.primary_color || '#4F46E5')
        setLogoUrl(o.logo_url || '')
        setFontFamily(o.font_family || 'Helvetica')
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  const save = async () => {
    try {
      await api.org.update({ name, primary_color: color, logo_url: logoUrl || null, font_family: fontFamily })
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    } catch (e: any) { setError(e.message) }
  }

  if (loading) return <div className="p-12 text-center text-gray-400">Loading...</div>

  return (
    <div>
      <h1 className="text-2xl font-bold mb-1">Settings</h1>
      <p className="text-gray-500 mb-6">Manage your organization settings and branding</p>

      {error && <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4 flex justify-between">
        {error} <button onClick={() => setError('')} className="text-red-500">x</button>
      </div>}

      <div className="bg-white rounded-xl border p-6 max-w-lg">
        <h2 className="font-semibold mb-4">Organization</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Company Name</label>
            <input className="w-full border rounded-lg px-3 py-2 text-sm" value={name}
              onChange={e => setName(e.target.value)} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <Image className="w-4 h-4 inline mr-1" /> Logo URL
            </label>
            <input className="w-full border rounded-lg px-3 py-2 text-sm" placeholder="https://example.com/logo.png"
              value={logoUrl} onChange={e => setLogoUrl(e.target.value)} />
            <p className="text-xs text-gray-400 mt-1">URL to your company logo (shown on proposals)</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <Palette className="w-4 h-4 inline mr-1" /> Brand Color
            </label>
            <div className="flex items-center gap-3">
              <input type="color" value={color} onChange={e => setColor(e.target.value)}
                className="w-10 h-10 rounded border cursor-pointer" />
              <input className="border rounded-lg px-3 py-2 text-sm flex-1" value={color}
                onChange={e => setColor(e.target.value)} />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <Type className="w-4 h-4 inline mr-1" /> Font Family
            </label>
            <select className="w-full border rounded-lg px-3 py-2 text-sm" value={fontFamily}
              onChange={e => setFontFamily(e.target.value)}>
              <option value="Helvetica">Helvetica</option>
              <option value="Arial">Arial</option>
              <option value="Times New Roman">Times New Roman</option>
              <option value="Courier New">Courier New</option>
              <option value="Verdana">Verdana</option>
            </select>
          </div>
          <button onClick={save}
            className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700">
            {saved ? 'Saved!' : 'Save Changes'}
          </button>
        </div>
      </div>
    </div>
  )
}
