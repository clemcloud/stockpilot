// Global token check
function requireAuth() {
    const token = localStorage.getItem('token');
    if (!token) window.location.href = '/';
    return token;
}

// Logout
function logout() {
    localStorage.removeItem('token');
    window.location.href = '/';
}