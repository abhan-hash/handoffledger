import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Layers,
  Activity,
  UserCheck,
  PlaneTakeoff,
  BarChart3,
  Shield,
  FolderGit2,
  ChevronDown,
  CheckCircle2,
  RefreshCw,
  RotateCcw,
  Menu,
  X,
  Sparkles,
  Info,
  Lock,
  Eye,
  User,
  Compass,
  ShieldCheck,
} from 'lucide-react'

export type TabId = 'overview' | 'ledger' | 'staging' | 'heatmap' | 'interview' | 'successor' | 'benchmark'
export type UserRole = 'departing' | 'successor' | 'reviewer'
export type ClearanceLevel = 'PUBLIC' | 'INTERNAL' | 'LEAD_ONLY' | 'RESTRICTED'

export interface ProjectOption {
  id: string
  name: string
  branch: string
  status: 'verified' | 'in_progress' | 'audited'
  claimsCount: number
}

export interface AppLayoutProps {
  activeTab: TabId
  onTabChange: (tab: TabId) => void
  currentRole: UserRole
  onRoleChange: (role: UserRole) => void
  qualityScore?: number
  projects?: ProjectOption[]
  activeProjectId?: string
  onSelectProject?: (projectId: string) => void
  backendOnline?: boolean
  isLoading?: boolean
  onRefresh?: () => void
  onResetDemo?: () => void
  unresolvedGapsCount?: number
  totalClaimsCount?: number
  children: React.ReactNode
}

const DEFAULT_PROJECTS: ProjectOption[] = [
  {
    id: 'handoff-v1',
    name: 'HandoffLedger v1_demo',
    branch: 'main · synthetic',
    status: 'verified',
    claimsCount: 12,
  },
  {
    id: 'payments-service',
    name: 'Payments & Billing Gateway',
    branch: 'release/v2.4',
    status: 'in_progress',
    claimsCount: 18,
  },
  {
    id: 'auth0-infra',
    name: 'Auth0 & IAM Infrastructure',
    branch: 'main · audited',
    status: 'audited',
    claimsCount: 9,
  },
]

