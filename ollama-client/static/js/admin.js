// Admin app state
let adminToken = localStorage.getItem('adminToken');
let refreshInterval = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    if (adminToken) {
        checkAdminAuth();
    } else {
        showAdminScreen('admin-login-screen');
    }

    // Add enter key handler
    document.getElementById('admin-password').addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            adminLogin();
        }
    });
});

function showAdminScreen(screenId) {
    document.querySelectorAll('.screen').forEach(screen => {
        screen.style.display = 'none';
    });
    document.getElementById(screenId).style.display = 'block';
}

// Authentication
async function adminLogin() {
    const username = document.getElementById('admin-username').value;
    const password = document.getElementById('admin-password').value;
    const errorDiv = document.getElementById('admin-login-error');

    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        if (response.ok) {
            const data = await response.json();
            adminToken = data.access_token;
            localStorage.setItem('adminToken', adminToken);
            await checkAdminAuth();
        } else {
            const error = await response.json();
            errorDiv.textContent = error.detail || 'Login failed';
        }
    } catch (error) {
        errorDiv.textContent = 'Network error: ' + error.message;
    }
}

async function checkAdminAuth() {
    try {
        const response = await fetch('/api/auth/me', {
            headers: { 'Authorization': `Bearer ${adminToken}` }
        });

        if (response.ok) {
            const user = await response.json();
            if (user.is_admin) {
                showAdminScreen('admin-dashboard');
                await loadAdminData();
                startAutoRefresh();
            } else {
                alert('Admin access required');
                adminLogout();
            }
        } else {
            adminLogout();
        }
    } catch (error) {
        adminLogout();
    }
}

function adminLogout() {
    adminToken = null;
    localStorage.removeItem('adminToken');
    stopAutoRefresh();
    showAdminScreen('admin-login-screen');
}

// Data loading
async function loadAdminData() {
    await Promise.all([
        loadSystemStatus(),
        loadDetailedStats()
    ]);
}

async function loadSystemStatus() {
    try {
        const response = await fetch('/api/admin/stats', {
            headers: { 'Authorization': `Bearer ${adminToken}` }
        });

        if (response.ok) {
            const stats = await response.json();
            updateSystemStatus(stats);
        }
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

function updateSystemStatus(stats) {
    // Ollama status
    const ollamaDiv = document.getElementById('ollama-status');
    if (stats.ollama.status === 'healthy') {
        ollamaDiv.innerHTML = `
            <p style="color: green;">✓ Healthy</p>
            <p><small>LLM: ${stats.ollama.llm_model} ${stats.ollama.llm_available ? '✓' : '✗'}</small></p>
            <p><small>Embedding: ${stats.ollama.embedding_model} ${stats.ollama.embedding_available ? '✓' : '✗'}</small></p>
        `;
    } else {
        ollamaDiv.innerHTML = `
            <p style="color: red;">✗ Unhealthy</p>
            <p><small>${stats.ollama.error}</small></p>
        `;
    }

    // Indexer status
    const indexerDiv = document.getElementById('indexer-status');
    if (stats.indexer.indexing_in_progress) {
        indexerDiv.innerHTML = '<p style="color: orange;">⟳ Indexing in progress...</p>';
    } else {
        indexerDiv.innerHTML = '<p style="color: green;">✓ Ready</p>';
        if (stats.indexer.last_index_time) {
            const lastIndex = new Date(stats.indexer.last_index_time);
            indexerDiv.innerHTML += `<p><small>Last indexed: ${lastIndex.toLocaleString()}</small></p>`;
        }
    }

    // Document stats
    const docDiv = document.getElementById('document-stats');
    docDiv.innerHTML = `
        <p><strong>Total chunks:</strong> ${stats.indexer.total_chunks || 0}</p>
        <p><strong>Unique sources:</strong> ${stats.indexer.unique_sources || 0}</p>
        <p><strong>Backend:</strong> ${stats.indexer.backend || 'Unknown'}</p>
    `;

    // Model info
    document.getElementById('llm-model').textContent = stats.ollama.llm_model;
    document.getElementById('embedding-model').textContent = stats.ollama.embedding_model;
}

async function loadDetailedStats() {
    try {
        const response = await fetch('/api/admin/stats', {
            headers: { 'Authorization': `Bearer ${adminToken}` }
        });

        if (response.ok) {
            const stats = await response.json();
            document.getElementById('stats-json').textContent = JSON.stringify(stats, null, 2);
        }
    } catch (error) {
        console.error('Failed to load detailed stats:', error);
    }
}

// Index management
async function triggerReindex() {
    if (!confirm('This will reindex all documents. Continue?')) {
        return;
    }

    const statusDiv = document.getElementById('index-status');

    try {
        const response = await fetch('/api/admin/reindex', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${adminToken}` }
        });

        if (response.ok) {
            statusDiv.className = 'status-message success';
            statusDiv.textContent = 'Reindexing started. This may take a while...';
            setTimeout(() => loadAdminData(), 2000);
        } else {
            const error = await response.json();
            statusDiv.className = 'status-message error';
            statusDiv.textContent = error.detail || 'Reindex failed';
        }
    } catch (error) {
        statusDiv.className = 'status-message error';
        statusDiv.textContent = 'Error: ' + error.message;
    }
}

async function clearIndex() {
    const password = prompt('Enter admin password to confirm:');
    if (!password) return;

    const statusDiv = document.getElementById('index-status');

    try {
        const response = await fetch('/api/admin/clear-index', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${adminToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ password })
        });

        if (response.ok) {
            statusDiv.className = 'status-message success';
            statusDiv.textContent = 'Index cleared successfully';
            setTimeout(() => loadAdminData(), 1000);
        } else {
            const error = await response.json();
            statusDiv.className = 'status-message error';
            statusDiv.textContent = error.detail || 'Clear failed';
        }
    } catch (error) {
        statusDiv.className = 'status-message error';
        statusDiv.textContent = 'Error: ' + error.message;
    }
}

// Model management
async function pullModel() {
    const modelName = document.getElementById('model-name-input').value.trim();
    if (!modelName) {
        alert('Please enter a model name');
        return;
    }

    const progressDiv = document.getElementById('pull-progress');
    progressDiv.innerHTML = 'Starting pull...\n';

    try {
        const response = await fetch(`/api/admin/pull-model/${modelName}`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${adminToken}` }
        });

        if (!response.ok) {
            throw new Error('Pull request failed');
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = JSON.parse(line.substring(6));

                    if (data.error) {
                        progressDiv.innerHTML += `Error: ${data.error}\n`;
                    } else if (data.status) {
                        const progress = data.completed && data.total
                            ? ` (${((data.completed / data.total) * 100).toFixed(1)}%)`
                            : '';
                        progressDiv.innerHTML += `${data.status}${progress}\n`;
                    }

                    progressDiv.scrollTop = progressDiv.scrollHeight;
                }
            }
        }

        progressDiv.innerHTML += '\nPull complete!\n';
    } catch (error) {
        progressDiv.innerHTML += `\nError: ${error.message}\n`;
    }
}

// Auto-refresh
function startAutoRefresh() {
    refreshInterval = setInterval(() => {
        loadSystemStatus();
    }, 5000); // Refresh every 5 seconds
}

function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }
}
