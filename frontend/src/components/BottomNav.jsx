import { useLocation } from 'react-router-dom';
import { Link } from 'react-router-dom';
import { Home, Activity, Calendar, MoreHorizontal } from 'lucide-react';
import '../styles/globals.css';

export default function BottomNav() {
  const location = useLocation();

  const isActive = (path) => {
    return location.pathname.startsWith(path);
  };

  return (
    <div className="fixed bottom-0 left-0 right-0 backdrop-blur-lg bg-obsidian-wave/95 border-t border-royal-nebula/10 py-2 px-4 max-w-md mx-auto z-10">
      <div className="flex items-center justify-between">
        <Link
          to="/dashboard"
          className={`nav-item transition-all ${isActive("/dashboard") ? "text-lime-light" : "text-gray-400"}`}
        >
          <Home className="w-5 h-5" />
          <span className="text-[10px] mt-0.5 font-medium">Inicio</span>
        </Link>

        <Link
          to="/player"
          className={`nav-item transition-all ${isActive("/player") ? "text-lime-light" : "text-gray-400"}`}
        >
          <Activity className="w-5 h-5" />
          <span className="text-[10px] mt-0.5 font-medium">Progreso</span>
        </Link>

        <Link to="/analyze" className="nav-item relative">
          <div className="w-10 h-10 bg-lime-light rounded-full flex items-center justify-center -mt-4 shadow-md">
            <img
              src="/images/Padelyzer-Isotipo-Blanco.png"
              alt="Padelyzer"
              className="w-5 h-5 invert"
            />
          </div>
          <span
            className={`text-[10px] font-medium ${isActive("/analyze") ? "text-lime-light" : "text-gray-400"}`}
          >
            Analizar
          </span>
        </Link>

        <Link
          to="/matches"
          className={`nav-item transition-all ${isActive("/matches") ? "text-lime-light" : "text-gray-400"}`}
        >
          <Calendar className="w-5 h-5" />
          <span className="text-[10px] mt-0.5 font-medium">Partidos</span>
        </Link>

        <Link
          to="/more"
          className={`nav-item transition-all ${isActive("/more") ? "text-lime-light" : "text-gray-400"}`}
        >
          <MoreHorizontal className="w-5 h-5" />
          <span className="text-[10px] mt-0.5 font-medium">Más</span>
        </Link>
      </div>
    </div>
  );
}