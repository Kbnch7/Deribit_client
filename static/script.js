const API_BASE = 'http://localhost:8000/api/';  // Измени на твой API URL

// Функция для отображения ошибок
function showError(elementId, message) {
    document.getElementById(elementId).innerHTML = `<div class="alert alert-danger">${message}</div>`;
}

// Функция для отображения списка цен в таблице
function displayPrices(elementId, prices) {
    if (!prices || prices.length === 0) {
        return `<p>No data found.</p>`;
    }
    let table = '<table class="table table-striped"><thead><tr><th>Ticker</th><th>Price</th><th>Timestamp</th></tr></thead><tbody>';
    prices.forEach(price => {
        table += `<tr><td>${price.ticker}</td><td>${price.price}</td><td>${price.timestamp}</td></tr>`;
    });
    table += '</tbody></table>';
    document.getElementById(elementId).innerHTML = table;
}

// Функция для отображения одной цены
function displayLatest(elementId, price) {
    if (!price) {
        return `<p>No data found.</p>`;
    }
    document.getElementById(elementId).innerHTML = `
        <div class="alert alert-info">
            Ticker: ${price.ticker}<br>
            Price: ${price.price}<br>
            Timestamp: ${price.timestamp}
        </div>`;
}

// Обработчик для All
document.getElementById('all-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const ticker = document.getElementById('all-ticker').value;
    const page = document.getElementById('all-page').value;
    const limit = document.getElementById('all-limit').value;
    try {
        const res = await fetch(`${API_BASE}all?ticker=${ticker}${page ? `&page=${page}` : ''}${limit ? `&limit=${limit}` : ''}`);
        if (!res.ok) throw new Error('API error');
        const data = await res.json();
        displayPrices('all-result', data);
    } catch (err) {
        showError('all-result', err.message);
    }
});

// Обработчик для Latest
document.getElementById('latest-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const ticker = document.getElementById('latest-ticker').value;
    try {
        const res = await fetch(`${API_BASE}latest?ticker=${ticker}`);
        if (!res.ok) throw new Error('API error');
        const data = await res.json();
        displayLatest('latest-result', data);
    } catch (err) {
        showError('latest-result', err.message);
    }
});

// Обработчик для By Date
document.getElementById('by-date-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const ticker = document.getElementById('date-ticker').value;
    const start = document.getElementById('start-date').value;
    const end = document.getElementById('end-date').value || '';
    const page = document.getElementById('time-page').value || '';
    const limit = document.getElementById('time-limit').value || '';
    const url = `${API_BASE}by_date?ticker=${ticker}&start=${start}${end ? `&end=${end}` : ''}${page ? `&page=${page}` : ''}${limit ? `&limit=${limit}` : ''}`;
    try {
        const res = await fetch(url);
        if (!res.ok) throw new Error('API error');
        const data = await res.json();
        displayPrices('by-date-result', data);
    } catch (err) {
        showError('by-date-result', err.message);
    }
});