// Global state
let token = localStorage.getItem('token');
let currentUser = null;
let currentConversationId = null;
let conversations = [];

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    if (token) {
        checkAuth();
    } else {
        showScreen('login-screen');
    }

    // Add enter key handler for message input
    document.getElementById('message-input').addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && e.ctrlKey) {
            sendMessage();
        }
    });

    // Add enter key handler for login
    document.getElementById('login-password').addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            login();
        }
    });

    // Add enter key handler for register
    document.getElementById('register-password').addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            register();
        }
    });
});

// Screen management
function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(screen => {
        screen.style.display = 'none';
    });
    document.getElementById(screenId).style.display = 'block';
}

function showLoginTab(tab) {
    document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

    if (tab === 'login') {
        document.querySelector('[onclick="showLoginTab(\'login\')"]').classList.add('active');
        document.getElementById('login-form').classList.add('active');
    } else {
        document.querySelector('[onclick="showLoginTab(\'register\')"]').classList.add('active');
        document.getElementById('register-form').classList.add('active');
    }
}

// Authentication
async function login() {
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    const errorDiv = document.getElementById('login-error');

    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        if (response.ok) {
            const data = await response.json();
            token = data.access_token;
            localStorage.setItem('token', token);
            await checkAuth();
        } else {
            const error = await response.json();
            errorDiv.textContent = error.detail || 'Login failed';
        }
    } catch (error) {
        errorDiv.textContent = 'Network error: ' + error.message;
    }
}

async function register() {
    const username = document.getElementById('register-username').value;
    const password = document.getElementById('register-password').value;
    const errorDiv = document.getElementById('register-error');

    try {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        if (response.ok) {
            const data = await response.json();
            token = data.access_token;
            localStorage.setItem('token', token);
            await checkAuth();
        } else {
            const error = await response.json();
            errorDiv.textContent = error.detail || 'Registration failed';
        }
    } catch (error) {
        errorDiv.textContent = 'Network error: ' + error.message;
    }
}

async function checkAuth() {
    try {
        const response = await fetch('/api/auth/me', {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            currentUser = await response.json();
            document.getElementById('username-display').textContent = currentUser.username;

            if (currentUser.is_admin) {
                document.getElementById('admin-link').style.display = 'block';
            }

            showScreen('chat-screen');
            await loadConversations();
        } else {
            logout();
        }
    } catch (error) {
        logout();
    }
}

function logout() {
    token = null;
    currentUser = null;
    currentConversationId = null;
    localStorage.removeItem('token');
    showScreen('login-screen');
}

// Conversations
async function loadConversations() {
    try {
        const response = await fetch('/api/conversations', {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            conversations = await response.json();
            renderConversations();
        }
    } catch (error) {
        console.error('Failed to load conversations:', error);
    }
}

function renderConversations() {
    const list = document.getElementById('conversation-list');
    list.innerHTML = '';

    conversations.forEach(conv => {
        const item = document.createElement('div');
        item.className = 'conversation-item';
        if (conv.id === currentConversationId) {
            item.classList.add('active');
        }

        item.innerHTML = `
            <h3>${conv.title}</h3>
            <p>${new Date(conv.updated_at).toLocaleString()}</p>
        `;

        item.onclick = () => loadConversation(conv.id);
        list.appendChild(item);
    });
}

async function createNewConversation() {
    try {
        const response = await fetch('/api/conversations', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ title: 'New Conversation' })
        });

        if (response.ok) {
            const conv = await response.json();
            await loadConversations();
            loadConversation(conv.id);
        }
    } catch (error) {
        console.error('Failed to create conversation:', error);
    }
}

