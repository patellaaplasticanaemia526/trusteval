import { useState } from 'react';
import { motion } from 'framer-motion';
import { Key, Eye, EyeOff, Save, Trash2, Gauge, Shield, Clock, FileText } from 'lucide-react';

const defaultKeys = [
  { id: 1, provider: 'OpenAI', key: 'sk-****************************1234', status: 'active', added: '2026-02-15' },
  { id: 2, provider: 'Anthropic', key: 'sk-ant-****************************5678', status: 'active', added: '2026-02-20' },
  { id: 3, provider: 'Google', key: '', status: 'inactive', added: '' },
];

const auditLog = [
  { id: 1, action: 'Evaluation started', model: 'GPT-4', user: 'admin', timestamp: '2026-03-15 14:30:22' },
  { id: 2, action: 'API key updated', model: 'OpenAI', user: 'admin', timestamp: '2026-03-14 10:15:03' },
  { id: 3, action: 'Evaluation completed', model: 'Claude 3 Opus', user: 'admin', timestamp: '2026-03-14 09:45:18' },
  { id: 4, action: 'Settings changed', model: '--', user: 'admin', timestamp: '2026-03-13 16:22:41' },
  { id: 5, action: 'Report exported', model: 'Gemini Pro', user: 'admin', timestamp: '2026-03-13 11:08:55' },
];

