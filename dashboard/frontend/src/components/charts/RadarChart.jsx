import {
  Radar,
  RadarChart as RechartsRadar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Legend,
} from 'recharts';

export default function RadarChart({
  data,
  dataKeyA = 'modelA',
  dataKeyB = 'modelB',
  nameA = 'Model A',
  nameB = 'Model B',
  showComparison = false,
}) {
  const defaultData = [
    { pillar: 'Bias', modelA: 85, modelB: 72 },
    { pillar: 'Hallucination', modelA: 78, modelB: 80 },
    { pillar: 'PII', modelA: 90, modelB: 65 },
    { pillar: 'Toxicity', modelA: 75, modelB: 88 },
  ];

  const chartData = data || defaultData;

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
      <ResponsiveContainer width="100%" height={320}>
        <RechartsRadar cx="50%" cy="50%" outerRadius="75%" data={chartData}>
          <PolarGrid stroke="#334155" />
          <PolarAngleAxis
            dataKey="pillar"
            tick={{ fill: '#94a3b8', fontSize: 13, fontWeight: 500 }}
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 100]}
            tick={{ fill: '#64748b', fontSize: 11 }}
            axisLine={false}
          />
          <Radar
            name={nameA}
            dataKey={dataKeyA}
            stroke="#6366F1"
            fill="#6366F1"
            fillOpacity={0.2}
            strokeWidth={2}
          />
          {showComparison && (
            <Radar
              name={nameB}
              dataKey={dataKeyB}
              stroke="#10B981"
              fill="#10B981"
              fillOpacity={0.15}
              strokeWidth={2}
            />
          )}
          {showComparison && (
            <Legend
              wrapperStyle={{ paddingTop: 16 }}
              formatter={(value) => (
                <span className="text-sm text-slate-300">{value}</span>
              )}
            />
          )}
        </RechartsRadar>
      </ResponsiveContainer>
    </div>
  );
}
