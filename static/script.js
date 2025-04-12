// State management
let isLoggedIn = false;
let chatHistory = [];

// DOM Elements
const loginSection = document.getElementById('login-section');
const chatInterface = document.getElementById('chat-interface');
const googleLoginButton = document.getElementById('google-login');
const saveKeysButton = document.getElementById('save-keys');
const sendButton = document.getElementById('send-button');
const userMessageInput = document.getElementById('user-message');
const chatHistoryDiv = document.getElementById('chat-history');
const responsePanels = {
    chatgpt: document.getElementById('chatgpt-response'),
    gemini: document.getElementById('gemini-response'),
    grok: document.getElementById('grok-response')
};

// Event Listeners
googleLoginButton.addEventListener('click', handleGoogleLogin);
saveKeysButton.addEventListener('click', saveApiKeys);
sendButton.addEventListener('click', sendMessage);
userMessageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

document.querySelectorAll('.select-response').forEach(button => {
    button.addEventListener('click', () => selectResponse(button.dataset.model));
});

// Functions
async function handleGoogleLogin() {
    try {
        const response = await fetch('/login');
        const data = await response.json();
        // In a real app, implement proper Google OAuth flow
        isLoggedIn = true;
        loginSection.classList.add('hidden');
        chatInterface.classList.remove('hidden');
    } catch (error) {
        console.error('Login failed:', error);
    }
}

async function saveApiKeys() {
    const apiKeys = {
        openai_key: document.getElementById('openai-key').value,
        gemini_key: document.getElementById('gemini-key').value,
        grok_key: document.getElementById('grok-key').value
    };

    try {
        const response = await fetch('/api/save-api-keys', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(apiKeys)
        });
        const data = await response.json();
        alert('API keys saved successfully!');
    } catch (error) {
        console.error('Failed to save API keys:', error);
        alert('Failed to save API keys');
    }
}

async function sendMessage() {
    const message = userMessageInput.value.trim();
    if (!message) return;

    // Add user message to chat history
    addMessageToHistory('user', message);
    userMessageInput.value = '';

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message })
        });
        const data = await response.json();

        // Display responses from each AI
        responsePanels.chatgpt.textContent = data.chatgpt;
        responsePanels.gemini.textContent = data.gemini;
        responsePanels.grok.textContent = data.grok;

        // By default, select ChatGPT's response
        selectResponse('chatgpt');
    } catch (error) {
        console.error('Failed to send message:', error);
        alert('Failed to send message');
    }
}

function selectResponse(model) {
    // Add the selected response to chat history
    const response = responsePanels[model].textContent;
    addMessageToHistory('ai', response, model);
}

function addMessageToHistory(role, content, model = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `p-4 rounded-lg ${
        role === 'user' ? 'bg-blue-100 ml-auto' : 'bg-gray-100'
    } max-w-[80%] ${role === 'user' ? 'ml-auto' : 'mr-auto'}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'font-medium';
    contentDiv.textContent = content;
    
    if (model) {
        const modelSpan = document.createElement('span');
        modelSpan.className = 'text-sm text-gray-500';
        modelSpan.textContent = ` (${model})`;
        contentDiv.appendChild(modelSpan);
    }
    
    messageDiv.appendChild(contentDiv);
    chatHistoryDiv.appendChild(messageDiv);
    chatHistoryDiv.scrollTop = chatHistoryDiv.scrollHeight;
}

async function recordFeedback(messageId, service, feedback) {
    try {
        const response = await fetch('/api/feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message_id: messageId,
                service: service,
                feedback: feedback
            })
        });
        
        if (response.ok) {
            updateMetrics();
        }
    } catch (error) {
        console.error('Error recording feedback:', error);
    }
}

async function updateMetrics() {
    try {
        const response = await fetch('/api/metrics');
        const metrics = await response.json();
        
        const metricsDisplay = document.getElementById('metrics-display');
        metricsDisplay.innerHTML = `
            <div class="metric">
                <span>Total API Calls:</span>
                <span>${metrics.total_calls}</span>
            </div>
            <div class="metric">
                <span>Total Cost:</span>
                <span>$${metrics.total_cost.toFixed(2)}</span>
            </div>
            <div class="metric">
                <span>Positive Feedback:</span>
                <span>${metrics.feedback_summary.positive}</span>
            </div>
            <div class="metric">
                <span>Negative Feedback:</span>
                <span>${metrics.feedback_summary.negative}</span>
            </div>
        `;
    } catch (error) {
        console.error('Error updating metrics:', error);
    }
}

// Update metrics every 30 seconds
setInterval(updateMetrics, 30000); 