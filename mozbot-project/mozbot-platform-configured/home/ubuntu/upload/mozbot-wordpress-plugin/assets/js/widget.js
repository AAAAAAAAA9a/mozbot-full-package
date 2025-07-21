/**
 * MozBot Widget Frontend Script
 * Handles the chat widget functionality on the frontend
 */

(function() {
    'use strict';
    
    // Check if MozBot config exists
    if (typeof mozbot_config === 'undefined') {
        console.warn('MozBot: Configuration not found');
        return;
    }
    
    // Widget state
    let isOpen = false;
    let messages = [];
    let isTyping = false;
    
    // Initialize widget when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initWidget);
    } else {
        initWidget();
    }
    
    function initWidget() {
        createWidgetHTML();
        bindEvents();
        addInitialMessage();
        applyCustomStyles();
    }
    
    function createWidgetHTML() {
        const container = document.getElementById('mozbot-widget-container');
        if (!container) {
            console.warn('MozBot: Widget container not found');
            return;
        }
        
        const widgetHTML = `
            <div id="mozbot-widget" class="mozbot-widget ${mozbot_config.position}">
                <div id="mozbot-chat-window" class="mozbot-chat-window" style="display: none;">
                    <div class="mozbot-header" style="background-color: ${mozbot_config.primary_color}">
                        <div class="mozbot-header-content">
                            <div class="mozbot-avatar">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                                </svg>
                            </div>
                            <div class="mozbot-info">
                                <div class="mozbot-name">${mozbot_config.bot_name}</div>
                                <div class="mozbot-status">Online now</div>
                            </div>
                        </div>
                        <div class="mozbot-controls">
                            <button id="mozbot-minimize" class="mozbot-control-btn" title="Minimize">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M19 13H5v-2h14v2z"/>
                                </svg>
                            </button>
                            <button id="mozbot-close" class="mozbot-control-btn" title="Close">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                                </svg>
                            </button>
                        </div>
                    </div>
                    
                    <div id="mozbot-messages" class="mozbot-messages">
                        <!-- Messages will be inserted here -->
                    </div>
                    
                    <div class="mozbot-input-area">
                        <div class="mozbot-input-container">
                            <textarea id="mozbot-input" placeholder="Type your message..." rows="1"></textarea>
                            <button id="mozbot-send" style="background-color: ${mozbot_config.primary_color}">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                                </svg>
                            </button>
                        </div>
                        <div class="mozbot-footer">
                            <div class="mozbot-actions">
                                <button class="mozbot-action-btn" title="Attach file">
                                    <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                                        <path d="M16.5 6v11.5c0 2.21-1.79 4-4 4s-4-1.79-4-4V5c0-1.38 1.12-2.5 2.5-2.5s2.5 1.12 2.5 2.5v10.5c0 .55-.45 1-1 1s-1-.45-1-1V6H10v9.5c0 1.38 1.12 2.5 2.5 2.5s2.5-1.12 2.5-2.5V5c0-2.21-1.79-4-4-4S7 2.79 7 5v12.5c0 3.04 2.46 5.5 5.5 5.5s5.5-2.46 5.5-5.5V6h-1.5z"/>
                                    </svg>
                                </button>
                                <button class="mozbot-action-btn" title="Emoji">
                                    <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                                        <path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5zm-7 0c.83 0 1.5-.67 1.5-1.5S9.33 8 8.5 8 7 8.67 7 9.5 7.67 11 8.5 11zm3.5 6.5c2.33 0 4.31-1.46 5.11-3.5H6.89c.8 2.04 2.78 3.5 5.11 3.5z"/>
                                    </svg>
                                </button>
                            </div>
                            <div class="mozbot-branding">Powered by MozBot</div>
                        </div>
                    </div>
                </div>
                
                <button id="mozbot-toggle" class="mozbot-toggle-btn" style="background-color: ${mozbot_config.primary_color}">
                    <svg id="mozbot-toggle-icon" width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M20 2H4c-1.1 0-1.99.9-1.99 2L2 22l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z"/>
                    </svg>
                </button>
            </div>
        `;
        
        container.innerHTML = widgetHTML;
        
        // Add CSS styles
        addWidgetStyles();
    }
    
    function addWidgetStyles() {
        if (document.getElementById('mozbot-widget-styles')) {
            return;
        }
        
        const styles = `
            <style id="mozbot-widget-styles">
                .mozbot-widget {
                    position: fixed;
                    z-index: 999999;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                }
                
                .mozbot-widget.bottom-right {
                    bottom: 20px;
                    right: 20px;
                }
                
                .mozbot-widget.bottom-left {
                    bottom: 20px;
                    left: 20px;
                }
                
                .mozbot-widget.top-right {
                    top: 20px;
                    right: 20px;
                }
                
                .mozbot-widget.top-left {
                    top: 20px;
                    left: 20px;
                }
                
                .mozbot-chat-window {
                    width: 350px;
                    height: 500px;
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
                    display: flex;
                    flex-direction: column;
                    margin-bottom: 15px;
                    animation: mozbotSlideIn 0.3s ease-out;
                }
                
                @keyframes mozbotSlideIn {
                    from {
                        opacity: 0;
                        transform: translateY(20px) scale(0.95);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0) scale(1);
                    }
                }
                
                .mozbot-header {
                    padding: 16px;
                    color: white;
                    border-radius: 12px 12px 0 0;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                
                .mozbot-header-content {
                    display: flex;
                    align-items: center;
                    gap: 12px;
                }
                
                .mozbot-avatar {
                    width: 36px;
                    height: 36px;
                    background: rgba(255,255,255,0.2);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                
                .mozbot-name {
                    font-weight: 600;
                    font-size: 14px;
                }
                
                .mozbot-status {
                    font-size: 12px;
                    opacity: 0.9;
                }
                
                .mozbot-controls {
                    display: flex;
                    gap: 8px;
                }
                
                .mozbot-control-btn {
                    background: rgba(255,255,255,0.2);
                    border: none;
                    color: white;
                    width: 28px;
                    height: 28px;
                    border-radius: 50%;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: background 0.2s;
                }
                
                .mozbot-control-btn:hover {
                    background: rgba(255,255,255,0.3);
                }
                
                .mozbot-messages {
                    flex: 1;
                    padding: 16px;
                    overflow-y: auto;
                    display: flex;
                    flex-direction: column;
                    gap: 12px;
                }
                
                .mozbot-message {
                    display: flex;
                    align-items: flex-start;
                    gap: 8px;
                    max-width: 85%;
                }
                
                .mozbot-message.user {
                    align-self: flex-end;
                    flex-direction: row-reverse;
                }
                
                .mozbot-message-avatar {
                    width: 28px;
                    height: 28px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 12px;
                    flex-shrink: 0;
                }
                
                .mozbot-message.bot .mozbot-message-avatar {
                    background: ${mozbot_config.primary_color};
                    color: white;
                }
                
                .mozbot-message.user .mozbot-message-avatar {
                    background: #e5e7eb;
                    color: #374151;
                }
                
                .mozbot-message-content {
                    padding: 10px 14px;
                    border-radius: 16px;
                    font-size: 14px;
                    line-height: 1.4;
                    word-wrap: break-word;
                }
                
                .mozbot-message.bot .mozbot-message-content {
                    background: ${mozbot_config.primary_color};
                    color: white;
                }
                
                .mozbot-message.user .mozbot-message-content {
                    background: #f3f4f6;
                    color: #374151;
                }
                
                .mozbot-typing {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    padding: 10px 14px;
                    background: ${mozbot_config.primary_color};
                    color: white;
                    border-radius: 16px;
                    max-width: 85%;
                }
                
                .mozbot-typing-dots {
                    display: flex;
                    gap: 4px;
                }
                
                .mozbot-typing-dot {
                    width: 6px;
                    height: 6px;
                    background: rgba(255,255,255,0.7);
                    border-radius: 50%;
                    animation: mozbotTyping 1.4s infinite ease-in-out;
                }
                
                .mozbot-typing-dot:nth-child(2) {
                    animation-delay: 0.2s;
                }
                
                .mozbot-typing-dot:nth-child(3) {
                    animation-delay: 0.4s;
                }
                
                @keyframes mozbotTyping {
                    0%, 60%, 100% {
                        transform: scale(1);
                        opacity: 0.7;
                    }
                    30% {
                        transform: scale(1.2);
                        opacity: 1;
                    }
                }
                
                .mozbot-input-area {
                    padding: 16px;
                    border-top: 1px solid #e5e7eb;
                }
                
                .mozbot-input-container {
                    display: flex;
                    gap: 8px;
                    align-items: flex-end;
                }
                
                #mozbot-input {
                    flex: 1;
                    border: 1px solid #d1d5db;
                    border-radius: 20px;
                    padding: 10px 16px;
                    font-size: 14px;
                    resize: none;
                    outline: none;
                    font-family: inherit;
                    max-height: 100px;
                }
                
                #mozbot-input:focus {
                    border-color: ${mozbot_config.primary_color};
                    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
                }
                
                #mozbot-send {
                    width: 40px;
                    height: 40px;
                    border: none;
                    border-radius: 50%;
                    color: white;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: transform 0.2s;
                }
                
                #mozbot-send:hover {
                    transform: scale(1.05);
                }
                
                #mozbot-send:disabled {
                    opacity: 0.5;
                    cursor: not-allowed;
                    transform: none;
                }
                
                .mozbot-footer {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-top: 8px;
                }
                
                .mozbot-actions {
                    display: flex;
                    gap: 8px;
                }
                
                .mozbot-action-btn {
                    background: none;
                    border: none;
                    color: #9ca3af;
                    cursor: pointer;
                    padding: 4px;
                    border-radius: 4px;
                    transition: color 0.2s;
                }
                
                .mozbot-action-btn:hover {
                    color: #6b7280;
                }
                
                .mozbot-branding {
                    font-size: 11px;
                    color: #9ca3af;
                }
                
                .mozbot-toggle-btn {
                    width: 60px;
                    height: 60px;
                    border: none;
                    border-radius: 50%;
                    color: white;
                    cursor: pointer;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: transform 0.2s, box-shadow 0.2s;
                }
                
                .mozbot-toggle-btn:hover {
                    transform: scale(1.05);
                    box-shadow: 0 6px 16px rgba(0,0,0,0.2);
                }
                
                @media (max-width: 480px) {
                    .mozbot-chat-window {
                        width: calc(100vw - 40px);
                        height: calc(100vh - 100px);
                        max-width: 350px;
                        max-height: 500px;
                    }
                }
            </style>
        `;
        
        document.head.insertAdjacentHTML('beforeend', styles);
    }
    
    function bindEvents() {
        const toggleBtn = document.getElementById('mozbot-toggle');
        const closeBtn = document.getElementById('mozbot-close');
        const minimizeBtn = document.getElementById('mozbot-minimize');
        const sendBtn = document.getElementById('mozbot-send');
        const input = document.getElementById('mozbot-input');
        
        if (toggleBtn) {
            toggleBtn.addEventListener('click', toggleWidget);
        }
        
        if (closeBtn) {
            closeBtn.addEventListener('click', closeWidget);
        }
        
        if (minimizeBtn) {
            minimizeBtn.addEventListener('click', minimizeWidget);
        }
        
        if (sendBtn) {
            sendBtn.addEventListener('click', sendMessage);
        }
        
        if (input) {
            input.addEventListener('keypress', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                }
            });
            
            input.addEventListener('input', autoResize);
        }
    }
    
    function toggleWidget() {
        const chatWindow = document.getElementById('mozbot-chat-window');
        const toggleIcon = document.getElementById('mozbot-toggle-icon');
        
        if (isOpen) {
            closeWidget();
        } else {
            openWidget();
        }
    }
    
    function openWidget() {
        const chatWindow = document.getElementById('mozbot-chat-window');
        const toggleIcon = document.getElementById('mozbot-toggle-icon');
        
        if (chatWindow && toggleIcon) {
            chatWindow.style.display = 'flex';
            toggleIcon.innerHTML = `
                <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
            `;
            isOpen = true;
            
            // Focus input
            setTimeout(() => {
                const input = document.getElementById('mozbot-input');
                if (input) input.focus();
            }, 300);
        }
    }
    
    function closeWidget() {
        const chatWindow = document.getElementById('mozbot-chat-window');
        const toggleIcon = document.getElementById('mozbot-toggle-icon');
        
        if (chatWindow && toggleIcon) {
            chatWindow.style.display = 'none';
            toggleIcon.innerHTML = `
                <path d="M20 2H4c-1.1 0-1.99.9-1.99 2L2 22l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z"/>
            `;
            isOpen = false;
        }
    }
    
    function minimizeWidget() {
        closeWidget();
    }
    
    function addInitialMessage() {
        if (mozbot_config.welcome_message) {
            addMessage(mozbot_config.welcome_message, 'bot');
        }
    }
    
    function sendMessage() {
        const input = document.getElementById('mozbot-input');
        const sendBtn = document.getElementById('mozbot-send');
        
        if (!input || !sendBtn) return;
        
        const message = input.value.trim();
        if (!message) return;
        
        // Add user message
        addMessage(message, 'user');
        
        // Clear input
        input.value = '';
        autoResize.call(input);
        
        // Disable send button temporarily
        sendBtn.disabled = true;
        
        // Show typing indicator
        showTyping();
        
        // Simulate bot response (replace with actual API call)
        setTimeout(() => {
            hideTyping();
            const response = getBotResponse(message);
            addMessage(response, 'bot');
            sendBtn.disabled = false;
        }, 1500);
    }
    
    function addMessage(text, sender) {
        const messagesContainer = document.getElementById('mozbot-messages');
        if (!messagesContainer) return;
        
        const messageElement = document.createElement('div');
        messageElement.className = `mozbot-message ${sender}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'mozbot-message-avatar';
        avatar.innerHTML = sender === 'bot' ? '🤖' : '👤';
        
        const content = document.createElement('div');
        content.className = 'mozbot-message-content';
        content.textContent = text;
        
        messageElement.appendChild(avatar);
        messageElement.appendChild(content);
        
        messagesContainer.appendChild(messageElement);
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        // Store message
        messages.push({ text, sender, timestamp: new Date() });
    }
    
    function showTyping() {
        const messagesContainer = document.getElementById('mozbot-messages');
        if (!messagesContainer || isTyping) return;
        
        const typingElement = document.createElement('div');
        typingElement.id = 'mozbot-typing-indicator';
        typingElement.className = 'mozbot-message bot';
        
        const avatar = document.createElement('div');
        avatar.className = 'mozbot-message-avatar';
        avatar.innerHTML = '🤖';
        
        const typingContent = document.createElement('div');
        typingContent.className = 'mozbot-typing';
        typingContent.innerHTML = `
            <div class="mozbot-typing-dots">
                <div class="mozbot-typing-dot"></div>
                <div class="mozbot-typing-dot"></div>
                <div class="mozbot-typing-dot"></div>
            </div>
        `;
        
        typingElement.appendChild(avatar);
        typingElement.appendChild(typingContent);
        
        messagesContainer.appendChild(typingElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        isTyping = true;
    }
    
    function hideTyping() {
        const typingIndicator = document.getElementById('mozbot-typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
        isTyping = false;
    }
    
    function getBotResponse(userMessage) {
        const message = userMessage.toLowerCase();
        
        if (message.includes('hello') || message.includes('hi')) {
            return "Hello! I'm here to help you. What can I assist you with today?";
        } else if (message.includes('help')) {
            return "I'd be happy to help! You can ask me about our products, services, or any questions you might have.";
        } else if (message.includes('price') || message.includes('cost')) {
            return "For pricing information, I'd recommend speaking with our sales team. Would you like me to connect you with them?";
        } else if (message.includes('support')) {
            return "I can help with basic support questions. For complex technical issues, I can escalate you to our support team.";
        } else {
            return "Thank you for your message! I'm processing your request. Is there anything specific I can help you with?";
        }
    }
    
    function autoResize() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 100) + 'px';
    }
    
    function applyCustomStyles() {
        // Apply any custom CSS from WordPress settings
        if (typeof mozbot_config.custom_css !== 'undefined' && mozbot_config.custom_css) {
            const customStyles = document.createElement('style');
            customStyles.textContent = mozbot_config.custom_css;
            document.head.appendChild(customStyles);
        }
    }
    
    // Public API
    window.MozBot = {
        open: openWidget,
        close: closeWidget,
        toggle: toggleWidget,
        sendMessage: function(message) {
            const input = document.getElementById('mozbot-input');
            if (input) {
                input.value = message;
                sendMessage();
            }
        },
        isOpen: function() {
            return isOpen;
        }
    };
    
})();

