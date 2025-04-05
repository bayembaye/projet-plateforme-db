import React from "react";
import { FaHome, FaBook, FaTasks } from "react-icons/fa"; 
import "./Sidebar.css";

const Sidebar = () => {
  return (
    <div className="sidebar">
      <div className="menu-item">
        <FaHome className="icon" />
        <span>Accueil</span>
      </div>
      <div className="menu-item">
        <FaBook className="icon" />
        <span>Notes</span>
      </div>
      <div className="menu-item">
        <FaTasks className="icon" />
        <span>À Faire</span>
      </div>
    </div>
  );
};

export default Sidebar;
