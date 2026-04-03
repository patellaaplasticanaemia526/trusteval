import { motion } from 'framer-motion';

const defaultData = {
  models: ['GPT-4', 'Claude 3', 'Gemini Pro', 'Llama 2'],
  pillars: ['Bias', 'Hallucination', 'PII', 'Toxicity'],
  scores: [
    [85, 78, 90, 75],
    [82, 88, 72, 92],
    [70, 65, 85, 80],
    [60, 72, 68, 78],
  ],
};

function getHeatColor(score) {
  if (score >= 85) return 'bg-emerald-500/40 text-emerald-300';
  if (score >= 75) return 'bg-emerald-500/20 text-emerald-400';
  if (score >= 65) return 'bg-amber-500/20 text-amber-400';
  if (score >= 50) return 'bg-amber-500/30 text-amber-300';
  return 'bg-red-500/30 text-red-400';
}

export default function HeatMap({ data }) {
  const { models, pillars, scores } = data || defaultData;

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
      <h3 className="text-sm font-semibold text-white mb-4">Model Comparison Heatmap</h3>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr>
              <th className="px-3 py-2 text-left text-xs font-semibold text-slate-400 uppercase">
                Model
              </th>
              {pillars.map((p) => (
                <th key={p} className="px-3 py-2 text-center text-xs font-semibold text-slate-400 uppercase">
                  {p}
                </th>
              ))}
              <th className="px-3 py-2 text-center text-xs font-semibold text-slate-400 uppercase">
                Avg
              </th>
            </tr>
          </thead>
          <tbody>
            {models.map((model, mi) => {
              const avg = Math.round(
                scores[mi].reduce((a, b) => a + b, 0) / scores[mi].length
              );
              return (
                <tr key={model} className="border-t border-slate-700/50">
                  <td className="px-3 py-3 text-sm font-medium text-white whitespace-nowrap">
                    {model}
                  </td>
                  {scores[mi].map((score, pi) => (
                    <td key={pi} className="px-2 py-2 text-center">
                      <motion.div
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: (mi * pillars.length + pi) * 0.03 }}
                        className={`inline-flex items-center justify-center w-14 h-10 rounded-lg text-sm font-bold ${getHeatColor(score)}`}
                      >
                        {score}
                      </motion.div>
                    </td>
                  ))}
                  <td className="px-2 py-2 text-center">
                    <div className={`inline-flex items-center justify-center w-14 h-10 rounded-lg text-sm font-bold ${getHeatColor(avg)}`}>
                      {avg}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
