import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { auth } from '../FirebaseConfig';
import { storage, db } from '../FirebaseConfig';
import { ref, uploadBytes, getDownloadURL } from 'firebase/storage';
import { doc, updateDoc } from 'firebase/firestore';
import '../styles/globals.css';

const OnboardingScreen = () => {
  const [videos, setVideos] = useState({
    derecha: null,
    reves: null,
    volea: null,
    bandeja: null,
    smash: null,
    globo: null,
    saque: null,       // Nuevo golpe
    bandaPared: null, // Nuevo golpe
    vibora: null,     // Nuevo golpe
  });
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const unsubscribe = auth.onAuthStateChanged((user) => {
      if (!user) {
        navigate('/login');
      }
    });
    return () => unsubscribe();
  }, [navigate]);

  const handleFileChange = (type) => (e) => {
    const file = e.target.files[0];
    if (file) {
      setVideos((prev) => ({ ...prev, [type]: file }));
    }
  };

  const handleSubmit = async () => {
    setUploading(true);
    setError('');

    try {
      const user = auth.currentUser;
      if (!user) throw new Error('Usuario no autenticado');

      // Subir cada video a Firebase Storage y obtener las URLs
      const videoUrls = {};
      for (const [type, file] of Object.entries(videos)) {
        if (file) {
          const storageRef = ref(storage, `videos/${user.uid}/${type}.mp4`);
          await uploadBytes(storageRef, file);
          const url = await getDownloadURL(storageRef);
          videoUrls[type] = url;
        }
      }

      // Guardar las URLs en Firestore
      const userRef = doc(db, 'profiles', user.uid);
      await updateDoc(userRef, { videos: videoUrls });

      // Redirigir al Dashboard
      navigate('/dashboard');
    } catch (err) {
      setError('Error al subir los videos. Intenta de nuevo.');
      console.error(err);
    } finally {
      setUploading(false);
    }
  };

  const videoTypes = [
    { key: 'derecha', label: 'Derecha' },
    { key: 'reves', label: 'Revés' },
    { key: 'volea', label: 'Volea' },
    { key: 'bandeja', label: 'Bandeja' },
    { key: 'smash', label: 'Smash' },
    { key: 'globo', label: 'Globo' },
    { key: 'saque', label: 'Saque' },           // Nuevo golpe
    { key: 'bandaPared', label: 'Banda de Pared' }, // Nuevo golpe
    { key: 'vibora', label: 'Víbora' },         // Nuevo golpe
  ];

  return (
    <div className="min-h-screen flex flex-col">
      <div className="flex-1 flex flex-col justify-center px-6 py-12">
        <div className="mb-10 text-center">
          <img
            src="/images/Padelyzer-Isotipo-Blanco.png"
            alt="Padelyzer"
            className="mx-auto mb-8 w-32 h-32 object-contain"
          />
          <h1 className="text-3xl font-semibold tracking-tight text-white">
            Configura tu <span className="text-lime-light">Padel IQ</span>
          </h1>
          <p className="mt-2 text-gray-400">
            Sube un video para cada tipo de golpe para que podamos evaluar tu nivel de juego.
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-900/30 border border-red-500/30 rounded-xl text-red-400 text-sm">
            {error}
          </div>
        )}

        <div className="space-y-4">
          {videoTypes.map(({ key, label }) => (
            <div key={key} className="space-y-2">
              <label className="block text-sm font-medium text-gray-200">{label}</label>
              <input
                type="file"
                accept="video/*"
                onChange={handleFileChange(key)}
                className="w-full p-3 bg-obsidian-wave border border-royal-nebula/40 rounded-xl text-white text-sm"
              />
            </div>
          ))}
        </div>

        <button
          onClick={handleSubmit}
          disabled={uploading || !Object.values(videos).some((file) => file)}
          className={`w-full py-3 px-4 mt-6 bg-lime-light text-noir-eclipse font-medium rounded-xl flex items-center justify-center shadow-sm hover:shadow-md transition-all ${
            uploading ? 'opacity-70' : ''
          }`}
        >
          {uploading ? 'Subiendo videos...' : 'Evaluar mi nivel'}
        </button>
      </div>
    </div>
  );
};

export default OnboardingScreen;