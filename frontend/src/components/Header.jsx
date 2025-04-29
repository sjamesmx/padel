import { Bell } from 'lucide-react';
import '../styles/globals.css';

export default function Header({ title, showNotification = true, showProfile = true }) {
  return (
    <div className="flex items-center justify-between py-4 px-4 backdrop-blur-lg bg-obsidian-wave/90 sticky top-0 z-10">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-xl overflow-hidden shadow-sm">
          <img
            src="/images/Padelyzer-Isotipo-Blanco.png"
            alt="Padelyzer"
            className="w-full h-full object-contain"
          />
        </div>
        <h1 className="font-semibold text-base tracking-tight">{title}</h1>
      </div>

      <div className="flex items-center gap-3">
        {showNotification && (
          <button className="w-8 h-8 flex items-center justify-center bg-obsidian-wave rounded-xl shadow-sm transition-all hover:shadow-md">
            <Bell className="w-4 h-4" />
          </button>
        )}

        {showProfile && (
          <div className="w-8 h-8 bg-lime-light rounded-xl flex items-center justify-center text-noir-eclipse font-bold text-xs shadow-sm">
            {title ? title.substring(0, 2).toUpperCase() : 'U'}
          </div>
        )}
      </div>
    </div>
  );
}