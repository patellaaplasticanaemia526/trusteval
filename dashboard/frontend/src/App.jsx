import { Routes, Route } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import NewEvaluation from './pages/NewEvaluation';
import EvaluationDetail from './pages/EvaluationDetail';
import ModelComparison from './pages/ModelComparison';
import Reports from './pages/Reports';
import Settings from './pages/Settings';
import NotFound from './pages/NotFound';

function App() {
  return (
    <Layout>
      <AnimatePresence mode="wait">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/evaluate" element={<NewEvaluation />} />
          <Route path="/evaluations/:id" element={<EvaluationDetail />} />
          <Route path="/compare" element={<ModelComparison />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </AnimatePresence>
    </Layout>
  );
}

export default App;
