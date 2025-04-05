import React, { useState, useRef,} from "react";
import Button from 'react-bootstrap/Button';
import { Form, Image, Spinner } from "react-bootstrap";
import './Register.css' ;
const Register = () => {
    const [user, setUser] = useState("");
    const [pwd, setPwd] = useState("");
    const [submitted, setSubmitted] = useState(false);
    const [errMsg, setErrMsg] = useState("");
    const [prenom, setPrenom] = useState("");
    const [nom, setNom] = useState("");
    const errRef = useRef(null);
    const handleSubmit = (e) => {
        console.log(e)
    }
    return (
        <div>
            {/* <h1>Registration</h1> */}
            <Form onSubmit={handleSubmit} style={{display:"inline-block"}} id="container-login" className="form2">
            <p ref={errRef} className={errMsg ? "errMsg" : "offscreen"} aria-live="assertive">{errMsg}</p>
            <div className="row" id="test">
            <Form.Group className="col-12 " controlId="formBasicEmail">
                <Form.Label className=''><h5>Adresse email : </h5></Form.Label>
                <Form.Control
                        type="email"
                        name="email"
                        value={user}
                        onChange={(e) => setUser(e.target.value)}
                        placeholder="Enter email"
                        required
                    />
            </Form.Group>
            <Form.Group className="col-12" controlId="formBasicPrenom">
                <Form.Label className=''><h5>Prenom : </h5></Form.Label>
                    <Form.Control
                            type="text"
                            name="prenom"
                            value={prenom}
                            onChange={(e) => setPrenom(e.target.value)}
                            placeholder="Prenom etudiant"
                            required  
                        />
            </Form.Group>
            <Form.Group className="col-12" controlId="formBasicNon">
                <Form.Label className=''><h5>Nom : </h5></Form.Label>
                    <Form.Control
                            type="text"
                            name="nom"
                            value={nom}
                            onChange={(e) => setNom(e.target.value)}
                            placeholder="Nom etudiant"
                            required  
                        />
            </Form.Group>
            <Form.Group className="col-12" controlId="formBasicPassword">
                <Form.Label className=''><h5>Mot de passe : </h5></Form.Label>
                    <Form.Control
                            type="password"
                            name="password"
                            value={pwd}
                            onChange={(e) => setPwd(e.target.value)}
                            placeholder="************"
                            required  
                        />
            </Form.Group>
            </div>
            <div>
            <Button
                variant="success"
                className="btn-xl float-end"
                type="submit"
                >
                S'inscrire {submitted ? <Spinner animation="grow" size="sm" role="status" /> : null}
          </Button>
            </div>
            
        </Form>
        </div>
    )
}
export default Register;