import { useState, useEffect } from 'react';
import { signInWithEmailAndPassword, signInWithPopup, GoogleAuthProvider, FacebookAuthProvider } from 'firebase/auth';
import { auth } from '../FirebaseConfig';
import { useNavigate } from 'react-router-dom';
import { Eye, EyeOff, Loader2, Mail, Lock, Check } from 'lucide-react';
import '../styles/globals.css';

const LoginScreen = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [emailError, setEmailError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const emailInput = document.getElementById('email');
    if (emailInput) {
      emailInput.focus();
    }
  }, []);

  useEffect(() => {
    const rememberedEmail = localStorage.getItem('rememberedEmail');
    if (rememberedEmail) {
      setEmail(rememberedEmail);
      setRememberMe(true);
    }
  }, []);

  useEffect(() => {
    const unsubscribe = auth.onAuthStateChanged((user) => {
      if (user && success) {
        setTimeout(() => {
          navigate('/dashboard');
        }, 2000);
      }
    });

    return () => unsubscribe();
  }, [success, navigate]);

  const validateEmail = (email) => {
    if (!email) return 'El correo electrónico es obligatorio';
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) return 'Formato de correo electrónico inválido';
    return '';
  };

  const validatePassword = (password) => {
    if (!password) return 'La contraseña es obligatoria';
    if (password.length < 6) return 'La contraseña debe tener al menos 6 caracteres';
    return '';
  };

  const handleEmailBlur = () => {
    setEmailError(validateEmail(email));
  };

  const handlePasswordBlur = () => {
    setPasswordError(validatePassword(password));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const emailValidation = validateEmail(email);
    const passwordValidation = validatePassword(password);

    if (emailValidation) {
      setEmailError(emailValidation);
      return;
    }

    if (passwordValidation) {
      setPasswordError(passwordValidation);
      return;
    }

    setError('');
    setIsLoading(true);

    try {
      await signInWithEmailAndPassword(auth, email, password);
      setSuccess(true);

      if (rememberMe) {
        localStorage.setItem('rememberedEmail', email);
      } else {
        localStorage.removeItem('rememberedEmail');
      }
    } catch (err) {
      setError('Correo o contraseña inválidos');
      setIsLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    setIsLoading(true);
    const provider = new GoogleAuthProvider();
    try {
      await signInWithPopup(auth, provider);
      setSuccess(true);
    } catch (err) {
      setError('Error al iniciar sesión con Google');
      setIsLoading(false);
    }
  };

  const handleFacebookLogin = async () => {
    setIsLoading(true);
    const provider = new FacebookAuthProvider();
    try {
      await signInWithPopup(auth, provider);
      setSuccess(true);
    } catch (err) {
      setError('Error al iniciar sesión con Facebook');
      setIsLoading(false);
    }
  };

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
            Bienvenido a <span className="text-lime-light">Padelyzer</span>
          </h1>
          <p className="mt-2 text-gray-400">Inicia sesión para continuar</p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-900/30 border border-red-500/30 rounded-xl text-red-400 text-sm">
            {error}
          </div>
        )}

        {success && (
          <div className="mb-6 p-4 bg-green-900/30 border border-green-500/30 rounded-xl text-green-400 text-sm flex items-center">
            <Check className="w-5 h-5 mr-2" />
            <span>¡Inicio de sesión exitoso! Redirigiendo...</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label htmlFor="email" className="block text-sm font-medium text-gray-200">
              Correo electrónico
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Mail className="h-5 w-5 text-gray-400" />
              </div>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                onBlur={handleEmailBlur}
                className={`w-full pl-10 pr-4 py-3.5 bg-obsidian-wave border ${
                  emailError ? "border-red-500" : "border-royal-nebula/40"
                } rounded-xl focus:outline-none focus:ring-2 focus:ring-lime-light/50 text-white`}
                placeholder="tu@email.com"
                autoComplete="email"
                required
                aria-label="Correo electrónico"
              />
            </div>
            {emailError && <p className="text-red-400 text-xs mt-1">{emailError}</p>}
          </div>

          <div className="space-y-2">
            <label htmlFor="password" className="block text-sm font-medium text-gray-200">
              Contraseña
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Lock className="h-5 w-5 text-gray-400" />
              </div>
              <input
                id="password"
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onBlur={handlePasswordBlur}
                className={`w-full pl-10 pr-10 py-3.5 bg-obsidian-wave border ${
                  passwordError ? "border-red-500" : "border-royal-nebula/40"
                } rounded-xl focus:outline-none focus:ring-2 focus:ring-lime-light/50 text-white`}
                placeholder="••••••••"
                autoComplete="current-password"
                required
                aria-label="Contraseña"
              />
              <button
                type="button"
                className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white transition-colors"
                onClick={() => setShowPassword(!showPassword)}
                aria-label={showPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
            {passwordError && <p className="text-red-400 text-xs mt-1">{passwordError}</p>}
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <input
                id="remember-me"
                name="remember-me"
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                className="h-4 w-4 text-lime-light focus:ring-lime-light border-gray-600 rounded bg-obsidian-wave"
              />
              <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-300">
                Recordarme
              </label>
            </div>
            <a
              href="/reset-password"
              className="text-sm text-lime-light hover:underline transition-colors"
            >
              ¿Olvidaste tu contraseña?
            </a>
          </div>

          <button
            type="submit"
            disabled={isLoading || success}
            className={
              isLoading
                ? "w-full py-3.5 px-4 bg-lime-light text-noir-eclipse font-medium rounded-xl transition-all flex items-center justify-center shadow-sm hover:shadow-md opacity-70"
                : success
                ? "w-full py-3.5 px-4 bg-lime-light text-noir-eclipse font-medium rounded-xl transition-all flex items-center justify-center shadow-sm hover:shadow-md opacity-70"
                : "w-full py-3.5 px-4 bg-lime-light hover:bg-lime-light/90 text-noir-eclipse font-medium rounded-xl transition-all flex items-center justify-center shadow-sm hover:shadow-md"
            }
          >
            {isLoading ? (
              <>
                <Loader2 className="animate-spin -ml-1 mr-2 h-5 w-5 text-noir-eclipse" />
                Iniciando sesión...
              </>
            ) : success ? (
              <>
                <Check className="-ml-1 mr-2 h-5 w-5 text-noir-eclipse" />
                ¡Sesión iniciada!
              </>
            ) : (
              "Iniciar sesión"
            )}
          </button>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-700"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 text-gray-400">O continúa con</span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <button
              type="button"
              onClick={handleGoogleLogin}
              disabled={isLoading || success}
              className={
                isLoading || success
                  ? "flex items-center justify-center py-3 px-4 border border-royal-nebula/40 rounded-xl text-white opacity-70"
                  : "flex items-center justify-center py-3 px-4 border border-royal-nebula/40 rounded-xl hover:bg-obsidian-wave transition-colors text-white"
              }
            >
             <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
    <path
    fill="#4285F4"
    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
  />
  <path
    fill="#34A853"
    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
  />
  <path
    fill="#FBBC05"
    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
  />
  <path
    fill="#EA4335"
    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
  />
</svg>
              Google
            </button>
            <button
              type="button"
              onClick={handleFacebookLogin}
              disabled={isLoading || success}
              className={
                isLoading || success
                  ? "flex items-center justify-center py-3 px-4 border border-royal-nebula/40 rounded-xl text-white opacity-70"
                  : "flex items-center justify-center py-3 px-4 border border-royal-nebula/40 rounded-xl hover:bg-obsidian-wave transition-colors text-white"
              }
            >
              <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                <path
                  fillRule="evenodd"
                  d="M22 12c0-5.523-4.477-10-10-10S2 6.477 2 12c0 4.991 3.657 9.128 8.438 9.878v-6.987h-2.54V12h2.54V9.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V12h2.773l-.443 2.89h-2.33v6.988C18.343 21.128 22 16.991 22 12z"
                  clipRule="evenodd"
                />
              </svg>
              Facebook
            </button>
          </div>

          <div className="text-center mt-4">
            <p className="text-base text-gray-400">
              ¿No tienes una cuenta?{" "}
              <a href="/signup" className="text-lime-light hover:underline transition-colors">
                Regístrate
              </a>
            </p>
          </div>
        </form>
      </div>

      <div className="p-6 text-center">
        <p className="text-sm text-gray-400">© 2025 Padelyzer. Todos los derechos reservados.</p>
      </div>
    </div>
  );
};

export default LoginScreen;