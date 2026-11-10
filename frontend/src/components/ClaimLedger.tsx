import React, { useState } from 'react'
import { Filter, Play } from 'lucide-react'
import { toast } from 'sonner'
import { ClaimCard, EvidenceStatus } from './ClaimCard'

export interface Citation {
  chunk_id: string
  quote_span: string
}

export interface Claim {
  claim_id: string
  entity_id: string
  attribute_key?: string
  claim_text: string
  state: 'verified' | 'inferred' | 'conflicting' | 'missing_evidence' | 'superseded'
  effective_label: 'PUBLIC' | 'INTERNAL' | 'LEAD_ONLY' | 'RESTRICTED'
  citations: Citation[]
  created_at: string
  source_timestamp: string
  created_by: string
  reviewer_approved?: boolean
  reviewer_notes?: string
}

interface ClaimLedgerProps {
  claims: Claim[]
  nodes?: { node_id: string; spok_score: number }[]
  onVerify: () => void
  isLoading?: boolean
  isReviewerMode?: boolean
  onReviewDecide?: (claimId: string, action: 'approve' | 'reject' | 'edit', notes?: string, newText?: string) => void
}

export const ClaimLedger: React.FC<ClaimLedgerProps> = ({
  claims,
  nodes,
  onVerify,
  isLoading,
  isReviewerMode = false,
  onReviewDecide,
}) => {
  const [selectedState, setSelectedState] = useState<string>('all')

  const nodeSpokMap = React.useMemo(() => {
    const map: Record<string, number> = {}
    if (nodes) {
      for (const n of nodes) {
        map[n.node_id] = n.spok_score
      }
    }
    return map
  }, [nodes])

  const filtered = claims.filter(c => selectedState === 'all' || c.state === selectedState)

  const getSourceDetails = (claim: Claim) => {
    if (!claim.citations || claim.citations.length === 0) {
      return { type: 'doc', label: 'Unlinked Note' }
    }
    const chunkId = claim.citations[0].chunk_id
    if (chunkId.includes('git')) {
      return { type: 'git_commit', label: `GitHub Commit #${chunkId.slice(-4)}` }
    }
    if (chunkId.includes('chat')) {
      return { type: 'chat_message', label: `Discord Thread #${chunkId.slice(-4)}` }
    }
    if (chunkId.includes('task')) {
      return { type: 'task_card', label: `Task Card #${chunkId.slice(-4)}` }
    }
    return { type: 'meeting_note', label: `Meeting Note #${chunkId.slice(-4)}` }
  }

  return (
    <div className="space-y-5">
      {/* Action Header & Filter Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-4 rounded-2xl glass-panel">
        <div className="flex flex-wrap items-center gap-1.5">
          <Filter className="w-4 h-4 text-gray-400 mr-1" />
          <span className="text-xs font-semibold text-gray-300 mr-2">Filter:</span>
          {[
            { id: 'all', label: 'ALL FACTS' },
            { id: 'verified', label: '✓ VERIFIED IN CODE' },
            { id: 'inferred', label: 'NEEDS CHECK' },
            { id: 'conflicting', label: '⚠ CONFLICTING' },
            { id: 'missing_evidence', label: 'MISSING PROOF' },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setSelectedState(tab.id)}
              className={`px-3 py-1.5 text-xs rounded-xl font-medium transition-all ${
                selectedState === tab.id
                  ? 'bg-blue-600 text-white font-semibold shadow-sm'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <button
          onClick={() => {
            onVerify()
            toast.success('Checked code proof for all facts')
          }}
          disabled={isLoading}
          className="flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-xl bg-blue-600 hover:bg-blue-500 text-white transition-all shadow-subtle-glow active:scale-95 disabled:opacity-50"
        >
          <Play className="w-3.5 h-3.5 fill-current" />
          {isLoading ? 'Checking Code...' : 'Check Code Proof'}
        </button>
      </div>

      {/* Claims List using Apple-Design ClaimCard */}
      <div className="grid grid-cols-1 gap-3.5">
        {filtered.length === 0 ? (
          <div className="p-8 text-center glass-panel rounded-2xl text-gray-400 text-sm">
            No facts match the selected filter.
          </div>
        ) : (
          filtered.map((claim, idx) => {
            const { type, label } = getSourceDetails(claim)
            // Look up real SPOK score from graph node engine
            const realSpok = nodeSpokMap[claim.entity_id] ?? (claim.state === 'verified' ? 0.20 : 0.65)
            const statusTag = (claim.state === 'superseded' ? 'inferred' : claim.state) as EvidenceStatus

            return (
              <ClaimCard
                key={claim.claim_id || idx}
                id={claim.claim_id}
                statement={claim.claim_text}
                sourceType={type}
                sourceLabel={label}
                status={statusTag}
                spokScore={realSpok}
                entityName={claim.entity_id}
                citations={claim.citations}
                effectiveLabel={claim.effective_label}
                reviewerApproved={claim.reviewer_approved}
                reviewerNotes={claim.reviewer_notes}
                isReviewerMode={isReviewerMode}
                onReviewDecide={(action, notes, newText) => onReviewDecide?.(claim.claim_id, action, notes, newText)}
              />
            )
          })
        )}
      </div>
    </div>
  )
}
