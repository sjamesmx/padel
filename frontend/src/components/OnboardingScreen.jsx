import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, NavLink } from 'react-router-dom';
import { getAuth } from 'firebase/auth';
import { getStorage, ref, uploadBytes, getDownloadURL } from 'firebase/storage';
import axios from 'axios';
import { Loader2, Upload, CheckCircle, AlertCircle, ChevronRight, Play, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import confetti from 'canvas-confetti';
import Header from '../components/Header';

const OnboardingScreen = () => {
  const [videoFiles, setVideoFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [alert, setAlert] = useState(null);
  const fileInputRef = useRef(null);
  const [latestPadelIQ, setLatestPadelIQ] = useState(null);
  const navigate = useNavigate();
  const auth = getAuth();
  const storage = getStorage();

  useEffect(() => {
    // Verificar autenticación
    if (!auth.currentUser) {
      setAlert({ type: 'error', message: 'Por favor, inicia sesión' });
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    }
  }, [navigate, auth]);

  const handleVideoUpload = async (e) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    const file = files[0];
    setIsUploading(true);
    setAlert(null);

    try {
      const userId = auth.currentUser?.uid;
      if (!userId) throw new Error('Usuario no autenticado');

      const timestamp = Date.now();
      const storageRef = ref(storage, `videos/${userId}/${timestamp}.mp4`);
      await uploadBytes(storageRef, file);
      const url = await getDownloadURL(storageRef);

      const response = await axios.post('https://padelyzer-backend-725346030775.us-central1.run.app/api/calculate_padel_iq', {        user_id: userId,
        video_url: url,
      });

      const newVideo = {
        id: `video-${timestamp}`,
        name: file.name.length > 20 ? `${file.name.substring(0, 20)}...` : file.name,
        padelIQ: response.data.padel_iq,
        date: new Date(),
      };

      setVideoFiles((prev) => [...prev, newVideo]);
      setLatestPadelIQ(response.data.padel_iq);
      setAlert({
        type: 'success',
        message: `Padel IQ actualizado: ${response.data.padel_iq}`,
      });

      // Lanzar confeti
      confetti({
        particleCount: 100,
        spread: 70,
        origin: { y: 0.6 },
      });
    } catch (error) {
      console.error('Error processing video:', error);
      setAlert({ type: 'error', message: 'Error al procesar video: ' + error.message });
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  const handleFinish = () => {
    navigate('/dashboard');
  };

  return (
    <div className="flex flex-col min-h-screen bg-black text-white">
      <div className="absolute inset-0 z-0 opacity-5 pointer-events-none">
        <div
          className="absolute inset-0"
          style={{
            backgroundImage: "url('/images/padel-pattern.png')",
            backgroundSize: "300px",
            backgroundRepeat: "repeat",
          }}
        ></div>
      </div>
      <Header title="Subir Videos" />

      <main className="flex-1 p-4 relative z-10">
        <div className="max-w-md mx-auto space-y-6">
          {/* Propuesta de valor */}
          <div className="text-center mb-8">
            <h2 className="text-xl font-bold mb-2">Descubre los puntos ciegos de tu juego</h2>
            <p className="text-gray-400">
              Padelyzer analiza tus videos para que entiendas y puedas mejorar tu técnica.
            </p>
            <div className="mt-2 text-lime-light font-semibold">Análisis. Ciencia. Triunfo.</div>
          </div>

          {/* Alerta */}
          <AnimatePresence>
            {alert && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className={`p-3 rounded-lg flex items-center gap-2 ${
                  alert.type === 'success' ? 'bg-lime-light/20 text-lime-light' : 'bg-red-500/20 text-red-400'
                }`}
              >
                {alert.type === 'success' ? (
                  <CheckCircle className="w-5 h-5" />
                ) : (
                  <AlertCircle className="w-5 h-5" />
                )}
                <span>{alert.message}</span>
                <button onClick={() => setAlert(null)} className="ml-auto">
                  <X className="w-4 h-4" />
                </button>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Botón de subida */}
          <div className="bg-obsidian-wave rounded-xl p-6 text-center">
            <input
              type="file"
              accept="video/*"
              className="hidden"
              onChange={handleVideoUpload}
              ref={fileInputRef}
            />

            <button
              onClick={triggerFileInput}
              disabled={isUploading}
              className={`w-full py-4 px-6 rounded-xl flex items-center justify-center gap-3 transition-all ${
                isUploading
                  ? 'bg-obsidian-wave border border-lime-light/30 text-gray-400'
                  : 'bg-lime-light text-noir-eclipse hover:bg-lime-light/90'
              }`}
            >
              {isUploading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Procesando video...</span>
                </>
              ) : (
                <>
                  <Upload className="w-5 h-5" />
                  <span>Seleccionar video</span>
                </>
              )}
            </button>

            <p className="mt-3 text-sm text-gray-400">Sube un video de tu juego para análisis automático</p>
          </div>

          {/* Lista de videos */}
          <div className="bg-obsidian-wave rounded-xl p-4">
            <h3 className="text-lg font-semibold mb-4">Videos subidos</h3>

            {videoFiles.length === 0 ? (
              <div className="text-center py-8 text-gray-400">
                <p>No hay videos subidos aún.</p>
                <p className="text-sm mt-2">Sube un video para comenzar a recibir análisis.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {videoFiles.map((video, index) => (
                  <motion.div
                    key={video.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className={`p-3 rounded-lg bg-noir-eclipse flex items-center gap-3 ${
                      latestPadelIQ === video.padelIQ ? 'border border-lime-light/30' : ''
                    }`}
                  >
                    <div className="w-12 h-12 bg-obsidian-wave rounded-lg flex items-center justify-center">
                      <Play className="w-5 h-5 text-lime-light" />
                    </div>

                    <div className="flex-1 min-w-0">
                      <p className="font-medium truncate">{video.name}</p>
                      <p className="text-sm text-gray-400">{new Date(video.date).toLocaleDateString()}</p>
                    </div>

                    <div className="flex items-center gap-1 bg-lime-light/10 px-2 py-1 rounded-full">
                      <span className="text-lime-light font-semibold">Padel IQ: {video.padelIQ}</span>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </div>

          {/* Información adicional */}
          <div className="bg-obsidian-wave rounded-xl p-4">
            <h3 className="text-lg font-semibold mb-2">¿Cómo funciona?</h3>
            <ul className="space-y-2 text-sm text-gray-300">
              <li className="flex items-start gap-2">
                <CheckCircle className="w-4 h-4 text-lime-light mt-0.5" />
                <span>Sube videos de tus partidos o prácticas</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle className="w-4 h-4 text-lime-light mt-0.5" />
                <span>Nuestro sistema analiza automáticamente tu técnica</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle className="w-4 h-4 text-lime-light mt-0.5" />
                <span>Recibe un Padel IQ actualizado basado en tu rendimiento</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle className="w-4 h-4 text-lime-light mt-0.5" />
                <span>Obtén recomendaciones personalizadas para mejorar</span>
              </li>
            </ul>
          </div>

          {/* Botón de finalizar */}
          <NavLink
            to="/dashboard"
            className="w-full py-3 px-4 bg-royal-nebula text-white font-medium rounded-xl flex items-center justify-center gap-2 hover:bg-royal-nebula/90 transition-colors"
            onClick={handleFinish}
          >
            <span>Terminar</span>
            <ChevronRight className="w-4 h-4" />
          </NavLink>
        </div>
      </main>
    </div>
  );
};

export default OnboardingScreen;