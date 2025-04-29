import { motion } from 'framer-motion';
import '../styles/globals.css';

export default function MetricCard({ title, icon, iconColor, children, className = "", delay = 0 }) {
  return (
    <motion.div
      className={`bg-obsidian-wave rounded-xl p-4 shadow-sm ${className}`}
      initial={{ y: 20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, delay }}
    >
      <div className="flex items-center gap-2 mb-4">
        <div className={`w-8 h-8 rounded-full bg-${iconColor}/20 flex items-center justify-center`}>
          <div className={`text-${iconColor}`}>{icon}</div>
        </div>
        <h3 className="text-lg font-semibold">{title}</h3>
      </div>
      {children}
    </motion.div>
  );
}