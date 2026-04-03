import { motion } from 'framer-motion';
import {
  Heart,
  Landmark,
  Scale,
  GraduationCap,
  ShoppingCart,
  Car,
  Factory,
  Globe,
} from 'lucide-react';

const industries = [
  { id: 'healthcare', label: 'Healthcare', icon: Heart, description: 'Medical diagnosis, patient records, clinical trials' },
  { id: 'finance', label: 'Finance', icon: Landmark, description: 'Trading, risk assessment, fraud detection' },
  { id: 'legal', label: 'Legal', icon: Scale, description: 'Contract analysis, case law, compliance' },
  { id: 'education', label: 'Education', icon: GraduationCap, description: 'Tutoring, grading, curriculum design' },
  { id: 'ecommerce', label: 'E-Commerce', icon: ShoppingCart, description: 'Product recommendations, reviews, pricing' },
  { id: 'automotive', label: 'Automotive', icon: Car, description: 'Autonomous driving, diagnostics, safety' },
  { id: 'manufacturing', label: 'Manufacturing', icon: Factory, description: 'Quality control, supply chain, maintenance' },
  { id: 'general', label: 'General', icon: Globe, description: 'Cross-industry general-purpose evaluation' },
];

export default function IndustrySelector({ selected, onSelect }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {industries.map((industry, i) => {
        const Icon = industry.icon;
        const isSelected = selected === industry.id;
        return (
          <motion.button
            key={industry.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
            onClick={() => onSelect(industry.id)}
            className={`flex flex-col items-center gap-3 p-6 rounded-xl border text-center transition-default ${
              isSelected
                ? 'bg-indigo-600/20 border-indigo-500 ring-1 ring-indigo-500/50'
                : 'bg-slate-800 border-slate-700 hover:border-slate-600 hover:bg-slate-800/80'
            }`}
          >
            <div
              className={`p-3 rounded-xl ${
                isSelected ? 'bg-indigo-600/30' : 'bg-slate-700'
              }`}
            >
              <Icon className={`w-7 h-7 ${isSelected ? 'text-indigo-400' : 'text-slate-400'}`} />
            </div>
            <span className={`font-semibold ${isSelected ? 'text-white' : 'text-slate-300'}`}>
              {industry.label}
            </span>
            <span className="text-xs text-slate-500 leading-relaxed">{industry.description}</span>
          </motion.button>
        );
      })}
    </div>
  );
}
