import React, { useState } from 'react'
import { Flame, Key, Compass, ListTodo, ShieldCheck, Lock, CheckSquare, ShieldAlert } from 'lucide-react'
import { toast } from 'sonner'
import { Claim } from './ClaimLedger'

export interface SuccessorViewProps {
  panes: {
    landmines: Claim[]
    accounts: Claim[]
    decisions: Claim[]
    backlog: Claim[]
  }
  canaryLeakDetected: boolean
  viewerClearance: string
}

export const SuccessorView: React.FC<SuccessorViewProps> = ({
  panes,
  canaryLeakDetected,
  viewerClearance,
}) => {
  const [acknowledged, setAcknowledged] = useState<boolean>(false)
  const [ackTimestamp, setAckTimestamp] = useState<string | null>(null)

  const handleAcknowledge = () => {
    const now = new Date().toISOString()
    setAcknowledged(true)
    setAckTimestamp(now)
    toast.success('Confirmed: Handover received successfully')
  }

  const renderClaimCard = (claim: Claim) => {
    const isRestrictedPlaceholder = claim.claim_text.includes('[RESTRICTED')

    return (
      <div
        key={claim.claim_id}
        className={`p-3.5 rounded-xl border text-xs transition-all ${
          isRestrictedPlaceholder
            ? 'bg-rose-500/5 border-rose-500/20 text-rose-300'
            : 'bg-black/30 border-white/5 text-gray-200 hover:border-white/15'
        }`}
      >
        <div className="flex items-center justify-between mb-1.5">
          <span className="font-mono text-[10px] text-gray-400 px-1.5 py-0.5 rounded bg-white/5">
            {claim.entity_id}
          </span>
          {isRestrictedPlaceholder ? (
            <span className="flex items-center gap-1 text-[10px] font-mono text-rose-400">
              <Lock className="w-3 h-3" /> Locked
            </span>
          ) : (
            <span className="text-[10px] font-mono text-gray-500">
              {claim.citations.length} sources
            </span>
          )}
        </div>
        <p className={`font-medium ${claim.state === 'superseded' ? 'line-through text-gray-500' : ''}`}>
          {claim.claim_text}
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Receipt Acknowledgment & Security Banner */}
      <div className="p-4 md:p-6 rounded-2xl glass-panel flex flex-wrap items-center justify-between gap-4 border border-blue-500/20 shadow-subtle-glow">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            <h3 className="text-sm font-semibold text-gray-100">Your Clearance Level: {viewerClearance}</h3>
          </div>
          <p className="text-xs text-gray-400">
            Permission filters active. Sensitive passwords and private keys are hidden so they never leak into handovers.
          </p>
        </div>

        {canaryLeakDetected ? (
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-rose-500/20 border border-rose-500 text-rose-300 text-xs font-mono font-bold">
            <ShieldAlert className="w-4 h-4" /> SECURITY ALERT: RESTRICTED SECRET DETECTED!
          </div>
        ) : (
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono">
            Protected: 0 Secrets Leaked
          </div>
        )}

        <div>
          {acknowledged ? (
            <div className="text-right">
              <span className="text-xs font-mono text-emerald-400 font-semibold flex items-center gap-1">
                <CheckSquare className="w-4 h-4" /> Handover Received & Confirmed
              </span>
              <span className="text-[10px] text-gray-500 font-mono">{ackTimestamp}</span>
            </div>
          ) : (
            <button
              onClick={handleAcknowledge}
              className="px-4 py-2 text-xs font-semibold rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white shadow-sm transition-all active:scale-95"
            >
              Confirm Handover Received
            </button>
          )}
        </div>
      </div>

      {/* 4 Cognitive Panes Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Pane 1: Landmines & Workarounds */}
        <div className="p-5 rounded-2xl glass-panel space-y-3">
          <div className="flex items-center justify-between border-b border-white/5 pb-2">
            <span className="text-xs font-semibold text-amber-400 flex items-center gap-1.5">
              <Flame className="w-4 h-4" /> Gotchas & Known Workarounds
            </span>
            <span className="text-xs font-mono text-gray-500">{panes.landmines.length}</span>
          </div>
          <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
            {panes.landmines.map(renderClaimCard)}
          </div>
        </div>

        {/* Pane 2: Accounts & Credentials */}
        <div className="p-5 rounded-2xl glass-panel space-y-3">
          <div className="flex items-center justify-between border-b border-white/5 pb-2">
            <span className="text-xs font-semibold text-blue-400 flex items-center gap-1.5">
              <Key className="w-4 h-4" /> Important Accounts & Access
            </span>
            <span className="text-xs font-mono text-gray-500">{panes.accounts.length}</span>
          </div>
          <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
            {panes.accounts.map(renderClaimCard)}
          </div>
        </div>

        {/* Pane 3: Decision Rationale */}
        <div className="p-5 rounded-2xl glass-panel space-y-3">
          <div className="flex items-center justify-between border-b border-white/5 pb-2">
            <span className="text-xs font-semibold text-purple-400 flex items-center gap-1.5">
              <Compass className="w-4 h-4" /> Key Decisions & Why
            </span>
            <span className="text-xs font-mono text-gray-500">{panes.decisions.length}</span>
          </div>
          <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
            {panes.decisions.map(renderClaimCard)}
          </div>
        </div>

        {/* Pane 4: Next Actions Backlog */}
        <div className="p-5 rounded-2xl glass-panel space-y-3">
          <div className="flex items-center justify-between border-b border-white/5 pb-2">
            <span className="text-xs font-semibold text-emerald-400 flex items-center gap-1.5">
              <ListTodo className="w-4 h-4" /> Pending Tasks & Next Steps
            </span>
            <span className="text-xs font-mono text-gray-500">{panes.backlog.length}</span>
          </div>
          <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
            {panes.backlog.map(renderClaimCard)}
          </div>
        </div>
      </div>
    </div>
  )
}
