import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

export default function MetricCard({ icon: Icon, label, value, trend, trendValue, delay = 0 }) {
  const trendConfig = {
    up: { icon: TrendingUp, color: 'text-emerald-400', bg: 'bg-emerald-400/10' },
    down: { icon: TrendingDown, color: 'text-red-400', bg: 'bg-red-400/10' },
    neutral: { icon: Minus, color: 'text-slate-400', bg: 'bg-slate-400/10' },
  };

  const t = trendConfig[trend] || trendConfig.neutral;
  const TrendIcon = t.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.4, ease: 'easeOut' }}
      className="bg-slate-800 border border-slate-700 rounded-xl p-6 hover:border-slate-600 transition-default"
    >
      <div className="flex items-start justify-between">
        <div className="p-2 rounded-lg bg-indigo-600/10">
          {Icon && <Icon className="w-5 h-5 text-indigo-400" />}
        </div>
        {trendValue && (
          <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${t.color} ${t.bg}`}>
            <TrendIcon className="w-3 h-3" />
            {trendValue}
          </div>
        )}
      </div>
      <div className="mt-4">
        <p className="text-2xl font-bold text-white">{value}</p>
        <p className="text-sm text-slate-400 mt-1">{label}</p>
      </div>
    </motion.div>
  );
}
