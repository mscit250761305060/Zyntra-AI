// API Endpoints
const API_BASE = '/api/v1/auth';

// State
let currentTab = 'login';

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    // Redirect if already authenticated
    await checkAuth();
    
    // Fetch auth config and init Google login
    await initAuthConfig();
    
    // Setup listeners
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    document.getElementById('signupForm').addEventListener('submit', handleSignup);
});

async function initAuthConfig() {
    try {
        const response = await fetch(`${API_BASE}/config`);
        if (response.ok) {
            const config = await response.json();
            if (config.google_client_id) {
                // Initialize Google Identity Services dynamically
                google.accounts.id.initialize({
                    client_id: config.google_client_id,
                    callback: handleGoogleLogin,
                    context: "signin",
                    ux_mode: "popup",
                    auto_prompt: false
                });
                
                google.accounts.id.renderButton(
                    document.getElementById("googleButtonContainer"),
                    { theme: "outline", size: "large", type: "standard", text: "continue_with", shape: "rectangular" }
                );
            }
        }
    } catch (e) {
        console.error("Failed to load auth config", e);
    }
}

async function checkAuth() {
    try {
        const response = await fetch(`${API_BASE}/me`);
        if (response.ok) {
            // Already logged in
            window.location.href = '/static/index.html';
        }
    } catch (e) {
        console.log("Not authenticated, staying on login page");
    }
}

function switchTab(tab) {
    currentTab = tab;
    document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
    document.getElementById(`${tab}Form`).classList.add('active');
    
    document.getElementById('authSubtitle').textContent = 
        tab === 'login' ? 'Welcome back' : 'Create an account';
        
    clearErrors();
}

function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    const btn = input.nextElementSibling;
    if (input.type === 'password') {
        input.type = 'text';
        btn.textContent = 'Hide';
    } else {
        input.type = 'password';
        btn.textContent = 'Show';
    }
}

function showError(formId, message) {
    const errorEl = document.getElementById(`${formId}Error`);
    errorEl.textContent = message;
    errorEl.style.display = 'block';
}

function clearErrors() {
    document.querySelectorAll('.error-message').forEach(el => {
        el.style.display = 'none';
        el.textContent = '';
    });
}

async function handleLogin(e) {
    e.preventDefault();
    clearErrors();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    const btn = document.getElementById('loginBtn');
    
    btn.textContent = 'Signing in...';
    btn.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Login failed');
        }
        
        // Save user details
        localStorage.setItem('userName', data.name);
        localStorage.setItem('userId', data.user_id);
        
        // Redirect
        window.location.href = '/static/index.html';
        
    } catch (error) {
        showError('login', error.message);
    } finally {
        btn.textContent = 'Continue';
        btn.disabled = false;
    }
}

async function handleSignup(e) {
    e.preventDefault();
    clearErrors();
    
    const name = document.getElementById('signupName').value;
    const email = document.getElementById('signupEmail').value;
    const password = document.getElementById('signupPassword').value;
    const btn = document.getElementById('signupBtn');
    
    btn.textContent = 'Creating account...';
    btn.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE}/signup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Signup failed');
        }
        
        // Save user details
        localStorage.setItem('userName', data.name);
        localStorage.setItem('userId', data.user_id);
        
        // Redirect
        window.location.href = '/static/index.html';
        
    } catch (error) {
        showError('signup', error.message);
    } finally {
        btn.textContent = 'Create Account';
        btn.disabled = false;
    }
}

// Google OAuth Callback
async function handleGoogleLogin(response) {
    try {
        const credential = response.credential;
        
        const res = await fetch(`${API_BASE}/google`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ credential })
        });
        
        const data = await res.json();
        
        if (!res.ok) {
            throw new Error(data.detail || 'Google Login failed');
        }
        
        localStorage.setItem('userName', data.name);
        localStorage.setItem('userId', data.user_id);
        window.location.href = '/static/index.html';
        
    } catch (error) {
        showError('login', error.message);
    }
}
