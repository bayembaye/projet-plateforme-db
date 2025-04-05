import React from "react";
import "./TopMenu.css"; // Import du CSS

function TopMenu() {
  return (
    <nav className="top-menu">
      <div className="logo">MonLogo</div>
      <ul className="menu-links">
        <li><a href="#">Accueil</a></li>
        <li><a href="#">Services</a></li>
        <li><a href="#">Contact</a></li>
        <li><a href="#">À propos</a></li>
      </ul>
    </nav>
  );
}

export default TopMenu;