export default function Settings() {
  const [apiKeys, setApiKeys] = useState(defaultKeys);
  const [showKeys, setShowKeys] = useState({});
  const [defaults, setDefaults] = useState({
    defaultIndustry: 'healthcare',
    defaultPillars: ['bias', 'hallucination', 'pii', 'toxicity'],
    concurrentEvals: 3,
    timeout: 300,
  });
  const [rateLimits, setRateLimits] = useState({
    requestsPerMinute: 60,
    requestsPerDay: 5000,
    maxTokensPerRequest: 4096,
  });
  const [activeTab, setActiveTab] = useState('keys');

  const tabs = [
    { id: 'keys', label: 'API Keys', icon: Key },
    { id: 'defaults', label: 'Defaults', icon: Shield },
    { id: 'limits', label: 'Rate Limits', icon: Gauge },
    { id: 'audit', label: 'Audit Log', icon: Clock },
  ];

  const toggleKeyVisibility = (id) => {
    setShowKeys((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="space-y-6 max-w-4xl"
    >
      {/* Tab navigation */}
      <div className="flex gap-1 bg-slate-800 border border-slate-700 rounded-xl p-1">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium flex-1 justify-center transition-default ${
                activeTab === tab.id
                  ? 'bg-indigo-600 text-white'
                  : 'text-slate-400 hover:text-white hover:bg-slate-700'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span className="hidden sm:inline">{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* API Keys */}
      {activeTab === 'keys' && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          <h3 className="text-lg font-semibold text-white">API Key Management</h3>
          <p className="text-sm text-slate-400">Manage your AI provider API keys securely.</p>

          {apiKeys.map((ak) => (
            <div
              key={ak.id}
              className="bg-slate-800 border border-slate-700 rounded-xl p-5 space-y-3"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-white font-medium">{ak.provider}</span>
                  <span
                    className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                      ak.status === 'active'
                        ? 'bg-emerald-500/15 text-emerald-400'
                        : 'bg-slate-700 text-slate-500'
                    }`}
                  >
                    {ak.status}
                  </span>
                </div>
                {ak.added && (
                  <span className="text-xs text-slate-500">Added {ak.added}</span>
                )}
              </div>

              <div className="flex gap-2">
                <div className="relative flex-1">
                  <input
                    type={showKeys[ak.id] ? 'text' : 'password'}
                    value={ak.key}
                    onChange={(e) =>
                      setApiKeys((prev) =>
                        prev.map((k) => (k.id === ak.id ? { ...k, key: e.target.value } : k))
                      )
                    }
                    placeholder="Enter API key..."
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-sm text-white placeholder-slate-600 font-mono focus:outline-none focus:border-indigo-500"
                  />
                  <button
                    onClick={() => toggleKeyVisibility(ak.id)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-white"
                  >
                    {showKeys[ak.id] ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
                <button className="p-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white transition-default">
                  <Save className="w-4 h-4" />
                </button>
                <button className="p-2 rounded-lg bg-slate-700 hover:bg-red-600/20 text-slate-400 hover:text-red-400 transition-default">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </motion.div>
      )}

      {/* Defaults */}
      {activeTab === 'defaults' && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          <h3 className="text-lg font-semibold text-white">Default Settings</h3>

          <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 space-y-5">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Default Industry</label>
              <select
                value={defaults.defaultIndustry}
                onChange={(e) => setDefaults({ ...defaults, defaultIndustry: e.target.value })}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-indigo-500"
              >
                <option value="healthcare">Healthcare</option>
                <option value="finance">Finance</option>
                <option value="legal">Legal</option>
                <option value="education">Education</option>
                <option value="general">General</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Concurrent Evaluations</label>
              <input
                type="number"
                value={defaults.concurrentEvals}
                onChange={(e) => setDefaults({ ...defaults, concurrentEvals: parseInt(e.target.value) || 1 })}
                min={1}
                max={10}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Timeout (seconds)</label>
              <input
                type="number"
                value={defaults.timeout}
                onChange={(e) => setDefaults({ ...defaults, timeout: parseInt(e.target.value) || 60 })}
                min={30}
                max={600}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-indigo-500"
              />
            </div>

            <button className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg px-4 py-2 text-sm font-medium transition-default">
              <Save className="w-4 h-4" />
              Save Defaults
            </button>
          </div>
        </motion.div>
      )}

      {/* Rate Limits */}
      {activeTab === 'limits' && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          <h3 className="text-lg font-semibold text-white">Rate Limits</h3>

          <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 space-y-5">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Requests per Minute</label>
              <div className="flex items-center gap-4">
                <input
                  type="range"
                  min={10}
                  max={200}
                  value={rateLimits.requestsPerMinute}
                  onChange={(e) => setRateLimits({ ...rateLimits, requestsPerMinute: parseInt(e.target.value) })}
                  className="flex-1 accent-indigo-600"
                />
                <span className="text-white font-mono text-sm w-12 text-right">{rateLimits.requestsPerMinute}</span>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Requests per Day</label>
              <div className="flex items-center gap-4">
                <input
                  type="range"
                  min={100}
                  max={10000}
                  step={100}
                  value={rateLimits.requestsPerDay}
                  onChange={(e) => setRateLimits({ ...rateLimits, requestsPerDay: parseInt(e.target.value) })}
                  className="flex-1 accent-indigo-600"
                />
                <span className="text-white font-mono text-sm w-16 text-right">{rateLimits.requestsPerDay}</span>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Max Tokens per Request</label>
              <div className="flex items-center gap-4">
                <input
                  type="range"
                  min={256}
                  max={32768}
                  step={256}
                  value={rateLimits.maxTokensPerRequest}
                  onChange={(e) => setRateLimits({ ...rateLimits, maxTokensPerRequest: parseInt(e.target.value) })}
                  className="flex-1 accent-indigo-600"
                />
                <span className="text-white font-mono text-sm w-16 text-right">{rateLimits.maxTokensPerRequest}</span>
              </div>
            </div>

            <button className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg px-4 py-2 text-sm font-medium transition-default">
              <Save className="w-4 h-4" />
              Save Limits
            </button>
          </div>
        </motion.div>
      )}

      {/* Audit Log */}
      {activeTab === 'audit' && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          <h3 className="text-lg font-semibold text-white">Audit Log</h3>
          <p className="text-sm text-slate-400">Track all actions performed in the system.</p>

          <div className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-slate-800/80 border-b border-slate-700">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-400 uppercase">Action</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-400 uppercase">Model/Target</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-400 uppercase">User</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-400 uppercase">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700/50">
                {auditLog.map((entry, i) => (
                  <tr key={entry.id} className={i % 2 === 0 ? 'bg-slate-800/50' : ''}>
                    <td className="px-4 py-3 text-slate-300 flex items-center gap-2">
                      <FileText className="w-4 h-4 text-slate-500" />
                      {entry.action}
                    </td>
                    <td className="px-4 py-3 text-slate-400 font-mono text-xs">{entry.model}</td>
                    <td className="px-4 py-3 text-slate-400">{entry.user}</td>
                    <td className="px-4 py-3 text-slate-500 font-mono text-xs">{entry.timestamp}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}
