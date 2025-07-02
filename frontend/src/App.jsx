import React, { useState, useRef } from 'react';
import { Play, Square, Loader2, Volume2 } from 'lucide-react';
import './App.css'; // Import the new CSS file

const TTSApp = () => {
  const [text, setText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [error, setError] = useState('');
  const currentAudioRef = useRef(null);

  const generateAndPlayTTS = async () => {
    if (!text.trim()) return;
    
    setIsLoading(true);
    setError('');
    
    try {
      // Stop any currently playing audio
      if (currentAudioRef.current) {
        currentAudioRef.current.pause();
        currentAudioRef.current = null;
        setIsPlaying(false);
      }

      const response = await fetch('http://localhost:8000/generate-speech', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          text: text,
          voice: 'default',
          speed: 1.0
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);
      
      // Create and play audio
      const audio = new Audio(audioUrl);
      currentAudioRef.current = audio;
      
      audio.onplay = () => setIsPlaying(true);
      audio.onended = () => {
        setIsPlaying(false);
        URL.revokeObjectURL(audioUrl);
        currentAudioRef.current = null;
      };
      audio.onerror = () => {
        setError('Error playing audio');
        setIsPlaying(false);
        currentAudioRef.current = null;
      };
      
      await audio.play();
      
    } catch (err) {
      setError(`Failed to generate speech: ${err.message}`);
      setIsPlaying(false);
    } finally {
      setIsLoading(false);
    }
  };

  const stopPlayback = () => {
    if (currentAudioRef.current) {
      currentAudioRef.current.pause();
      currentAudioRef.current = null;
      setIsPlaying(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      generateAndPlayTTS();
    }
  };

  const getStatus = () => {
    if (isLoading) return { class: 'tts-status-loading', text: '🔄 Generating...' };
    if (isPlaying) return { class: 'tts-status-ready', text: '🔊 Playing' };
    if (error) return { class: 'tts-status-error', text: '❌ Error' };
    return { class: 'tts-status-ready', text: '✅ Ready' };
  };

  const status = getStatus();

  return (
    <div className="tts-container">
      <div className="tts-card">
        <div className="tts-header">
          <div className="tts-header-icon">
            <Volume2 className="tts-icon" />
            <h1 className="tts-title">Voice Studio</h1>
          </div>
          <p className="tts-subtitle">Transform your text into natural speech instantly</p>
          <div className={`tts-status ${status.class}`}>
            {status.text}
          </div>
        </div>

        <div className="tts-input-section">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Enter your text here... Press Enter to generate speech instantly!"
            className="tts-textarea"
            disabled={isLoading}
          />
          <div className="tts-char-counter">
            {text.length} / 1000 characters
          </div>
        </div>

        {error && (
          <div className="tts-error">
            {error}
          </div>
        )}

        <div className="tts-button-section">
          {!isPlaying ? (
            <button
              onClick={generateAndPlayTTS}
              disabled={isLoading || !text.trim()}
              className="tts-button tts-button-primary"
            >
              {isLoading ? (
                <>
                  <Loader2 className="tts-spinner" />
                  <span>Generating Speech...</span>
                </>
              ) : (
                <>
                  <Play size={20} />
                  <span>Generate & Play</span>
                </>
              )}
            </button>
          ) : (
            <button
              onClick={stopPlayback}
              className="tts-button tts-button-secondary"
            >
              <Square size={20} />
              <span>Stop Playback</span>
            </button>
          )}
        </div>

        <div className="tts-footer">
          <p>Powered by open-source espeak TTS engine</p>
          <p>Press <kbd className="tts-kbd">Enter</kbd> in the text area for quick generation</p>
        </div>
      </div>
    </div>
  );
};

export default TTSApp;