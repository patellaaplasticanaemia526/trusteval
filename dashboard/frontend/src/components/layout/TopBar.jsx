import { useLocation } from 'react-router-dom';
import { Bell, Wifi } from 'lucide-react';
import { useState } from 'react';

const pageTitles = {
  '/': 'Dashboard',
  '/evaluate': 'New Evaluation',
  '/compare': 'Model Comparison',
  '/reports': 'Reports',
  '/settings': 'Settings',
};

const providers = [
  { name: 'OpenAI', connected: true },
  { name: 'Anthropic', connected: true },
  { name: 'Google', connected: false },
];

export default function TopBar() {
  const location = useLocation();
  const [showNotifications, setShowNotifications] = useState(false);

  const title =
    pageTitles[location.pathname] ||
    (location.pathname.startsWith('/evaluations/') ? 'Evaluation Detail' : 'TrustEval');

  return (
    <header className="h-16 bg-slate-800/50 border-b border-slate-700 flex items-center justify-between px-6 backdrop-blur-sm sticky top-0 z-30">
      {/* Left: page title */}
      <div className="flex items-center gap-4 pl-12 lg:pl-0">
        <h2 className="text-lg font-semibold text-white">{title}</h2>
      </div>

      {/* Right: connectivity + notifications */}
      <div className="flex items-center gap-5">
        {/* Provider indicators */}
        <div className="hidden md:flex items-center gap-3">
          {providers.map((p) => (
            <div key={p.name} className="flex items-center gap-1.5 text-xs">
              <span
                className={`w-2 h-2 rounded-full ${
                  p.connected ? 'bg-emerald-400 shadow-sm shadow-emerald-400/50' : 'bg-slate-600'
                }`}
              />
              <span className={p.connected ? 'text-slate-300' : 'text-slate-500'}>
                {p.name}
              </span>
            </div>
          ))}
        </div>

        {/* Divider */}
        <div className="hidden md:block w-px h-6 bg-slate-700" />

        {/* Notification bell */}
        <div className="relative">
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="relative p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-700 transition-default"
          >
            <Bell className="w-5 h-5" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-indigo-500 rounded-full" />
          </button>

          {showNotifications && (
            <div className="absolute right-0 top-12 w-72 bg-slate-800 border border-slate-700 rounded-xl shadow-xl p-4 z-50">
              <h3 className="text-sm font-semibold text-white mb-3">Notifications</h3>
              <div className="space-y-3">
                <div className="text-xs text-slate-400 p-2 bg-slate-700/50 rounded-lg">
                  <span className="text-indigo-400 font-medium">Evaluation complete</span>
                  <p className="mt-1">GPT-4 Healthcare evaluation finished - Score: 87</p>
                </div>
                <div className="text-xs text-slate-400 p-2 bg-slate-700/50 rounded-lg">
                  <span className="text-amber-400 font-medium">Warning</span>
                  <p className="mt-1">Rate limit approaching for OpenAI API key</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
