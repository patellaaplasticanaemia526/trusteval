import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronRight, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';

const mockTestCases = {
  bias: [
    { id: 1, name: 'Gender bias in hiring context', status: 'pass', score: 92, details: 'No significant gender bias detected' },
    { id: 2, name: 'Racial bias in recommendations', status: 'pass', score: 88, details: 'Minor bias in certain edge cases' },
    { id: 3, name: 'Age discrimination detection', status: 'warn', score: 65, details: 'Some age-related patterns identified' },
    { id: 4, name: 'Socioeconomic bias in language', status: 'pass', score: 90, details: 'Response quality consistent across contexts' },
  ],
  hallucination: [
    { id: 5, name: 'Factual accuracy on known events', status: 'pass', score: 95, details: 'Correctly cited verifiable facts' },
    { id: 6, name: 'Citation verification', status: 'fail', score: 40, details: 'Generated non-existent citations' },
    { id: 7, name: 'Medical facts accuracy', status: 'warn', score: 72, details: 'Minor inaccuracies in drug interaction info' },
    { id: 8, name: 'Statistical claims validation', status: 'pass', score: 85, details: 'Statistics generally accurate with sources' },
  ],
  pii: [
    { id: 9, name: 'SSN detection and masking', status: 'pass', score: 98, details: 'All SSN patterns properly masked' },
    { id: 10, name: 'Email extraction prevention', status: 'pass', score: 95, details: 'Email addresses properly handled' },
    { id: 11, name: 'Phone number protection', status: 'pass', score: 92, details: 'Phone numbers detected and masked' },
    { id: 12, name: 'Address anonymization', status: 'warn', score: 70, details: 'Some partial addresses leaked' },
  ],
  toxicity: [
    { id: 13, name: 'Hate speech resistance', status: 'pass', score: 96, details: 'Properly refused hateful content' },
    { id: 14, name: 'Profanity handling', status: 'pass', score: 90, details: 'Appropriate content filtering' },
    { id: 15, name: 'Manipulation resistance', status: 'warn', score: 68, details: 'Some jailbreak attempts partially successful' },
    { id: 16, name: 'Violence content filtering', status: 'pass', score: 94, details: 'Strong content safety measures' },
  ],
};

const statusConfig = {
  pass: { icon: CheckCircle, color: 'text-emerald-400', bg: 'bg-emerald-400/10' },
  fail: { icon: XCircle, color: 'text-red-400', bg: 'bg-red-400/10' },
  warn: { icon: AlertTriangle, color: 'text-amber-400', bg: 'bg-amber-400/10' },
};

function PillarSection({ pillar, score }) {
  const [expanded, setExpanded] = useState(false);
  const tests = mockTestCases[pillar] || [];
  const passCount = tests.filter((t) => t.status === 'pass').length;

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between p-5 hover:bg-slate-700/30 transition-default"
      >
        <div className="flex items-center gap-4">
          {expanded ? (
            <ChevronDown className="w-5 h-5 text-slate-400" />
          ) : (
            <ChevronRight className="w-5 h-5 text-slate-400" />
          )}
          <div className="text-left">
            <h4 className="font-semibold text-white capitalize">{pillar}</h4>
            <p className="text-xs text-slate-400 mt-0.5">
              {passCount}/{tests.length} tests passed
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span
            className={`text-lg font-bold ${
              score >= 80 ? 'text-emerald-400' : score >= 60 ? 'text-amber-400' : 'text-red-400'
            }`}
          >
            {score}
          </span>
          <span className="text-sm text-slate-500">/ 100</span>
        </div>
      </button>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="border-t border-slate-700">
              <table className="w-full text-sm">
                <thead className="bg-slate-800/80">
                  <tr>
                    <th className="px-5 py-2.5 text-left text-xs font-semibold text-slate-400 uppercase">Test Case</th>
                    <th className="px-5 py-2.5 text-left text-xs font-semibold text-slate-400 uppercase">Status</th>
                    <th className="px-5 py-2.5 text-left text-xs font-semibold text-slate-400 uppercase">Score</th>
                    <th className="px-5 py-2.5 text-left text-xs font-semibold text-slate-400 uppercase">Details</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700/50">
                  {tests.map((test, i) => {
                    const s = statusConfig[test.status];
                    const StatusIcon = s.icon;
                    return (
                      <tr key={test.id} className={i % 2 === 0 ? 'bg-slate-800/50' : ''}>
                        <td className="px-5 py-3 text-slate-300">{test.name}</td>
                        <td className="px-5 py-3">
                          <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${s.color} ${s.bg}`}>
                            <StatusIcon className="w-3 h-3" />
                            {test.status.toUpperCase()}
                          </span>
                        </td>
                        <td className="px-5 py-3">
                          <span className={test.score >= 80 ? 'text-emerald-400' : test.score >= 60 ? 'text-amber-400' : 'text-red-400'}>
                            {test.score}
                          </span>
                        </td>
                        <td className="px-5 py-3 text-slate-400 text-xs">{test.details}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default function PillarBreakdown({ pillarScores }) {
  const scores = pillarScores || { bias: 85, hallucination: 78, pii: 90, toxicity: 75 };

  return (
    <div className="space-y-3">
      <h3 className="text-lg font-semibold text-white mb-4">Pillar Breakdown</h3>
      {Object.entries(scores).map(([pillar, score]) => (
        <PillarSection key={pillar} pillar={pillar} score={score} />
      ))}
    </div>
  );
}
