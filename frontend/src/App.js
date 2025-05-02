import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { getAuth, onAuthStateChanged } from 'firebase/auth';
import LoginScreen from './screens/LoginScreen';
import SignupScreen from './screens/SignupScreen';
import ResetPasswordScreen from './screens/ResetPasswordScreen';
import OnboardingScreen from './components/OnboardingScreen';
import Dashboard from './screens/Dashboard';
import SplashScreen from './screens/SplashScreen';
import ClubsScreen from './components/ClubsScreen';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const auth = getAuth();

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
      setLoading(false);
    });
    return () => unsubscribe();
  }, [auth]);

  if (loading) return <div>Loading...</div>;

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/login" element={!user ? <LoginScreen /> : <Navigate to="/onboarding" />} />
          <Route path="/signup" element={!user ? <SignupScreen /> : <Navigate to="/onboarding" />} />
          <Route path="/reset-password" element={!user ? <ResetPasswordScreen /> : <Navigate to="/onboarding" />} />
          <Route path="/onboarding" element={user ? <OnboardingScreen /> : <Navigate to="/login" />} />
          <Route path="/dashboard" element={user ? <Dashboard /> : <Navigate to="/login" />} />
          <Route path="/" element={<SplashScreen />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;