import React, { useState, useEffect } from 'react';

interface ExcitingLoaderProps {
  duration?: number; // Total loading duration in seconds
}

const ExcitingLoader: React.FC<ExcitingLoaderProps> = ({ duration = 30 }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [progress, setProgress] = useState(0);

  const steps = [
    { icon: '📊', text: 'Processing your data', color: '#ff6b6b' },
    { icon: '🔍', text: 'Finding hidden patterns', color: '#4ecdc4' },
    { icon: '🎯', text: 'Generating insights', color: '#45b7d1' },
    { icon: '✨', text: 'Almost ready!', color: '#96ceb4' },
  ];

  const tips = [
    '💡 Pro tip: Our AI is analyzing sentiment, clustering topics, and detecting patterns in your data!',
    '🧠 The AI brain is processing thousands of data points to find meaningful insights!',
    '⚡ Advanced machine learning algorithms are working behind the scenes!',
    '🎨 Creating beautiful visualizations and interactive charts for you!',
    '🔬 Using cutting-edge NLP techniques to understand your feedback!',
  ];

  const [currentTip, setCurrentTip] = useState(0);

  useEffect(() => {
    const stepInterval = setInterval(() => {
      setCurrentStep((prev) => (prev + 1) % steps.length);
    }, duration * 1000 / steps.length);

    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) return 100;
        return prev + (100 / (duration * 10)); // Update every 100ms
      });
    }, 100);

    const tipInterval = setInterval(() => {
      setCurrentTip((prev) => (prev + 1) % tips.length);
    }, 3000);

    return () => {
      clearInterval(stepInterval);
      clearInterval(progressInterval);
      clearInterval(tipInterval);
    };
  }, [duration, steps.length, tips.length]);

  return (
    <div className="loading-state">
      <div className="loading-animation">
        <div className="loading-brain">
          <div className="brain-lobe lobe-1"></div>
          <div className="brain-lobe lobe-2"></div>
          <div className="brain-lobe lobe-3"></div>
          <div className="brain-lobe lobe-4"></div>
        </div>
        <div className="loading-particles">
          <div className="particle particle-1"></div>
          <div className="particle particle-2"></div>
          <div className="particle particle-3"></div>
          <div className="particle particle-4"></div>
          <div className="particle particle-5"></div>
        </div>
      </div>
      <div className="loading-content">
        <h2 className="loading-title">🧠 AI Brain is Thinking...</h2>
        <div className="loading-steps">
          {steps.map((step, index) => (
            <div
              key={index}
              className={`loading-step ${index === currentStep ? 'active' : ''}`}
              style={{ '--step-color': step.color } as React.CSSProperties}
            >
              <span className="step-icon">{step.icon}</span>
              <span className="step-text">{step.text}</span>
            </div>
          ))}
        </div>
        <div className="loading-progress">
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${Math.min(progress, 100)}%` }}
            ></div>
          </div>
          <div className="loading-tips">
            <p className="tip-text">{tips[currentTip]}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExcitingLoader;
