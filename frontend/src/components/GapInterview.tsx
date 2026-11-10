import React, { useState } from 'react'
import { HelpCircle, CheckCircle, Edit3, XCircle, ArrowRight, ArrowLeft, Sparkles, Send } from 'lucide-react'
import { toast } from 'sonner'

export interface InterviewQuestion {
  question_id: string
  target_node_id: string
  node_name: string
  entity_type: string
  spok_score: number
  interview_priority: number
  candidate_hypothesis: string
  status: 'unanswered' | 'confirmed' | 'edited' | 'refuted'
}

interface GapInterviewProps {
  questions: InterviewQuestion[]
  onRespond: (questionId: string, action: 'confirm' | 'edit' | 'refute', text?: string) => void
}

export const GapInterview: React.FC<GapInterviewProps> = ({ questions, onRespond }) => {
  const [currentIndex, setCurrentIndex] = useState<number>(0)
  const [isEditing, setIsEditing] = useState<boolean>(false)
  const [editText, setEditText] = useState<string>('')

  if (!questions || questions.length === 0) {
    return (
      <div className="p-8 text-center glass-panel rounded-2xl">
        <CheckCircle className="w-12 h-12 text-emerald-400 mx-auto mb-3" />
        <h3 className="text-lg font-semibold text-gray-200">No Critical Gaps Remaining</h3>
        <p className="text-sm text-gray-400 mt-1">
          All high-priority single-point-of-knowledge risks have been resolved.
        </p>
      </div>
    )
  }

  const currentQ = questions[currentIndex]

  const handleConfirm = () => {
    onRespond(currentQ.question_id, 'confirm')
    toast.success(`Confirmed knowledge for ${currentQ.node_name}`)
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(currentIndex + 1)
    }
  }

  const handleRefute = () => {
    onRespond(currentQ.question_id, 'refute')
    toast.error(`Marked hypothesis for ${currentQ.node_name} as refuted`)
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(currentIndex + 1)
    }
  }

  const handleEditSubmit = () => {
    if (!editText.trim()) {
      toast.error('Please enter clarification text')
      return
    }
    onRespond(currentQ.question_id, 'edit', editText)
    toast.success(`Updated knowledge record for ${currentQ.node_name}`)
    setIsEditing(false)
    setEditText('')
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(currentIndex + 1)
    }
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Progress Header */}
      <div className="flex items-center justify-between p-4 rounded-xl glass-panel text-xs text-gray-400 font-mono">
        <span>Step {currentIndex + 1} of {questions.length}</span>
        <div className="w-48 bg-black/40 h-2 rounded-full overflow-hidden">
          <div
            className="h-full bg-blue-500 transition-all duration-300"
            style={{ width: `${((currentIndex + 1) / questions.length) * 100}%` }}
          />
        </div>
        <span>Target: <strong className="text-blue-400">{currentQ.node_name}</strong></span>
      </div>

      {/* Main Question Card */}
      <div className="p-6 md:p-8 rounded-2xl glass-panel space-y-6 border border-white/5 relative overflow-hidden">
        {/* Subtle accent glow */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/5 rounded-full blur-3xl pointer-events-none" />

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="p-2 rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20">
              <Sparkles className="w-5 h-5" />
            </span>
            <div>
              <span className="text-[11px] font-mono text-gray-400 uppercase">Recognition Mode Probe</span>
              <h3 className="text-lg font-bold text-gray-100">{currentQ.node_name}</h3>
            </div>
          </div>

          <div className="text-right">
            <span className="text-xs font-mono text-gray-400">Risk Score:</span>
            <div className="text-base font-bold text-rose-400 font-mono">
              {(currentQ.spok_score * 100).toFixed(0)}%
            </div>
          </div>
        </div>

        {/* AI Candidate Hypothesis */}
        <div className="p-4 rounded-xl bg-black/40 border border-white/10 space-y-2">
          <span className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider flex items-center gap-1.5">
            <HelpCircle className="w-3.5 h-3.5 text-blue-400" /> Synthesized Draft Hypothesis
          </span>
          <p className="text-sm text-gray-200 leading-relaxed font-medium">
            "{currentQ.candidate_hypothesis}"
          </p>
        </div>

        {/* Action Controls */}
        {isEditing ? (
          <div className="space-y-3 animate-in fade-in">
            <textarea
              value={editText}
              onChange={e => setEditText(e.target.value)}
              placeholder="Provide the accurate decision rationale or workaround..."
              rows={3}
              className="w-full p-3 rounded-xl bg-black/60 border border-white/15 text-sm text-gray-200 focus:outline-none focus:border-blue-500 font-sans"
            />
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setIsEditing(false)}
                className="px-4 py-2 text-xs font-medium rounded-lg text-gray-400 hover:text-gray-200 hover:bg-white/5"
              >
                Cancel
              </button>
              <button
                onClick={handleEditSubmit}
                className="flex items-center gap-1.5 px-4 py-2 text-xs font-semibold rounded-lg bg-blue-600 hover:bg-blue-500 text-white shadow-subtle-glow"
              >
                <Send className="w-3.5 h-3.5" /> Save Correction
              </button>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
            <button
              onClick={handleConfirm}
              className="flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-emerald-500/15 hover:bg-emerald-500/25 border border-emerald-500/30 text-emerald-300 font-semibold text-xs transition-all active:scale-95"
            >
              <CheckCircle className="w-4 h-4" /> Confirm (Accurate)
            </button>

            <button
              onClick={() => {
                setIsEditing(true)
                setEditText(currentQ.candidate_hypothesis)
              }}
              className="flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-blue-500/15 hover:bg-blue-500/25 border border-blue-500/30 text-blue-300 font-semibold text-xs transition-all active:scale-95"
            >
              <Edit3 className="w-4 h-4" /> Correct Details
            </button>

            <button
              onClick={handleRefute}
              className="flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-rose-500/15 hover:bg-rose-500/25 border border-rose-500/30 text-rose-300 font-semibold text-xs transition-all active:scale-95"
            >
              <XCircle className="w-4 h-4" /> Refute (Incorrect)
            </button>
          </div>
        )}

        {/* Wizard Navigation */}
        <div className="flex justify-between items-center pt-4 border-t border-white/5 text-xs text-gray-400">
          <button
            onClick={() => setCurrentIndex(Math.max(0, currentIndex - 1))}
            disabled={currentIndex === 0}
            className="flex items-center gap-1 hover:text-gray-200 disabled:opacity-30 disabled:pointer-events-none"
          >
            <ArrowLeft className="w-4 h-4" /> Previous
          </button>

          <button
            onClick={() => setCurrentIndex(Math.min(questions.length - 1, currentIndex + 1))}
            disabled={currentIndex === questions.length - 1}
            className="flex items-center gap-1 hover:text-gray-200 disabled:opacity-30 disabled:pointer-events-none"
          >
            Next <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
}
