import { motion } from 'framer-motion';

function SkeletonLine({ width = '100%', height = 16, delay = 0 }) {
  return (
    <motion.div
      initial={{ opacity: 0.3 }}
      animate={{ opacity: [0.3, 0.6, 0.3] }}
      transition={{ duration: 1.5, repeat: Infinity, delay }}
      className="bg-slate-700 rounded"
      style={{ width, height }}
    />
  );
}

export function SkeletonCard() {
  return (
    <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 space-y-4">
      <div className="flex items-center justify-between">
        <SkeletonLine width={40} height={40} />
        <SkeletonLine width={60} height={20} delay={0.1} />
      </div>
      <SkeletonLine width="60%" height={28} delay={0.2} />
      <SkeletonLine width="40%" height={16} delay={0.3} />
    </div>
  );
}

export function SkeletonTable({ rows = 5, cols = 4 }) {
  return (
    <div className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden">
      <div className="flex gap-4 p-4 border-b border-slate-700">
        {Array.from({ length: cols }).map((_, i) => (
          <SkeletonLine key={i} width={`${100 / cols}%`} height={14} delay={i * 0.05} />
        ))}
      </div>
      {Array.from({ length: rows }).map((_, ri) => (
        <div
          key={ri}
          className={`flex gap-4 p-4 ${ri % 2 === 0 ? 'bg-slate-800/50' : ''}`}
        >
          {Array.from({ length: cols }).map((_, ci) => (
            <SkeletonLine
              key={ci}
              width={`${100 / cols}%`}
              height={14}
              delay={(ri + ci) * 0.03}
            />
          ))}
        </div>
      ))}
    </div>
  );
}

export default function LoadingSpinner({ type = 'cards', count = 4 }) {
  if (type === 'table') return <SkeletonTable />;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {Array.from({ length: count }).map((_, i) => (
        <SkeletonCard key={i} />
      ))}
    </div>
  );
}
