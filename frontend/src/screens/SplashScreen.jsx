import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import '../styles/globals.css';

const SplashScreen = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const timer = setTimeout(() => {
      navigate('/login');
    }, 2000);

    return () => clearTimeout(timer);
  }, [navigate]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center">
      {/* Fondo sutil con patrón de pádel */}
      <div className="absolute inset-0 z-0 opacity-5 pointer-events-none">
        <div
          className="absolute inset-0"
          style={{
            backgroundImage: "url('/images/padel-pattern.png')",
            backgroundSize: "300px",
            backgroundRepeat: "repeat",
            opacity: 0.05,
          }}
        ></div>
      </div>

      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="relative z-10 flex flex-col items-center"
      >
        <div className="w-32 h-32 bg-lime-light rounded-2xl flex items-center justify-center mb-6 shadow-apple">
          <img
            src="/images/Padelyzer-Isotipo-Blanco.png"
            alt="Padelyzer"
            className="w-20 h-20 invert"
          />
        </div>

        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.5 }}
          className="text-3xl font-bold text-white tracking-tight"
        >
          Padelyzer
        </motion.h1>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6, duration: 0.5 }}
          className="text-gray-400 mt-2"
        >
          Tu asistente personal de pádel
        </motion.p>
      </motion.div>
    </div>
  );
};

export default SplashScreen;