import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Home, ArrowLeft, ShieldQuestion } from 'lucide-react';

export default function NotFound() {
  const navigate = useNavigate();

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      className="flex flex-col items-center justify-center min-h-[60vh] text-center"
    >
      <div className="p-6 rounded-2xl bg-slate-800/50 border border-slate-700 mb-6">
        <ShieldQuestion className="w-16 h-16 text-slate-600" />
      </div>

      <h1 className="text-6xl font-bold text-white mb-2">404</h1>
      <p className="text-xl text-slate-400 mb-2">Page Not Found</p>
      <p className="text-sm text-slate-500 mb-8 max-w-md">
        The page you are looking for does not exist or has been moved. Check the URL or navigate back to the dashboard.
      </p>

      <div className="flex gap-3">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg px-4 py-2 text-sm font-medium transition-default"
        >
          <ArrowLeft className="w-4 h-4" />
          Go Back
        </button>
        <button
          onClick={() => navigate('/')}
          className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg px-4 py-2 text-sm font-medium transition-default"
        >
          <Home className="w-4 h-4" />
          Dashboard
        </button>
      </div>
    </motion.div>
  );
}
