import React, { useState } from "react";
import "../components/Dashboard.css";
import PersonIcon from "@mui/icons-material/Person";
import HomeIcon from "@mui/icons-material/Home";
import MenuBookIcon from "@mui/icons-material/MenuBook";
import ChecklistIcon from "@mui/icons-material/Checklist";
import CalendarTodayIcon from "@mui/icons-material/CalendarToday";

function Dashboard() {
  const [activePage, setActivePage] = useState("accueil");

  return (
    <div className="container">
      {/* Menu latéral */}
      <aside className="sidebar">
        <div
          className={`menu-item ${activePage === "accueil" ? "active" : ""}`}
          onClick={() => setActivePage("accueil")}
        >
          <HomeIcon className="icon" />
          <span>Accueil</span>
        </div>
        <div className="separator"></div>

        <div
          className={`menu-item ${activePage === "notes" ? "active" : ""}`}
          onClick={() => setActivePage("notes")}
        >
          <MenuBookIcon className="icon" />
          <span>Notes</span>
        </div>
        <div className="separator"></div>

        <div
          className={`menu-item ${activePage === "a-faire" ? "active" : ""}`}
          onClick={() => setActivePage("a-faire")}
        >
          <ChecklistIcon className="icon" />
          <span>À Faire</span>
        </div>
      </aside>

      {/* Contenu principal */}
      <div className="main-content">
        <header className="top-menu">
          <div className="menu-icon">☰</div>
          <div className="user-profile">
            <PersonIcon style={{ fontSize: 24, verticalAlign: "middle" }} /> NOM_ETUD
          </div>
        </header>

        {/* Contenu dynamique */}
        <div className="dashboard-content">
          {activePage === "accueil" && (
            <>
              {/* Bloc Notes */}
              <div className="notes-box">
                <h2 className="notes-title">Notes</h2>
                <div className="card">
                  <p><strong>nom_matière</strong></p>
                  <p>
                    <PersonIcon style={{ fontSize: 18, verticalAlign: "middle" }} /> 
                    nom_prof •  
                    <CalendarTodayIcon className="calendar-icon" /> 00/00/2000
                  </p>
                  <span className="grade green">10</span>
                </div>
                <div className="card">
                  <p><strong>nom_matière</strong></p>
                  <p>
                    <PersonIcon style={{ fontSize: 18, verticalAlign: "middle" }} /> 
                    nom_prof •  
                    <CalendarTodayIcon className="calendar-icon" /> 00/00/2000
                  </p>
                  <span className="grade red">9</span>
                </div>
                <button className="button">📄 Consulter les notes</button>
              </div>

              {/* Bloc À faire */}
              <div className="tasks-box">
                <h2 className="tasks-title">À Faire</h2>
                <div className="card">
                  <p><strong>nom_matière</strong></p>
                  <p>
                    <PersonIcon style={{ fontSize: 18, verticalAlign: "middle" }} /> 
                    nom_prof
                  </p>
                  <span className="task-date">
                    <CalendarTodayIcon className="calendar-icon" /> 00/00/2000
                  </span>
                </div>
                <button className="button">📤 Rendre devoir</button>
              </div>
            </>
          )}

          {activePage === "notes" && (
            <div>
              <h2>Notes</h2>
              <p>Ici, tu peux consulter toutes tes notes.</p>
            </div>
          )}

          {activePage === "a-faire" && (
            <div>
              <h2>À Faire</h2>
              <p>Liste des tâches à faire.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
