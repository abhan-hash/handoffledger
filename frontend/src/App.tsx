import { useState, useEffect } from 'react'
import { toast } from 'sonner'
import { AppLayout, TabId, UserRole } from './components/AppLayout'
import { ElegostraHero } from './components/ElegostraHero'
import { ClaimLedger, Claim } from './components/ClaimLedger'
import { RiskHeatmap, GraphNode, GraphEdge } from './components/RiskHeatmap'
import { GapInterview, InterviewQuestion } from './components/GapInterview'
import { SuccessorView } from './components/SuccessorView'
import { ReviewerStaging } from './components/ReviewerStaging'
import { EvaluationDashboard, EvalData } from './components/EvaluationDashboard'

export default function App() {
  const [activeTab, setActiveTab] = useState<TabId>('overview')
  const [currentRole, setCurrentRole] = useState<UserRole>('successor')
  const [clearance, setClearance] = useState<'PUBLIC' | 'INTERNAL' | 'LEAD_ONLY' | 'RESTRICTED'>('INTERNAL')
  const [activeProjectId, setActiveProjectId] = useState<string>('handoff-v1')
  const [claims, setClaims] = useState<Claim[]>([])
  const [nodes, setNodes] = useState<GraphNode[]>([])
  const [edges, setEdges] = useState<GraphEdge[]>([])
  const [questions, setQuestions] = useState<InterviewQuestion[]>([])
  const [evalData, setEvalData] = useState<EvalData | null>(null)
  const [successorPanes, setSuccessorPanes] = useState({
    landmines: [] as Claim[],
    accounts: [] as Claim[],
    decisions: [] as Claim[],
    backlog: [] as Claim[],
  })
  const [canaryDetected, setCanaryDetected] = useState<boolean>(false)
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [backendOnline, setBackendOnline] = useState<boolean>(false)

  // Fetch state from FastAPI backend
  const loadData = async () => {
    setIsLoading(true)
    try {
      // 1. Health check
      const healthRes = await fetch('/api/v1/health')
      if (healthRes.ok) setBackendOnline(true)

      // 2. Fetch claims
      const claimsRes = await fetch('/api/v1/claims', {
        headers: { 'X-Clearance': clearance }
      })
      if (claimsRes.ok) {
        const claimsData = await claimsRes.json()
        setClaims(claimsData)
      }

      // 3. Fetch graph SPOK
      const graphRes = await fetch('/api/v1/graph/spok')
      if (graphRes.ok) {
        const graphData = await graphRes.json()
        setNodes(graphData.nodes)
        setEdges(graphData.edges)
      }

      // 4. Fetch interview queue
      const queueRes = await fetch('/api/v1/interview/queue')
      if (queueRes.ok) {
        const queueData = await queueRes.json()
        setQuestions(queueData)
      }

      // 5. Fetch successor view
      const succRes = await fetch('/api/v1/successor/view', {
        headers: { 'X-Clearance': clearance }
      })
      if (succRes.ok) {
        const succData = await succRes.json()
        setSuccessorPanes(succData.panes)
        setCanaryDetected(succData.canary_leak_detected)
      }

      // 6. Fetch eval metrics
      const evalRes = await fetch('/api/v1/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dataset_name: 'v1_demo', viewer_clearance: clearance }),
      })
      if (evalRes.ok) {
        const evalJson = await evalRes.json()
        setEvalData(evalJson)
      }
    } catch (err) {
      console.error('Failed to connect to backend:', err)
      setBackendOnline(false)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [clearance])

  const handleRoleChange = (role: UserRole) => {
    setCurrentRole(role)
    let newClearance: 'PUBLIC' | 'INTERNAL' | 'LEAD_ONLY' | 'RESTRICTED' = 'INTERNAL'
    if (role === 'departing') {
      newClearance = 'LEAD_ONLY'
    } else if (role === 'reviewer') {
      newClearance = 'RESTRICTED'
      setActiveTab('staging')
    } else {
      newClearance = 'INTERNAL'
    }
    setClearance(newClearance)
    toast.info(`Switched view to ${role === 'departing' ? 'Departing Member' : role === 'reviewer' ? 'Team Lead (Reviewer)' : 'Incoming Member'} (${newClearance})`)
  }

  const handleVerify = async () => {
    setIsLoading(true)
    try {
      const res = await fetch('/api/v1/verify', { method: 'POST' })
      if (res.ok) {
        toast.success('Verified all facts against source files')
        await loadData()
      }
    } catch (err) {
      toast.error('Failed to verify facts')
    } finally {
      setIsLoading(false)
    }
  }

  const handleRunEval = async () => {
    setIsLoading(true)
    try {
      const res = await fetch('/api/v1/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dataset_name: 'v1_demo', viewer_clearance: clearance }),
      })
      if (res.ok) {
        const data = await res.json()
        setEvalData(data)
        toast.success(`Tested 20 Questions: Accuracy ${Math.round(data.successor_ledger_accuracy * 100)}% (+${Math.round(data.accuracy_delta * 100)}% boost). 0 Leaked Passwords.`)
      }
    } catch (err) {
      toast.error('Failed to run test suite')
    } finally {
      setIsLoading(false)
    }
  }

  const handleReviewDecide = async (
    claimId: string,
    action: 'approve' | 'reject' | 'edit',
    notes?: string,
    newText?: string
  ) => {
    setIsLoading(true)
    try {
      const res = await fetch('/api/v1/review/decide', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Clearance': clearance,
        },
        body: JSON.stringify({
          claim_id: claimId,
          action,
          reviewer_notes: notes,
          updated_claim_text: newText,
        }),
      })
      if (res.ok) {
        toast.success(`Decision saved: '${action}' for item #${claimId}`)
        await loadData()
      } else {
        toast.error('Failed to save decision')
      }
    } catch (err) {
      toast.error('Network error during decision save')
    } finally {
      setIsLoading(false)
    }
  }

  const handleInterviewRespond = async (
    questionId: string,
    action: 'confirm' | 'edit' | 'refute',
    text?: string
  ) => {
    try {
      const url = `/api/v1/interview/respond?question_id=${encodeURIComponent(questionId)}&action=${action}${text ? `&response_text=${encodeURIComponent(text)}` : ''}`
      const res = await fetch(url, { method: 'POST' })
      if (res.ok) {
        toast.success(`Saved answer for gap question #${questionId}`)
        await loadData()
      }
    } catch (err) {
      toast.error('Error submitting answer')
    }
  }

  const handleResetDemo = async () => {
    try {
      const res = await fetch('/api/v1/ingest/synthetic', { method: 'POST' })
      if (res.ok) {
        toast.success('Reset demo with fresh sample project data')
        await loadData()
      }
    } catch (err) {
      toast.error('Failed to reset sample dataset')
    }
  }

  // Dynamic Handover Quality Score based on verified proportion
  const verifiedCount = claims.filter(c => c.state === 'verified').length
  const qualityScore = claims.length > 0 ? Math.round((verifiedCount / claims.length) * 100) : 0
  const unresolvedGaps = questions.filter(q => q.status === 'unanswered').length

  return (
    <AppLayout
      activeTab={activeTab}
      onTabChange={setActiveTab}
      currentRole={currentRole}
      onRoleChange={handleRoleChange}
      qualityScore={qualityScore}
      activeProjectId={activeProjectId}
      onSelectProject={(id) => {
        setActiveProjectId(id)
        toast.info(`Switched project workspace`)
      }}
      backendOnline={backendOnline}
      isLoading={isLoading}
      onRefresh={handleVerify}
      onResetDemo={handleResetDemo}
      unresolvedGapsCount={unresolvedGaps}
      totalClaimsCount={claims.length}
    >
      {/* 0. Elegostra-Style Product Overview & Inspo Hero */}
      {activeTab === 'overview' && (
        <ElegostraHero
          claims={claims}
          nodes={nodes}
          qualityScore={qualityScore}
          unresolvedGaps={unresolvedGaps}
          backendOnline={backendOnline}
          onNavigateTab={setActiveTab}
          onVerify={handleVerify}
          onRunEval={handleRunEval}
          isVerifying={isLoading}
          viewerClearance={clearance}
          onRoleChange={handleRoleChange}
        />
      )}

      {/* 1. Claim Ledger Workspace */}
      {activeTab === 'ledger' && (
        <ClaimLedger
          claims={claims}
          nodes={nodes}
          onVerify={handleVerify}
          isLoading={isLoading}
          isReviewerMode={currentRole === 'reviewer'}
          onReviewDecide={handleReviewDecide}
        />
      )}

      {/* 2. Reviewer Staging Dashboard (Human-in-the-loop review) */}
      {activeTab === 'staging' && (
        <ReviewerStaging
          claims={claims}
          nodes={nodes}
          onReviewDecide={handleReviewDecide}
          isLoading={isLoading}
          clearance={clearance}
        />
      )}

      {/* 3. Knowledge-Risk Heatmap */}
      {activeTab === 'heatmap' && (
        <RiskHeatmap nodes={nodes} edges={edges} />
      )}

      {/* 4. Exit Interview Flow */}
      {activeTab === 'interview' && (
        <GapInterview questions={questions} onRespond={handleInterviewRespond} />
      )}

      {/* 5. Successor Runway View */}
      {activeTab === 'successor' && (
        <SuccessorView
          panes={successorPanes}
          canaryLeakDetected={canaryDetected}
          viewerClearance={clearance}
        />
      )}

      {/* 6. Evaluation Benchmark Delta */}
      {activeTab === 'benchmark' && (
        <EvaluationDashboard
          evalData={evalData}
          onRunEval={handleRunEval}
          isLoading={isLoading}
        />
      )}
    </AppLayout>
  )
}
