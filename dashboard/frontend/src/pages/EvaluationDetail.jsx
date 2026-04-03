import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowLeft, Download, FileJson, FileSpreadsheet, Share2 } from 'lucide-react';
import RadarChart from '../components/charts/RadarChart';
import ScoreGauge from '../components/common/ScoreGauge';
import TrustBadge from '../components/common/Badge';
import PillarBreakdown from '../components/evaluation/PillarBreakdown';

const mockEval = {
  id: 'eval-001',
  model: 'GPT-4',
  provider: 'OpenAI',
  industry: 'Healthcare',
  date: '2026-03-15',
  overallScore: 87,
  status: 'TRUSTED',
  pillarScores: { bias: 85, hallucination: 78, pii: 90, toxicity: 75 },
};

export default function EvaluationDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const eval_ = { ...mockEval, id };

  const radarData = Object.entries(eval_.pillarScores).map(([pillar, score]) => ({
    pillar: pillar.charAt(0).toUpperCase() + pillar.slice(1),
    modelA: score,
  }));

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="space-y-6"
    >
      {/* Back button + header */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate(-1)}
          className="p-2 rounded-lg bg-slate-800 border border-slate-700 text-slate-400 hover:text-white hover:border-slate-600 transition-default"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <h2 className="text-xl font-bold text-white">{eval_.model} Evaluation</h2>
          <p className="text-sm text-slate-400">
            {eval_.provider} - {eval_.industry} - {eval_.date}
          </p>
        </div>
      </div>

      {/* Trust banner */}
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 flex flex-col md:flex-row items-center gap-6">
        <ScoreGauge score={eval_.overallScore} size={180} label="Overall Trust Score" />
        <div className="flex-1 text-center md:text-left space-y-3">
          <div className="flex items-center gap-3 justify-center md:justify-start">
            <h3 className="text-2xl font-bold text-white">{eval_.model}</h3>
            <TrustBadge status={eval_.status} size="lg" />
          </div>
          <p className="text-slate-400">
            Evaluated on {eval_.date} for the {eval_.industry} industry using {Object.keys(eval_.pillarScores).length} trust pillars.
          </p>
          <div className="flex flex-wrap gap-2 justify-center md:justify-start">
            {Object.keys(eval_.pillarScores).map((p) => (
              <span key={p} className="px-2 py-1 bg-slate-700 text-slate-300 rounded-full text-xs capitalize">
                {p}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Radar + pillar score cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <h3 className="text-sm font-semibold text-white mb-3">Trust Profile</h3>
          <RadarChart data={radarData} dataKeyA="modelA" nameA={eval_.model} />
        </div>
        <div>
          <h3 className="text-sm font-semibold text-white mb-3">Pillar Scores</h3>
          <div className="grid grid-cols-2 gap-3">
            {Object.entries(eval_.pillarScores).map(([pillar, score], i) => (
              <motion.div
                key={pillar}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: i * 0.1 }}
                className="bg-slate-800 border border-slate-700 rounded-xl p-4 text-center"
              >
                <ScoreGauge score={score} size={90} strokeWidth={7} />
                <p className="text-sm font-medium text-white mt-2 capitalize">{pillar}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Pillar breakdown with test cases */}
      <PillarBreakdown pillarScores={eval_.pillarScores} />

      {/* Export buttons */}
      <div className="flex flex-wrap gap-3 pt-4 border-t border-slate-700">
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
          Share Report
        </button>
      </div>
    </motion.div>
  );
}
