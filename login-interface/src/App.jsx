import React, { useState, useEffect } from "react";
import { FormControl,Button,FormGroup,InputLabel,FormHelperText,Input,Snackbar,CircularProgress } from "@mui/material";
import axios from "axios" ;
import { useNavigate } from "react-router-dom"; // Import de useNavigate
import "./App.css";
import img1 from "./assets/img1.jpg";
import img2 from "./assets/img2.jpg";
import img3 from "./assets/img3.jpg";
import Alert1 from "./components/Alert1";

function App() {
  const navigate = useNavigate(); // Hook pour la navigationnavigation
  const images = [img1, img2, img3];
  const [currentImage, setCurrentImage] = useState(0);
  const [email,setEMail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(false);
  const [submit,setSubmit] = useState(false);
  const handleClose = (event, reason) => {
          if (reason === 'clickaway') {
            return;
          }
      
          setError(false);
        };
  useEffect(() => {
    console.log(email);
    const interval = setInterval(() => {
      setCurrentImage((prev) => (prev + 1) % images.length);
    }, 5000);
    return () => clearInterval(interval);
  }, [email,setEMail]);
  const handleSubmit = async (e) => {
    e.preventDefault(); // Evite le rechargement de la page au clic sur le bouton
    setSubmit(true);
    const url ='http://localhost:8000' ;
    if(email === "admin" && password === "admin"){
      navigate('/dashboard');
      axios({
        url: `${url}/api/login/email=${email}/password=${password}`, // exemple de route pour se logger 
        method:'POST',
      }).then(result => {
        console.log(result);
        setError(null);
      })
      .catch(error => {
        setError(error.message);
        setSubmit(false);
      });
    } else {
      setError(true);
      setSubmit(false);
      // alert("Identifiants incorrects");
    }
  }
  return (
    <div className="app">
      <Alert1 open={error} handleClose={handleClose} />
      <div
        className="background-slider"
        style={{ backgroundImage: `url(${images[currentImage]})` }}
      ></div>
      <div className="login-container">
        <div className="login-box">
          <h2 className="login-title">connectez-vous</h2>
          <input  required type="text" placeholder="Nom d'utilisateur" name='email' className="login-input" onChange={(e) => setEMail(e.target.value)}/>
          <input required type="password" placeholder="Mot de passe" name='password' className="login-input" onChange={(e)=> setPassword(e.target.value)} />
          {/* Bouton pour aller vers le Dashboard */}
          <Button variant="contained" color="primary" onClick={handleSubmit}>
            Se Connecter
            {submit ? <CircularProgress size={30} color="primary" /> : null}
          </Button>
          <Button variant="contained" color="warning" onClick={()=> navigate('/dashboard')}>Dashboard</Button>
          <div className="login-links">
            <a href="#" className="forgot-password">Mot de passe oublié ?</a>
            <a href="" color="warning" className="signup" onClick={()=> navigate('/register')}>S'inscrire</a>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
