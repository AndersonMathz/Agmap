// Sistema de Autenticação WebGIS Seguro

// Elementos do DOM
const loginForm = document.getElementById('loginForm');
const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');
const togglePasswordBtn = document.getElementById('togglePassword');
const errorMessage = document.getElementById('errorMessage');
const errorText = document.getElementById('errorText');
const loginBtn = document.querySelector('.btn-login');

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Sistema de autenticação inicializado');
    
    // Verificar se há parâmetro de logout
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('logout') === '1') {
        showLogoutMessage();
    }
    
    // Configurar event listeners
    setupEventListeners();
});

// Configurar event listeners
function setupEventListeners() {
    // Formulário de login
    loginForm.addEventListener('submit', handleLogin);
    
    // Toggle de senha
    togglePasswordBtn.addEventListener('click', togglePasswordVisibility);
    
    // Enter para submeter
    usernameInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            passwordInput.focus();
        }
    });
    
    passwordInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleLogin(e);
        }
    });
}

// Manipular login
async function handleLogin(event) {
    event.preventDefault();
    
    const username = usernameInput.value.trim();
    const password = passwordInput.value;
    
    console.log('🔐 Tentativa de login para:', username);
    
    // Validações básicas
    if (!username || !password) {
        showError('Por favor, preencha todos os campos.');
        return;
    }
    
    // Mostrar loading
    setLoadingState(true);
    
    try {
        console.log('📡 Enviando requisição de login...');
        
        // Fazer requisição para o backend
        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                username: username,
                password: password
            })
        });
        
        console.log('📥 Resposta recebida:', response.status, response.statusText);
        
        const data = await response.json();
        console.log('📄 Dados da resposta:', data);
        
        if (response.ok && data.success) {
            console.log('✅ Login bem-sucedido, redirecionando para:', data.redirect);
            window.location.href = data.redirect;
        } else {
            console.log('❌ Login falhou:', data.error);
            showError(data.error || 'Erro no login');
        }
        
    } catch (error) {
        console.error('❌ Erro na requisição:', error);
        showError('Erro de conexão. Tente novamente.');
    } finally {
        setLoadingState(false);
    }
}

// Toggle de visibilidade da senha
function togglePasswordVisibility() {
    const type = passwordInput.type === 'password' ? 'text' : 'password';
    passwordInput.type = type;
    
    const icon = togglePasswordBtn.querySelector('i');
    icon.className = type === 'password' ? 'fas fa-eye' : 'fas fa-eye-slash';
}

// Mostrar erro
function showError(message) {
    errorText.textContent = message;
    errorMessage.style.display = 'block';
    
    // Focar no campo de usuário
    usernameInput.focus();
}

// Esconder erro
function hideError() {
    errorMessage.style.display = 'none';
}

// Definir estado de loading
function setLoadingState(loading) {
    if (loading) {
        loginBtn.disabled = true;
        loginBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Autenticando...';
    } else {
        loginBtn.disabled = false;
        loginBtn.innerHTML = '<i class="fas fa-sign-in-alt"></i> Entrar';
    }
}

// Mostrar mensagem de logout
function showLogoutMessage() {
    const successMessage = document.createElement('div');
    successMessage.className = 'alert alert-success';
    successMessage.innerHTML = '<i class="fas fa-check-circle"></i> Logout realizado com sucesso!';
    
    loginForm.parentNode.insertBefore(successMessage, loginForm);
    
    // Remover mensagem após 3 segundos
    setTimeout(() => {
        successMessage.remove();
    }, 3000);
} 