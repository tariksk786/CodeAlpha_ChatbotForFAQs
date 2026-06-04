/**
 * Voice assistant service for Speech-To-Text and Text-To-Speech
 * Leverages HTML5 standard Web Speech API
 */

class VoiceAssistant {
    constructor() {
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.isListening = false;
        this.isSpeakingEnabled = false; // Toggle to read answers out loud
        this.speechVoice = null;

        this.initSpeechRecognition();
        this.initSpeechSynthesis();
    }

    initSpeechRecognition() {
        // Find standard or Webkit SpeechRecognition
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            console.warn("Speech Recognition API is not supported in this browser.");
            return;
        }

        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.lang = 'en-US';
        this.recognition.interimResults = false;
        this.recognition.maxAlternatives = 1;

        // Bind events
        this.recognition.onstart = () => {
            this.isListening = true;
            this.updateMicButtonUI(true);
        };

        this.recognition.onend = () => {
            this.isListening = false;
            this.updateMicButtonUI(false);
        };

        this.recognition.onerror = (e) => {
            console.error("Speech Recognition Error:", e);
            this.isListening = false;
            this.updateMicButtonUI(false);
            
            if (e.error === 'not-allowed') {
                Swal.fire("Microphone Blocked", "Please grant microphone permissions in your browser settings to use voice input.", "warning");
            }
        };

        this.recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            const inputField = document.getElementById('chat-input');
            const chatForm = document.getElementById('chat-form');
            
            if (inputField) {
                inputField.value = transcript;
                
                // Add minor glow feedback, then auto submit
                inputField.classList.add('glow-on-hover');
                setTimeout(() => {
                    inputField.classList.remove('glow-on-hover');
                    // Submit the chat form
                    if (chatForm) {
                        const eventSubmit = new Event('submit', { cancelable: true });
                        chatForm.dispatchEvent(eventSubmit);
                    }
                }, 800);
            }
        };
    }

    initSpeechSynthesis() {
        if (!this.synthesis) {
            console.warn("Speech Synthesis is not supported in this browser.");
            return;
        }

        // Load voices asynchronously
        const loadVoices = () => {
            const voices = this.synthesis.getVoices();
            // Try to find a high quality English voice (like Google US English or Microsoft David)
            this.speechVoice = voices.find(voice => voice.lang.startsWith('en-') && voice.name.includes('Google')) ||
                               voices.find(voice => voice.lang.startsWith('en-')) ||
                               voices[0];
        };

        if (this.synthesis.onvoiceschanged !== undefined) {
            this.synthesis.onvoiceschanged = loadVoices;
        }
        loadVoices();
    }

    startListening() {
        if (!this.recognition) {
            Swal.fire("Not Supported", "Speech recognition is not supported in your browser. Try Google Chrome or Microsoft Edge.", "info");
            return;
        }
        if (this.isListening) {
            this.recognition.stop();
        } else {
            // Stop any ongoing synthesis before listening
            this.stopSpeaking();
            try {
                this.recognition.start();
            } catch (e) {
                console.error(e);
            }
        }
    }

    speak(text) {
        if (!this.synthesis || !this.isSpeakingEnabled) return;

        // Cancel current speak
        this.stopSpeaking();

        // Remove html tag tokens or markdown from speech text
        const cleanText = text
            .replace(/<[^>]*>/g, '') // remove HTML tags
            .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '$1'); // remove markdown links, keep text

        const utterance = new SpeechSynthesisUtterance(cleanText);
        if (this.speechVoice) {
            utterance.voice = this.speechVoice;
        }
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        
        this.synthesis.speak(utterance);
    }

    stopSpeaking() {
        if (this.synthesis) {
            this.synthesis.cancel();
        }
    }

    toggleSpeakingMode(btnElement) {
        this.isSpeakingEnabled = !this.isSpeakingEnabled;
        if (!this.isSpeakingEnabled) {
            this.stopSpeaking();
        }
        
        // Update speaker UI
        if (btnElement) {
            if (this.isSpeakingEnabled) {
                btnElement.classList.add('text-info');
                btnElement.innerHTML = '<i class="fas fa-volume-up"></i>';
                btnElement.title = 'Mute AI Voice Output';
            } else {
                btnElement.classList.remove('text-info');
                btnElement.innerHTML = '<i class="fas fa-volume-mute"></i>';
                btnElement.title = 'Enable AI Voice Output';
            }
        }
    }

    isSpeakActive() {
        return this.isSpeakingEnabled;
    }

    updateMicButtonUI(active) {
        const micBtn = document.getElementById('voice-input-btn');
        if (!micBtn) return;

        if (active) {
            micBtn.classList.add('text-danger', 'animate-pulse');
            micBtn.innerHTML = '<i class="fas fa-microphone-alt"></i>';
            micBtn.style.animation = 'typing-bounce 1s infinite';
        } else {
            micBtn.classList.remove('text-danger', 'animate-pulse');
            micBtn.innerHTML = '<i class="fas fa-microphone"></i>';
            micBtn.style.animation = 'none';
        }
    }
}

// Instantiate and bind to global context on DOM Load
document.addEventListener('DOMContentLoaded', () => {
    window.FAQVoiceAssistant = new VoiceAssistant();

    // Bind Voice Microphone trigger button
    const micBtn = document.getElementById('voice-input-btn');
    if (micBtn) {
        micBtn.addEventListener('click', () => {
            window.FAQVoiceAssistant.startListening();
        });
    }

    // Bind Voice Output Toggle button
    const speakerBtn = document.getElementById('voice-output-toggle');
    if (speakerBtn) {
        speakerBtn.addEventListener('click', function() {
            window.FAQVoiceAssistant.toggleSpeakingMode(this);
        });
    }
});
