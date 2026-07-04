'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import axios from 'axios'

interface DiagnosisType {
  root_cause: string
  explanation: string
  fix: string
  kubectl_command: string
  confidence: number
}

interface Investigation {
  id: string
  root_cause: string
  confidence: number
  timestamp: string
}

export default function Dashboard() {
  const router = useRouter()
  const [isInvestigating, setIsInvestigating] = useState(false)
  const [diagnosis, setDiagnosis] = useState<DiagnosisType | null>(null)
  const [history, setHistory] = useState<Investigation[]>([])
  const [error, setError] = useState<string | null>(null)
  const [progress, setProgress] = useState<string[]>([])
  const [userEmail, setUserEmail] = useState('')
  const [clusters, setClusters] = useState<any[]>([])
  const [selectedCluster, setSelectedCluster] = useState<string>('')

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    const email = localStorage.getItem('user_email')

    if (!token) {
      router.push('/login')
      return
    }

    setUserEmail(email || 'User')
    loadClusters()
    loadHistory()
  }, [router])

  const loadClusters = async () => {
    try {
      const response = await axios.get(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/clusters/list`
      )

      if (response.data.clusters && response.data.clusters.length > 0) {
        setClusters(response.data.clusters)
        setSelectedCluster(response.data.clusters[0].name)
      }
    } catch (err) {
      console.error('Failed to load clusters:', err)
    }
  }

  const handleClusterChange = async (clusterName: string) => {
    setSelectedCluster(clusterName)

    try {
      await axios.post(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/clusters/switch`,
        {},
        { params: { cluster_name: clusterName } }
      )
    } catch (err) {
      console.error('Failed to switch cluster:', err)
    }
  }

  const loadHistory = async () => {
    try {
      const userId = localStorage.getItem('user_id')
      if (!userId) return

      const response = await axios.get(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/investigations`,
        { params: { user_id: userId, limit: 10 } }
      )

      if (response.data.investigations) {
        setHistory(response.data.investigations)
      }
    } catch (err) {
      console.error('Failed to load history:', err)
    }
  }

  const updateProgress = (step: string) => {
    setProgress(prev => [...prev, step])
  }

  const handleInvestigate = async () => {
    setIsInvestigating(true)
    setError(null)
    setDiagnosis(null)
    setProgress([])

    try {
      const userId = localStorage.getItem('user_id')
      if (!userId) {
        router.push('/login')
        return
      }

      updateProgress('Checking Pods')
      updateProgress('Reading Logs')
      updateProgress('Analyzing Events')
      updateProgress('Inspecting Deployments')
      updateProgress('Checking Networking')
      updateProgress('AI Reasoning')

      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/investigate`,
        {},
        { params: { user_id: userId } }
      )

      updateProgress('Root Cause Found')

      if (response.data.diagnosis) {
        setDiagnosis(response.data.diagnosis)
        loadHistory()
      } else {
        setError(response.data.diagnosis_error || 'No diagnosis received from backend')
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Investigation failed'
      setError(errorMsg)
      updateProgress('Error: ' + errorMsg)
    } finally {
      setIsInvestigating(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_id')
    localStorage.removeItem('user_email')
    router.push('/login')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900">
      {/* Animated background elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 right-0 w-96 h-96 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-5 animate-blob"></div>
        <div className="absolute -bottom-8 left-20 w-96 h-96 bg-indigo-500 rounded-full mix-blend-multiply filter blur-3xl opacity-5 animate-blob animation-delay-2000"></div>
      </div>

      {/* Header */}
      <div className="relative z-10 border-b border-slate-700/50 bg-slate-900/40 backdrop-blur-xl">
        <div className="max-w-6xl mx-auto px-8 py-6 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">AI Kubernetes Agent</h1>
            <p className="text-slate-400 text-sm mt-1">Logged in as <span className="text-blue-400">{userEmail}</span></p>
          </div>

          <div className="flex items-center gap-6">
            {/* Cluster Selector */}
            {clusters.length > 0 && (
              <div className="flex items-center gap-3 bg-slate-800/50 px-4 py-2 rounded-lg border border-slate-700/50">
                <span className="text-slate-400 text-sm font-medium">Cluster:</span>
                <select
                  value={selectedCluster}
                  onChange={(e) => handleClusterChange(e.target.value)}
                  className="bg-transparent text-slate-300 text-sm font-medium focus:outline-none cursor-pointer max-w-xs truncate"
                >
                  {clusters.map((cluster) => (
                    <option key={cluster.name} value={cluster.name}>
                      {cluster.name}
                    </option>
                  ))}
                </select>
              </div>
            )}

            <button
              onClick={handleLogout}
              className="text-slate-400 hover:text-slate-200 text-sm font-medium transition px-4 py-2 hover:bg-slate-800/50 rounded-lg"
            >
              Sign out
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="relative z-10 min-h-[calc(100vh-80px)] flex flex-col items-center justify-center px-4 py-12">
        {/* Before Investigation */}
        {!diagnosis && progress.length === 0 && (
          <div className="text-center mb-12 max-w-2xl">
            <h2 className="text-6xl font-bold text-white mb-4 leading-tight">AI Kubernetes Agent</h2>
            <p className="text-xl text-slate-400 font-light">Intelligent cluster troubleshooting powered by AI</p>
          </div>
        )}

        {/* Investigation Button */}
        {!diagnosis && (
          <div className="mb-12">
            <button
              onClick={handleInvestigate}
              disabled={isInvestigating}
              className="group relative px-10 py-4 font-semibold text-lg text-white overflow-hidden rounded-xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed hover:scale-105 transform"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-blue-600 via-blue-500 to-cyan-500 group-hover:from-blue-700 group-hover:via-blue-600 group-hover:to-cyan-600 transition-all duration-300"></div>
              <div className="absolute inset-0 bg-gradient-to-r from-blue-600 via-blue-500 to-cyan-500 blur opacity-0 group-hover:opacity-100 group-hover:blur-xl transition-all duration-300"></div>
              <span className="relative flex items-center gap-2">
                {isInvestigating ? (
                  <>
                    <span className="animate-spin">⟳</span>
                    Investigating...
                  </>
                ) : (
                  <>
                    <span>🔍</span>
                    Investigate Cluster
                  </>
                )}
              </span>
            </button>
          </div>
        )}

        {/* Progress */}
        {isInvestigating && progress.length > 0 && !diagnosis && (
          <div className="max-w-2xl w-full mb-8 space-y-6">
            {/* Header with progress indicator */}
            <div className="text-center">
              <div className="flex items-center justify-center gap-3 mb-4">
                <div className="animate-spin">
                  <div className="w-4 h-4 border-2 border-blue-400 border-t-transparent rounded-full"></div>
                </div>
                <span className="text-slate-300 font-medium">Investigating Kubernetes Cluster...</span>
              </div>
              <div className="w-full h-1 bg-slate-700/50 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-blue-500 via-cyan-500 to-blue-500 transition-all duration-300"
                  style={{ width: `${(progress.length / 7) * 100}%` }}
                ></div>
              </div>
            </div>

            {/* Investigation Status */}
            <div className="bg-slate-800/50 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-8 shadow-2xl">
              <h3 className="text-slate-400 text-xs font-bold uppercase tracking-widest mb-6">Investigation Status</h3>

              <div className="space-y-4">
                {/* All possible steps */}
                {['Checking Pods', 'Reading Logs', 'Analyzing Events', 'Inspecting Deployments', 'Checking Networking', 'AI Reasoning', 'Root Cause Found'].map((step, idx) => {
                  const isCompleted = progress.includes(step)
                  const isInProgress = progress[progress.length - 1] === step

                  return (
                    <div key={idx} className="flex items-center gap-4 group">
                      <div className="flex-shrink-0">
                        {isCompleted && !isInProgress ? (
                          <div className="w-6 h-6 rounded-full bg-green-500/20 border border-green-500/50 flex items-center justify-center text-green-400 text-sm font-bold">
                            ✓
                          </div>
                        ) : isInProgress ? (
                          <div className="w-6 h-6 rounded-full bg-blue-500/20 border border-blue-500/50 flex items-center justify-center">
                            <div className="animate-spin text-blue-400 text-sm">⟳</div>
                          </div>
                        ) : (
                          <div className="w-6 h-6 rounded-full bg-slate-700/30 border border-slate-600/50 flex items-center justify-center text-slate-500 text-sm">
                            ◦
                          </div>
                        )}
                      </div>
                      <span className={`text-sm font-medium transition-all ${
                        isCompleted
                          ? 'text-green-400'
                          : isInProgress
                          ? 'text-blue-400'
                          : 'text-slate-500'
                      }`}>
                        {step}
                      </span>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="bg-red-900/20 backdrop-blur-xl border border-red-700/50 rounded-xl p-6 max-w-2xl w-full mb-8 shadow-xl">
            <p className="font-semibold text-red-400">⚠️ Error</p>
            <p className="text-red-300 text-sm mt-2">{error}</p>
          </div>
        )}

        {/* No Previous Investigations */}
        {!diagnosis && progress.length === 0 && history.length === 0 && (
          <p className="text-slate-500 text-sm">No previous investigations yet.</p>
        )}

        {/* Diagnosis Section */}
        {diagnosis && (
          <div className="max-w-4xl w-full space-y-6">
            {/* Root Cause Card */}
            <div className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-8 shadow-2xl hover:shadow-xl transition-all duration-300">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-slate-400 text-xs font-bold uppercase tracking-widest">🎯 Root Cause</h2>
                {diagnosis.root_cause === 'No issues detected' ? (
                  <span className="px-3 py-1 rounded-full text-xs font-bold bg-green-500/20 border border-green-500/50 text-green-400">✓ Healthy</span>
                ) : (
                  <span className="px-3 py-1 rounded-full text-xs font-bold bg-red-500/20 border border-red-500/50 text-red-400">⚠ Issues Found</span>
                )}
              </div>
              <p className="text-white text-3xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">{diagnosis.root_cause}</p>
            </div>

            {/* Two Column Layout */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Explanation */}
              <div className="bg-slate-800/50 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-8 shadow-xl hover:shadow-2xl transition-all duration-300">
                <h3 className="text-slate-400 text-xs font-bold uppercase tracking-widest mb-4">📝 Explanation</h3>
                <p className="text-slate-300 text-sm leading-relaxed">{diagnosis.explanation}</p>
              </div>

              {/* Confidence */}
              <div className="bg-slate-800/50 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-8 shadow-xl hover:shadow-2xl transition-all duration-300">
                <h3 className="text-slate-400 text-xs font-bold uppercase tracking-widest mb-1">⚡ Diagnosis Confidence</h3>
                <p className="text-slate-500 text-xs mb-4">How certain the AI is about this finding — not a health score</p>
                <div className="flex items-center gap-4">
                  <div className="text-5xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">{diagnosis.confidence}%</div>
                  <div className="flex-1">
                    <div className="w-full bg-slate-700/50 rounded-full h-3 overflow-hidden border border-slate-600/50">
                      <div
                        className="bg-gradient-to-r from-blue-500 to-cyan-500 h-3 rounded-full transition-all duration-1000"
                        style={{ width: `${diagnosis.confidence}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Suggested Fix */}
            <div className="bg-slate-800/50 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-8 shadow-xl hover:shadow-2xl transition-all duration-300">
              <h3 className="text-slate-400 text-xs font-bold uppercase tracking-widest mb-4">🔧 Suggested Fix</h3>
              <p className="text-slate-300 text-sm leading-relaxed">{diagnosis.fix}</p>
            </div>

            {/* kubectl Command */}
            {diagnosis.kubectl_command !== 'N/A' && (
              <div className="bg-slate-950/50 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-8 shadow-xl hover:shadow-2xl transition-all duration-300">
                <h3 className="text-slate-400 text-xs font-bold uppercase tracking-widest mb-4">⌨️ kubectl Command</h3>
                <div className="bg-slate-950 rounded-xl p-4 font-mono text-green-400 text-sm break-all border border-slate-700/50 hover:border-slate-600/50 transition-colors">
                  {diagnosis.kubectl_command}
                </div>
              </div>
            )}

            {/* New Investigation Button */}
            <div className="flex justify-center pt-6">
              <button
                onClick={() => setDiagnosis(null)}
                className="group relative px-8 py-3 font-semibold text-white overflow-hidden rounded-xl transition-all duration-300 hover:scale-105 transform"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-cyan-500 group-hover:from-blue-700 group-hover:to-cyan-600 transition-all"></div>
                <span className="relative flex items-center gap-2">
                  🔄 New Investigation
                </span>
              </button>
            </div>
          </div>
        )}

        {/* History Section */}
        {diagnosis && history.length > 0 && (
          <div className="max-w-4xl w-full mt-12 pt-12 border-t border-slate-700/50">
            <h2 className="text-white font-bold mb-6 text-lg">📊 Recent Investigations</h2>
            <div className="space-y-3">
              {history.map((item) => (
                <div key={item.id} className="bg-slate-800/50 backdrop-blur-xl border border-slate-700/50 rounded-xl p-4 flex justify-between items-center hover:bg-slate-800/70 transition-all duration-300 group cursor-pointer">
                  <div>
                    <p className="text-white font-semibold text-sm group-hover:text-blue-400 transition">{item.root_cause}</p>
                    <p className="text-slate-500 text-xs mt-1">
                      {new Date(item.timestamp).toLocaleString()}
                    </p>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <div className="bg-gradient-to-r from-green-400 to-emerald-400 bg-clip-text text-transparent font-bold text-sm">{item.confidence}%</div>
                    <div className="text-slate-500 text-xs">Confidence</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        @keyframes blob {
          0%, 100% { transform: translate(0, 0) scale(1); }
          33% { transform: translate(30px, -50px) scale(1.1); }
          66% { transform: translate(-20px, 20px) scale(0.9); }
        }

        .animate-blob {
          animation: blob 7s infinite;
        }

        .animation-delay-2000 {
          animation-delay: 2s;
        }
      `}</style>
    </div>
  )
}
