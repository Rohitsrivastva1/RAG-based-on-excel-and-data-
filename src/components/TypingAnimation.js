import React, { useState, useEffect } from 'react';

const TypingAnimation = ({ text, speed = 30, onComplete }) => {
  const [displayedText, setDisplayedText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (currentIndex < text.length) {
      const timeout = setTimeout(() => {
        setDisplayedText(prev => prev + text[currentIndex]);
        setCurrentIndex(prev => prev + 1);
      }, speed);

      return () => clearTimeout(timeout);
    } else if (onComplete) {
      onComplete();
    }
  }, [currentIndex, text, speed, onComplete]);

  useEffect(() => {
    setDisplayedText('');
    setCurrentIndex(0);
  }, [text]);

  return (
    <div style={{ position: 'relative' }}>
      {displayedText}
      {currentIndex < text.length && (
        <span 
          style={{
            display: 'inline-block',
            width: '2px',
            height: '1.2em',
            backgroundColor: '#00d4aa',
            marginLeft: '2px',
            animation: 'blink 1s infinite'
          }}
        />
      )}
      <style jsx>{`
        @keyframes blink {
          0%, 50% { opacity: 1; }
          51%, 100% { opacity: 0; }
        }
      `}</style>
    </div>
  );
};

export default TypingAnimation;
