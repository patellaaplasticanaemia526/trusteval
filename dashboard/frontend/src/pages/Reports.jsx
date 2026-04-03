import { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Download, Search, Filter, FileText, Calendar, Building2 } from 'lucide-react';
import DataTable from '../components/common/DataTable';
import TrustBadge from '../components/common/Badge';

const allReports = [
  { id: 'eval-001', model: 'GPT-4', provider: 'OpenAI', industry: 'Healthcare', score: 87, status: 'TRUSTED', date: '2026-03-15', pillars: 4 },
  { id: 'eval-002', model: 'Claude 3 Opus', provider: 'Anthropic', industry: 'Finance', score: 91, status: 'TRUSTED', date: '2026-03-14', pillars: 4 },
  { id: 'eval-003', model: 'Gemini Pro', provider: 'Google', industry: 'Legal', score: 64, status: 'CONDITIONAL', date: '2026-03-13', pillars: 3 },
  { id: 'eval-004', model: 'Llama 2 70B', provider: 'Meta', industry: 'Education', score: 52, status: 'UNTRUSTED', date: '2026-03-12', pillars: 4 },
  { id: 'eval-005', model: 'GPT-4 Turbo', provider: 'OpenAI', industry: 'E-Commerce', score: 79, status: 'CONDITIONAL', date: '2026-03-11', pillars: 4 },
  { id: 'eval-006', model: 'Claude 3 Sonnet', provider: 'Anthropic', industry: 'Healthcare', score: 84, status: 'TRUSTED', date: '2026-03-10', pillars: 3 },
  { id: 'eval-007', model: 'GPT-3.5 Turbo', provider: 'OpenAI', industry: 'Finance', score: 68, status: 'CONDITIONAL', date: '2026-03-09', pillars: 4 },
  { id: 'eval-008', model: 'Gemini Ultra', provider: 'Google', industry: 'Healthcare', score: 76, status: 'CONDITIONAL', date: '2026-03-08', pillars: 2 },
];

const columns = [
  { key: 'model', label: 'Model' },
  { key: 'provider', label: 'Provider' },
  { key: 'industry', label: 'Industry' },
  {
    key: 'score',
    label: 'Score',
    render: (val) => (
      <span className={`font-bold ${val >= 80 ? 'text-emerald-400' : val >= 60 ? 'text-amber-400' : 'text-red-400'}`}>
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
  { key: 'pillars', label: 'Pillars' },
  { key: 'date', label: 'Date' },
  {
    key: 'actions',
    label: '',
    sortable: false,
    render: (_, row) => (
      <button
        onClick={(e) => {
          e.stopPropagation();
        }}
        className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-700 transition-default"
        title="Download report"
      >
        <Download className="w-4 h-4" />
      </button>
    ),
  },
];

export default function Reports() {
  const navigate = useNavigate();
  const [search, setSearch] = useState('');
  const [industryFilter, setIndustryFilter] = useState('all');
  const [providerFilter, setProviderFilter] = useState('all');
  const [dateFilter, setDateFilter] = useState('all');

  const industries = ['all', ...new Set(allReports.map((r) => r.industry))];
  const providers = ['all', ...new Set(allReports.map((r) => r.provider))];

  const filtered = allReports.filter((r) => {
    const matchSearch =
      !search ||
      r.model.toLowerCase().includes(search.toLowerCase()) ||
      r.provider.toLowerCase().includes(search.toLowerCase());
    const matchIndustry = industryFilter === 'all' || r.industry === industryFilter;
    const matchProvider = providerFilter === 'all' || r.provider === providerFilter;
    return matchSearch && matchIndustry && matchProvider;
  });

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white">Evaluation Reports</h2>
          <p className="text-sm text-slate-400">{filtered.length} reports found</p>
        </div>
        <button className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg px-4 py-2 text-sm font-medium transition-default">
          <Download className="w-4 h-4" />
          Export All
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input
            type="text"
            placeholder="Search models or providers..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg pl-10 pr-4 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </div>

        <select
          value={industryFilter}
          onChange={(e) => setIndustryFilter(e.target.value)}
          className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 text-sm text-white focus:outline-none focus:border-indigo-500"
        >
          {industries.map((ind) => (
            <option key={ind} value={ind}>
              {ind === 'all' ? 'All Industries' : ind}
            </option>
          ))}
        </select>

        <select
          value={providerFilter}
          onChange={(e) => setProviderFilter(e.target.value)}
          className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 text-sm text-white focus:outline-none focus:border-indigo-500"
        >
          {providers.map((prov) => (
            <option key={prov} value={prov}>
              {prov === 'all' ? 'All Providers' : prov}
            </option>
          ))}
        </select>
      </div>

      {/* Table */}
      <DataTable
        columns={columns}
        data={filtered}
        onRowClick={(row) => navigate(`/evaluations/${row.id}`)}
      />
    </motion.div>
  );
}
