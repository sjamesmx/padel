const functions = require('firebase-functions');
const admin = require('firebase-admin');
admin.initializeApp();

exports.createUserDocument = functions.auth.user().onCreate(async (user) => {
  const db = admin.firestore();
  await db.collection('users').doc(user.uid).set({
    email: user.email,
    createdAt: admin.firestore.FieldValue.serverTimestamp(),
    trialEnd: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000), // Trial de 14 días
    referrals: 0,
    plan: 'free',
    padel_iq: 0,
    fuerza: 0
  });
});