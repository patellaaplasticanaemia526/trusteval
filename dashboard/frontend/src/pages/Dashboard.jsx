import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
  ClipboardCheck,
  TrendingUp,
  Bot,
  Building2,
  PlusCircle,
  GitCompareArrows,
  ArrowRight,
} from 'lucide-react';
import MetricCard from '../components/common/MetricCard';
import DataTable from '../components/common/DataTable';
import TrustBadge from '../components/common/Badge';
import TrendChart from '../components/charts/TrendChart';

const summaryCards = [
  { icon: ClipboardCheck, label: 'Total Evaluations', value: '47', trend: 'up', trendValue: '+12%' },
  { icon: TrendingUp, label: 'Avg Trust Score', value: '82.4', trend: 'up', trendValue: '+3.2' },
  { icon: Bot, label: 'Models Evaluated', value: '8', trend: 'neutral', trendValue: '--' },
  { icon: Building2, label: 'Industry Coverage', value: '5/8', trend: 'up', trendValue: '+1' },
];

const recentEvaluations = [
  { id: 'eval-001', model: 'GPT-4', provider: 'OpenAI', industry: 'Healthcare', score: 87, status: 'TRUSTED', date: '2026-03-15' },
  { id: 'eval-002', model: 'Claude 3 Opus', provider: 'Anthropic', industry: 'Finance', score: 91, status: 'TRUSTED', date: '2026-03-14' },
  { id: 'eval-003', model: 'Gemini Pro', provider: 'Google', industry: 'Legal', score: 64, status: 'CONDITIONAL', date: '2026-03-13' },
  { id: 'eval-004', model: 'Llama 2 70B', provider: 'Meta', industry: 'Education', score: 52, status: 'UNTRUSTED', date: '2026-03-12' },
  { id: 'eval-005', model: 'GPT-4 Turbo', provider: 'OpenAI', industry: 'E-Commerce', score: 79, status: 'CONDITIONAL', date: '2026-03-11' },
];

const columns = [
  { key: 'model', label: 'Model' },
  { key: 'provider', label: 'Provider' },
  { key: 'industry', label: 'Industry' },
  {
    key: 'score',
    label: 'Score',
    render: (val) => (
      <span
        className={`font-bold ${
          val >= 80 ? 'text-emerald-400' : val >= 60 ? 'text-amber-400' : 'text-red-400'
        }`}
      >
        {val}
      </span>
    ),
  },
  {
    key: 'status',
    label: 'Status',
    render: (val) => <TrustBadge status={val} size="sm" />,
    sortable: false,
  },
  { key: 'date', label: 'Date' },
];

const industryData = [
  { date: 'Healthcare', score: 84 },
  { date: 'Finance', score: 88 },
  { date: 'Legal', score: 71 },
  { date: 'Education', score: 65 },
  { date: 'E-Commerce', score: 79 },
];

export default function Dashboard() {
  const navigate = useNavigate();

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="space-y-6"
    >
      {/* Summary cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {summaryCards.map((card, i) => (
          <MetricCard key={card.label} {...card} delay={i * 0.08} />
        ))}
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <TrendChart title="Trust Score Trend" />
        <TrendChart
          title="Industry Distribution"
          data={industryData}
          lines={[{ key: 'score', name: 'Avg Score', color: '#10B981' }]}
        />
      </div>

      {/* Recent evaluations */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">Recent Evaluations</h3>
          <button
            onClick={() => navigate('/reports')}
            className="text-sm text-indigo-400 hover:text-indigo-300 flex items-center gap-1 transition-default"
          >
            View all <ArrowRight className="w-4 h-4" />
          </button>
        </div>
        <DataTable
          columns={columns}
          data={recentEvaluations}
          onRowClick={(row) => navigate(`/evaluations/${row.id}`)}
        />
      </motion.div>

      {/* Quick actions */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <motion.button
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          onClick={() => navigate('/evaluate')}
          className="flex items-center gap-4 bg-indigo-600/10 border border-indigo-500/30 rounded-xl p-5 hover:bg-indigo-600/20 transition-default text-left group"
        >
          <div className="p-3 rounded-lg bg-indigo-600/20 group-hover:bg-indigo-600/30 transition-default">
            <PlusCircle className="w-6 h-6 text-indigo-400" />
          </div>
          <div>
            <p className="font-semibold text-white">New Evaluation</p>
            <p className="text-sm text-slate-400">Start a new trust assessment</p>
          </div>
        </motion.button>
        <motion.button
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.45 }}
          onClick={() => navigate('/compare')}
          className="flex items-center gap-4 bg-emerald-600/10 border border-emerald-500/30 rounded-xl p-5 hover:bg-emerald-600/20 transition-default text-left group"
        >
          <div className="p-3 rounded-lg bg-emerald-600/20 group-hover:bg-emerald-600/30 transition-default">
            <GitCompareArrows className="w-6 h-6 text-emerald-400" />
          </div>
          <div>
            <p className="font-semibold text-white">Compare Models</p>
            <p className="text-sm text-slate-400">Side-by-side trust comparison</p>
          </div>
        </motion.button>
      </div>
    </motion.div>
  );
}
