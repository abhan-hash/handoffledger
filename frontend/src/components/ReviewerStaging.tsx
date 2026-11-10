import React, { useState } from 'react'
import {
  ShieldCheck,
  AlertTriangle,
  AlertOctagon,
  CheckCircle2,
  Filter,
  Sparkles,
} from 'lucide-react'
import { toast } from 'sonner'
import { Claim } from './ClaimLedger'
import { ClaimCard, EvidenceStatus } from './ClaimCard'

export interface ReviewerStagingProps {
  claims: Claim[]
  nodes?: { node_id: string; spok_score: number }[]
  onReviewDecide: (claimId: string, action: 'approve' | 'reject' | 'edit', notes?: string, newText?: string) => void
  isLoading?: boolean
  clearance?: string
}

export const ReviewerStaging: React.FC<ReviewerStagingProps> = ({
  claims,
  nodes,
  onReviewDecide,
  isLoading = false,
  clearance = 'LEAD_ONLY',
}) => {
  const [filterMode, setFilterMode] = useState<'triage' | 'conflicts' | 'verified' | 'all'>('triage')

  const nodeSpokMap = React.useMemo(() => {
    const map: Record<string, number> = {}
    if (nodes) {
      for (const n of nodes) {
        map[n.node_id] = n.spok_score
      }
    }
    return map
  }, [nodes])

  // Categorize claims
  const conflictingClaims = claims.filter(c => c.state === 'conflicting')
  const unapprovedClaims = claims.filter(c => !c.reviewer_approved && c.state !== 'superseded')
  const verifiedClaims = claims.filter(c => c.state === 'verified')

  const filteredClaims = React.useMemo(() => {
    switch (filterMode) {
      case 'conflicts':
        return conflictingClaims
      case 'verified':
        return verifiedClaims
      case 'triage':
        return unapprovedClaims
      case 'all':
      default:
        return claims
    }
  }, [claims, filterMode, conflictingClaims, verifiedClaims, unapprovedClaims])

  const handleBatchApproveVerified = () => {
    const unapprovedVerified = verifiedClaims.filter(c => !c.reviewer_approved)
    if (unapprovedVerified.length === 0) {
      toast.info('All verified facts are already approved.')
      return
    }
    unapprovedVerified.forEach(c => {
      onReviewDecide(c.claim_id, 'approve', 'Batch approved verified fact')
    })
    toast.success(`Batch approved ${unapprovedVerified.length} verified facts!`)
  }

  return (
    <div className="space-y-6">
      {/* Top Banner: Reviewer Clearance & Triage Summary */}
      <div className="p-5 rounded-3xl bg-gradient-to-r from-purple-950/40 via-zinc-900/60 to-black/80 border border-purple-500/20 backdrop-blur-xl shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className="w-12 h-12 rounded-2xl bg-purple-500/15 border border-purple-500/30 flex items-center justify-center text-purple-400">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-bold text-white">Review & Approve Knowledge Handover</h2>
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-purple-500/20 text-purple-300 border border-purple-500/40">
                LEAD ACCESS: {clearance}
              </span>
            </div>
            <p className="text-xs text-zinc-400 mt-0.5">
              Review, edit, or approve all generated facts before sharing with incoming team members. Nothing is handed over without human sign-off.
            </p>
          </div>
        </div>

        <button
          onClick={handleBatchApproveVerified}
          disabled={isLoading || verifiedClaims.filter(c => !c.reviewer_approved).length === 0}
          className="flex items-center gap-2 px-4 py-2.5 rounded-2xl bg-purple-600 hover:bg-purple-500 disabled:opacity-40 text-white text-xs font-semibold shadow-lg shadow-purple-600/20 active:scale-95 transition-all"
        >
          <Sparkles className="w-3.5 h-3.5" />
          Auto-Approve Verified Facts ({verifiedClaims.filter(c => !c.reviewer_approved).length})
        </button>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5">
        <div
          onClick={() => setFilterMode('conflicts')}
          className={`p-4 rounded-2xl border transition-all cursor-pointer ${
            filterMode === 'conflicts'
              ? 'bg-rose-950/30 border-rose-500/40 shadow-rose-900/20'
              : 'glass-panel hover:border-white/10'
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-rose-400 flex items-center gap-1.5">
              <AlertOctagon className="w-3.5 h-3.5" /> Conflicting Statements
            </span>
            <span className="text-lg font-bold font-mono text-white">{conflictingClaims.length}</span>
          </div>
          <p className="text-[11px] text-zinc-400 mt-1">Disagreements in docs or chats</p>
        </div>

        <div
          onClick={() => setFilterMode('triage')}
          className={`p-4 rounded-2xl border transition-all cursor-pointer ${
            filterMode === 'triage'
              ? 'bg-amber-950/30 border-amber-500/40 shadow-amber-900/20'
              : 'glass-panel hover:border-white/10'
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-amber-400 flex items-center gap-1.5">
              <AlertTriangle className="w-3.5 h-3.5" /> Needs Review
            </span>
            <span className="text-lg font-bold font-mono text-white">{unapprovedClaims.length}</span>
          </div>
          <p className="text-[11px] text-zinc-400 mt-1">Unapproved or estimated facts</p>
        </div>

        <div
          onClick={() => setFilterMode('verified')}
          className={`p-4 rounded-2xl border transition-all cursor-pointer ${
            filterMode === 'verified'
              ? 'bg-emerald-950/30 border-emerald-500/40 shadow-emerald-900/20'
              : 'glass-panel hover:border-white/10'
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-emerald-400 flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5" /> Code-Verified Facts
            </span>
            <span className="text-lg font-bold font-mono text-white">{verifiedClaims.length}</span>
          </div>
          <p className="text-[11px] text-zinc-400 mt-1">Proven directly in code and commits</p>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center justify-between p-3.5 rounded-2xl glass-panel">
        <div className="flex items-center gap-2">
          <Filter className="w-3.5 h-3.5 text-gray-400 mr-1" />
          <span className="text-xs font-semibold text-gray-300 mr-2">Filter View:</span>
          {(['triage', 'conflicts', 'verified', 'all'] as const).map(mode => (
            <button
              key={mode}
              onClick={() => setFilterMode(mode)}
              className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all ${
                filterMode === mode
                  ? 'bg-purple-600 text-white font-semibold shadow-sm'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'
              }`}
            >
              {mode === 'triage'
                ? 'NEEDS REVIEW'
                : mode === 'conflicts'
                ? 'CONFLICTS ONLY'
                : mode === 'verified'
                ? 'VERIFIED IN CODE'
                : 'ALL FACTS'}
            </button>
          ))}
        </div>
        <span className="text-xs font-mono text-zinc-400">Showing {filteredClaims.length} facts</span>
      </div>

      {/* Claims List with Reviewer Controls */}
      <div className="space-y-4">
        {filteredClaims.length === 0 ? (
          <div className="p-12 text-center glass-panel rounded-3xl text-zinc-400 text-sm space-y-2">
            <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto opacity-75" />
            <p className="font-semibold text-white">All Clear in this Category</p>
            <p className="text-xs text-zinc-500">No facts currently require review under the active filter.</p>
          </div>
        ) : (
          filteredClaims.map((claim, idx) => {
            const realSpok = nodeSpokMap[claim.entity_id] ?? (claim.state === 'verified' ? 0.20 : 0.65)
            const statusTag = (claim.state === 'superseded' ? 'inferred' : claim.state) as EvidenceStatus

            return (
              <ClaimCard
                key={claim.claim_id || idx}
                id={claim.claim_id}
                statement={claim.claim_text}
                sourceType={claim.citations?.[0]?.chunk_id.includes('git') ? 'git_commit' : 'doc'}
                sourceLabel={claim.citations?.[0]?.chunk_id || 'Canonical Source'}
                status={statusTag}
                spokScore={realSpok}
                entityName={claim.entity_id}
                citations={claim.citations}
                effectiveLabel={claim.effective_label}
                reviewerApproved={claim.reviewer_approved}
                reviewerNotes={claim.reviewer_notes}
                isReviewerMode={true}
                onReviewDecide={(action, notes, newText) => onReviewDecide(claim.claim_id, action, notes, newText)}
              />
            )
          })
        )}
      </div>
    </div>
  )
}

export default ReviewerStaging
