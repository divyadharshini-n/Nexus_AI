import React, { useEffect, useState } from 'react';
import './IntroScreen.css';

const IntroScreen = ({ onComplete }) => {
  const [show, setShow] = useState(true);

  useEffect(() => {
    // Auto-hide intro after 5 seconds
    const timer = setTimeout(() => {
      setShow(false);
      if (onComplete) onComplete();
    }, 5000);

    return () => clearTimeout(timer);
  }, [onComplete]);

  if (!show) return null;

  return (
    <div className="intro-screen">
      {/* Animated Electric Wave Background */}
      <div className="electric-waves">
        <div className="wave wave-1"></div>
        <div className="wave wave-2"></div>
        <div className="wave wave-3"></div>
        <div className="wave wave-4"></div>
      </div>

      {/* Grid Pattern Overlay */}
      <div className="grid-pattern"></div>

      {/* Main Content */}
      <div className="intro-content">
        {/* Main Title */}
        <h1 className="intro-title">
          <span className="title-word">NEXUS</span>
          <span className="title-word">AI</span>
          <span className="title-word">PRESENTS</span>
        </h1>

        {/* Divider Line */}
        <div className="divider-line"></div>

        {/* Subtitle */}
        <p className="intro-subtitle">
          <span className="subtitle-word">INTELLIGENT</span>
          <span className="subtitle-word">PLC</span>
          <span className="subtitle-word">PROGRAMMING</span>
          <span className="subtitle-word">ASSISTANT</span>
          <span className="subtitle-word">FOR</span>
          <span className="subtitle-word">MITSUBISHI</span>
          <span className="subtitle-word">ELECTRIC</span>
          <span className="subtitle-word">AUTOMATION</span>
        </p>
      </div>

      {/* Corner Accents */}
      <div className="corner-accent corner-tl"></div>
      <div className="corner-accent corner-tr"></div>
      <div className="corner-accent corner-bl"></div>
      <div className="corner-accent corner-br"></div>
    </div>
  );
};

export default IntroScreen;
