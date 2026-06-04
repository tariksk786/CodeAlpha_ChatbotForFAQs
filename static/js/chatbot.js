/**
 * Frontend Chat interface logic for AI FAQ Chatbot
 * Manages UI rendering, REST APIs communication, persistent history, and document exports.
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');
    const clearHistoryBtn = document.getElementById('clear-history');
    const exportPdfBtn = document.getElementById('export-pdf');
    const exportTxtBtn = document.getElementById('export-txt');
    const themeToggleBtn = document.getElementById('theme-toggle');
    const voiceInputBtn = document.getElementById('voice-input-btn');
    const initialSuggestions = document.getElementById('initial-suggestions');

    // State Variables
    let chatHistory = [];
    const HISTORY_KEY = 'faq_chatbot_history';

    // Theme toggling initialization
    const savedTheme = localStorage.getItem('theme') || 'dark';
    if (savedTheme === 'light') {
        document.body.classList.add('light-theme');
        updateThemeToggleIcon('light');
    } else {
        updateThemeToggleIcon('dark');
    }

    // Load Chat History from LocalStorage
    loadPersistentHistory();

    // Event Listeners
    if (chatForm) {
        chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            submitMessage();
        });
    }

    if (clearHistoryBtn) {
        clearHistoryBtn.addEventListener('click', clearChatHistory);
    }

    if (exportPdfBtn) {
        exportPdfBtn.addEventListener('click', exportToPDF);
    }

    if (exportTxtBtn) {
        exportTxtBtn.addEventListener('click', exportToTXT);
    }

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', toggleTheme);
    }

    // Helper functions for Chat History
    function loadPersistentHistory() {
        const stored = localStorage.getItem(HISTORY_KEY);
        if (stored) {
            try {
                chatHistory = JSON.parse(stored);
                if (chatHistory.length > 0) {
                    // Hide default welcome suggestions if history exists
                    if (initialSuggestions) initialSuggestions.style.display = 'none';
                    
                    chatHistory.forEach(msg => {
                        appendMessage(msg.text, msg.sender, msg.metadata, false);
                    });
                    scrollToBottom();
                }
            } catch (e) {
                console.error("Error parsing chat history:", e);
                chatHistory = [];
            }
        }
    }

    function saveMessageToHistory(text, sender, metadata = null) {
        chatHistory.push({ text, sender, metadata });
        localStorage.setItem(HISTORY_KEY, JSON.stringify(chatHistory));
        if (initialSuggestions) initialSuggestions.style.display = 'none';
    }

    function clearChatHistory() {
        Swal.fire({
            title: 'Clear Chat History?',
            text: "This will erase your current session log. You cannot undo this action.",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#4F46E5',
            cancelButtonColor: '#1e293b',
            confirmButtonText: 'Yes, clear it!'
        }).then((result) => {
            if (result.isConfirmed) {
                chatHistory = [];
                localStorage.removeItem(HISTORY_KEY);
                chatMessages.innerHTML = '';
                
                // Show initial suggestions again
                if (initialSuggestions) initialSuggestions.style.display = 'block';
                
                // Add default welcome message
                appendWelcomeMessage();
                
                Swal.fire({
                    title: 'Cleared!',
                    text: 'Your chat history has been reset.',
                    icon: 'success',
                    timer: 1500,
                    showConfirmButton: false
                });
            }
        });
    }

    function appendWelcomeMessage() {
        const welcome = "Hello! I am your AI-powered FAQ assistant. Ask me anything, or select one of the suggested questions below.";
        appendMessage(welcome, 'bot', null, false);
    }

    // Append Message to Chat Container
    function appendMessage(text, sender, metadata = null, save = true) {
        if (!chatMessages) return;

        const isBot = sender === 'bot';
        const bubbleWrapper = document.createElement('div');
        bubbleWrapper.className = `d-flex w-100 mb-3 ${isBot ? 'justify-content-start' : 'justify-content-end'}`;

        const bubble = document.createElement('div');
        bubble.className = `chat-bubble ${isBot ? 'chat-bubble-bot' : 'chat-bubble-user'} fade-in-up`;

        // Parse markdown links & newlines simply
        let formattedText = text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/\n/g, "<br>");
        
        // Match [link text](url) and replace with anchor
        formattedText = formattedText.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" class="text-info font-weight-bold">$1</a>');

        bubble.innerHTML = `<div>${formattedText}</div>`;

        // If bot message and contains confidence scores or feedback mechanisms
        if (isBot && metadata) {
            // Confidence Meter
            if (metadata.confidence !== undefined && metadata.confidence > 0) {
                const confVal = metadata.confidence;
                let confClass = 'confidence-low';
                if (confVal >= 75) confClass = 'confidence-high';
                else if (confVal >= 40) confClass = 'confidence-medium';

                const badge = document.createElement('div');
                badge.className = `mt-2 d-inline-block confidence-badge ${confClass}`;
                badge.innerHTML = `<i class="fas fa-bullseye me-1"></i> Match Confidence: ${confVal}%`;
                bubble.appendChild(badge);
            }

            // Suggestions List
            if (metadata.related_questions && metadata.related_questions.length > 0) {
                const suggContainer = document.createElement('div');
                suggContainer.className = 'suggested-questions-container';
                
                const title = document.createElement('div');
                title.className = 'text-muted small mt-2 w-100';
                title.innerHTML = 'Related questions you could ask:';
                suggContainer.appendChild(title);

                metadata.related_questions.forEach(q => {
                    const btn = document.createElement('button');
                    btn.className = 'btn-suggestion';
                    btn.innerText = q;
                    btn.addEventListener('click', () => {
                        chatInput.value = q;
                        submitMessage();
                    });
                    suggContainer.appendChild(btn);
                });
                bubble.appendChild(suggContainer);
            }

            // Thumbs Up / Down Feedback buttons
            if (metadata.query_id) {
                const feedbackDiv = document.createElement('div');
                feedbackDiv.className = 'chat-feedback-buttons';
                feedbackDiv.innerHTML = `
                    <button class="btn-feedback" data-feedback="1" data-query-id="${metadata.query_id}" title="Helpful">
                        <i class="far fa-thumbs-up"></i>
                    </button>
                    <button class="btn-feedback" data-feedback="-1" data-query-id="${metadata.query_id}" title="Not Helpful">
                        <i class="far fa-thumbs-down"></i>
                    </button>
                `;
                
                // Add event listeners to feedback buttons
                feedbackDiv.querySelectorAll('.btn-feedback').forEach(btn => {
                    btn.addEventListener('click', function() {
                        const score = parseInt(this.getAttribute('data-feedback'));
                        const qId = parseInt(this.getAttribute('data-query-id'));
                        submitFeedback(qId, score, feedbackDiv);
                    });
                });
                bubble.appendChild(feedbackDiv);
            }
        }

        bubbleWrapper.appendChild(bubble);
        chatMessages.appendChild(bubbleWrapper);
        scrollToBottom();

        if (save) {
            saveMessageToHistory(text, sender, metadata);
        }
    }

    // Submit Message to Backend API
    function submitMessage() {
        const text = chatInput.value.trim();
        if (!text) return;

        // Clear input field
        chatInput.value = '';
        
        // Append user message to UI
        appendMessage(text, 'user');

        // Show typing indicator
        showTypingIndicator();

        // API Call
        fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        })
        .then(response => {
            if (!response.ok) throw new Error("HTTP error " + response.status);
            return response.json();
        })
        .then(data => {
            hideTypingIndicator();
            appendMessage(data.answer, 'bot', {
                confidence: data.confidence,
                related_questions: data.related_questions,
                query_id: data.query_id
            });
            
            // Speak response if Text-To-Speech is active/enabled (implemented in voice.js)
            if (window.FAQVoiceAssistant && window.FAQVoiceAssistant.isSpeakActive()) {
                window.FAQVoiceAssistant.speak(data.answer);
            }
        })
        .catch(err => {
            hideTypingIndicator();
            appendMessage("I'm sorry, but I'm having trouble connecting to the server. Please check your network connection and try again.", 'bot');
            console.error("Chat error:", err);
        });
    }

    // Submit Feedback API
    function submitFeedback(queryId, score, container) {
        fetch('/api/chat/feedback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query_id: queryId, feedback: score })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                container.innerHTML = `<span class="text-success small"><i class="fas fa-check"></i> Thank you for your feedback!</span>`;
            } else {
                console.error("Feedback failed:", data.error);
            }
        })
        .catch(err => console.error("Feedback API error:", err));
    }

    // Show/Hide Typing Indicator
    function showTypingIndicator() {
        if (!chatMessages) return;
        const indicator = document.createElement('div');
        indicator.id = 'bot-typing-indicator';
        indicator.className = 'd-flex w-100 mb-3 justify-content-start';
        indicator.innerHTML = `
            <div class="chat-bubble chat-bubble-bot fade-in-up">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        `;
        chatMessages.appendChild(indicator);
        scrollToBottom();
    }

    function hideTypingIndicator() {
        const ind = document.getElementById('bot-typing-indicator');
        if (ind) ind.remove();
    }

    function scrollToBottom() {
        if (chatMessages) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    // Setup clicking on pre-loaded greeting suggestions
    document.querySelectorAll('.suggestion-card').forEach(card => {
        card.addEventListener('click', function() {
            const question = this.getAttribute('data-question');
            if (question) {
                chatInput.value = question;
                submitMessage();
            }
        });
    });

    // Theme toggler implementation
    function toggleTheme() {
        const isLight = document.body.classList.toggle('light-theme');
        const theme = isLight ? 'light' : 'dark';
        localStorage.setItem('theme', theme);
        updateThemeToggleIcon(theme);
    }

    function updateThemeToggleIcon(theme) {
        if (!themeToggleBtn) return;
        if (theme === 'light') {
            themeToggleBtn.innerHTML = '<i class="fas fa-moon"></i>';
            themeToggleBtn.title = 'Switch to Dark Mode';
        } else {
            themeToggleBtn.innerHTML = '<i class="fas fa-sun"></i>';
            themeToggleBtn.title = 'Switch to Light Mode';
        }
    }

    // Exporters
    function exportToTXT() {
        if (chatHistory.length === 0) {
            Swal.fire("Chat is empty", "Start talking to the bot before downloading a transcript.", "info");
            return;
        }

        let textContent = "=========================================\n";
        textContent += "      AI FAQ CHATBOT TRANSCRIPT\n";
        textContent += "=========================================\n\n";

        chatHistory.forEach((msg, idx) => {
            const time = new Date().toLocaleTimeString();
            const senderName = msg.sender === 'user' ? 'USER' : 'AI BOT';
            textContent += `[${time}] ${senderName}: ${msg.text}\n`;
            if (msg.metadata && msg.metadata.confidence) {
                textContent += `(Match Confidence: ${msg.metadata.confidence}%)\n`;
            }
            textContent += "\n";
        });

        const blob = new Blob([textContent], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `faq_chatbot_chat_${new Date().toISOString().slice(0,10)}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    function exportToPDF() {
        if (chatHistory.length === 0) {
            Swal.fire("Chat is empty", "Start talking to the bot before exporting to PDF.", "info");
            return;
        }

        // Verify if jsPDF is loaded
        if (!window.jspdf) {
            Swal.fire("Export Error", "jsPDF library is not loaded. Please verify your connection.", "error");
            return;
        }

        try {
            const { jsPDF } = window.jspdf;
            const doc = new jsPDF();
            
            doc.setFont("Helvetica", "bold");
            doc.setFontSize(18);
            doc.text("AI FAQ Chatbot Conversation Transcript", 14, 20);
            
            doc.setFont("Helvetica", "normal");
            doc.setFontSize(10);
            doc.text(`Generated on: ${new Date().toLocaleString()}`, 14, 27);
            doc.line(14, 30, 196, 30);
            
            let y = 38;
            const pageHeight = doc.internal.pageSize.height;
            
            chatHistory.forEach((msg) => {
                // Check page height limit to create new page if necessary
                if (y > pageHeight - 30) {
                    doc.addPage();
                    y = 20;
                }
                
                const senderName = msg.sender === 'user' ? 'User' : 'AI Chatbot';
                doc.setFont("Helvetica", "bold");
                doc.setFontSize(11);
                doc.text(`${senderName}:`, 14, y);
                
                doc.setFont("Helvetica", "normal");
                doc.setFontSize(11);
                
                const lines = doc.splitTextToSize(msg.text, 175);
                y += 6;
                
                lines.forEach(line => {
                    if (y > pageHeight - 20) {
                        doc.addPage();
                        y = 20;
                    }
                    doc.text(line, 14, y);
                    y += 6;
                });
                
                if (msg.metadata && msg.metadata.confidence) {
                    doc.setFont("Helvetica", "italic");
                    doc.setFontSize(9);
                    doc.setTextColor(100, 100, 100);
                    doc.text(`Match Confidence: ${msg.metadata.confidence}%`, 14, y);
                    doc.setTextColor(0, 0, 0);
                    y += 6;
                }
                
                y += 4; // Add extra padding between bubble paragraphs
            });
            
            doc.save(`faq_chatbot_chat_${new Date().toISOString().slice(0,10)}.pdf`);
        } catch (e) {
            console.error("PDF generation failed:", e);
            Swal.fire("Export Failed", "An error occurred while generating the PDF: " + e.message, "error");
        }
    }
});
