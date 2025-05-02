import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { auth } from '../FirebaseConfig';
import axios from 'axios';
import {
  Activity,
  BarChart3,
  Upload,
  ChevronRight,
  Zap,
  Clock,
  Calendar,
  TrendingUp,
  Move,
  Target,
  BookOpen,
  Lightbulb,
  Dumbbell,
  Users,
} from 'lucide-react';
import Header from '../components/Header';
import BottomNav from '../components/BottomNav';
import FirstLoginRedirect from '../components/FirstLoginRedirect';
import InfoTooltip from '../components/InfoTooltip';
import Card from '../components/Card';
import MetricCard from '../components/MetricCard';
import ViewSelector from '../components/ViewSelector';
import '../styles/globals.css';

const Dashboard = () => {
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const [activeView, setActiveView] = useState('overview');

  useEffect(() => {
    const unsubscribe = auth.onAuthStateChanged(async (user) => {
      if (!user) {
        setError('No estás autenticado. Por favor, inicia sesión.');
        setTimeout(() => {
          navigate('/login');
        }, 2000);
        setLoading(false);
        return;
      }

      try {
        const response = await axios.get('https://padelyzer-backend-725346030775.us-central1.run.app/api/get_profile', {
          headers: { Authorization: user.uid }
        });
        setProfile(response.data);
      } catch (err) {
        setError('Error al obtener el perfil. Intenta de nuevo.');
      } finally {
        setLoading(false);
      }
    });

    return () => unsubscribe();
  }, [navigate, error]);

  const views = [
    { id: 'overview', label: 'Resumen' },
    { id: 'performance', label: 'Rendimiento' },
    { id: 'training', label: 'Entrenamiento' },
  ];

  if (loading) return <div className="p-4 text-white">Cargando...</div>;
  if (error) return <div className="p-4 text-red-500">{error}</div>;

  return (
    <div className="min-h-screen flex flex-col">
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

      <FirstLoginRedirect />
      <Header title="Padelyzer" />

      <main className="px-4 pt-4 pb-20 relative z-10">
        {/* Encabezado con saludo y mensaje motivacional */}
        <div className="mb-4">
          <h1 className="text-xl font-semibold tracking-tight mb-0">
            Hola, {profile ? profile.name : 'Usuario'}
          </h1>
          <div className="flex items-center">
            <TrendingUp className="w-4 h-4 text-lime-light mr-1" />
            <p className="text-lime-light text-sm font-medium">¡Sigue así! Has mejorado un 5% este mes.</p>
          </div>
        </div>

        {/* Selector de vistas */}
        <ViewSelector views={views} activeView={activeView} onChange={setActiveView} />

        {/* Sección principal - Pádel IQ */}
        <div className="card p-4 mb-4 shadow-apple relative overflow-hidden">
          <div className="absolute top-0 right-0 w-full h-full bg-gradient-to-br from-transparent via-transparent to-lime-light/5 pointer-events-none"></div>

          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <div className="w-14 h-14 bg-gradient-to-br from-purple-500/40 to-lime-light/40 rounded-2xl flex items-center justify-center shadow-sm">
                <span className="text-xl font-semibold text-white">{profile ? profile.padel_iq : '87'}</span>
              </div>
              <div>
                <div className="flex items-center gap-1">
                  <h3 className="font-semibold text-lg mb-0">Pádel IQ</h3>
                  <InfoTooltip content="El Pádel IQ es una medida de tu nivel general como jugador, basada en tus habilidades técnicas, tácticas y físicas." />
                </div>
                <p className="text-xs text-gray-400 capitalize">{profile ? profile.fuerza : 'Fuerza'}</p>
                <div className="flex items-center mt-0.5 text-lime-light text-xs">
                  <TrendingUp className="w-3 h-3 mr-1" />
                  <span>+5% último mes</span>
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-4 gap-2 mb-3">
            <div className="bg-obsidian-wave rounded-xl p-2 text-center shadow-sm">
              <div className="flex justify-center mb-0.5">
                <Zap className="w-4 h-4 text-yellow-400" />
              </div>
              <p className="text-lg font-semibold mb-0">82</p>
              <p className="text-[10px] text-gray-400">Golpeo</p>
            </div>
            <div className="bg-obsidian-wave rounded-xl p-2 text-center shadow-sm">
              <div className="flex justify-center mb-0.5">
                <Move className="w-4 h-4 text-blue-400" />
              </div>
              <p className="text-lg font-semibold mb-0">78</p>
              <p className="text-[10px] text-gray-400">Movimiento</p>
            </div>
            <div className="bg-obsidian-wave rounded-xl p-2 text-center shadow-sm">
              <div className="flex justify-center mb-0.5">
                <Activity className="w-4 h-4 text-green-400" />
              </div>
              <p className="text-lg font-semibold mb-0">91</p>
              <p className="text-[10px] text-gray-400">Técnica</p>
            </div>
            <div className="bg-obsidian-wave rounded-xl p-2 text-center shadow-sm">
              <div className="flex justify-center mb-0.5">
                <BarChart3 className="w-4 h-4 text-purple-400" />
              </div>
              <p className="text-lg font-semibold mb-0">85</p>
              <p className="text-[10px] text-gray-400">Resultados</p>
            </div>
          </div>

          <Link
            to="/player"
            className="w-full py-2 px-3 bg-lime-light text-noir-eclipse font-medium rounded-xl flex items-center justify-center shadow-sm hover:shadow-md transition-all text-sm"
          >
            <span>Ver mi progreso completo</span>
            <ChevronRight className="w-4 h-4 ml-1" />
          </Link>
        </div>

        {/* Accesos rápidos */}
        <div className="mb-4">
          <h3 className="font-semibold text-base mb-3">Accesos rápidos</h3>
          <div className="grid grid-cols-4 gap-2">
            <Link to="/player" className="bg-obsidian-wave rounded-xl p-2 text-center shadow-sm">
              <div className="w-8 h-8 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-1">
                <Activity className="w-4 h-4 text-green-500" />
              </div>
              <p className="text-[10px] text-gray-300">Progreso</p>
            </Link>

            <Link to="/analyze" className="bg-obsidian-wave rounded-xl p-2 text-center shadow-sm">
              <div className="w-8 h-8 bg-lime-light/20 rounded-full flex items-center justify-center mx-auto mb-1">
                <Upload className="w-4 h-4 text-lime-light" />
              </div>
              <p className="text-[10px] text-gray-300">Analizar</p>
            </Link>

            <Link to="/matches" className="bg-obsidian-wave rounded-xl p-2 text-center shadow-sm">
              <div className="w-8 h-8 bg-blue-500/20 rounded-full flex items-center justify-center mx-auto mb-1">
                <Calendar className="w-4 h-4 text-blue-500" />
              </div>
              <p className="text-[10px] text-gray-300">Partidos</p>
            </Link>

            <Link to="/learn" className="bg-obsidian-wave rounded-xl p-2 text-center shadow-sm">
              <div className="w-8 h-8 bg-purple-500/20 rounded-full flex items-center justify-center mx-auto mb-1">
                <BookOpen className="w-4 h-4 text-purple-500" />
              </div>
              <p className="text-[10px] text-gray-300">Aprender</p>
            </Link>
          </div>
        </div>

        {/* Nuevos módulos */}
        <div className="grid grid-cols-2 gap-3 mb-4">
          <Link to="/training">
            <Card className="p-3">
              <div className="flex flex-col items-center text-center">
                <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center mb-1">
                  <Dumbbell className="h-5 w-5 text-blue-600" />
                </div>
                <h3 className="font-medium text-sm">Entrenamiento</h3>
                <p className="text-[10px] text-gray-500">Mejora tu juego</p>
              </div>
            </Card>
          </Link>

          <Link to="/matches/finder">
            <Card className="p-3">
              <div className="flex flex-col items-center text-center">
                <div className="h-10 w-10 rounded-full bg-red-100 flex items-center justify-center mb-1">
                  <Users className="h-5 w-5 text-red-600" />
                </div>
                <h3 className="font-medium text-sm">Matches</h3>
                <p className="text-[10px] text-gray-500">Encuentra rivales</p>
              </div>
            </Card>
          </Link>
        </div>

        {/* Objetivos y metas */}
        <div className="card p-4 mb-4 shadow-apple">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Target className="w-5 h-5 text-lime-light" />
              <h3 className="font-semibold text-base">Mis objetivos</h3>
            </div>
            <Link to="/goals" className="text-lime-light text-xs">
              Ver todos
            </Link>
          </div>

          <div className="space-y-2 mb-3">
            <div className="bg-obsidian-wave rounded-xl p-2">
              <div className="flex justify-between items-center mb-1">
                <div className="flex items-center gap-2">
                  <div className="w-7 h-7 rounded-full bg-yellow-400/20 flex items-center justify-center">
                    <Zap className="w-4 h-4 text-yellow-400" />
                  </div>
                  <span className="font-medium text-sm">Aumentar velocidad de smash</span>
                </div>
                <span className="text-xs text-lime-light">75%</span>
              </div>
              <div className="h-1 bg-noir-eclipse/50 rounded-full overflow-hidden">
                <div className="h-full bg-lime-light" style={{ width: "75%" }}></div>
              </div>
              <div className="flex justify-between mt-0.5">
                <span className="text-[10px] text-gray-400">Actual: 90 km/h</span>
                <span className="text-[10px] text-gray-400">Meta: 95 km/h</span>
              </div>
            </div>

            <div className="bg-obsidian-wave rounded-xl p-2">
              <div className="flex justify-between items-center mb-1">
                <div className="flex items-center gap-2">
                  <div className="w-7 h-7 rounded-full bg-blue-400/20 flex items-center justify-center">
                    <Activity className="w-4 h-4 text-blue-400" />
                  </div>
                  <span className="font-medium text-sm">Mejorar precisión de revés</span>
                </div>
                <span className="text-xs text-lime-light">40%</span>
              </div>
              <div className="h-1 bg-noir-eclipse/50 rounded-full overflow-hidden">
                <div className="h-full bg-lime-light" style={{ width: "40%" }}></div>
              </div>
              <div className="flex justify-between mt-0.5">
                <span className="text-[10px] text-gray-400">Actual: 68%</span>
                <span className="text-[10px] text-gray-400">Meta: 80%</span>
              </div>
            </div>
          </div>

          <Link
            to="/goals/new"
            className="w-full py-2 px-3 bg-obsidian-wave border border-royal-nebula/30 text-white rounded-xl flex items-center justify-center text-sm"
          >
            <span>Añadir nuevo objetivo</span>
            <ChevronRight className="w-4 h-4 ml-1" />
          </Link>
        </div>

        {/* Sección de acciones */}
        <div className="space-y-3 mb-4">
          <div className="bg-gradient-to-r from-royal-nebula/30 to-lime-light/30 rounded-xl p-4 shadow-apple">
            <div className="flex items-center">
              <div className="flex-1">
                <h3 className="font-semibold text-base text-white mb-1">Analizar mi juego</h3>
                <p className="text-sm text-gray-200 mb-2">Sube un vídeo para obtener un análisis completo</p>
                <Link
                  to="/analyze"
                  className="inline-flex items-center px-3 py-2 bg-lime-light text-noir-eclipse rounded-xl text-sm font-medium shadow-sm hover:shadow-md transition-all"
                >
                  <Upload className="w-4 h-4 mr-1" />
                  Analizar video
                </Link>
              </div>
              <div className="w-20 h-20 flex items-center justify-center">
                <div className="w-16 h-16 bg-royal-nebula/30 rounded-xl flex items-center justify-center">
                  <Upload className="w-6 h-6 text-lime-light" />
                </div>
              </div>
            </div>
          </div>

          <div className="bg-obsidian-wave rounded-xl p-4 shadow-apple border border-royal-nebula/20">
            <div className="flex items-center">
              <div className="flex-1">
                <h3 className="font-semibold text-base mb-1">Registrar partido</h3>
                <p className="text-xs text-gray-400 mb-2">Programa y analiza tus partidos</p>
                <Link
                  to="/matches/new"
                  className="inline-flex items-center px-3 py-2 bg-obsidian-wave border border-royal-nebula/30 text-white rounded-xl text-sm font-medium shadow-sm hover:shadow-md transition-all"
                >
                  <Calendar className="w-4 h-4 mr-1" />
                  Registrar partido
                </Link>
              </div>
              <div className="w-14 h-14 bg-obsidian-wave rounded-xl flex items-center justify-center">
                <Calendar className="w-6 h-6 text-royal-nebula" />
              </div>
            </div>
          </div>
        </div>

        {/* Próximo partido */}
        <div className="card p-4 mb-4 shadow-apple">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Calendar className="w-5 h-5 text-blue-400" />
              <h3 className="font-semibold text-base">Próximo partido</h3>
            </div>
          </div>

          <div className="bg-obsidian-wave rounded-xl p-3">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <div className="w-9 h-9 rounded-xl bg-blue-400/20 flex items-center justify-center">
                  <Calendar className="w-5 h-5 text-blue-400" />
                </div>
                <div>
                  <p className="font-medium text-sm">vs. Club Padel Madrid</p>
                  <div className="flex items-center gap-1 text-gray-400 text-xs mt-0.5">
                    <Clock className="w-3 h-3" />
                    <span>Mañana, 18:30</span>
                  </div>
                </div>
              </div>
              <span className="px-2 py-1 bg-blue-400/20 text-blue-400 rounded-full text-xs">Amistoso</span>
            </div>

            <div className="flex justify-between">
              <Link to="/matches/upcoming" className="text-lime-light text-xs flex items-center">
                <span>Ver detalles</span>
                <ChevronRight className="w-4 h-4 ml-1" />
              </Link>
              <Link to="/matches/prepare" className="text-lime-light text-xs flex items-center">
                <span>Preparar partido</span>
                <ChevronRight className="w-4 h-4 ml-1" />
              </Link>
            </div>
          </div>
        </div>

        {/* Sección de actividad */}
        <div className="grid grid-cols-2 gap-3 mb-4">
          <MetricCard
            title="Actividad"
            icon={<Activity className="w-5 h-5" />}
            iconColor="blue-500"
            className="p-4"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-gray-400">Hoy</span>
            </div>
            <p className="text-xl font-semibold">42 min</p>
            <div className="mt-1">
              <div className="h-1 bg-noir-eclipse rounded-full overflow-hidden">
                <div className="h-full bg-blue-500" style={{ width: "70%" }}></div>
              </div>
              <div className="flex justify-between mt-0.5">
                <span className="text-[10px] text-gray-400">0 min</span>
                <span className="text-[10px] text-gray-400">Meta: 60 min</span>
              </div>
            </div>
          </MetricCard>

          <MetricCard
            title="Rendimiento"
            icon={<Zap className="w-5 h-5" />}
            iconColor="lime-light"
            className="p-4"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-gray-400">Esta semana</span>
            </div>
            <div className="flex items-center">
              <p className="text-xl font-semibold">87%</p>
              <div className="ml-auto relative w-10 h-10">
                <svg className="w-full h-full" viewBox="0 0 36 36">
                  <circle cx="18" cy="18" r="15" fill="none" stroke="#0A0C10" strokeWidth="3" />
                  <circle
                    cx="18"
                    cy="18"
                    r="15"
                    fill="none"
                    stroke="#B9FF66"
                    strokeWidth="3"
                    strokeDasharray="94.2 100"
                    strokeDashoffset="25"
                    transform="rotate(-90 18 18)"
                  />
                </svg>
              </div>
            </div>
            <Link to="/player" className="text-[10px] text-lime-light mt-1 inline-block">
              Ver progreso detallado
            </Link>
          </MetricCard>
        </div>

        {/* Consejos del día */}
        <div className="card p-4 mb-4 shadow-apple">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Lightbulb className="w-5 h-5 text-yellow-400" />
              <h3 className="font-semibold text-base">Consejo del día</h3>
            </div>
            <Link to="/learn/tips" className="text-lime-light text-xs">
              Ver más
            </Link>
          </div>

          <div className="bg-obsidian-wave rounded-xl p-3">
            <div className="flex items-start gap-2">
              <div className="mt-1">
                <div className="w-9 h-9 rounded-xl bg-yellow-400/20 flex items-center justify-center">
                  <Lightbulb className="w-5 h-5 text-yellow-400" />
                </div>
              </div>
              <div>
                <h4 className="font-medium text-sm">Mejora tu revés</h4>
                <p className="text-xs text-gray-300 mt-0.5">
                  Para un revés más potente, asegúrate de rotar bien las caderas y transferir el peso del cuerpo
                  hacia adelante durante el golpe.
                </p>
                <Link
                  to="/learn/techniques/backhand"
                  className="text-lime-light text-xs flex items-center mt-1"
                >
                  <span>Ver técnica completa</span>
                  <ChevronRight className="w-4 h-4 ml-1" />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </main>

      <BottomNav />
    </div>
  );
};

export default Dashboard;