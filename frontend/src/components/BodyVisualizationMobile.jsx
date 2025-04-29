import { useState } from 'react';
import { ZoomIn, ZoomOut, RotateCcw, Activity, ChevronRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import '../styles/globals.css';

export default function BodyVisualizationMobile() {
  const [zoom, setZoom] = useState(1);
  const [showMuscleHighlights, setShowMuscleHighlights] = useState(true);

  // Datos de ejemplo para las métricas
  const muscleActivation = {
    shoulders: 0.9,
    arms: 0.85,
    core: 0.5,
    legs: 0.65,
  };

  return (
    <div className="flex flex-col h-full">
      <div className="relative flex-1 bg-noir-eclipse rounded-2xl overflow-hidden shadow-sm">
        <div
          className="w-full h-full flex items-center justify-center"
          style={{ transform: `scale(${zoom})`, transition: "transform 0.3s ease" }}
        >
          {/* Placeholder para la visualización del cuerpo */}
          <div className="text-center p-6 flex flex-col items-center justify-center h-full relative">
            {/* Fondo con patrón de puntos */}
            <div className="absolute inset-0 opacity-5">
              <div
                className="w-full h-full"
                style={{
                  backgroundImage: "radial-gradient(circle, rgba(255, 255, 255, 0.8) 1px, transparent 1px)",
                  backgroundSize: "20px 20px",
                }}
              ></div>
            </div>

            {/* Contenido principal */}
            <div className="relative z-10">
              <div className="w-32 h-32 bg-blue-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
                <Activity className="w-16 h-16 text-blue-500" />
              </div>

              <h3 className="text-xl font-medium text-white mb-3">Análisis Biomecánico</h3>

              <div className="max-w-xs mx-auto bg-obsidian-wave/70 p-4 rounded-xl backdrop-blur-sm">
                <p className="text-sm text-gray-300 leading-relaxed mb-3">
                  Visualiza y analiza tus movimientos para mejorar tu técnica y prevenir lesiones.
                </p>
                <Link
                  to="/practice/biomechanics"
                  className="inline-flex items-center text-lime-light text-sm"
                >
                  Ver detalles <ChevronRight className="w-4 h-4 ml-1" />
                </Link>
              </div>
            </div>
          </div>
        </div>

        <div className="absolute bottom-3 right-3 flex gap-2">
          <button
            className="w-8 h-8 bg-obsidian-wave/80 rounded-full flex items-center justify-center backdrop-blur-sm"
            onClick={() => setZoom(Math.min(2, zoom + 0.2))}
          >
            <ZoomIn className="w-4 h-4" />
          </button>
          <button
            className="w-8 h-8 bg-obsidian-wave/80 rounded-full flex items-center justify-center backdrop-blur-sm"
            onClick={() => setZoom(Math.max(0.5, zoom - 0.2))}
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <button
            className="w-8 h-8 bg-obsidian-wave/80 rounded-full flex items-center justify-center backdrop-blur-sm"
            onClick={() => setZoom(1)}
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>

        <div className="absolute bottom-3 left-3">
          <button
            className="px-3 py-1.5 bg-obsidian-wave/80 rounded-full text-xs backdrop-blur-sm"
            onClick={() => setShowMuscleHighlights(!showMuscleHighlights)}
          >
            {showMuscleHighlights ? "Ocultar" : "Mostrar"} activación
          </button>
        </div>
      </div>

      <div className="mt-4">
        <h3 className="text-sm font-medium mb-3">Activación Muscular</h3>
        <div className="space-y-3">
          <div>
            <div className="flex justify-between items-center mb-1.5">
              <span className="text-sm">Hombros</span>
              <span className="font-medium text-sm">{Math.round(muscleActivation.shoulders * 100)}%</span>
            </div>
            <div className="h-2 bg-obsidian-wave rounded-full overflow-hidden">
              <div className="h-full bg-blue-500" style={{ width: `${muscleActivation.shoulders * 100}%` }}></div>
            </div>
          </div>

          <div>
            <div className="flex justify-between items-center mb-1.5">
              <span className="text-sm">Brazos</span>
              <span className="font-medium text-sm">{Math.round(muscleActivation.arms * 100)}%</span>
            </div>
            <div className="h-2 bg-obsidian-wave rounded-full overflow-hidden">
              <div className="h-full bg-green-500" style={{ width: `${muscleActivation.arms * 100}%` }}></div>
            </div>
          </div>

          <div>
            <div className="flex justify-between items-center mb-1.5">
              <span className="text-sm">Core</span>
              <span className="font-medium text-sm">{Math.round(muscleActivation.core * 100)}%</span>
            </div>
            <div className="h-2 bg-obsidian-wave rounded-full overflow-hidden">
              <div className="h-full bg-orange-500" style={{ width: `${muscleActivation.core * 100}%` }}></div>
            </div>
          </div>

          <div>
            <div className="flex justify-between items-center mb-1.5">
              <span className="text-sm">Piernas</span>
              <span className="font-medium text-sm">{Math.round(muscleActivation.legs * 100)}%</span>
            </div>
            <div className="h-2 bg-obsidian-wave rounded-full overflow-hidden">
              <div className="h-full bg-purple-500" style={{ width: `${muscleActivation.legs * 100}%` }}></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}