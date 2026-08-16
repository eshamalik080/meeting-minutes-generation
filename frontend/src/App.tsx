import { useEffect, useState } from 'react'

type HealthResponse = {
  status: string
  service: string
}

function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch('/api/health')
      .then((res) => {
        if (!res.ok) throw new Error(`Backend responded with ${res.status}`)
        return res.json()
      })
      .then(setHealth)
      .catch((err) => setError(err.message))
  }, [])

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-950 text-slate-100">
      <div className="text-center space-y-4">
        <h1 className="text-3xl font-semibold tracking-tight">
          Meeting Minutes — Phase 0 scaffold
        </h1>
        <p className="text-slate-400">
          If this text is styled, Tailwind is working. Below is a live check
          against the FastAPI backend via the Vite dev proxy.
        </p>
        <div className="rounded-lg border border-slate-800 bg-slate-900 px-6 py-4 inline-block">
          {health && (
            <p className="text-emerald-400 font-mono text-sm">
              backend: {health.status} ({health.service})
            </p>
          )}
          {error && (
            <p className="text-rose-400 font-mono text-sm">
              backend unreachable: {error} — start it with `uvicorn app.main:app --reload` in backend/
            </p>
          )}
          {!health && !error && (
            <p className="text-slate-500 font-mono text-sm">checking backend...</p>
          )}
        </div>
      </div>
    </div>
  )
}

export default App