export const AppLayout: React.FC<AppLayoutProps> = ({
  activeTab,
  onTabChange,
  currentRole,
  onRoleChange,
  qualityScore = 84,
  projects = DEFAULT_PROJECTS,
  activeProjectId = 'handoff-v1',
  onSelectProject,
  backendOnline = true,
  isLoading = false,
  onRefresh,
  onResetDemo,
  unresolvedGapsCount = 5,
  totalClaimsCount = 12,
  children,
}) => {
  const [isProjectDropdownOpen, setIsProjectDropdownOpen] = useState(false)
  const [isScorePopoverOpen, setIsScorePopoverOpen] = useState(false)
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const projectDropdownRef = useRef<HTMLDivElement>(null)
  const scorePopoverRef = useRef<HTMLDivElement>(null)

  const activeProject = projects.find((p) => p.id === activeProjectId) || projects[0]

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        projectDropdownRef.current &&
        !projectDropdownRef.current.contains(event.target as Node)
      ) {
        setIsProjectDropdownOpen(false)
      }
      if (
        scorePopoverRef.current &&
        !scorePopoverRef.current.contains(event.target as Node)
      ) {
        setIsScorePopoverOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const navItems = [
    {
      group: 'GET STARTED',
      items: [
        {
          id: 'overview' as TabId,
          label: 'Platform Overview',
          icon: Compass,
          badge: 'Start Here',
          badgeColor: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
          description: 'How HandoffLedger stops team knowledge loss',
        },
      ],
    },
    {
      group: 'FACTS & KNOWLEDGE',
      items: [
        {
          id: 'ledger' as TabId,
          label: 'Verified Facts',
          icon: Layers,
          badge: totalClaimsCount > 0 ? `${totalClaimsCount}` : undefined,
          description: 'Every project decision backed by real code proof',
        },
        {
          id: 'staging' as TabId,
          label: 'Review & Approve',
          icon: ShieldCheck,
          badge: currentRole === 'reviewer' ? 'Lead Review' : undefined,
          badgeColor: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
          description: 'Check, edit, and approve facts before sharing',
        },
        {
          id: 'heatmap' as TabId,
          label: 'Knowledge Bottlenecks',
          icon: Activity,
          badge: 'Risk Map',
          badgeColor: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
          description: 'Find where you depend on only one person',
        },
      ],
    },
    {
      group: 'TRANSITION & ONBOARDING',
      items: [
        {
          id: 'interview' as TabId,
          label: 'Quick Exit Interview',
          icon: UserCheck,
          badge: unresolvedGapsCount > 0 ? `${unresolvedGapsCount} to answer` : undefined,
          badgeColor: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
          description: '10 fast questions for the departing member',
        },
        {
          id: 'successor' as TabId,
          label: 'Day-1 Starter Kit',
          icon: PlaneTakeoff,
          badge: 'For New Hires',
          description: 'Gotchas, accounts, decisions & next steps',
        },
      ],
    },
    {
      group: 'READINESS & TESTING',
      items: [
        {
          id: 'benchmark' as TabId,
          label: 'Handover Test Score',
          icon: BarChart3,
          badge: '+45% Gain',
          badgeColor: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
          description: 'Tested against 20 real onboarding questions',
        },
      ],
    },
  ]

  const roles: { id: UserRole; label: string; icon: any; clearance: string }[] = [
    {
      id: 'departing',
      label: 'Departing Member',
      icon: User,
      clearance: 'LEAD_ONLY',
    },
    {
      id: 'successor',
      label: 'New Incoming Member',
      icon: Eye,
      clearance: 'INTERNAL',
    },
    {
      id: 'reviewer',
      label: 'Team Lead (Reviewer)',
      icon: Lock,
      clearance: 'RESTRICTED',
    },
  ]

  return (
    // Outer Ambient Canvas Framing (Screenshot 1: Soft lavender #d8daf0 background with rounded master card)
    <div className="min-h-screen master-frame p-2 sm:p-5 lg:p-7 flex justify-center selection:bg-purple-500/25 selection:text-white">
      {/* Master Container Card: Rounded 32px / 36px, Soft Elevation, Clean Separation */}
      <div className="w-full max-w-[1480px] bg-[#0c0e18] rounded-[28px] sm:rounded-4xl border border-white/10 shadow-tactile-card overflow-hidden flex flex-col text-zinc-100">
        
        {/* =========================================================================
            HEADER BAR (64px / 8px Grid: h-16, px-5 md:px-7)
            Semi-transparent border divider: border-b border-white/10
            ========================================================================= */}
        <header className="h-16 sticky top-0 z-40 bg-[#0c0e18]/85 backdrop-blur-2xl border-b border-white/10 px-4 md:px-6 flex items-center justify-between gap-4">
          {/* Left: Mobile Toggle & Brand & Project Selector */}
          <div className="flex items-center gap-3 md:gap-4">
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="md:hidden p-2 rounded-xl text-zinc-400 hover:text-zinc-200 hover:bg-white/5 active:scale-[0.97] transition-transform duration-150"
              aria-label="Toggle navigation menu"
            >
              {isMobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>

            {/* Brand Logo & Title */}
            <div
              onClick={() => onTabChange('overview')}
              className="flex items-center gap-2.5 cursor-pointer group"
            >
              <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-emerald-500 via-teal-500 to-cyan-500 flex items-center justify-center font-bold text-white shadow-[0_0_16px_rgba(16,185,129,0.35)] border border-white/20 group-hover:scale-105 transition-transform">
                <Shield className="w-4 h-4 text-white" />
              </div>
              <div className="hidden sm:block">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-bold tracking-tight text-white group-hover:text-emerald-400 transition-colors">
                    HandoffLedger
                  </span>
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">
                    v1.0
                  </span>
                  <span className="hidden lg:inline-flex items-center gap-1 text-[10px] font-mono px-2 py-0.5 rounded-md bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 font-medium">
                    <Sparkles className="w-2.5 h-2.5 text-emerald-400" />
                    NVIDIA Nemotron Ultra 550B
                  </span>
                </div>
              </div>
            </div>

            <div className="h-4 w-px bg-white/10 hidden sm:block" />

            {/* Project Selector Dropdown */}
            <div className="relative" ref={projectDropdownRef}>
              <button
                onClick={() => setIsProjectDropdownOpen(!isProjectDropdownOpen)}
                className="group flex items-center gap-2 px-3 py-1.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 text-xs text-zinc-300 active:scale-[0.97] transition-all duration-150 focus:outline-none"
              >
                <FolderGit2 className="w-3.5 h-3.5 text-zinc-400 group-hover:text-emerald-400 transition-colors duration-150" />
                <span className="font-medium text-zinc-200 max-w-[130px] sm:max-w-[190px] truncate">
                  {activeProject.name}
                </span>
                <ChevronDown
                  className={`w-3.5 h-3.5 text-zinc-500 transition-transform duration-200 ${
                    isProjectDropdownOpen ? 'rotate-180 text-zinc-300' : ''
                  }`}
                />
              </button>

              <AnimatePresence>
                {isProjectDropdownOpen && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95, y: -4 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95, y: -4 }}
                    transition={{ duration: 0.16, ease: [0.23, 1, 0.32, 1] }}
                    style={{ transformOrigin: 'top left' }}
                    className="absolute left-0 mt-2 w-72 rounded-2xl bg-[#121524] backdrop-blur-2xl border border-white/15 shadow-[0_16px_40px_rgba(0,0,0,0.7)] p-2 z-50 focus:outline-none"
                  >
                    <div className="px-2.5 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-zinc-400">
                      Active Projects
                    </div>
                    <div className="space-y-1">
                      {projects.map((proj) => {
                        const isCurrent = proj.id === activeProject.id
                        return (
                          <button
                            key={proj.id}
                            onClick={() => {
                              if (onSelectProject) onSelectProject(proj.id)
                              setIsProjectDropdownOpen(false)
                            }}
                            className={`w-full text-left px-3 py-2 rounded-xl text-xs flex items-center justify-between transition-colors duration-150 active:scale-[0.98] ${
                              isCurrent
                                ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                                : 'text-zinc-300 hover:bg-white/5 hover:text-white'
                            }`}
                          >
                            <div>
                              <div className="font-medium truncate">{proj.name}</div>
                              <div className="text-[10px] text-zinc-500 font-mono mt-0.5">
                                {proj.branch}
                              </div>
                            </div>
                            <div className="flex items-center gap-2">
                              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-black/40 text-zinc-400">
                                {proj.claimsCount}c
                              </span>
                              {isCurrent && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />}
                            </div>
                          </button>
                        )
                      })}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>

          {/* Right: Quality Score Badge + Role Switcher + Actions */}
          <div className="flex items-center gap-2.5 md:gap-3.5">
            {/* Handover Quality Score Badge */}
            <div className="relative" ref={scorePopoverRef}>
              <button
                onClick={() => setIsScorePopoverOpen(!isScorePopoverOpen)}
                className="group flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 shadow-[0_0_16px_rgba(16,185,129,0.25)] text-xs text-emerald-400 font-medium active:scale-[0.97] transition-all duration-150 focus:outline-none"
                title="Handover Quality Score"
              >
                <div className="relative flex items-center justify-center">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                </div>
                <span className="font-semibold tracking-tight">{qualityScore}% Score</span>
                <Sparkles className="w-3 h-3 text-emerald-400/80 group-hover:text-emerald-300 transition-colors" />
              </button>

              <AnimatePresence>
                {isScorePopoverOpen && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95, y: -4 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95, y: -4 }}
                    transition={{ duration: 0.16, ease: [0.23, 1, 0.32, 1] }}
                    style={{ transformOrigin: 'top right' }}
                    className="absolute right-0 mt-2 w-72 rounded-2xl bg-[#121524] backdrop-blur-2xl border border-white/15 shadow-[0_16px_40px_rgba(0,0,0,0.7)] p-4 z-50 text-zinc-200"
                  >
                    <div className="flex items-center justify-between pb-3 border-b border-white/10">
                      <span className="text-xs font-semibold text-zinc-200">Handover Completeness Score</span>
                      <span className="text-xs font-bold font-mono text-emerald-400">{qualityScore}%</span>
                    </div>
                    <div className="space-y-2.5 pt-3 text-xs">
                      <div className="flex items-center justify-between text-zinc-400">
                        <span>Code-Backed Facts</span>
                        <span className="font-mono text-emerald-400 font-semibold">Verified Proof</span>
                      </div>
                      <div className="w-full h-1.5 rounded-full bg-white/10 overflow-hidden">
                        <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${qualityScore}%` }} />
                      </div>

                      <div className="flex items-center justify-between text-zinc-400 pt-1">
                        <span>Key-Person Dependency</span>
                        <span className="font-mono text-cyan-400 font-semibold">Monitored</span>
                      </div>

                      <div className="flex items-center justify-between text-zinc-400 pt-1">
                        <span>Password & Secret Leaks</span>
                        <span className="font-mono text-emerald-400 font-semibold">0 Detected (Safe)</span>
                      </div>

                      <div className="pt-2 text-[11px] text-zinc-400 border-t border-white/10 flex items-start gap-1.5">
                        <Info className="w-3.5 h-3.5 text-zinc-400 shrink-0 mt-0.5" />
                        <span>Ready to finalize once remaining questions are confirmed.</span>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Current Role Switcher with layoutId sliding pill */}
            <div className="hidden lg:flex items-center p-1 rounded-xl bg-white/5 border border-white/10">
              {roles.map((r) => {
                const isActive = currentRole === r.id
                const Icon = r.icon
                return (
                  <button
                    key={r.id}
                    onClick={() => onRoleChange(r.id)}
                    className={`relative flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors duration-150 active:scale-[0.97] focus:outline-none ${
                      isActive ? 'text-white' : 'text-zinc-400 hover:text-zinc-200'
                    }`}
                  >
                    {isActive && (
                      <motion.div
                        layoutId="activeRoleIndicator"
                        className="absolute inset-0 bg-white/15 rounded-lg shadow-sm border border-white/20 -z-10"
                        transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                      />
                    )}
                    <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-emerald-400' : 'text-zinc-500'}`} />
                    <span>{r.label}</span>
                  </button>
                )
              })}
            </div>

            {/* Actions: Verify & Demo Reset */}
            {onRefresh && (
              <button
                onClick={onRefresh}
                disabled={isLoading}
                title="Re-run Verification Pass"
                className="p-2 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-zinc-400 hover:text-zinc-200 active:scale-[0.97] transition-all duration-150 disabled:opacity-50"
              >
                <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin text-emerald-400' : ''}`} />
              </button>
            )}

            {onResetDemo && (
              <button
                onClick={onResetDemo}
                title="Reset Demo Dataset"
                className="hidden sm:flex p-2 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-zinc-400 hover:text-zinc-200 active:scale-[0.97] transition-all duration-150"
              >
                <RotateCcw className="w-4 h-4" />
              </button>
            )}

            {/* Backend Online status */}
            <div
              className="flex items-center gap-1.5 text-[11px] font-mono px-2 py-1 rounded-full bg-white/5 border border-white/10"
              title={backendOnline ? 'Backend API Connected' : 'Offline / Mock Mode'}
            >
              <span
                className={`w-1.5 h-1.5 rounded-full ${
                  backendOnline ? 'bg-emerald-400 shadow-[0_0_8px_#34d399]' : 'bg-amber-400'
                }`}
              />
              <span className="hidden xl:inline text-zinc-400">
                {backendOnline ? 'API' : 'Offline'}
              </span>
            </div>
          </div>
        </header>

        {/* =========================================================================
            WORKSPACE BODY: SIDEBAR + CONTENT AREA
            ========================================================================= */}
        <div className="flex-1 flex overflow-hidden">
          {/* Desktop Sidebar (w-64) */}
          <aside className="hidden md:flex flex-col w-64 bg-[#0a0c16]/70 border-r border-white/10 p-4 space-y-6 shrink-0 justify-between select-none">
            <div className="space-y-6">
              {navItems.map((group, gIdx) => (
                <div key={gIdx} className="space-y-1.5">
                  <div className="px-3 py-1 text-[10px] font-bold uppercase tracking-wider text-zinc-500">
                    {group.group}
                  </div>
                  <div className="space-y-1">
                    {group.items.map((item) => {
                      const isActive = activeTab === item.id
                      const Icon = item.icon
                      return (
                        <button
                          key={item.id}
                          onClick={() => onTabChange(item.id)}
                          className={`relative w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium transition-colors duration-150 active:scale-[0.98] group focus:outline-none ${
                            isActive ? 'text-white' : 'text-zinc-400 hover:text-zinc-200'
                          }`}
                        >
                          {isActive && (
                            <motion.div
                              layoutId="activeSidebarIndicator"
                              className="absolute inset-0 bg-white/10 rounded-xl border border-white/15 shadow-sm -z-10"
                              transition={{ type: 'spring', stiffness: 380, damping: 30 }}
                            />
                          )}

                          <div className="flex items-center gap-2.5 min-w-0">
                            <Icon
                              className={`w-4 h-4 shrink-0 transition-colors duration-150 ${
                                isActive
                                  ? 'text-emerald-400'
                                  : 'text-zinc-500 group-hover:text-zinc-300'
                              }`}
                            />
                            <span className="truncate">{item.label}</span>
                          </div>

                          {item.badge && (
                            <span
                              className={`text-[10px] font-mono px-2 py-0.5 rounded-md border font-medium shrink-0 ml-2 ${
                                item.badgeColor ||
                                (isActive
                                  ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30'
                                  : 'bg-white/5 text-zinc-400 border-white/10')
                              }`}
                            >
                              {item.badge}
                            </span>
                          )}
                        </button>
                      )
                    })}
                  </div>
                </div>
              ))}
            </div>

            {/* Bottom Profile & SPOK Risk summary */}
            <div className="space-y-3 pt-4 border-t border-white/10">
              <div className="p-3 rounded-xl bg-white/5 border border-white/10 space-y-1.5">
                <div className="flex items-center justify-between text-[11px]">
                  <span className="text-zinc-400 font-medium">Risk Exposure</span>
                  <span className="text-amber-400 font-mono font-semibold">Peak: 0.88</span>
                </div>
                <div className="w-full h-1.5 rounded-full bg-white/10 overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-emerald-500 via-amber-500 to-rose-500 rounded-full"
                    style={{ width: '68%' }}
                  />
                </div>
                <div className="text-[10px] text-zinc-400">
                  1 single-point bottleneck detected
                </div>
              </div>

              <div className="flex items-center gap-2.5 p-2 rounded-xl bg-white/5 border border-white/5">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-emerald-500 to-teal-600 flex items-center justify-center font-bold text-white text-xs shadow-sm">
                  AC
                </div>
                <div className="min-w-0 flex-1">
                  <div className="text-xs font-semibold text-zinc-200 truncate">Alex Chen</div>
                  <div className="text-[10px] text-zinc-400 truncate">Departing Lead · Infra</div>
                </div>
              </div>
            </div>
          </aside>

          {/* Mobile Slide-in Drawer */}
          <AnimatePresence>
            {isMobileMenuOpen && (
              <>
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.2 }}
                  onClick={() => setIsMobileMenuOpen(false)}
                  className="md:hidden fixed inset-0 bg-black/70 backdrop-blur-sm z-50"
                />

                <motion.div
                  initial={{ x: '-100%' }}
                  animate={{ x: 0 }}
                  exit={{ x: '-100%' }}
                  transition={{ type: 'spring', stiffness: 380, damping: 30 }}
                  className="md:hidden fixed top-0 bottom-0 left-0 w-72 bg-[#0c0e18] border-r border-white/15 p-4 z-50 flex flex-col justify-between"
                >
                  <div className="space-y-6">
                    <div className="flex items-center justify-between pb-3 border-b border-white/10">
                      <div className="flex items-center gap-2">
                        <Shield className="w-5 h-5 text-emerald-400" />
                        <span className="font-bold text-white text-sm">HandoffLedger</span>
                      </div>
                      <button
                        onClick={() => setIsMobileMenuOpen(false)}
                        className="p-1.5 rounded-lg text-zinc-400 hover:text-zinc-200 hover:bg-white/10"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>

                    <div className="space-y-4">
                      {navItems.map((group, gIdx) => (
                        <div key={gIdx} className="space-y-1">
                          <div className="text-[10px] font-bold uppercase tracking-wider text-zinc-500 px-2">
                            {group.group}
                          </div>
                          {group.items.map((item) => {
                            const isActive = activeTab === item.id
                            const Icon = item.icon
                            return (
                              <button
                                key={item.id}
                                onClick={() => {
                                  onTabChange(item.id)
                                  setIsMobileMenuOpen(false)
                                }}
                                className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-medium transition-colors ${
                                  isActive
                                    ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                                    : 'text-zinc-400 hover:text-zinc-200 hover:bg-white/5'
                                }`}
                              >
                                <div className="flex items-center gap-2">
                                  <Icon className="w-4 h-4" />
                                  <span>{item.label}</span>
                                </div>
                                {item.badge && (
                                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-black/40 text-zinc-400">
                                    {item.badge}
                                  </span>
                                )}
                              </button>
                            )
                          })}
                        </div>
                      ))}
                    </div>
                  </div>
                </motion.div>
              </>
            )}
          </AnimatePresence>

          {/* Main Content Area */}
          <main className="flex-1 overflow-y-auto p-3 sm:p-6 lg:p-8">
            <div className="max-w-7xl mx-auto space-y-6">
              {children}
            </div>
          </main>
        </div>
      </div>
    </div>
  )
}
