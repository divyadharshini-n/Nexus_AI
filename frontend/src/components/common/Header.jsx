import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../../services/authService';
import '../../styles/Header.css';

const MANUALS = [
  { name: 'ST Syntax', file: 'ST_Syntax.pdf' },
  { name: 'ST Programming', file: 'ST programming.pdf' },
  { name: 'Program Design', file: 'Program design.pdf' },
  { name: 'Operating Manual', file: 'Operating manual.pdf' },
  { name: 'Instructions Functions & Function Blocks', file: 'Instructions-Fun-fb.pdf' },
  { name: 'IEC 61508', file: 'IEC 61508.pdf' },
  { name: 'FA Equipment for Beginners - PLCs', file: 'FA_Equip_for_Begin_eng_PLCs-A.pdf' },
  { name: 'Datatype Conversion', file: 'DataypeConversion.pdf' },
  { name: 'Application Manual', file: 'Application manual.pdf' },
  { name: 'Program Basics ST', file: '1-Program_Basics_ST_na_eng.pdf' },
  { name: 'PLC System Maintenance', file: '1-PLC_System_Mainte_na_eng.pdf' },
  { name: 'PLC Machinery Safety Basics', file: '1-PLC_Machinery_Safety_Basics_eng.pdf' },
  { name: 'MELSEC iQ-F Basics', file: '1-MELSEC-iQ-F_Basics_na_eng-A (1).pdf' },
  { name: 'GX Works3 Basics', file: '1-GX_Wks3_Basics_na_eng[1].pdf' },
  { name: 'JY997D55801Z Manual', file: 'jy997d55801z[1].pdf' }
];

function Header({ title, onViewManual }) {
  const [showManualsDropdown, setShowManualsDropdown] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  const [isDarkMode, setIsDarkMode] = useState(true);
  const dropdownRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadCurrentUser();
  }, []);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowManualsDropdown(false);
      }
    };

    if (showManualsDropdown) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [showManualsDropdown]);

  const loadCurrentUser = async () => {
    try {
      const user = await authService.getCurrentUser();
      setCurrentUser(user);
    } catch (error) {
      console.error('Failed to load user:', error);
    }
  };

  const handleLogout = () => {
    authService.logout();
    navigate('/home');
  };

  const handleManualClick = (manual) => {
    setShowManualsDropdown(false);
    if (onViewManual) {
      onViewManual(manual);
    }
  };

  const handleThemeToggle = () => {
    setIsDarkMode(!isDarkMode);
    document.documentElement.setAttribute('data-theme', isDarkMode ? 'light' : 'dark');
    localStorage.setItem('theme', isDarkMode ? 'light' : 'dark');
  };

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    setIsDarkMode(savedTheme === 'dark');
    document.documentElement.setAttribute('data-theme', savedTheme);
  }, []);

  return (
    <div className="global-header">
      <div className="header-left">
        <h1 className="header-title">{title}</h1>
      </div>
      
      <div className="header-right">
        <button 
          className={`theme-toggle ${isDarkMode ? 'dark' : 'light'}`}
          onClick={handleThemeToggle}
          title={isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
        >
          <span className="toggle-icon">{isDarkMode ? '🌙' : '☀️'}</span>
          <span className="toggle-label">{isDarkMode ? 'OFF' : 'ON'}</span>
        </button>

        <div className="manuals-dropdown" ref={dropdownRef}>
          <button
            className="btn-view-manuals"
            onClick={() => setShowManualsDropdown(!showManualsDropdown)}
          >
            View Manuals
            <span className={`dropdown-arrow ${showManualsDropdown ? 'open' : ''}`}>▼</span>
          </button>
          
          {showManualsDropdown && (
            <div className="manuals-dropdown-menu">
              <div className="manuals-dropdown-header">Available Manuals</div>
              {MANUALS.map((manual, index) => (
                <div
                  key={index}
                  className="manual-item"
                  onClick={() => handleManualClick(manual)}
                >
                  <span className="manual-icon"></span>
                  <span className="manual-name">{manual.name}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {currentUser && (
          <div className="user-info">
            <span className="user-name">{currentUser.username}</span>
            {currentUser.is_admin && <span className="admin-badge">Admin</span>}
          </div>
        )}

        <button className="btn-logout" onClick={handleLogout}>
          Logout
        </button>
      </div>
    </div>
  );
}

export default Header;
