import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  CheckCircle2,
  AlertTriangle,
  AlertOctagon,
  HelpCircle,
  GitCommit,
  MessageSquare,
  FileText,
  CheckSquare,
  ChevronRight,
  ExternalLink,
  Shield,
  Activity,
} from 'lucide-react'

export type EvidenceStatus = 'verified' | 'inferred' | 'conflicting' | 'missing_evidence'

export interface CitationItem {
  chunk_id: string
  quote_span: string
}

export interface ClaimCardProps {
  id?: string
  statement: string
  sourceType?: 'git_commit' | 'chat_message' | 'task_card' | 'meeting_note' | string
  sourceLabel?: string // e.g., "GitHub Commit #4f2a"
  status: EvidenceStatus
  spokScore: number // 0.0 to 1.0
  entityName?: string
  citations?: CitationItem[]
  effectiveLabel?: 'PUBLIC' | 'INTERNAL' | 'LEAD_ONLY' | 'RESTRICTED'
  onClick?: () => void
}

export const ClaimCard: React.FC<ClaimCardProps> = ({
  statement,
  sourceType = 'git_commit',
  sourceLabel = 'GitHub Commit #4f2a',
  status,
  spokScore = 0.0,
  entityName,
  citations = [],
  effectiveLabel = 'PUBLIC',
  onClick,
}) => {
  const [isExpanded, setIsExpanded] = useState<boolean>(false)

  // Apple-style status tagging with vibrational translucent color
  const getStatusBadge = () => {
    switch (status) {
      case 'verified':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold tracking-wide bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 shadow-[0_0_12px_-3px_rgba(16,185,129,0.2)]">
            <CheckCircle2 className="w-3.5 h-3.5" />
            Verified
          </span>
        )
      case 'inferred':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold tracking-wide bg-amber-500/10 text-amber-400 border border-amber-500/20 shadow-[0_0_12px_-3px_rgba(245,158,11,0.2)]">
            <AlertTriangle className="w-3.5 h-3.5" />
            Inferred
          </span>
        )
      case 'conflicting':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold tracking-wide bg-rose-500/10 text-rose-400 border border-rose-500/20 shadow-[0_0_12px_-3px_rgba(244,63,94,0.2)]">
            <AlertOctagon className="w-3.5 h-3.5" />
            Conflicting
          </span>
        )
      case 'missing_evidence':
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold tracking-wide bg-zinc-500/10 text-zinc-400 border border-zinc-500/20">
            <HelpCircle className="w-3.5 h-3.5" />
            Missing Evidence
          </span>
        )
    }
  }

  // Source icon
  const getSourceIcon = () => {
    switch (sourceType) {
      case 'chat_message':
        return <MessageSquare className="w-3.5 h-3.5 text-blue-400" />
      case 'task_card':
        return <CheckSquare className="w-3.5 h-3.5 text-purple-400" />
      case 'meeting_note':
        return <FileText className="w-3.5 h-3.5 text-amber-400" />
      case 'git_commit':
      default:
        return <GitCommit className="w-3.5 h-3.5 text-cyan-400" />
    }
  }

  // SPOK score dynamic coloring
  const clampedScore = Math.min(1.0, Math.max(0.0, spokScore))
  const getScoreColor = () => {
    if (clampedScore >= 0.7) return 'text-rose-400 bg-rose-500'
    if (clampedScore >= 0.4) return 'text-amber-400 bg-amber-500'
    return 'text-emerald-400 bg-emerald-500'
  }

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 12, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -8, scale: 0.98 }}
      transition={{
        type: 'spring',
        stiffness: 340,
        damping: 28, // Critically damped per Apple WWDC guidelines
      }}
      whileHover={{
        y: -3,
        transition: { type: 'spring', stiffness: 400, damping: 25 },
      }}
      whileTap={{
        scale: 0.985,
        transition: { type: 'spring', stiffness: 500, damping: 30 },
      }}
      onClick={() => {
        setIsExpanded(!isExpanded)
        onClick?.()
      }}
      className="group relative cursor-pointer overflow-hidden rounded-2xl border border-white/[0.08] bg-[#0f111a]/70 p-5 backdrop-blur-xl transition-colors duration-200 hover:border-white/[0.18] hover:shadow-[0_12px_32px_-4px_rgba(0,0,0,0.6),0_0_20px_-4px_rgba(59,130,246,0.12)] shadow-[inset_0_1px_0_0_rgba(255,255,255,0.08),0_4px_16px_-2px_rgba(0,0,0,0.4)]"
      style={{
        WebkitBackdropFilter: 'blur(20px)',
      }}
    >
      {/* Subtle top-edge light catch */}
      <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent opacity-50 group-hover:opacity-100 transition-opacity" />

      {/* Header Row: Source Badge & Status */}
      <div className="flex flex-wrap items-center justify-between gap-2.5">
        <div className="flex items-center gap-2">
          {/* Source Chunk Badge */}
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-white/[0.04] border border-white/[0.06] text-xs font-mono text-gray-300">
            {getSourceIcon()}
            <span className="font-medium text-gray-200">{sourceLabel}</span>
          </div>

          {entityName && (
            <span className="px-2 py-0.5 rounded text-[11px] font-mono text-gray-400 bg-white/[0.03]">
              {entityName}
            </span>
          )}

          {effectiveLabel && effectiveLabel !== 'PUBLIC' && (
            <span className="flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-mono border border-purple-500/30 bg-purple-500/10 text-purple-300">
              <Shield className="w-3 h-3" /> {effectiveLabel}
            </span>
          )}
        </div>

        {/* Status Tag */}
        <div>{getStatusBadge()}</div>
      </div>

      {/* Main Claim Statement */}
      <div className="mt-3.5">
        <p className="text-sm font-medium leading-relaxed tracking-[-0.01em] text-gray-100 group-hover:text-white transition-colors">
          {statement}
        </p>
      </div>

      {/* SPOK Risk Meter & Chevron */}
      <div className="mt-4 pt-3.5 border-t border-white/[0.06] flex items-center justify-between gap-4">
        {/* Mini SPOK Progress Bar */}
        <div className="flex items-center gap-2.5 flex-1 max-w-xs">
          <Activity className="w-3.5 h-3.5 text-gray-400" />
          <span className="text-[11px] font-mono text-gray-400 font-medium">SPOK:</span>
          
          <div className="relative h-1.5 flex-1 rounded-full bg-white/[0.06] overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${clampedScore * 100}%` }}
              transition={{ type: 'spring', stiffness: 200, damping: 25 }}
              className={`h-full rounded-full ${getScoreColor().split(' ')[1]}`}
            />
          </div>

          <span className={`text-xs font-mono font-bold ${getScoreColor().split(' ')[0]}`}>
            {(clampedScore * 100).toFixed(0)}%
          </span>
        </div>

        {/* Expand Indicator */}
        <div className="flex items-center gap-1 text-[11px] font-mono text-gray-400 group-hover:text-blue-400 transition-colors">
          <span>{citations.length} {citations.length === 1 ? 'citation' : 'citations'}</span>
          <motion.div
            animate={{ rotate: isExpanded ? 90 : 0 }}
            transition={{ type: 'spring', stiffness: 400, damping: 25 }}
          >
            <ChevronRight className="w-3.5 h-3.5" />
          </motion.div>
        </div>
      </div>

      {/* Expandable Evidence Drawer (Apple Physical Accordion) */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{
              type: 'spring',
              stiffness: 350,
              damping: 30,
            }}
            className="overflow-hidden"
          >
            <div className="mt-3.5 pt-3.5 border-t border-white/[0.06] space-y-2.5">
              <span className="text-[10px] font-mono uppercase tracking-wider text-gray-400 flex items-center gap-1">
                <ExternalLink className="w-3 h-3 text-blue-400" /> Verbatim Source Proof
              </span>

              {citations.length === 0 ? (
                <p className="text-xs text-zinc-400 italic">No direct citations recorded for this claim.</p>
              ) : (
                citations.map((c, i) => (
                  <div
                    key={i}
                    className="p-2.5 rounded-xl bg-black/40 border border-white/[0.05] text-xs font-mono text-gray-300 space-y-1"
                  >
                    <div className="text-[10px] text-blue-400 flex items-center justify-between">
                      <span>Chunk ID: {c.chunk_id}</span>
                    </div>
                    <blockquote className="border-l-2 border-blue-500/40 pl-2.5 italic text-gray-300 text-[11px]">
                      "{c.quote_span}"
                    </blockquote>
                  </div>
                ))
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
export default ClaimCard
