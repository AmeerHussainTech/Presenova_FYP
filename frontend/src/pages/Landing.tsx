/**
 * Landing Page Component
 * Minimalist, aesthetic, clean, calm, and fully mobile-responsive landing page for Presenova.
 */

import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Landing.css';

interface FeatureItem {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
}

const Landing: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated, isLoading } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState<boolean>(false);
  const [isLightTheme, setIsLightTheme] = useState<boolean>(() => {
    return document.documentElement.classList.contains('light-theme');
  });

  // Redirect authenticated users to Dashboard
  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      navigate('/analytics', { replace: true });
    }
  }, [isAuthenticated, isLoading, navigate]);

  const toggleTheme = () => {
    const root = document.documentElement;
    if (root.classList.contains('light-theme')) {
      root.classList.remove('light-theme');
      setIsLightTheme(false);
      localStorage.setItem('presenova_theme', 'dark');
    } else {
      root.classList.add('light-theme');
      setIsLightTheme(true);
      localStorage.setItem('presenova_theme', 'light');
    }
  };

  const featureList: FeatureItem[] = [
    {
      id: 'doc-analyzer',
      title: 'Document & Slide Analyzer',
      description: 'Upload PPTX/PDF decks for comprehensive 7Cs communication compliance and structure audits.',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
          <polyline points="14 2 14 8 20 8" />
          <line x1="16" y1="13" x2="8" y2="13" />
          <line x1="16" y1="17" x2="8" y2="17" />
          <polyline points="10 9 9 9 8 9" />
        </svg>
      ),
    },
    {
      id: 'speech-analyzer',
      title: 'Speech & Vocal Telemetry',
      description: 'Analyze speaking pace (WPM), filler word density, articulation clarity, and emotional sentiment.',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
          <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
          <line x1="12" y1="19" x2="12" y2="23" />
          <line x1="8" y1="23" x2="16" y2="23" />
        </svg>
      ),
    },
    {
      id: 'interactive-coach',
      title: 'Interactive AI Defense Coach',
      description: 'Simulate high-stakes academic viva defenses and investor Q&A sessions with dynamic LLM questioning.',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          <line x1="9" y1="10" x2="15" y2="10" />
        </svg>
      ),
    },
    {
      id: 'live-teleprompter',
      title: 'Live Coaching & Teleprompter',
      description: 'Real-time webcam delivery coaching with pacing HUD overlays and automated speech synthesis.',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polygon points="23 7 16 12 23 17 23 7" />
          <rect x="1" y="5" width="15" height="14" rx="2" ry="2" />
        </svg>
      ),
    },
    {
      id: 'slide-rewriter',
      title: 'Presentation Rewriter',
      description: 'Instant side-by-side slide content refinement with intelligent diff inspection and readability boost.',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="1 4 1 10 7 10" />
          <polyline points="23 20 23 14 17 14" />
          <path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15" />
        </svg>
      ),
    },
    {
      id: 'presentation-gen',
      title: 'AI Presentation Generator',
      description: 'Generate polished multi-slide pitch decks and academic presentations with AI-generated visuals.',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="2" y="3" width="20" height="14" rx="2" ry="2" />
          <line x1="8" y1="21" x2="16" y2="21" />
          <line x1="12" y1="17" x2="12" y2="21" />
        </svg>
      ),
    },
    {
      id: 'viva-gen',
      title: 'Academic Viva Generator',
      description: 'Predict critical examiner questions tailored to your specific thesis or presentation topic.',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10" />
          <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
          <line x1="12" y1="17" x2="12.01" y2="17" />
        </svg>
      ),
    },
    {
      id: 'auth-cloud',
      title: 'Secure Session Telemetry',
      description: 'Firebase cloud identity, session history tracking, and downloadable PDF performance audits.',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
        </svg>
      ),
    },
  ];

  return (
    <div className="landing-page">
      {/* ── 1. Minimal Sticky Navbar ── */}
      <header className="landing-nav">
        <div className="landing-nav-container">
          <Link to="/" className="landing-logo">
            <span className="landing-logo-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />
              </svg>
            </span>
            Presenova
          </Link>

          <nav>
            <ul className="landing-nav-menu">
              <li><a href="#features" className="landing-nav-link">Features</a></li>
              <li><a href="#how-it-works" className="landing-nav-link">How it Works</a></li>
              <li><a href="#highlights" className="landing-nav-link">Highlights</a></li>
            </ul>
          </nav>

          <div className="landing-nav-actions">
            <button
              onClick={toggleTheme}
              className="landing-theme-btn"
              title={isLightTheme ? 'Switch to Dark Mode' : 'Switch to Light Mode'}
              aria-label="Toggle Color Theme"
            >
              {isLightTheme ? (
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
                </svg>
              ) : (
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="5" />
                  <line x1="12" y1="1" x2="12" y2="3" />
                  <line x1="12" y1="21" x2="12" y2="23" />
                  <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
                  <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
                  <line x1="1" y1="12" x2="3" y2="12" />
                  <line x1="21" y1="12" x2="23" y2="12" />
                  <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
                  <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
                </svg>
              )}
            </button>

            <Link to="/login" className="btn btn-ghost">Log In</Link>
            <Link to="/login" className="btn btn-primary">Get Started</Link>

            <button
              className="landing-hamburger"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              aria-label="Toggle navigation menu"
            >
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                {mobileMenuOpen ? (
                  <>
                    <line x1="18" y1="6" x2="6" y2="18" />
                    <line x1="6" y1="6" x2="18" y2="18" />
                  </>
                ) : (
                  <>
                    <line x1="3" y1="12" x2="21" y2="12" />
                    <line x1="3" y1="6" x2="21" y2="6" />
                    <line x1="3" y1="18" x2="21" y2="18" />
                  </>
                )}
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile menu dropdown */}
        <div className={`landing-mobile-drawer ${mobileMenuOpen ? 'open' : ''}`}>
          <div className="landing-mobile-links">
            <a
              href="#features"
              className="landing-mobile-link"
              onClick={() => setMobileMenuOpen(false)}
            >
              Features
            </a>
            <a
              href="#how-it-works"
              className="landing-mobile-link"
              onClick={() => setMobileMenuOpen(false)}
            >
              How it Works
            </a>
            <a
              href="#highlights"
              className="landing-mobile-link"
              onClick={() => setMobileMenuOpen(false)}
            >
              Highlights
            </a>
          </div>
          <Link
            to="/login"
            className="btn btn-primary"
            style={{ width: '100%', minHeight: '48px' }}
            onClick={() => setMobileMenuOpen(false)}
          >
            Get Started Free
          </Link>
        </div>
      </header>

      {/* ── 2. Hero Section ── */}
      <main>
        <section className="landing-hero">
          <div className="hero-badge">
            <span>✨</span> AI-Powered Presentation Coaching Platform
          </div>

          <h1 className="hero-headline">
            Master Your Presentations with <span>Real-Time AI Coaching</span>
          </h1>

          <p className="hero-subheading">
            Evaluate slide decks against the 7Cs communication framework, analyze vocal delivery pace, simulate rigorous academic viva defense, and refine presentations seamlessly.
          </p>

          <div className="hero-cta-group">
            <Link to="/login" className="btn btn-primary" style={{ padding: '0.85rem 2rem', fontSize: '1rem' }}>
              Get Started Free
            </Link>
            <a href="#how-it-works" className="btn btn-secondary" style={{ padding: '0.85rem 1.8rem', fontSize: '1rem' }}>
              See How It Works
            </a>
          </div>

          {/* Clean Dashboard Preview Mock */}
          <div className="hero-mockup-wrapper" aria-hidden="true">
            <div className="mockup-header">
              <div className="mockup-dots">
                <span className="mockup-dot" />
                <span className="mockup-dot" />
                <span className="mockup-dot" />
              </div>
              <span className="mockup-title">Presenova Multi-Modal Telemetry</span>
              <span style={{ fontSize: '0.75rem', color: 'var(--success)', fontWeight: 600 }}>● Engine Active</span>
            </div>

            <div className="mockup-grid">
              <div className="mockup-card">
                <span className="mockup-card-title">Overall Performance Score</span>
                <div className="mockup-score-row">
                  <span className="mockup-score-val">94</span>
                  <span className="mockup-score-label">+12% vs last session</span>
                </div>
                <div className="mockup-bars">
                  <div className="mockup-bar-item">
                    <span>Clarity & Conciseness</span>
                    <div className="mockup-bar-track"><div className="mockup-bar-fill" style={{ width: '92%' }} /></div>
                  </div>
                  <div className="mockup-bar-item">
                    <span>Pacing & Rhythm (142 WPM)</span>
                    <div className="mockup-bar-track"><div className="mockup-bar-fill" style={{ width: '88%' }} /></div>
                  </div>
                  <div className="mockup-bar-item">
                    <span>7Cs Communication Compliance</span>
                    <div className="mockup-bar-track"><div className="mockup-bar-fill" style={{ width: '96%' }} /></div>
                  </div>
                </div>
              </div>

              <div className="mockup-card">
                <span className="mockup-card-title">Live AI Defense Simulation</span>
                <div className="mockup-chat-preview">
                  <div className="mockup-chat-bubble mockup-chat-ai">
                    <strong>Examiner AI:</strong> How does your model handle edge-case noise during vocal inflection shifts?
                  </div>
                  <div className="mockup-chat-bubble mockup-chat-user">
                    <strong>Presenter:</strong> We apply continuous spectral filtering with adaptive sliding window buffers...
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ── 3. Features Grid ── */}
        <section id="features" className="landing-section">
          <div className="section-header">
            <span className="section-tag">Capabilities</span>
            <h2 className="section-title">8 Comprehensive Coaching Modules</h2>
            <p className="section-subtitle">
              Every tool you need to analyze, practice, and perfect public speaking and technical defenses.
            </p>
          </div>

          <div className="features-grid">
            {featureList.map((f) => (
              <div key={f.id} className="feature-card-item">
                <div className="feature-icon-box">
                  {f.icon}
                </div>
                <h3 className="feature-title">{f.title}</h3>
                <p className="feature-description">{f.description}</p>
              </div>
            ))}
          </div>
        </section>

        {/* ── 4. How It Works ── */}
        <section id="how-it-works" className="landing-section" style={{ paddingTop: '2rem' }}>
          <div className="section-header">
            <span className="section-tag">Process</span>
            <h2 className="section-title">How Presenova Works</h2>
            <p className="section-subtitle">
              Three streamlined steps from rough draft to confident, polished delivery.
            </p>
          </div>

          <div className="steps-grid">
            <div className="step-card">
              <span className="step-number">01</span>
              <h3 className="step-title">Upload or Connect</h3>
              <p className="step-text">
                Import your PowerPoint deck, enter speech transcripts, or activate your microphone and webcam for live rehearsal.
              </p>
            </div>

            <div className="step-card">
              <span className="step-number">02</span>
              <h3 className="step-title">Multi-Modal AI Analysis</h3>
              <p className="step-text">
                Receive instant metrics across the 7Cs communication framework, speech cadence, filler words, and slide readability.
              </p>
            </div>

            <div className="step-card">
              <span className="step-number">03</span>
              <h3 className="step-title">Improve & Track Progress</h3>
              <p className="step-text">
                Practice simulated defense questions, apply smart slide rewrites, and track performance trends over time.
              </p>
            </div>
          </div>
        </section>

        {/* ── 5. Highlights Strip ── */}
        <section id="highlights" className="highlights-strip">
          <div className="highlights-container">
            <div className="highlight-item">
              <span className="highlight-label">
                <span>⚡</span> Real-Time Latency
              </span>
              <p className="highlight-desc">Instant WebSocket-driven telemetry and speech feedback as you speak.</p>
            </div>

            <div className="highlight-item">
              <span className="highlight-label">
                <span>🛡️</span> 7Cs Standard
              </span>
              <p className="highlight-desc">Strict compliance scoring for Clarity, Conciseness, Concreteness, and Correctness.</p>
            </div>

            <div className="highlight-item">
              <span className="highlight-label">
                <span>🔒</span> Privacy First
              </span>
              <p className="highlight-desc">Isolated session boundaries and secure Firebase JWT token verification.</p>
            </div>

            <div className="highlight-item">
              <span className="highlight-label">
                <span>💻</span> Multi-Platform
              </span>
              <p className="highlight-desc">Responsive modern web platform paired with cross-platform desktop executables.</p>
            </div>
          </div>
        </section>

        {/* ── 6. Final CTA Section ── */}
        <section className="landing-cta-section">
          <div className="cta-box">
            <h2 className="cta-headline">Ready to Perfect Your Next Presentation?</h2>
            <p className="cta-subtext">
              Join students, researchers, and professionals who master their communication skills with Presenova.
            </p>
            <Link to="/login" className="btn btn-primary" style={{ padding: '0.9rem 2.5rem', fontSize: '1.05rem' }}>
              Get Started Free
            </Link>
          </div>
        </section>
      </main>

      {/* ── 7. Minimal Footer ── */}
      <footer className="landing-footer">
        <div className="footer-container">
          <div className="footer-top">
            <Link to="/" className="landing-logo">
              <span className="landing-logo-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />
                </svg>
              </span>
              Presenova
            </Link>

            <ul className="footer-links">
              <li><a href="#features" className="footer-link">Features</a></li>
              <li><a href="#how-it-works" className="footer-link">How it Works</a></li>
              <li><Link to="/download" className="footer-link">Download Desktop App</Link></li>
              <li><Link to="/login" className="footer-link">Log In</Link></li>
            </ul>
          </div>

          <div className="footer-bottom">
            <span>Presenova — AI-Powered Presentation Coaching Platform</span>
            <span>Final Year Project (FYP) © 2026. All rights reserved.</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
