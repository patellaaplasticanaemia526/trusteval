import { useState } from 'react';
import { motion } from 'framer-motion';
import { Trophy, ArrowRight } from 'lucide-react';
import RadarChart from '../components/charts/RadarChart';
import HeatMap from '../components/charts/HeatMap';
import TrustBadge from '../components/common/Badge';
import DataTable from '../components/common/DataTable';

const modelOptions = [
  { id: 'gpt4', name: 'GPT-4', provider: 'OpenAI', scores: { bias: 85, hallucination: 78, pii: 90, toxicity: 75 }, overall: 82 },
  { id: 'claude3', name: 'Claude 3 Opus', provider: 'Anthropic', scores: { bias: 82, hallucination: 88, pii: 72, toxicity: 92 }, overall: 84 },
  { id: 'gemini', name: 'Gemini Pro', provider: 'Google', scores: { bias: 70, hallucination: 65, pii: 85, toxicity: 80 }, overall: 75 },
  { id: 'llama2', name: 'Llama 2 70B', provider: 'Meta', scores: { bias: 60, hallucination: 72, pii: 68, toxicity: 78 }, overall: 70 },
];

export default function ModelComparison() {
  const [modelA, setModelA] = useState('gpt4');
  const [modelB, setModelB] = useState('claude3');

  const a = modelOptions.find((m) => m.id === modelA);
  const b = modelOptions.find((m) => m.id === modelB);

  const radarData = Object.keys(a.scores).map((pillar) => ({
    pillar: pillar.charAt(0).toUpperCase() + pillar.slice(1),
    modelA: a.scores[pillar],
    modelB: b.scores[pillar],
  }));

  const diffData = Object.keys(a.scores).map((pillar) => ({
    pillar: pillar.charAt(0).toUpperCase() + pillar.slice(1),
    modelAScore: a.scores[pillar],
    modelBScore: b.scores[pillar],
    diff: a.scores[pillar] - b.scores[pillar],
  }));

  const diffColumns = [
    { key: 'pillar', label: 'Pillar' },
    {
      key: 'modelAScore',
      label: a.name,
      render: (val) => <span className="font-mono font-bold text-indigo-400">{val}</span>,
    },
    {
      key: 'modelBScore',
      label: b.name,
      render: (val) => <span className="font-mono font-bold text-emerald-400">{val}</span>,
    },
    {
      key: 'diff',
      label: 'Difference',
      render: (val) => (
        <span className={`font-mono font-bold ${val > 0 ? 'text-indigo-400' : val < 0 ? 'text-emerald-400' : 'text-slate-400'}`}>
          {val > 0 ? `+${val}` : val}
        </span>
      ),
    },
  ];

  const winner = a.overall >= b.overall ? a : b;
  const winnerStatus = winner.overall >= 80 ? 'TRUSTED' : winner.overall >= 60 ? 'CONDITIONAL' : 'UNTRUSTED';

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="space-y-6"
    >
      {/* Model selectors */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">Model A</label>
          <select
            value={modelA}
            onChange={(e) => setModelA(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-indigo-500"
          >
            {modelOptions.map((m) => (
              <option key={m.id} value={m.id}>
                {m.name} ({m.provider})
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">Model B</label>
          <select
            value={modelB}
            onChange={(e) => setModelB(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-indigo-500"
          >
            {modelOptions.map((m) => (
              <option key={m.id} value={m.id}>
                {m.name} ({m.provider})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Winner banner */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-slate-800 border border-slate-700 rounded-xl p-5 flex items-center gap-4"
      >
        <div className="p-3 rounded-xl bg-amber-500/10">
          <Trophy className="w-6 h-6 text-amber-400" />
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <p className="text-lg font-bold text-white">{winner.name}</p>
            <TrustBadge status={winnerStatus} size="sm" />
          </div>
          <p className="text-sm text-slate-400">
            Leading with an overall score of {winner.overall} across all trust pillars
          </p>
        </div>
        <div className="text-3xl font-bold text-white">{winner.overall}</div>
      </motion.div>

      {/* Side-by-side radar */}
      <div>
        <h3 className="text-sm font-semibold text-white mb-3">Trust Profile Comparison</h3>
        <RadarChart
          data={radarData}
          dataKeyA="modelA"
          dataKeyB="modelB"
          nameA={a.name}
          nameB={b.name}
          showComparison
        />
      </div>

      {/* Difference table */}
      <div>
        <h3 className="text-sm font-semibold text-white mb-3">Score Comparison</h3>
        <DataTable columns={diffColumns} data={diffData} />
      </div>

      {/* Full heatmap */}
      <HeatMap />
    </motion.div>
  );
}