async function loadConversation(conversationId) {
    try {
        const response = await fetch(`/api/conversations/${conversationId}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            const conversation = await response.json();
            currentConversationId = conversationId;
            document.getElementById('chat-title').textContent = conversation.title;
            document.getElementById('export-btn').disabled = false;

            renderMessages(conversation.messages);
            renderConversations();
        }
    } catch (error) {
        console.error('Failed to load conversation:', error);
    }
}

function renderMessages(messages) {
    const messagesDiv = document.getElementById('messages');
    messagesDiv.innerHTML = '';

    messages.forEach(msg => {
        addMessageToUI(msg.role, msg.content, msg.sources);
    });

    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function addMessageToUI(role, content, sources = null) {
    const messagesDiv = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = content;
    messageDiv.appendChild(contentDiv);

    if (sources && sources.length > 0) {
        const sourcesDiv = document.createElement('div');
        sourcesDiv.className = 'message-sources';
        sourcesDiv.innerHTML = '<strong>Sources:</strong>';

        sources.forEach(source => {
            const sourceItem = document.createElement('div');
            sourceItem.className = 'source-item';
            sourceItem.innerHTML = `<strong>${source.file_name}</strong>: ${source.text}`;
            sourcesDiv.appendChild(sourceItem);
        });

        messageDiv.appendChild(sourcesDiv);
    }

    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;

    return messageDiv;
}

// Chat
async function sendMessage() {
    const input = document.getElementById('message-input');
    const message = input.value.trim();

    if (!message) return;

    const useRAG = document.getElementById('rag-toggle').checked;
    const sendBtn = document.getElementById('send-btn');

    // Disable input
    input.disabled = true;
    sendBtn.disabled = true;

    // Add user message to UI
    addMessageToUI('user', message);
    input.value = '';

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                conversation_id: currentConversationId,
                use_rag: useRAG
            })
        });

        if (!response.ok) {
            throw new Error('Chat request failed');
        }

        // Handle streaming response
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        let assistantMessageDiv = null;
        let contentDiv = null;
        let sources = null;

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = JSON.parse(line.substring(6));

                    if (data.type === 'sources') {
                        sources = data.sources;
                    } else if (data.type === 'content') {
                        if (!assistantMessageDiv) {
                            assistantMessageDiv = document.createElement('div');
                            assistantMessageDiv.className = 'message assistant';
                            contentDiv = document.createElement('div');
                            contentDiv.className = 'message-content';
                            assistantMessageDiv.appendChild(contentDiv);
                            document.getElementById('messages').appendChild(assistantMessageDiv);
                        }
                        contentDiv.textContent += data.content;
                        document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;
                    } else if (data.type === 'done') {
                        currentConversationId = data.conversation_id;

                        // Add sources if available
                        if (sources && sources.length > 0 && assistantMessageDiv) {
                            const sourcesDiv = document.createElement('div');
                            sourcesDiv.className = 'message-sources';
                            sourcesDiv.innerHTML = '<strong>Sources:</strong>';

                            sources.forEach(source => {
                                const sourceItem = document.createElement('div');
                                sourceItem.className = 'source-item';
                                sourceItem.innerHTML = `<strong>${source.file_name}</strong>: ${source.text}`;
                                sourcesDiv.appendChild(sourceItem);
                            });

                            assistantMessageDiv.appendChild(sourcesDiv);
                        }

                        await loadConversations();
                    } else if (data.type === 'error') {
                        alert('Error: ' + data.error);
                    }
                }
            }
        }
    } catch (error) {
        console.error('Chat error:', error);
        alert('Failed to send message: ' + error.message);
    } finally {
        input.disabled = false;
        sendBtn.disabled = false;
        input.focus();
    }
}

// Search
function searchMode() {
    document.getElementById('search-modal').style.display = 'block';
}

function closeSearchModal() {
    document.getElementById('search-modal').style.display = 'none';
}

async function performSearch() {
    const query = document.getElementById('search-input').value.trim();
    if (!query) return;

    const resultsDiv = document.getElementById('search-results');
    resultsDiv.innerHTML = '<p>Searching...</p>';

    try {
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query })
        });

        if (response.ok) {
            const data = await response.json();
            renderSearchResults(data.results);
        } else {
            resultsDiv.innerHTML = '<p>Search failed</p>';
        }
    } catch (error) {
        resultsDiv.innerHTML = '<p>Error: ' + error.message + '</p>';
    }
}

function renderSearchResults(results) {
    const resultsDiv = document.getElementById('search-results');

    if (results.length === 0) {
        resultsDiv.innerHTML = '<p>No results found</p>';
        return;
    }

    resultsDiv.innerHTML = '';

    results.forEach(result => {
        const item = document.createElement('div');
        item.className = 'search-result-item';
        item.innerHTML = `
            <h4>${result.file_name}</h4>
            <p>${result.text}</p>
            <small>Chunk ${result.chunk_index + 1} | Distance: ${result.distance.toFixed(4)}</small>
        `;
        resultsDiv.appendChild(item);
    });
}

// Export
async function exportConversation() {
    if (!currentConversationId) return;

    try {
        const response = await fetch(`/api/conversations/${currentConversationId}/export`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `conversation_${currentConversationId}.json`;
            a.click();
            window.URL.revokeObjectURL(url);
        }
    } catch (error) {
        alert('Export failed: ' + error.message);
    }
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('search-modal');
    if (event.target === modal) {
        closeSearchModal();
    }
}
