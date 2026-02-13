// NexusAIHome.jsx
import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const NexusAIHome = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
          }
        });
      },
      { threshold: 0.15 }
    );

    document.querySelectorAll('.card').forEach((card) => observer.observe(card));

    // Cleanup on unmount
    return () => observer.disconnect();
  }, []);

  return (
    <>
      <style>{`
        :root {
          --primary-blue:   #d40000;
          --secondary-green: #312c2a;
          --accent-silver:  #A9A9A9;
          --dark-text:      #ffffff;
          --light-bg:       #1a1a1e;
          --white:          #0f0f11;
          --highlight-red:  #c8102e;
          --icon-red:       #c8102e;
        }

        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }

        body {
          font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          color: var(--dark-text);
          line-height: 1.6;
          background: var(--white);
        }

        p, li, td {
          color: #b0b0b0;
        }

        .container {
          max-width: 1240px;
          margin: 0 auto;
          padding: 0 24px;
        }

        h1, h2, h3 {
          color: var(--primary-blue);
          line-height: 1.22;
        }

        section {
          padding: 100px 0;
        }

        /* Compact Login Button */
        .login-btn-header {
          position: fixed;
          top: 10px;
          right: 10px;
          background: var(--primary-blue);
          color: white;
          border: none;
          padding: 15px 15px;
          font-size: 0.7rem;
          font-weight: 600;
          border-radius: 2px;
          cursor: pointer;
          transition: all 0.2s ease;
          z-index: 1000;
          box-shadow: 0 1px 3px rgba(212, 0, 0, 0.3);
          line-height: 1;
          width: fit-content;
          display: inline-block;
          white-space: nowrap;
        }

        .login-btn-header:hover {
          background: #b30000;
          box-shadow: 0 2px 6px rgba(212, 0, 0, 0.4);
          transform: translateY(-1px);
        }

        .login-btn-header:active {
          transform: translateY(0);
        }

        /* Hero */
        .hero {
          background: linear-gradient(135deg, #0f0f11 0%, #1a1a1e 100%);
          text-align: center;
          padding: 180px 24px 140px;
        }

        .hero h1 {
          font-size: clamp(2.8rem, 6.5vw, 4.2rem);
          margin-bottom: 1.6rem;
          opacity: 0;
          transform: translateY(40px);
          animation: smoothRise 2.2s cubic-bezier(0.23, 1, 0.32, 1) 0.4s forwards;
        }

        .hero p {
          font-size: clamp(1.2rem, 3vw, 1.45rem);
          max-width: 860px;
          margin: 0 auto 2.8rem;
          color: #b0b0b0;
          opacity: 0;
          transform: translateY(30px);
          animation: smoothRise 1.8s cubic-bezier(0.23, 1, 0.32, 1) 1s forwards;
        }

        .tagline {
          font-size: 1.5rem;
          font-style: italic;
          color: var(--highlight-red);
          font-weight: 600;
          opacity: 0;
          transform: translateY(25px);
          animation: smoothRise 1.7s cubic-bezier(0.23, 1, 0.32, 1) 1.8s forwards, pulseRed 4s ease-in-out infinite;
        }

        @keyframes pulseRed {
          0%, 100% { opacity: 0.92; text-shadow: 0 0 8px rgba(200,16,46,0.3); }
          50%      { opacity: 1;   text-shadow: 0 0 18px rgba(200,16,46,0.6); }
        }

        @keyframes smoothRise {
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .section-title {
          text-align: center;
          font-size: clamp(2.3rem, 5vw, 3rem);
          margin-bottom: 3rem;
          position: relative;
          opacity: 0;
          transform: translateY(50px);
          animation: smoothRise 1.9s cubic-bezier(0.23, 1, 0.32, 1) forwards;
        }

        .section-title::after {
          content: "";
          position: absolute;
          bottom: -18px;
          left: 50%;
          transform: translateX(-50%) scaleX(0);
          width: 100px;
          height: 5px;
          background: var(--secondary-green);
          border-radius: 3px;
          transform-origin: center;
          animation: growLine 2.4s cubic-bezier(0.23, 1, 0.32, 1) 0.6s forwards;
        }

        @keyframes growLine {
          to {
            transform: translateX(-50%) scaleX(1);
          }
        }

        .card-grid {
          display: grid;
          gap: 2rem;
          margin: 3rem 0;
        }

        @media (min-width: 780px) {
          .card-grid { grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)); }
        }

        .card {
          background: #1a1a1e;
          padding: 2.2rem;
          border-radius: 12px;
          box-shadow: 0 6px 24px rgba(0,0,0,0.3);
          border-left: 6px solid var(--secondary-green);
          opacity: 0;
          transform: translateY(60px);
          transition: all 1.1s cubic-bezier(0.23, 1, 0.32, 1);
        }

        .card.visible {
          opacity: 1;
          transform: translateY(0);
        }

        .card:hover {
          transform: translateY(-10px);
          box-shadow: 0 16px 40px rgba(0,0,0,0.5);
        }

        .card strong {
          display: block;
          font-size: 1.3rem;
          margin-bottom: 0.8rem;
          color: var(--primary-blue);
        }

        .card p {
          color: #b0b0b0;
        }

        table {
          width: 100%;
          border-collapse: collapse;
          margin: 3rem 0;
          font-size: 1.02rem;
          background: #0f0f11;
        }

        th, td {
          padding: 18px 20px;
          text-align: left;
          border-bottom: 1px solid #33333a;
          color: #ffffff;
        }

        th {
          background: var(--primary-blue);
          color: white;
          font-weight: 600;
        }

        tr:nth-child(odd) {
          background: #0f0f11;
        }

        tr:nth-child(even) {
          background: #1a1a1e;
        }

        .highlight-box {
          background: #252429;
          padding: 2.6rem;
          border-radius: 12px;
          margin: 3.5rem 0;
          border-left: 6px solid var(--secondary-green);
          box-shadow: 0 6px 28px rgba(0,0,0,0.3);
        }

        .highlight-box h3 {
          font-size: 1.9rem;
          margin-bottom: 1.4rem;
          opacity: 0;
          transform: translateY(40px);
          animation: smoothRise 1.8s cubic-bezier(0.23, 1, 0.32, 1) 0.7s forwards;
        }

        .highlight-box p,
        .highlight-box ul,
        .highlight-box li {
          color: #b0b0b0;
        }

        /* Industry icons layout */
        .industry-icons {
          display: flex;
          flex-wrap: wrap;
          justify-content: center;
          gap: 2.5rem 3rem;
          margin: 4rem 0;
          text-align: center;
        }

        .industry-item {
          flex: 0 0 160px;
          max-width: 180px;
        }

        .industry-item img {
          width: 68px;
          height: 68px;
          margin-bottom: 1rem;
          object-fit: contain;
        }

        .industry-item strong {
          display: block;
          font-size: 1.08rem;
          color: var(--primary-blue);
          margin-bottom: 0.6rem;
        }

        .industry-item p {
          font-size: 0.94rem;
          color: #b0b0b0;
          line-height: 1.45;
        }

        @media (max-width: 768px) {
          .industry-icons {
            gap: 2rem 1.8rem;
          }
          .industry-item {
            flex: 0 0 45%;
            max-width: 45%;
          }
          .industry-item img {
            width: 56px;
            height: 56px;
          }
        }

        footer {
          background: var(--primary-blue);
          color: white;
          padding: 100px 24px 60px;
          text-align: center;
        }

        .footer-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
          gap: 4rem;
          max-width: 1240px;
          margin: 0 auto 4rem;
        }

        footer a {
          color: #ffffff;
          text-decoration: none;
        }

        footer a:hover {
          text-decoration: underline;
        }

        .copyright {
          margin-top: 3rem;
          opacity: 0.9;
          font-size: 0.98rem;
        }

        @media (prefers-reduced-motion: reduce) {
          *, *::before, *::after {
            animation: none !important;
            transition: none !important;
          }
        }

        @media (max-width: 768px) {
          .hero { padding: 120px 20px 80px; }
          section { padding: 70px 0; }
          .section-title { font-size: 2.4rem; }
        }
      `}</style>

      {/* Compact Login Button */}
      <button className="login-btn-header" onClick={() => navigate('/login')}>Login</button>

      {/* Hero */}
      <section className="hero">
        <div className="container">
          <h2 style={{color: '#fff', fontSize: '4rem', fontWeight: '700', letterSpacing: '6px', textTransform: 'uppercase', marginBottom: '40px'}}>NEXUS AI</h2>
          <h1>Transform Control Logic into Code - Simply Speak Your Vision</h1>
          <p>
            Revolutionary AI-powered platform that converts natural language descriptions into production-ready structured text for Mitsubishi Electric PLCs. No coding expertise required—just describe your process, and let Nexus AI handle the rest.
          </p>
          <p className="tagline">Empowering Engineers to Build Smarter, Faster, and Better</p>
        </div>
      </section>

      {/* About */}
      <section>
        <div className="container">
          <h2 className="section-title">About Nexus AI</h2>
          <p>
            Nexus AI is the industry's first natural language processing platform specifically designed for industrial automation. Built for Mitsubishi Electric FX5U and IQ-F series PLCs, Nexus AI bridges the gap between engineering intent and executable code, transforming weeks of programming work into minutes of intelligent automation.
          </p>
          <p>
            Whether you're describing a simple tank filling sequence or a complex multi-stage dip dyeing process, Nexus AI understands your requirements, validates safety logic, generates optimized structured text code, and maintains complete audit trails—all while adhering to IEC 61131-3 standards.
          </p>
        </div>
      </section>

      {/* Problem */}
      <section style={{ background: 'var(--light-bg)' }}>
        <div className="container">
          <h2 className="section-title">Industrial Automation's Critical Challenges</h2>
          <div className="card-grid">
            <div className="card">
              Programming Bottlenecks: Traditional PLC programming requires specialized expertise in ladder logic or structured text, creating dependency on scarce automation engineers and delaying project timelines
            </div>
            <div className="card">
              Human Error & Inconsistency: Manual code development introduces mistakes in safety interlocks, missed edge cases, and inconsistent coding standards across team members and projects
            </div>
            <div className="card">
              Knowledge Transfer Gaps: Control logic documentation often becomes outdated, making system maintenance and modifications difficult when original programmers are unavailable
            </div>
            <div className="card">
              Lack of Traceability: Traditional workflows lack comprehensive audit trails, making it challenging to track who changed what, when, and why—critical for quality management systems
            </div>
            <div className="card">
              Validation Overhead: Ensuring all safety interlocks, emergency stops, and fail-safe mechanisms are properly implemented requires extensive manual review and testing
            </div>
          </div>
          <p
            style={{
              textAlign: 'center',
              fontWeight: 600,
              marginTop: '3rem',
              fontSize: '1.22rem',
              color: '#b0b0b0',
            }}
          >
            These challenges result in extended project timelines, increased costs, safety risks, and reduced operational efficiency across manufacturing facilities worldwide.
          </p>
        </div>
      </section>

      {/* How it Works */}
      <section>
        <div className="container">
          <h2 className="section-title">From Natural Language to Production Code in Four Intelligent Steps</h2>
          <div className="card-grid">
            <div className="card">
              <strong>1. Describe Your Control Logic</strong>
              Input your process requirements in plain English—either by typing directly, pasting from documents, or importing specification files. No need to worry about syntax, labels, or programming conventions. Simply describe what needs to happen: "When the tank reaches high level, stop the inlet pump and activate the mixer for 5 minutes."
            </div>
            <div className="card">
              <strong>2. AI-Powered Stage Planning</strong>
              Nexus AI analyzes your description and intelligently divides the control logic into logical stages (Idle, Safety Check, Tank Filling, Mixing, Discharge, etc.). The system automatically includes mandatory safety stages and structures the workflow for optimal PLC execution.
            </div>
            <div className="card">
              <strong>3. Intelligent Validation & Enhancement</strong>
              For each stage, Nexus AI validates completeness: Are all required interlocks present? Is the emergency stop logic properly implemented? Are outputs properly sequenced? The AI identifies missing safety logic, suggests fail-safe mechanisms, and flags potential issues—ensuring robust, production-ready control sequences before a single line of code is generated.
            </div>
            <div className="card">
              <strong>4. Structured Text Code Generation</strong>
              Once validation is complete, Nexus AI generates optimized structured text code conforming to IEC 61131-3 standards. Code is organized into program blocks, function blocks, and functions with proper local labels and global variables. The generated code is immediately exportable to GX Works 3 for Mitsubishi FX5U and IQ-F series PLCs.
            </div>
          </div>
        </div>
      </section>

      {/* Key Features */}
      <section style={{ background: 'var(--light-bg)' }}>
        <div className="container">
          <h2 className="section-title">Comprehensive Platform for Modern Industrial Automation</h2>
          <table>
            <tr><th>Feature</th><th>Description</th></tr>
            <tr><td>Natural Language Processing</td><td>Convert plain English control logic descriptions into executable code without learning programming syntax</td></tr>
            <tr><td>Role-Based Access Control</td><td>Three-tier hierarchy (Admin, Team Lead, Team Member) with granular permissions for project management and code generation</td></tr>
            <tr><td>Intelligent Stage Division</td><td>Automatic breakdown of complex processes into logical, manageable stages with mandatory safety and idle stages</td></tr>
            <tr><td>AI Validation Engine</td><td>Comprehensive logic validation identifying missing interlocks, safety gaps, and incomplete sequences before code generation</td></tr>
            <tr><td>Structured Text Output</td><td>IEC 61131-3 compliant code generation with proper program blocks, function blocks, and variable organization</td></tr>
            <tr><td>Mitsubishi PLC Optimization</td><td>Specifically engineered for FX5U and IQ-F series PLCs with vendor-specific instruction optimization</td></tr>
            <tr><td>AIdu Assistant</td><td>Built-in AI chatbot providing instant answers about Mitsubishi Electric PLCs, programming best practices, and troubleshooting guidance</td></tr>
            <tr><td>Complete Audit Trail</td><td>Detailed logging of every change—who modified what, when, and why—with exportable audit reports for compliance</td></tr>
            <tr><td>Program & Audit Reports</td><td>Generate comprehensive documentation including code evolution, change history, and project timeline for quality management</td></tr>
            <tr><td>Stage-Level Code Export</td><td>Export complete projects or individual stages for flexible integration with existing development workflows</td></tr>
            <tr><td>Real-Time Collaboration</td><td>Multiple team members can work on different stages simultaneously with automatic conflict resolution</td></tr>
            <tr><td>Version Control</td><td>Automatic versioning of control logic and generated code with rollback capability to any previous state</td></tr>
          </table>
        </div>
      </section>

      {/* Unique Advantages */}
      <section>
        <div className="container">
          <h2 className="section-title">Why Nexus AI Stands Apart</h2>
          <div className="card-grid">
            <div className="card">
              Industry-First Natural Language PLC Programming: While other platforms require learning ladder logic or structured text syntax, Nexus AI accepts plain English descriptions. This democratizes PLC programming, enabling process engineers, maintenance technicians, and project managers to directly contribute to control logic development without specialized coding training.
            </div>
            <div className="card">
              Built-In Safety Intelligence: Nexus AI doesn't just translate your words—it actively enhances your control logic. The validation engine automatically checks for missing emergency stops, incomplete interlocks, and unsafe state transitions. Safety is engineered into every generated program, not added as an afterthought.
            </div>
            <div className="card">
              Mitsubishi Electric Specialization: Unlike generic code generators, Nexus AI is purpose-built for Mitsubishi Electric's FX5U and IQ-F series PLCs. We leverage vendor-specific instructions, optimize for Mitsubishi's execution model, and ensure seamless integration with GX Works 3 development environment.
            </div>
            <div className="card">
              Enterprise-Grade Collaboration: Traditional PLC development is isolated and siloed. Nexus AI brings modern software development practices to industrial automation: role-based access control, concurrent editing, comprehensive audit trails, and automatic documentation generation. Your entire team works from a single source of truth.
            </div>
            <div className="card">
              Stage-Based Intelligence: By breaking control logic into stages, Nexus AI enables granular validation, focused testing, and modular code organization. Each stage can be independently verified, modified, and exported— dramatically simplifying complex automation projects.
            </div>
            <div className="card">
              Continuous Learning & Improvement: Nexus AI learns from every project. The more you use it, the better it understands your specific terminology, process patterns, and coding preferences. The platform evolves with your organization's needs.
            </div>
          </div>
        </div>
      </section>

      {/* Target Users */}
      <section style={{ background: 'var(--light-bg)' }}>
        <div className="container">
          <h2 className="section-title">Engineered for Every Role in Industrial Automation</h2>
          <table>
            <tr><th>User Role</th><th>How Nexus AI Helps</th></tr>
            <tr><td>Automation Engineers</td><td>Accelerate code development by 10x, eliminate repetitive coding tasks, focus on system optimization rather than syntax</td></tr>
            <tr><td>Project Managers</td><td>Reduce project timelines, improve resource allocation, maintain real-time visibility into development progress</td></tr>
            <tr><td>Process Engineers</td><td>Directly translate process knowledge into control logic without learning programming languages</td></tr>
            <tr><td>Maintenance Teams</td><td>Quickly understand existing control logic, make modifications confidently with AI validation, access comprehensive documentation</td></tr>
            <tr><td>Quality Managers</td><td>Ensure consistent coding standards, maintain complete audit trails for compliance, generate documentation automatically</td></tr>
            <tr><td>System Integrators</td><td>Deliver projects faster, reduce engineering costs, provide clients with fully documented and validated control systems</td></tr>
          </table>
        </div>
      </section>

      {/* Proven Across Diverse Industrial Applications */}
      <section>
        <div className="container">
          <h2 className="section-title">Proven Across Diverse Industrial Applications</h2>

          <div className="industry-icons">
            <div className="industry-item">
              <img
                src="https://img.freepik.com/premium-vector/recycling-vector-illustration-style_717774-16501.jpg"
                alt="Textile"
              />
              <strong>Textile Industry</strong>
              <p>Dip dyeing machines, fabric tension control, automated cutting systems, batch processing controllers</p>
            </div>

            <div className="industry-item">
              <img
                src="https://cdn.vectorstock.com/i/500p/60/87/healthy-food-and-drink-icon-water-with-apple-sign-vector-35226087.jpg"
                alt="Food & Beverage"
              />
              <strong>Food & Beverage</strong>
              <p>Bottling line control, mixing and blending processes, temperature and pressure regulation, CIP systems</p>
            </div>

            <div className="industry-item">
              <img
                src="https://img.freepik.com/premium-vector/lab-process-icon_1134104-2350.jpg"
                alt="Chemical Processing"
              />
              <strong>Chemical Processing</strong>
              <p>Reactor control sequences, batch recipe management, dosing and mixing automation, safety interlock systems</p>
            </div>

            <div className="industry-item">
              <img
                src="https://static.vecteezy.com/system/resources/previews/028/671/125/non_2x/water-treatment-icon-ecological-design-environmental-concept-in-isolation-on-white-background-free-vector.jpg"
                alt="Water Treatment"
              />
              <strong>Water Treatment</strong>
              <p>Pump sequencing, tank level management, filtration control, chemical dosing automation</p>
            </div>

            <div className="industry-item">
              <img
                src="https://cdn.vectorstock.com/i/500p/08/32/forklift-icon-black-and-white-vector-46420832.jpg"
                alt="Material Handling"
              />
              <strong>Material Handling</strong>
              <p>Conveyor systems, sorting machines, robotic pick-and-place, warehouse automation</p>
            </div>

            <div className="industry-item">
              <img
                src="https://img.freepik.com/premium-vector/packaging-icon-style_822882-3419.jpg"
                alt="Packaging"
              />
              <strong>Packaging</strong>
              <p>Filling machines, labeling systems, cartoning equipment, palletizing automation</p>
            </div>

            <div className="industry-item">
              <img
                src="https://img.freepik.com/premium-vector/propeller-generating-strong-air-flow-with-arrows-icon_98396-156504.jpg"
                alt="HVAC Systems"
              />
              <strong>HVAC Systems</strong>
              <p>Chiller control, air handler sequencing, building automation, energy management systems</p>
            </div>
          </div>

          <div className="highlight-box">
            <h3>Dip Dyeing Machine Prototype - Team Nexus AI</h3>
            <p>
              A complete dip dyeing control system was developed using Nexus AI, demonstrating the platform's capability to handle complex, multistage industrial processes:
            </p>
            <ul>
              <li>Process complexity: 7 distinct stages (Idle, Tank Level Check, Gantry Homing, Parameter Input, Dye Process, Rinse Process, Dry Process)</li>
              <li>Hardware integration: Mitsubishi FX5U PLC, HMI, servo motors, VFDs, multiple sensors and actuators</li>
              <li>Safety features: Emergency stop logic, collision prevention, tank overflow protection, limit switch monitoring</li>
              <li>Development time: 80% reduction compared to traditional manual coding approach</li>
              <li>Code quality: Zero safety gaps identified during validation and testing</li>
            </ul>
            <p>
              The generated structured text code successfully controlled the 2m × 1.5m × 3m prototype with precise gantry positioning, multi-layer dyeing depth control, and automated rinse/dry sequences—validated through both virtual Gemini 3D simulation and physical prototype operation.
            </p>
          </div>
        </div>
      </section>

      {/* Benefits Summary */}
      <section style={{ background: 'var(--light-bg)' }}>
        <div className="container">
          <h2 className="section-title">Measurable Impact on Your Automation Projects</h2>
          <table>
            <tr><th>Metric</th><th>Improvement</th></tr>
            <tr><td>Code Development Time</td><td>80-90% reduction</td></tr>
            <tr><td>Programming Errors</td><td>95% decrease in safety gaps and logic errors</td></tr>
            <tr><td>Project Timeline</td><td>60-70% faster completion</td></tr>
            <tr><td>Documentation Accuracy</td><td>100% up-to-date with automatic generation</td></tr>
            <tr><td>Knowledge Transfer</td><td>Immediate through natural language descriptions</td></tr>
            <tr><td>Audit Compliance</td><td>Complete traceability with zero manual effort</td></tr>
            <tr><td>Team Productivity</td><td>5-10x increase in control logic output</td></tr>
            <tr><td>Cost Savings</td><td>40-50% reduction in engineering labor costs</td></tr>
          </table>
        </div>
      </section>

      {/* Footer */}
      <footer>
        <div className="container">
          <div className="footer-grid">
            <div>
              <h3>Nexus AI</h3>
              <p>A Team Nexus AI Innovation</p>
              <p>Developed for Mitsubishi Electric Cup 2026</p>
              <p>Theme: Automating the World Through Digital Innovations</p>
            </div>
            <div>
              <h3>Quick Links</h3>
              <p>About Us • Features • Pricing • Industries • Resources • Blog • Documentation • Support • Contact</p>
            </div>
            <div>
              <h3>Legal</h3>
              <p>Privacy Policy • Terms of Service • Security • Compliance</p>
            </div>
          </div>
          <div className="copyright">
            © 2026 Nexus AI. All rights reserved.<br />
            Mitsubishi Electric and GX Works are trademarks of Mitsubishi Electric Corporation.
          </div>
        </div>
      </footer>
    </>
  );
};

export default NexusAIHome;