import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { auth, db } from '../FirebaseConfig';
import { doc, getDoc } from 'firebase/firestore';

export default function FirstLoginRedirect() {
  const navigate = useNavigate();
  const [isFirstLogin, setIsFirstLogin] = useState(true);

  useEffect(() => {
    const unsubscribe = auth.onAuthStateChanged(async (user) => {
      if (!user) return;

      const userRef = doc(db, 'profiles', user.uid);
      const userDoc = await getDoc(userRef);
      const hasVideos = userDoc.exists() && userDoc.data().videos;

      if (!hasVideos) {
        localStorage.setItem("hasLoggedInBefore", "true");
        navigate("/onboarding");
      } else {
        setIsFirstLogin(false);
      }
    });

    return () => unsubscribe();
  }, [navigate]);

  return null;
}