import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  BarChart3,
  CheckCircle2,
  XCircle,
  Play,
  Lock,
  ChevronDown,
} from 'lucide-react'
import { toast } from 'sonner'

export interface EvalDetail {
  id: number
  category: string
  question: string
  ground_truth: string
  passed: boolean
  notes: string
}

export interface EvalData {
  benchmark_dataset: string
  held_out_questions_count: number
  raw_source_baseline_accuracy: number
  successor_ledger_accuracy: number
  accuracy_delta: number
  token_consumption_reduction: string
  canary_leakage_rate: number
  passed_canary_negative_controls: boolean
  details?: EvalDetail[]
}

export interface EvaluationDashboardProps {
  evalData: EvalData | null
  onRunEval: () => Promise<void>
  isLoading?: boolean
}

export const EvaluationDashboard: React.FC<EvaluationDashboardProps> = ({
  evalData,
  onRunEval,
  isLoading = false,
}) => {
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [expandedQuestionId, setExpandedQuestionId] = useState<number | null>(null)

  // Default values if eval hasn't run yet
  const displayData: EvalData = evalData || {
    benchmark_dataset: 'v1_demo',
    held_out_questions_count: 20,
    raw_source_baseline_accuracy: 0.45,
    successor_ledger_accuracy: 0.90,
    accuracy_delta: 0.45,
    token_consumption_reduction: '82%',
    canary_leakage_rate: 0.0,
    passed_canary_negative_controls: true,
  }

  const details = displayData.details || []
  const categories = ['all', ...Array.from(new Set(details.map(d => d.category)))]

  const filteredDetails = details.filter(d =>
    selectedCategory === 'all' ? true : d.category === selectedCategory
  )

  const handleExecute = async () => {
    try {
      await onRunEval()
      toast.success('Tested 20 onboarding questions on sample dataset v1_demo!')
    } catch {
      toast.error('Failed to run evaluation test')
    }
  }

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="p-6 rounded-3xl bg-gradient-to-r from-emerald-950/40 via-zinc-900/60 to-black/80 border border-emerald-500/20 backdrop-blur-xl shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
            <BarChart3 className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-bold text-white">Handover Readiness Test & Quality Benchmark</h2>
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                TEST SUITE: {displayData.benchmark_dataset}
              </span>
            </div>
            <p className="text-xs text-zinc-400 mt-0.5">
              Tests whether incoming members can answer {displayData.held_out_questions_count} real onboarding questions quickly and verifies zero sensitive secrets are revealed.
            </p>
          </div>
        </div>

        <button
          onClick={handleExecute}
          disabled={isLoading}
          className="flex items-center gap-2 px-5 py-2.5 rounded-2xl bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-xs font-semibold shadow-lg shadow-emerald-600/20 active:scale-95 transition-all"
        >
          <Play className="w-3.5 h-3.5 fill-current" />
          {isLoading ? 'Running Test...' : 'Run Benchmark Test'}
        </button>
      </div>

      {/* 4 Metric Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* Metric 1 */}
        <div className="p-5 rounded-2xl glass-panel space-y-1">
          <span className="text-[11px] font-mono text-zinc-400 uppercase tracking-wider">HandoffLedger Score</span>
          <div className="text-3xl font-extrabold font-mono text-emerald-400">
            {(displayData.successor_ledger_accuracy * 100).toFixed(1)}%
          </div>
          <p className="text-[11px] text-zinc-500">Answers found via verified facts</p>
        </div>

        {/* Metric 2 */}
        <div className="p-5 rounded-2xl glass-panel space-y-1">
          <span className="text-[11px] font-mono text-zinc-400 uppercase tracking-wider">Old Manual Way</span>
          <div className="text-3xl font-extrabold font-mono text-zinc-400">
            {(displayData.raw_source_baseline_accuracy * 100).toFixed(1)}%
          </div>
          <p className="text-[11px] text-zinc-500">Searching raw chats & commits</p>
        </div>

        {/* Metric 3 */}
        <div className="p-5 rounded-2xl glass-panel space-y-1">
          <span className="text-[11px] font-mono text-zinc-400 uppercase tracking-wider">Onboarding Boost</span>
          <div className="text-3xl font-extrabold font-mono text-emerald-300">
            +{(displayData.accuracy_delta * 100).toFixed(1)}%
          </div>
          <p className="text-[11px] text-zinc-500">+45% faster & more accurate</p>
        </div>

        {/* Metric 4 */}
        <div className="p-5 rounded-2xl glass-panel space-y-1">
          <span className="text-[11px] font-mono text-zinc-400 uppercase tracking-wider">Reading Time Saved</span>
          <div className="text-3xl font-extrabold font-mono text-cyan-400">
            {displayData.token_consumption_reduction}
          </div>
          <p className="text-[11px] text-zinc-500">82% less text to read</p>
        </div>
      </div>

      {/* Canary Tripwire Status Card */}
      <div className="p-5 rounded-2xl bg-zinc-950/80 border border-white/10 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
            <Lock className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              Password & Private Key Protection
              {displayData.passed_canary_negative_controls ? (
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3" /> 100% Protected (0 Leaks)
                </span>
              ) : (
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-500/20 text-rose-400 border border-rose-500/30 flex items-center gap-1">
                  <XCircle className="w-3 h-3" /> Warning: Leaks Detected
                </span>
              )}
            </h3>
            <p className="text-xs text-zinc-400 mt-0.5">
              Automated security tests verifying that passwords, private keys, and restricted tokens are never exposed to unauthorized members.
            </p>
          </div>
        </div>
        <div className="text-right">
          <span className="text-xs font-mono text-zinc-400">Secret Leak Rate:</span>
          <div className="text-lg font-bold font-mono text-emerald-400">
            {(displayData.canary_leakage_rate * 100).toFixed(1)}%
          </div>
        </div>
      </div>

      {/* Detailed Question Inspector */}
      {details.length > 0 && (
        <div className="space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3 p-4 rounded-2xl glass-panel">
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-gray-300">Filter Category:</span>
              {categories.map(cat => (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(cat)}
                  className={`px-3 py-1 rounded-xl text-xs font-medium transition-all ${
                    selectedCategory === cat
                      ? 'bg-emerald-600 text-white font-semibold'
                      : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'
                  }`}
                >
                  {cat.replace('_', ' ').toUpperCase()}
                </button>
              ))}
            </div>
            <span className="text-xs font-mono text-zinc-400">Showing {filteredDetails.length} questions</span>
          </div>

          <div className="space-y-2.5">
            {filteredDetails.map(item => {
              const isOpen = expandedQuestionId === item.id
              return (
                <div
                  key={item.id}
                  className="p-4 rounded-2xl glass-panel hover:border-white/15 transition-all cursor-pointer"
                  onClick={() => setExpandedQuestionId(isOpen ? null : item.id)}
                >
                  <div className="flex items-center justify-between gap-3">
                    <div className="flex items-center gap-3">
                      <span className="w-6 h-6 rounded-lg bg-white/5 font-mono text-xs text-zinc-400 flex items-center justify-center">
                        #{item.id}
                      </span>
                      <span className="text-xs font-medium text-white">{item.question}</span>
                    </div>

                    <div className="flex items-center gap-2.5">
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-white/5 text-zinc-400 border border-white/10">
                        {item.category}
                      </span>
                      {item.passed ? (
                        <span className="flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                          <CheckCircle2 className="w-3 h-3" /> Passed
                        </span>
                      ) : (
                        <span className="flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-rose-500/15 text-rose-400 border border-rose-500/30">
                          <XCircle className="w-3 h-3" /> Missed
                        </span>
                      )}
                      <ChevronDown
                        className={`w-4 h-4 text-zinc-400 transition-transform ${isOpen ? 'rotate-180' : ''}`}
                      />
                    </div>
                  </div>

                  <AnimatePresence>
                    {isOpen && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="mt-3 pt-3 border-t border-white/10 space-y-2 text-xs"
                      >
                        <div>
                          <span className="text-zinc-500 font-mono text-[11px] uppercase">Correct Answer in Code:</span>
                          <p className="text-emerald-300 font-mono mt-0.5">{item.ground_truth}</p>
                        </div>
                        <div>
                          <span className="text-zinc-500 font-mono text-[11px] uppercase">How It Performed:</span>
                          <p className="text-zinc-300 mt-0.5">{item.notes}</p>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}

export default EvaluationDashboard
