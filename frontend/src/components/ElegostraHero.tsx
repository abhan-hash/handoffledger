import React, { useState } from 'react'
import { motion } from 'framer-motion'
import {
  Shield,
  Layers,
  Activity,
  PlaneTakeoff,
  CheckCircle2,
  RefreshCw,
  Lock,
  ChevronRight,
  Sparkles,
} from 'lucide-react'
import { Claim } from './ClaimLedger'
import { GraphNode } from './RiskHeatmap'

interface ElegostraHeroProps {
  claims: Claim[]
  nodes: GraphNode[]
  qualityScore: number
  unresolvedGaps: number
  backendOnline: boolean
  onNavigateTab: (tab: 'ledger' | 'heatmap' | 'interview' | 'successor' | 'benchmark') => void
  onVerify: () => void
  onRunEval: () => void
  isVerifying?: boolean
  viewerClearance: string
  onRoleChange: (role: 'departing' | 'successor' | 'reviewer') => void
}

export const ElegostraHero: React.FC<ElegostraHeroProps> = ({
  claims,
  nodes,
  qualityScore,
  unresolvedGaps,
  backendOnline,
  onNavigateTab,
  onVerify,
  onRunEval,
  isVerifying = false,
  viewerClearance,
  onRoleChange,
}) => {
  const [sliderConcentration, setSliderConcentration] = useState<number>(0.85)
  const [demoClearance, setDemoClearance] = useState<'PUBLIC' | 'RESTRICTED'>('PUBLIC')
  const [searchQuery, setSearchQuery] = useState<string>('')

  // Live SPOK preview based on slider
  const liveSpok = Math.min(1.0, 0.5 * sliderConcentration + 0.25 * 0.45 + 0.25 * 0.20)

  // Filter claims for widget 3
  const previewClaims = claims.filter(c =>
    searchQuery === '' ? true : c.claim_text.toLowerCase().includes(searchQuery.toLowerCase())
  ).slice(0, 3)

  return (
    <div className="space-y-16 py-4">
      {/* =========================================================================
          HERO SECTION (Framed Canvas + Central Sculptural Core + Orbital Cards)
          ========================================================================= */}
      <section className="relative pt-8 pb-20 px-4 sm:px-8 text-center overflow-hidden">
        {/* Decorative Pill Badge */}
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold mb-6 shadow-sm">
          <span className={`w-2 h-2 rounded-full ${backendOnline ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`} />
          Verifiable Knowledge Handover & SPOK Risk Engine ({viewerClearance})
        </div>

        {/* Hero Title */}
        <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-white max-w-4xl mx-auto leading-[1.08]">
          Connecting team activity to verifiable continuity
        </h1>

        {/* Hero Subtitle */}
        <p className="mt-5 text-base sm:text-lg text-zinc-400 max-w-2xl mx-auto leading-relaxed">
          HandoffLedger reconstructs project state from raw git commits and chat logs,
          verifies atomic claim citations, calculates single-point-of-knowledge risk,
          and guarantees zero canary credential leakage.
        </p>

        {/* Hero Pill Action Buttons */}
        <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
          <button
            onClick={() => onNavigateTab('ledger')}
            className="px-7 py-3.5 rounded-full bg-emerald-500 hover:bg-emerald-400 text-zinc-950 font-bold text-xs tracking-wide shadow-lg shadow-emerald-500/20 active:scale-[0.97] transition-all duration-150 flex items-center gap-2"
          >
            <Layers className="w-4 h-4 text-zinc-950" />
            Explore Claim Ledger ({claims.length} Claims)
          </button>

          <button
            onClick={() => onNavigateTab('heatmap')}
            className="px-7 py-3.5 rounded-full bg-white/10 hover:bg-white/15 text-white border border-white/15 font-semibold text-xs tracking-wide shadow-sm active:scale-[0.97] transition-all duration-150 flex items-center gap-2"
          >
            <Activity className="w-4 h-4 text-emerald-400" />
            View SPOK Heatmap ({nodes.length} Entities)
          </button>

          <button
            onClick={onVerify}
            disabled={isVerifying}
            className="px-5 py-3.5 rounded-full bg-white/5 hover:bg-white/10 text-zinc-300 font-medium text-xs border border-white/10 active:scale-[0.97] transition-all duration-150 flex items-center gap-1.5"
            title="Re-run deterministic citation verifier"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isVerifying ? 'animate-spin text-emerald-400' : ''}`} />
            <span>Verify Pipeline</span>
          </button>
        </div>

        {/* -------------------------------------------------------------------------
            CENTRAL SCULPTURAL KNOWLEDGE CORE & ORBITAL TRAJECTORY TRACKS
            ------------------------------------------------------------------------- */}
        <div className="relative mt-16 max-w-4xl mx-auto h-[440px] flex items-center justify-center select-none">
          {/* Orbital Ellipses */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none" viewBox="0 0 840 440">
            <ellipse
              cx="420"
              cy="220"
              rx="390"
              ry="140"
              fill="none"
              stroke="rgba(255,255,255,0.08)"
              strokeWidth="1.5"
              strokeDasharray="5 5"
            />
            <ellipse
              cx="420"
              cy="220"
              rx="280"
              ry="95"
              fill="none"
              stroke="rgba(255,255,255,0.12)"
              strokeWidth="1.5"
            />
          </svg>

          {/* Central 3D Concentric Geometric Sculpture */}
          <div className="relative z-10 w-44 h-44 rounded-full bg-gradient-to-tr from-emerald-500 via-teal-400 to-cyan-400 shadow-[0_24px_60px_-10px_rgba(16,185,129,0.45)] flex items-center justify-center p-3 cursor-pointer group">
            <div className="w-full h-full rounded-full border-4 border-white/30 flex items-center justify-center relative overflow-hidden backdrop-blur-sm">
              <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_30%,rgba(255,255,255,0.4),transparent_60%)]" />
              <div className="text-center text-white relative z-10 space-y-0.5">
                <span className="text-[10px] font-mono tracking-widest uppercase opacity-85">SPOK Index</span>
                <div className="text-4xl font-extrabold font-mono tracking-tight">0.88</div>
                <div className="text-[10px] font-semibold bg-white/20 px-2 py-0.5 rounded-full inline-block backdrop-blur-md">
                  Single Point
                </div>
              </div>
            </div>
          </div>

          {/* Floating Orbital Card 1: Top-Left (Verified Architecture Claim) */}
          <motion.div
            whileHover={{ y: -6, scale: 1.03 }}
            transition={{ type: 'spring', stiffness: 340, damping: 26 }}
            onClick={() => onNavigateTab('ledger')}
            className="absolute top-4 left-2 sm:left-12 p-3.5 rounded-2xl bg-[#141829]/90 border border-white/15 backdrop-blur-xl shadow-2xl text-left max-w-[210px] cursor-pointer hover:border-emerald-400 transition-colors"
          >
            <div className="flex items-center justify-between gap-2">
              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold tracking-wide bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3" /> Verified
              </span>
              <span className="text-[10px] font-mono text-zinc-400">git:4f2a</span>
            </div>
            <div className="mt-1.5 text-xs font-semibold text-zinc-100 line-clamp-2">
              PostgreSQL 16 on port 5432 (Migrated from SQLite)
            </div>
          </motion.div>

          {/* Floating Orbital Card 2: Top-Right (Canary Assertion Passed) */}
          <motion.div
            whileHover={{ y: -6, scale: 1.03 }}
            transition={{ type: 'spring', stiffness: 340, damping: 26 }}
            onClick={() => onNavigateTab('benchmark')}
            className="absolute top-6 right-2 sm:right-12 p-3.5 rounded-2xl bg-[#141829]/90 border border-white/15 backdrop-blur-xl shadow-2xl text-left max-w-[220px] cursor-pointer hover:border-blue-400 transition-colors"
          >
            <div className="flex items-center justify-between gap-2">
              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-500/15 text-blue-400 border border-blue-500/30 flex items-center gap-1">
                <Shield className="w-3 h-3" /> Canary Guard
              </span>
              <span className="text-[10px] font-mono text-emerald-400 font-bold">0 Leaks</span>
            </div>
            <div className="mt-1.5 text-xs font-semibold text-zinc-100">
              Zero Canary Disclosures on Held-Out Negative Probes
            </div>
          </motion.div>

          {/* Floating Orbital Card 3: Bottom-Left (Quality Score) */}
          <motion.div
            whileHover={{ y: -6, scale: 1.03 }}
            transition={{ type: 'spring', stiffness: 340, damping: 26 }}
            className="absolute bottom-6 left-4 sm:left-20 p-3.5 rounded-2xl bg-[#141829]/90 border border-white/15 backdrop-blur-xl shadow-2xl text-left min-w-[170px]"
          >
            <div className="text-[10px] font-semibold text-zinc-400 uppercase tracking-wider">
              Handover Completeness
            </div>
            <div className="text-2xl font-bold font-mono text-white mt-0.5">
              {qualityScore}% Score
            </div>
            <div className="w-full h-1.5 rounded-full bg-white/10 overflow-hidden mt-1.5">
              <div
                className="h-full bg-emerald-500 rounded-full transition-all duration-500"
                style={{ width: `${qualityScore}%` }}
              />
            </div>
          </motion.div>

          {/* Floating Orbital Card 4: Bottom-Right (Exit Interview Queue) */}
          <motion.div
            whileHover={{ y: -6, scale: 1.03 }}
            transition={{ type: 'spring', stiffness: 340, damping: 26 }}
            onClick={() => onNavigateTab('interview')}
            className="absolute bottom-6 right-4 sm:right-20 p-3.5 rounded-2xl bg-[#141829]/90 border border-white/15 backdrop-blur-xl shadow-2xl text-left min-w-[180px] cursor-pointer hover:border-purple-400 transition-colors"
          >
            <div className="text-[10px] font-semibold text-zinc-400 uppercase tracking-wider">
              Exit Interview
            </div>
            <div className="text-sm font-bold text-purple-400 flex items-center justify-between mt-1">
              <span>{unresolvedGaps} Critical Gaps</span>
              <ChevronRight className="w-4 h-4 text-purple-400" />
            </div>
            <div className="text-[10px] text-zinc-400 mt-0.5">Draft-and-verify recognition</div>
          </motion.div>
        </div>
      </section>

      {/* =========================================================================
          FEATURE SECTION WITH 3-COLUMN TACTILE PREVIEWS
          ========================================================================= */}
      <section className="px-4 sm:px-8 space-y-10">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-end pb-4 border-b border-white/10">
          <div>
            <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white leading-tight">
              Smarter tools for team continuity & knowledge retention
            </h2>
          </div>
          <div>
            <p className="text-zinc-400 text-sm leading-relaxed">
              Replace subjective handover notes with checkable claims, automated
              SPOK bottleneck detection, and security-lattice filtered successor views.
            </p>
          </div>
        </div>

        {/* 3-Column Feature Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Card 1: SPOK Risk Heatmap Engine */}
          <div className="p-6 rounded-3xl bg-white/[0.03] border border-white/10 shadow-sm flex flex-col justify-between space-y-6 hover:border-white/20 transition-all">
            <div className="space-y-3">
              <div className="w-10 h-10 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
                <Activity className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-bold text-white">SPOK Risk Engine</h3>
              <p className="text-xs text-zinc-400 leading-relaxed">
                Single-point-of-knowledge score computed deterministically from author concentration,
                time decay half-life (60 days), and evidence weakness penalties.
              </p>
            </div>

            {/* Tactile Preview Widget: Fluid Progress & Slider */}
            <div className="p-4 rounded-2xl bg-black/40 border border-white/10 shadow-sm space-y-3">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-zinc-300">Author Concentration ($C_n$)</span>
                <span className="font-mono font-bold text-emerald-400">{Math.round(sliderConcentration * 100)}%</span>
              </div>
              <input
                type="range"
                min="0.1"
                max="1.0"
                step="0.05"
                value={sliderConcentration}
                onChange={(e) => setSliderConcentration(parseFloat(e.target.value))}
                className="w-full h-1.5 bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-emerald-500"
              />
              <div className="flex items-center justify-between text-[11px] pt-1 border-t border-white/10">
                <span className="text-zinc-400">Resulting Node SPOK</span>
                <span className="font-mono font-bold text-white">{liveSpok.toFixed(2)}</span>
              </div>
            </div>
          </div>

          {/* Card 2: Security Lattice Vault */}
          <div className="p-6 rounded-3xl bg-white/[0.03] border border-white/10 shadow-sm flex flex-col justify-between space-y-6 hover:border-white/20 transition-all">
            <div className="space-y-3">
              <div className="w-10 h-10 rounded-2xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
                <Lock className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-bold text-white">Lattice Clearance & Canary</h3>
              <p className="text-xs text-zinc-400 leading-relaxed">
                Enforces pre-generation clearance (PUBLIC &lt; INTERNAL &lt; RESTRICTED).
                Inaccessible items render as structural stubs with zero disclosure.
              </p>
            </div>

            {/* Tactile Preview Widget: Card with Clearance Switch */}
            <div className="p-4 rounded-2xl bg-black/40 border border-white/10 shadow-sm space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-zinc-300">Simulate Clearance</span>
                <div className="flex gap-1 p-0.5 bg-white/10 rounded-lg text-[10px] font-semibold">
                  <button
                    onClick={() => setDemoClearance('PUBLIC')}
                    className={`px-2 py-0.5 rounded-md ${demoClearance === 'PUBLIC' ? 'bg-white/20 text-white' : 'text-zinc-400'}`}
                  >
                    PUBLIC
                  </button>
                  <button
                    onClick={() => setDemoClearance('RESTRICTED')}
                    className={`px-2 py-0.5 rounded-md ${demoClearance === 'RESTRICTED' ? 'bg-purple-600 text-white shadow-sm' : 'text-zinc-400'}`}
                  >
                    RESTRICTED
                  </button>
                </div>
              </div>

              <div className="p-3 rounded-xl bg-black/60 border border-white/10 text-xs font-mono">
                {demoClearance === 'PUBLIC' ? (
                  <span className="text-zinc-400 italic">
                    [RESTRICTED CLAIM: Access Clearance Required. Contact Admin.]
                  </span>
                ) : (
                  <span className="text-purple-400 font-semibold">
                    DEPLOY_KEY: CANARY_SECRET_UUIDv4_9823f4b1
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Card 3: Successor Runway Ledger */}
          <div className="p-6 rounded-3xl bg-white/[0.03] border border-white/10 shadow-sm flex flex-col justify-between space-y-6 hover:border-white/20 transition-all">
            <div className="space-y-3">
              <div className="w-10 h-10 rounded-2xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
                <PlaneTakeoff className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-bold text-white">Successor Runway View</h3>
              <p className="text-xs text-zinc-400 leading-relaxed">
                4-pane action dashboard: Active Landmines & Workarounds, Account Ownership,
                Architecture Decisions, and Immediate Next Actions.
              </p>
            </div>

            {/* Tactile Preview Widget: Filterable Micro-List */}
            <div className="p-4 rounded-2xl bg-black/40 border border-white/10 shadow-sm space-y-2.5">
              <input
                type="text"
                placeholder="Filter claims..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-2.5 py-1 text-xs bg-white/5 border border-white/10 text-white rounded-lg focus:outline-none focus:border-blue-400"
              />
              <div className="space-y-1.5">
                {previewClaims.map(c => (
                  <div key={c.claim_id} className="p-2 rounded-lg bg-white/5 border border-white/5 flex items-center justify-between text-[11px]">
                    <span className="truncate max-w-[150px] font-medium text-zinc-200">{c.claim_text}</span>
                    <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${
                      c.state === 'verified' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-amber-500/20 text-amber-400'
                    }`}>
                      {c.state}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* =========================================================================
          DARK SHOWCASE BLOCK (Obsidian + Topography Curves + Canary Assertion)
          ========================================================================= */}
      <section className="px-4 sm:px-8">
        <div className="relative rounded-[32px] bg-gradient-to-b from-[#0e1224] to-[#080912] text-white p-8 sm:p-14 overflow-hidden shadow-2xl border border-white/15">
          {/* Wireframe Contour Topography Vector Curves */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none opacity-20" viewBox="0 0 1000 500">
            <path d="M 0,100 Q 250,50 500,180 T 1000,120" fill="none" stroke="#ffffff" strokeWidth="1.5" />
            <path d="M 0,250 Q 300,320 600,150 T 1000,300" fill="none" stroke="#ffffff" strokeWidth="1.5" />
            <path d="M 0,400 Q 350,200 700,420 T 1000,350" fill="none" stroke="#ffffff" strokeWidth="1.5" />
          </svg>

          <div className="relative z-10 grid grid-cols-1 lg:grid-cols-2 gap-10 items-center">
            {/* Left Content */}
            <div className="space-y-5">
              <span className="text-xs font-mono font-bold tracking-wider uppercase text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20 inline-block">
                Held-Out Benchmark Harness
              </span>
              <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight leading-tight">
                Objective evaluation with zero canary disclosures
              </h2>
              <p className="text-zinc-400 text-sm leading-relaxed max-w-lg">
                We benchmark handover completeness against 20 pre-written ground truth questions on fixed synthetic release <strong className="text-white">v1_demo</strong>.
                Successors achieve a <strong className="text-emerald-400">+45.0% accuracy gain</strong> with an <strong className="text-purple-400">82.0% token reduction</strong>.
              </p>

              <div className="pt-2 flex flex-wrap items-center gap-3">
                <button
                  onClick={() => onNavigateTab('benchmark')}
                  className="px-6 py-3 rounded-full bg-emerald-500 hover:bg-emerald-400 text-zinc-950 font-bold text-xs tracking-wide active:scale-[0.97] transition-all shadow-lg shadow-emerald-500/20"
                >
                  View 20-Question Delta
                </button>
                <button
                  onClick={onRunEval}
                  className="px-6 py-3 rounded-full bg-white/10 hover:bg-white/15 text-white font-medium text-xs border border-white/10 active:scale-[0.97] transition-all"
                >
                  Run Dynamic Benchmark Test
                </button>
              </div>

              {/* Quick Persona Switcher */}
              <div className="pt-3 border-t border-white/10 flex items-center gap-2 text-xs text-zinc-400">
                <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
                <span>Switch perspective:</span>
                <button
                  onClick={() => onRoleChange('departing')}
                  className="underline hover:text-white"
                >
                  Leaver
                </button>
                <span>·</span>
                <button
                  onClick={() => onRoleChange('successor')}
                  className="underline hover:text-white"
                >
                  Successor
                </button>
                <span>·</span>
                <button
                  onClick={() => onRoleChange('reviewer')}
                  className="underline hover:text-white"
                >
                  Auditor
                </button>
              </div>
            </div>

            {/* Right Visual Floating Cards */}
            <div className="relative flex items-center justify-center min-h-[260px]">
              <motion.div
                whileHover={{ y: -4 }}
                className="w-72 sm:w-80 p-5 rounded-2xl bg-gradient-to-br from-indigo-900/60 to-purple-900/40 border border-white/15 backdrop-blur-xl shadow-2xl relative z-20 space-y-3"
              >
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-mono text-purple-300">ADMIN CANARY VAULT</span>
                  <Lock className="w-4 h-4 text-purple-400" />
                </div>
                <div className="text-xl font-bold font-mono text-white">CANARY_ASSERTION</div>
                <div className="p-2.5 rounded-lg bg-black/40 border border-white/10 font-mono text-xs text-emerald-400 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>0 Leakage in Context Sinks</span>
                </div>
              </motion.div>

              <motion.div
                whileHover={{ y: -4 }}
                className="hidden sm:block absolute -top-4 -right-2 w-64 p-4 rounded-2xl bg-gradient-to-tr from-amber-600/30 to-orange-500/20 border border-amber-500/30 backdrop-blur-md z-10"
              >
                <span className="text-[10px] font-mono text-amber-300">DELTA EVALUATION</span>
                <div className="text-2xl font-bold font-mono text-amber-400 mt-1">+45.0%</div>
                <div className="text-[11px] text-zinc-300 mt-0.5">Accuracy gain vs raw commits</div>
              </motion.div>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
