<section className="how-section">
        <h2>How Nexus AI Works</h2>
        <h3>From Natural Language to Production Code in Four Intelligent Steps</h3>
        <ol className="how-list">
          <li>
            <strong>Describe Your Control Logic</strong><br />
            Input your process requirements in plain English—either by typing directly, pasting from documents, or importing specification files. No need to worry about syntax, labels, or programming conventions. Simply describe what needs to happen: "When the tank reaches high level, stop the inlet pump and activate the mixer for 5 minutes."
          </li>
          <li>
            <strong>AI-Powered Stage Planning</strong><br />
            Nexus AI analyzes your description and intelligently divides the control logic into logical stages (Idle, Safety Check, Tank Filling, Mixing, Discharge, etc.). The system automatically includes mandatory safety stages and structures the workflow for optimal PLC execution. Each stage becomes a manageable unit for validation and code generation.
          </li>
          <li>
            <strong>Intelligent Validation & Enhancement</strong><br />
            For each stage, Nexus AI validates completeness: Are all required interlocks present? Is the emergency stop logic properly implemented? Are outputs properly sequenced? The AI identifies missing safety logic, suggests fail-safe mechanisms, and flags potential issues—ensuring robust, production-ready control sequences before a single line of code is generated.
          </li>
          <li>
            <strong>Structured Text Code Generation</strong><br />
            Once validation is complete, Nexus AI generates optimized structured text code conforming to IEC 61131-3 standards. Code is organized into program blocks, function blocks, and functions with proper local labels and global variables. The generated code is immediately exportable to GX Works 3 for Mitsubishi FX5U and IQ-F series PLCs.
          </li>
        </ol>
        <div className="how-visual-note">
          <em>[Recommended: Animated flowchart showing English text input → AI analysis → Stage breakdown → Validation → Code output]</em>
        </div>
      </section>
import React from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/Home.css';

function HomePage() {
  const navigate = useNavigate();

  return (
    <div className="home-container">
      <section className="hero-section">
        <h2 className="nexus-main-title">NEXUS AI</h2>
        <h1 className="headline">Transform Control Logic into Code - Simply Speak Your Vision</h1>
        <p className="subheadline">Revolutionary AI-powered platform that converts natural language descriptions into production-ready structured text for Mitsubishi Electric PLCs. No coding expertise required—just describe your process, and let Nexus AI handle the rest.</p>
        <div className="cta-group">
          <button className="cta-btn red" onClick={() => navigate('/login')}>Start Your Free Trial</button>
          <button className="cta-btn white">Watch Demo</button>
          <button className="cta-btn black">Contact Sales</button>
        </div>
        <p className="supporting-tagline">Empowering Engineers to Build Smarter, Faster, and Better</p>
      </section>
      <section className="about-section">
        <h2>About Nexus AI</h2>
        <p>Nexus AI is the industry's first natural language processing platform specifically designed for industrial automation. Built for Mitsubishi Electric FX5U and IQ-F series PLCs, Nexus AI bridges the gap between engineering intent and executable code, transforming weeks of programming work into minutes of intelligent automation. Whether you're describing a simple tank filling sequence or a complex multi-stage dip dyeing process, Nexus AI understands your requirements, validates safety logic, generates optimized structured text code, and maintains complete audit trails—all while adhering to IEC 61131-3 standards.</p>
      </section>
      <section className="problem-section">
        <h2>The Problem We Solve</h2>
        <div className="challenge-cards">
          <div className="challenge-card">Programming Bottlenecks: Traditional PLC programming requires specialized expertise in ladder logic or structured text, creating dependency on scarce automation engineers and delaying project timelines</div>
          <div className="challenge-card">Human Error & Inconsistency: Manual code development introduces mistakes in safety interlocks, missed edge cases, and inconsistent coding standards across team members and projects</div>
          <div className="challenge-card">Knowledge Transfer Gaps: Control logic documentation often becomes outdated, making system maintenance and modifications difficult when original programmers are unavailable</div>
          <div className="challenge-card">Lack of Traceability: Traditional workflows lack comprehensive audit trails, making it challenging to track who changed what, when, and why—critical for quality management systems</div>
          <div className="challenge-card">Validation Overhead: Ensuring all safety interlocks, emergency stops, and fail-safe mechanisms are properly implemented requires extensive manual review and testing</div>
        </div>
        <p className="problem-impact">These challenges result in extended project timelines, increased costs, safety risks, and reduced operational efficiency across manufacturing facilities worldwide.</p>
      </section>
      <section className="impact-section">
        <h2>From Natural Language to Production Code in Four Intelligent Steps</h2>
        <ol className="impact-list">
          <li>Describe Your Control Logic</li>
          <li>AI-Powered Stage Planning</li>
          <li>Intelligent Validation & Enhancement</li>
          <li>Structured Text Code Generation</li>
        </ol>
      </section>
      {/* Add more sections as needed, following your content structure */}
      <section className="login-section">
        <button className="login-btn" onClick={() => navigate('/login')}>Login</button>
      </section>
    </div>
  );
}

export default HomePage;