import { motion } from 'framer-motion';
import EvalWizard from '../components/evaluation/EvalWizard';

export default function NewEvaluation() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <EvalWizard />
    </motion.div>
  );
}
