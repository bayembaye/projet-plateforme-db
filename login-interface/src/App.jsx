import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom"; // Import de useNavigate
import "./App.css";
import img1 from "./assets/img1.jpg";
import img2 from "./assets/img2.jpg";
import img3 from "./assets/img3.jpg";
import Dashboard from "./pages/Dashboard";


function App() {
  const navigate = useNavigate(); // Hook pour la navigationnavigation
  const images = [img1, img2, img3];
  const [currentImage, setCurrentImage] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentImage((prev) => (prev + 1) % images.length);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="app">
      <div
        className="background-slider"
        style={{ backgroundImage: `url(${images[currentImage]})` }}
      ></div>

      <div className="login-container">
        <div className="login-box">
          <h2 className="login-title">connectez-vous</h2>
          <input type="text" placeholder="Nom d'utilisateur" className="login-input" />
          <input type="password" placeholder="Mot de passe" className="login-input" />
          <button className="login-button">se connecter</button>

          {/* Bouton pour aller vers le Dashboard */}
          <button className="dashboard-button" onClick={() => navigate("/dashboard")}>
            Aller au Dashboard
          </button>

          <div className="login-links">
            <a href="#" className="forgot-password">Mot de passe oublié ?</a>
            <a href="#" className="signup">S'inscrire</a>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
