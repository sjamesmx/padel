import { motion } from 'framer-motion';
import '../styles/globals.css';

export default function ViewSelector({ views, activeView, onChange, className = "" }) {
  return (
    <div className={`bg-obsidian-wave rounded-xl overflow-hidden mb-6 ${className}`}>
      <div className="relative flex">
        {views.map((view) => (
          <button
            key={view.id}
            className={`flex-1 py-3 px-2 text-center relative z-10 transition-colors duration-200 flex items-center justify-center gap-2 ${
              activeView === view.id ? "text-noir-eclipse" : "text-gray-300"
            }`}
            onClick={() => onChange(view.id)}
          >
            {view.icon && (
              <span className={activeView === view.id ? "text-noir-eclipse" : "text-gray-400"}>{view.icon}</span>
            )}
            <span className="text-sm font-medium">{view.label}</span>
          </button>
        ))}
        <motion.div
          className="absolute top-0 bottom-0 bg-lime-light rounded-lg z-0"
          initial={false}
          animate={{
            width: `${100 / views.length}%`,
            x: `${views.findIndex((v) => v.id === activeView) * 100}%`,
          }}
          transition={{ type: "spring", stiffness: 300, damping: 30 }}
        />
      </div>
    </div>
  );
}