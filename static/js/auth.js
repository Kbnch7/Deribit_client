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

function createLogoutButton(logoutUrl = "/api/auth/logout") {
    console.log(123)
    const auth_block = document.getElementById("auth-block")
    const cardBody = document.createElement("div");
    cardBody.className = "card-body text-center p-3";

    const logoutLink = document.createElement("a");
    logoutLink.href = logoutUrl;
    logoutLink.id = "logout-button";
    logoutLink.className = "text-secondary text-decoration-none fw-medium";
    logoutLink.textContent = "Выйти из профиля";

    cardBody.appendChild(logoutLink);
    auth_block.appendChild(cardBody);

    return auth_block;
}

window.onload = function() {
    const token = getCookie('jwt_token');
    if (token) {
        const userData = parseJwt(token);
        if (userData && userData.name) {
            createLogoutButton()
            console.log(userData.name)
            const authBtn = document.getElementById('login-button');
            if (authBtn) {
                authBtn.innerText = `Аккаунт: ${userData.name}`;
                authBtn.setAttribute("href", "#");
            }
        }
    }
};