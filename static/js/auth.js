function getCookie(name) {
    let value = `; ${document.cookie}`;
    let parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

function parseJwt(token) {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        return JSON.parse(window.atob(base64));
    } catch (e) {
        return null;
    }
}

window.onload = function() {
    const token = getCookie('jwt_token');
    if (token) {
        const userData = parseJwt(token);
        if (userData && userData.name) {
            console.log(userData.name)
            const authBtn = document.getElementById('login-button');
            
            if (authBtn) {
                authBtn.innerText = `Аккаунт: ${userData.name}`;
                authBtn.setAttribute("href", "#");
            }
        }
    }
};