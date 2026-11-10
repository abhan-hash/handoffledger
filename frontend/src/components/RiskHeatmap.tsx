import React, { useState } from 'react'
import { Activity, GitCommit, Clock, AlertOctagon, Eye, EyeOff } from 'lucide-react'

export interface GraphNode {
  node_id: string
  name: string
  entity_type: string
  spok_score: number
  concentration: number
  stale_decay: number
  evidence_weakness: number
  in_degree: number
  interview_priority: number
  is_filtered_from_heatmap: boolean
}

export interface GraphEdge {
  source_id: string
  target_id: string
  relation: string
  weight: number
}

interface RiskHeatmapProps {
  nodes: GraphNode[]
  edges: GraphEdge[]
}

export const RiskHeatmap: React.FC<RiskHeatmapProps> = ({ nodes, edges }) => {
  const [hidePeripheral, setHidePeripheral] = useState<boolean>(true)
  const [selectedNode, setSelectedNode] = useState<string | null>(null)

  const visibleNodes = nodes.filter(n => (hidePeripheral ? !n.is_filtered_from_heatmap : true))

  const getScoreColor = (score: number) => {
    if (score >= 0.7) return 'text-rose-400 bg-rose-500/10 border-rose-500/30'
    if (score >= 0.4) return 'text-amber-400 bg-amber-500/10 border-amber-500/30'
    return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30'
  }

  const getProgressBar = (val: number, color: string) => (
    <div className="w-full bg-black/40 h-1.5 rounded-full overflow-hidden">
      <div
        className={`h-full ${color} transition-all duration-300`}
        style={{ width: `${Math.round(val * 100)}%` }}
      />
    </div>
  )

  return (
    <div className="space-y-6">
      {/* Controls Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-4 rounded-xl glass-panel">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-blue-400" />
          <span className="text-sm font-semibold text-gray-200">Knowledge-Risk Topography</span>
          <span className="text-xs text-gray-400">({visibleNodes.length} active entities)</span>
        </div>

        <button
          onClick={() => setHidePeripheral(!hidePeripheral)}
          className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium rounded-lg border border-white/10 hover:border-white/20 bg-white/5 text-gray-300 transition-colors"
        >
          {hidePeripheral ? <Eye className="w-3.5 h-3.5 text-blue-400" /> : <EyeOff className="w-3.5 h-3.5 text-gray-400" />}
          {hidePeripheral ? 'Hiding Peripheral Noise (In-Degree < 2)' : 'Showing All Low-Signal Nodes'}
        </button>
      </div>

      {/* Nodes Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {visibleNodes.map(node => {
          const isSelected = selectedNode === node.node_id
          const incomingDeps = edges.filter(e => e.target_id === node.node_id)

          return (
            <div
              key={node.node_id}
              onClick={() => setSelectedNode(isSelected ? null : node.node_id)}
              className={`p-5 rounded-2xl glass-panel glass-panel-hover cursor-pointer border transition-all ${
                isSelected ? 'border-blue-500 ring-2 ring-blue-500/20' : 'border-white/5'
              }`}
            >
              {/* Header */}
              <div className="flex items-start justify-between gap-2 mb-3">
                <div>
                  <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-white/5 text-gray-400">
                    {node.entity_type}
                  </span>
                  <h3 className="text-base font-semibold text-gray-100 mt-1">{node.name}</h3>
                </div>

                <div className={`px-2.5 py-1 rounded-xl text-xs font-mono font-bold border ${getScoreColor(node.spok_score)}`}>
                  SPOK: {(node.spok_score * 100).toFixed(0)}%
                </div>
              </div>

              {/* Sub-Metric Bars */}
              <div className="space-y-2 mt-4 text-xs font-mono">
                <div>
                  <div className="flex justify-between text-gray-400 mb-1">
                    <span className="flex items-center gap-1"><GitCommit className="w-3 h-3 text-blue-400" /> Concentration:</span>
                    <span className="text-gray-200">{(node.concentration * 100).toFixed(0)}%</span>
                  </div>
                  {getProgressBar(node.concentration, 'bg-blue-500')}
                </div>

                <div>
                  <div className="flex justify-between text-gray-400 mb-1">
                    <span className="flex items-center gap-1"><Clock className="w-3 h-3 text-amber-400" /> Stale Decay:</span>
                    <span className="text-gray-200">{(node.stale_decay * 100).toFixed(0)}%</span>
                  </div>
                  {getProgressBar(node.stale_decay, 'bg-amber-500')}
                </div>

                <div>
                  <div className="flex justify-between text-gray-400 mb-1">
                    <span className="flex items-center gap-1"><AlertOctagon className="w-3 h-3 text-rose-400" /> Evidence Weakness:</span>
                    <span className="text-gray-200">{(node.evidence_weakness * 100).toFixed(0)}%</span>
                  </div>
                  {getProgressBar(node.evidence_weakness, 'bg-rose-500')}
                </div>
              </div>

              {/* In-Degree & Priority Footer */}
              <div className="mt-4 pt-3 border-t border-white/5 flex items-center justify-between text-xs text-gray-400 font-mono">
                <span>In-Degree: <strong className="text-gray-200">{node.in_degree}</strong></span>
                <span>Priority Index: <strong className="text-blue-400">{node.interview_priority.toFixed(2)}</strong></span>
              </div>

              {/* Dependencies Drill-Down */}
              {isSelected && (
                <div className="mt-3 pt-2 text-xs text-gray-400 animate-in fade-in">
                  <p className="font-semibold text-gray-300 mb-1">Dependent Components ({incomingDeps.length}):</p>
                  {incomingDeps.length === 0 ? (
                    <span className="italic text-gray-500">No dependent components registered</span>
                  ) : (
                    <ul className="list-disc pl-4 space-y-0.5 font-mono text-[11px] text-blue-300">
                      {incomingDeps.map((e, idx) => (
                        <li key={idx}>{e.source_id}</li>
                      ))}
                    </ul>
                  )}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
