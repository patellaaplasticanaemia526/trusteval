import { motion } from 'framer-motion';
import { Download, FileJson, FileSpreadsheet, Share2 } from 'lucide-react';
import ScoreGauge from '../common/ScoreGauge';
import TrustBadge from '../common/Badge';

export default function EvalResults({ results }) {
  const {
    overallScore = 82,
    trustStatus = 'TRUSTED',
    pillarScores = {
      bias: 85,
      hallucination: 78,
      pii: 90,
      toxicity: 75,
    },
    model = 'gpt-4',
    provider = 'OpenAI',
    industry = 'Healthcare',
  } = results || {};

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Trust banner */}
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 flex flex-col sm:flex-row items-center gap-6">
        <ScoreGauge score={overallScore} size={160} label="Overall Trust Score" />
        <div className="flex-1 text-center sm:text-left">
          <div className="flex items-center gap-3 justify-center sm:justify-start mb-2">
            <h3 className="text-xl font-bold text-white">{model}</h3>
            <TrustBadge status={trustStatus} />
          </div>
          <p className="text-slate-400">
            {provider} - {industry} industry evaluation
          </p>
        </div>
      </div>

      {/* Pillar score cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {Object.entries(pillarScores).map(([pillar, score], i) => (
          <motion.div
            key={pillar}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="bg-slate-800 border border-slate-700 rounded-xl p-4 text-center"
          >
            <ScoreGauge score={score} size={100} strokeWidth={8} />
            <p className="text-sm font-medium text-white mt-2 capitalize">{pillar}</p>
          </motion.div>
        ))}
      </div>

      {/* Export buttons */}
      <div className="flex flex-wrap gap-3">
        <button className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg px-4 py-2 text-sm font-medium transition-default">
          <Download className="w-4 h-4" />
          Export PDF
        </button>
        <button className="flex items-center gap-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg px-4 py-2 text-sm font-medium transition-default">
          <FileJson className="w-4 h-4" />
          Export JSON
        </button>
        <button className="flex items-center gap-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg px-4 py-2 text-sm font-medium transition-default">
          <FileSpreadsheet className="w-4 h-4" />
          Export CSV
        </button>
        <button className="flex items-center gap-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg px-4 py-2 text-sm font-medium transition-default">
          <Share2 className="w-4 h-4" />
          Share
        </button>
      </div>
    </motion.div>
  );
}
