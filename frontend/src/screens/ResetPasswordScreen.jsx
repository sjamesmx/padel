import { useState } from 'react';
import { sendPasswordResetEmail } from 'firebase/auth';
import { auth } from '../FirebaseConfig';
import '../styles/globals.css';

const ResetPasswordScreen = () => {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [emailError, setEmailError] = useState('');

  const validateEmail = (email) => {
    if (!email) return 'El correo electrónico es obligatorio';
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) return 'Formato de correo electrónico inválido';
    return '';
  };

  const handleEmailBlur = () => {
    setEmailError(validateEmail(email));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const emailValidation = validateEmail(email);
    if (emailValidation) {
      setEmailError(emailValidation);
      return;
    }

    setError('');
    setMessage('');
    setIsLoading(true);

    try {
      await sendPasswordResetEmail(auth, email);
      setMessage('Enlace enviado a tu correo');
    } catch (err) {
      setError('Error al enviar el enlace. Verifica tu correo.');
    } finally {
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
            Recupera tu cuenta en <span className="text-lime-light">Padelyzer</span>
          </h1>
          <p className="mt-2 text-gray-400">Ingresa tu correo para recibir un enlace de restablecimiento</p>
        </div>

        {message && (
          <div className="mb-6 p-4 bg-green-900/30 border border-green-500/30 rounded-xl text-green-400 text-sm flex items-center">
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
            </svg>
            <span>{message}</span>
          </div>
        )}

        {error && (
          <div className="mb-6 p-4 bg-red-900/30 border border-red-500/30 rounded-xl text-red-400 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label htmlFor="email" className="block text-sm font-medium text-gray-200">
              Correo electrónico
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
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
                autoFocus
                required
                aria-label="Correo electrónico"
              />
            </div>
            {emailError && <p className="text-red-400 text-xs mt-1">{emailError}</p>}
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className={
              isLoading
                ? "w-full py-3.5 px-4 bg-lime-light text-noir-eclipse font-medium rounded-xl transition-all flex items-center justify-center shadow-sm hover:shadow-md opacity-70"
                : "w-full py-3.5 px-4 bg-lime-light hover:bg-lime-light/90 text-noir-eclipse font-medium rounded-xl transition-all flex items-center justify-center shadow-sm hover:shadow-md"
            }
          >
            {isLoading ? (
              <>
                <svg className="animate-spin -ml-1 mr-2 h-5 w-5 text-noir-eclipse" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Enviando...
              </>
            ) : (
              "Enviar enlace"
            )}
          </button>

          <div className="text-center mt-4">
            <p className="text-base text-gray-400">
              <a href="/login" className="text-lime-light hover:underline transition-colors">
                Volver al inicio de sesión
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

export default ResetPasswordScreen;