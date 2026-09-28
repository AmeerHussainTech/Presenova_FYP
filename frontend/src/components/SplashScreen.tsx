/**
 * SplashScreen Component
 * Minimalist session-based splash greeting with background server wake-up probe
 */

import React, { useEffect, useState } from 'react';
import { healthCheck } from '../services/api';
import './SplashScreen.css';

const SESSION_KEY = 'presenova_splash_shown';

const SplashScreen: React.FC = () => {
  const [isVisible, setIsVisible] = useState<boolean>(() => {
    try {
      return !sessionStorage.getItem(SESSION_KEY);
    } catch {
      return false;
    }
  });

  const [isFading, setIsFading] = useState<boolean>(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!isVisible) return;

    let isMounted = true;

    // Minimum display duration (1.2s)
    const minTimer = new Promise<void>((resolve) => setTimeout(resolve, 1200));

    // Notice shown if backend takes > 2s to wake up (Render cold-start)
    const wakeNoticeTimer = setTimeout(() => {
      if (isMounted) {
        setStatusMessage('Connecting to AI engine...');
      }
    }, 2000);

    // Concurrently trigger health check with an 8s hard ceiling
    const healthPromise = Promise.race([
      healthCheck(),
      new Promise<boolean>((resolve) => setTimeout(() => resolve(true), 8000)),
    ]);

    Promise.all([minTimer, healthPromise]).then(() => {
      if (!isMounted) return;
      clearTimeout(wakeNoticeTimer);

      setIsFading(true);

      try {
        sessionStorage.setItem(SESSION_KEY, 'true');
      } catch (err) {
        console.warn('sessionStorage is unavailable:', err);
      }

      // Remove from DOM after fade out completes
      setTimeout(() => {
        if (isMounted) {
          setIsVisible(false);
        }
      }, 400);
    });

    return () => {
      isMounted = false;
      clearTimeout(wakeNoticeTimer);
    };
  }, [isVisible]);

  if (!isVisible) return null;

  return (
    <div
      className={`splash-overlay ${isFading ? 'fade-out' : ''}`}
      role="status"
      aria-label="Loading Presenova"
      aria-live="polite"
    >
      <div className="splash-content">
        <div className="splash-logo-wrap">
          <svg
            className="splash-logo-icon"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />
          </svg>
        </div>

        <h1 className="splash-title">
          Presenova<span>.</span>
        </h1>
        <p className="splash-tagline">AI Presentation & Speech Coaching Platform</p>

        <div className="splash-loader-bar" aria-hidden="true">
          <div className="splash-loader-fill" />
        </div>

        {statusMessage && (
          <div className="splash-status">
            <span className="splash-status-dot" />
            <span>{statusMessage}</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default SplashScreen;
