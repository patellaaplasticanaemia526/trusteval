import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ChevronRight,
  ChevronLeft,
  Play,
  Check,
  Loader2,
  Eye,
  EyeOff,
  Bot,
  BrainCircuit,
  Sparkles,
  Cloud,
} from 'lucide-react';
import IndustrySelector from './IndustrySelector';

const providers = [
  { id: 'openai', label: 'OpenAI', models: ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo'], icon: Sparkles },
  { id: 'anthropic', label: 'Anthropic', models: ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku'], icon: BrainCircuit },
  { id: 'google', label: 'Google', models: ['gemini-pro', 'gemini-ultra', 'palm-2'], icon: Cloud },
  { id: 'meta', label: 'Meta', models: ['llama-2-70b', 'llama-2-13b', 'llama-2-7b'], icon: Bot },
];

const pillars = [
  { id: 'bias', label: 'Bias Detection', description: 'Evaluate model fairness across demographics and scenarios', color: 'indigo' },
  { id: 'hallucination', label: 'Hallucination', description: 'Measure factual accuracy and groundedness of responses', color: 'purple' },
  { id: 'pii', label: 'PII Protection', description: 'Test handling of personal identifiable information', color: 'cyan' },
  { id: 'toxicity', label: 'Toxicity', description: 'Assess content safety and harmful output prevention', color: 'rose' },
];

const stepVariants = {
  enter: { x: 50, opacity: 0 },
  center: { x: 0, opacity: 1 },
  exit: { x: -50, opacity: 0 },
};

export default function EvalWizard() {
  const [step, setStep] = useState(0);
  const [industry, setIndustry] = useState('');
  const [provider, setProvider] = useState('');
  const [model, setModel] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [showKey, setShowKey] = useState(false);
  const [selectedPillars, setSelectedPillars] = useState([]);
  const [running, setRunning] = useState(false);
  const [progress, setProgress] = useState(0);

  const steps = ['Industry', 'Provider & Model', 'Pillars', 'Review & Run'];

  const togglePillar = (id) => {
    setSelectedPillars((prev) =>
      prev.includes(id) ? prev.filter((p) => p !== id) : [...prev, id]
    );
  };

  const canNext = () => {
    if (step === 0) return !!industry;
    if (step === 1) return !!provider && !!model && !!apiKey;
    if (step === 2) return selectedPillars.length > 0;
    return true;
  };

  const handleRun = () => {
    setRunning(true);
    setProgress(0);
    const interval = setInterval(() => {
      setProgress((p) => {
        if (p >= 100) {
          clearInterval(interval);
          return 100;
        }
        return p + Math.random() * 8 + 2;
      });
    }, 300);
  };

  const selectedProvider = providers.find((p) => p.id === provider);

  return (
    <div className="max-w-4xl mx-auto">
      {/* Step indicators */}
      <div className="flex items-center justify-center gap-2 mb-8">
        {steps.map((s, i) => (
          <div key={s} className="flex items-center gap-2">
            <button
              onClick={() => i < step && setStep(i)}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium transition-default ${
                i === step
                  ? 'bg-indigo-600 text-white'
                  : i < step
                  ? 'bg-indigo-600/20 text-indigo-400 cursor-pointer'
                  : 'bg-slate-800 text-slate-500'
              }`}
            >
              {i < step ? <Check className="w-4 h-4" /> : <span>{i + 1}</span>}
              <span className="hidden sm:inline">{s}</span>
            </button>
            {i < steps.length - 1 && (
              <div className={`w-8 h-px ${i < step ? 'bg-indigo-500' : 'bg-slate-700'}`} />
            )}
          </div>
        ))}
      </div>

      {/* Step content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={step}
          variants={stepVariants}
          initial="enter"
          animate="center"
          exit="exit"
          transition={{ duration: 0.3 }}
        >
          {/* Step 1: Industry */}
          {step === 0 && (
            <div>
              <h3 className="text-xl font-semibold text-white mb-2">Select Industry</h3>
              <p className="text-slate-400 mb-6">
                Choose the industry context for this evaluation to load relevant test scenarios.
              </p>
              <IndustrySelector selected={industry} onSelect={setIndustry} />
            </div>
          )}

          {/* Step 2: Provider & Model */}
          {step === 1 && (
            <div>
              <h3 className="text-xl font-semibold text-white mb-2">Select Provider & Model</h3>
              <p className="text-slate-400 mb-6">
                Choose the AI provider and model you want to evaluate.
              </p>

              {/* Provider grid */}
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
                {providers.map((p) => {
                  const Icon = p.icon;
                  return (
                    <button
                      key={p.id}
                      onClick={() => {
                        setProvider(p.id);
                        setModel('');
                      }}
                      className={`flex flex-col items-center gap-2 p-4 rounded-xl border transition-default ${
                        provider === p.id
                          ? 'bg-indigo-600/20 border-indigo-500'
                          : 'bg-slate-800 border-slate-700 hover:border-slate-600'
                      }`}
                    >
                      <Icon className={`w-8 h-8 ${provider === p.id ? 'text-indigo-400' : 'text-slate-400'}`} />
                      <span className={`text-sm font-medium ${provider === p.id ? 'text-white' : 'text-slate-300'}`}>
                        {p.label}
                      </span>
                    </button>
                  );
                })}
              </div>

              {/* Model dropdown */}
              {selectedProvider && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Model</label>
                    <select
                      value={model}
                      onChange={(e) => setModel(e.target.value)}
                      className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                    >
                      <option value="">Select a model...</option>
                      {selectedProvider.models.map((m) => (
                        <option key={m} value={m}>
                          {m}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">API Key</label>
                    <div className="relative">
                      <input
                        type={showKey ? 'text' : 'password'}
                        value={apiKey}
                        onChange={(e) => setApiKey(e.target.value)}
                        placeholder="Enter your API key..."
                        className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 pr-10 font-mono text-sm"
                      />
                      <button
                        onClick={() => setShowKey(!showKey)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-white"
                      >
                        {showKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Step 3: Pillars */}
          {step === 2 && (
            <div>
              <h3 className="text-xl font-semibold text-white mb-2">Select Evaluation Pillars</h3>
              <p className="text-slate-400 mb-6">
                Choose the trust dimensions to evaluate. Select at least one.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {pillars.map((pillar) => {
                  const isActive = selectedPillars.includes(pillar.id);
                  return (
                    <motion.button
                      key={pillar.id}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => togglePillar(pillar.id)}
                      className={`flex items-start gap-4 p-5 rounded-xl border text-left transition-default ${
                        isActive
                          ? 'bg-indigo-600/20 border-indigo-500'
                          : 'bg-slate-800 border-slate-700 hover:border-slate-600'
                      }`}
                    >
                      <div
                        className={`w-5 h-5 mt-0.5 rounded border-2 flex items-center justify-center shrink-0 transition-colors ${
                          isActive
                            ? 'bg-indigo-600 border-indigo-600'
                            : 'border-slate-600'
                        }`}
                      >
                        {isActive && <Check className="w-3 h-3 text-white" />}
                      </div>
                      <div>
                        <p className={`font-semibold ${isActive ? 'text-white' : 'text-slate-300'}`}>
                          {pillar.label}
                        </p>
                        <p className="text-sm text-slate-500 mt-1">{pillar.description}</p>
                      </div>
                    </motion.button>
                  );
                })}
              </div>
            </div>
          )}

          {/* Step 4: Review & Run */}
          {step === 3 && (
            <div>
              <h3 className="text-xl font-semibold text-white mb-2">Review & Run</h3>
              <p className="text-slate-400 mb-6">
                Confirm your evaluation configuration and start the assessment.
              </p>

              <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 space-y-4 mb-6">
                <div className="flex justify-between py-2 border-b border-slate-700">
                  <span className="text-slate-400">Industry</span>
                  <span className="text-white font-medium capitalize">{industry}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-slate-700">
                  <span className="text-slate-400">Provider</span>
                  <span className="text-white font-medium capitalize">{provider}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-slate-700">
                  <span className="text-slate-400">Model</span>
                  <span className="text-white font-medium font-mono">{model}</span>
                </div>
                <div className="flex justify-between py-2">
                  <span className="text-slate-400">Pillars</span>
                  <div className="flex gap-2 flex-wrap justify-end">
                    {selectedPillars.map((p) => (
                      <span
                        key={p}
                        className="px-2 py-1 bg-indigo-600/20 text-indigo-400 text-xs rounded-full font-medium capitalize"
                      >
                        {p}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {running ? (
                <div className="space-y-4">
                  <div className="flex items-center gap-3">
                    <Loader2 className="w-5 h-5 text-indigo-400 animate-spin" />
                    <span className="text-white font-medium">
                      {progress >= 100 ? 'Evaluation complete!' : 'Running evaluation...'}
                    </span>
                  </div>
                  <div className="w-full bg-slate-700 rounded-full h-2.5">
                    <motion.div
                      className="h-2.5 rounded-full bg-indigo-600"
                      initial={{ width: 0 }}
                      animate={{ width: `${Math.min(progress, 100)}%` }}
                      transition={{ duration: 0.3 }}
                    />
                  </div>
                  <p className="text-sm text-slate-400">{Math.round(Math.min(progress, 100))}% complete</p>
                </div>
              ) : (
                <button
                  onClick={handleRun}
                  className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg px-6 py-3 font-medium transition-default"
                >
                  <Play className="w-5 h-5" />
                  Start Evaluation
                </button>
              )}
            </div>
          )}
        </motion.div>
      </AnimatePresence>

      {/* Navigation buttons */}
      {!running && (
        <div className="flex justify-between mt-8 pt-6 border-t border-slate-700">
          <button
            onClick={() => setStep((s) => Math.max(0, s - 1))}
            disabled={step === 0}
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-slate-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-default"
          >
            <ChevronLeft className="w-4 h-4" />
            Back
          </button>
          {step < 3 && (
            <button
              onClick={() => setStep((s) => Math.min(3, s + 1))}
              disabled={!canNext()}
              className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg px-4 py-2 font-medium transition-default"
            >
              Next
              <ChevronRight className="w-4 h-4" />
            </button>
          )}
        </div>
      )}
    </div>
  );
}
