import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import LoginScreen from './screens/LoginScreen';
import SignupScreen from './screens/SignupScreen';
import ResetPasswordScreen from './screens/ResetPasswordScreen';
import Dashboard from './screens/Dashboard';
import SplashScreen from './screens/SplashScreen';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/login" element={<LoginScreen />} />
          <Route path="/signup" element={<SignupScreen />} />
          <Route path="/reset-password" element={<ResetPasswordScreen />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/" element={<SplashScreen />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;