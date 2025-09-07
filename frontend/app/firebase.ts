import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
      apiKey: "AIzaSyAksht4ON0zfE0HW6XhcJxHu0WwJWCc5mE",
      authDomain: "url-shortener-abadb.firebaseapp.com",
      projectId: "url-shortener-abadb",
      storageBucket: "url-shortener-abadb.firebasestorage.app",
      messagingSenderId: "177262317164",
      appId: "1:177262317164:web:d6ecbe0e5f8cefe7dc1249",
      measurementId: "G-74PTBDNNBL"
    };
    
// Initialize Firebase
const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);