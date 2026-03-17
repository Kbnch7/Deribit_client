// --- НАСТРОЙКИ ---
    // Определяем тикер из URL или берем дефолтный
    const urlParams = new URLSearchParams(window.location.search);
    let currentTicker = urlParams.get('ticker') || 'btc_usd';
    
    // Глобальные переменные состояния
    let allData = []; // Храним тут ВЕСЬ массив данных, чтобы склеивать историю корректно
    let updateInterval;
    let isLoadingHistory = false;
    let isRealtimeActive = false;

    // --- 1. СОЗДАНИЕ ГРАФИКА (Светлая тема) ---
    const container = document.getElementById('chart');
    const chart = LightweightCharts.createChart(container, {
        layout: { 
            background: { color: '#ffffff' }, 
            textColor: '#333333',
        },
        grid: { 
            vertLines: { color: '#f0f3fa' }, 
            horzLines: { color: '#f0f3fa' } 
        },
        timeScale: { 
            borderColor: '#d1d5db', 
            timeVisible: true,
            secondsVisible: true,
        },
        rightPriceScale: {
            borderColor: '#d1d5db',
        },
        crosshair: {
            mode: LightweightCharts.CrosshairMode.Normal,
        },
    });

    // Добавляем серию (Синий стиль TradingView)
    const areaSeries = chart.addSeries(LightweightCharts.AreaSeries, {
        lineColor: '#2962FF',
        topColor: 'rgba(41, 98, 255, 0.3)',
        bottomColor: 'rgba(41, 98, 255, 0.0)',
        lineWidth: 2,
    });

    // Адаптация под размер окна
    window.addEventListener('resize', () => {
        chart.applyOptions({ width: container.clientWidth });
    });

    // --- 2. ЛОГИКА ЗАГРУЗКИ ---

    // А) Первоначальная загрузка (последние 1000 точек)
    async function loadInitialHistory() {
        // Сбрасываем старые данные
        allData = [];
        
        // Запрос к API
        const apiUrl = `/api/charts/linear?ticker=${currentTicker}&limit=1000`;

        try {
            const response = await fetch(apiUrl);
            if (!response.ok) throw new Error('Ошибка загрузки старта');
            
            let data = await response.json();
            
            // ФИЛЬТР: Убираем null значения и сортируем (на всякий случай)
            data = data.filter(d => d.value !== null);

            if (data.length > 0) {
                allData = data; // Сохраняем в память
                areaSeries.setData(allData);
                chart.timeScale().fitContent(); // Центрируем график
                
                // Обновляем ценник
                updatePriceLabel(data[data.length - 1].value);
            }

            // Запускаем живое обновление
            startRealtimeUpdates();

        } catch (err) {
            console.error('Ошибка старта:', err);
            // Пробуем снова через 3 секунды, если сеть упала
            setTimeout(loadInitialHistory, 3000);
        }
    }

    // Функция-чистильщик: удаляет дубликаты по времени и сортирует
function mergeAndSort(array1, array2) {
    // 1. Сливаем два массива
    const combined = [...array1, ...array2];
    
    // 2. Используем Map, чтобы удалить дубликаты (ключ = time)
    // Если время совпадает, Map перезапишет значение (оставит одно)
    const uniqueMap = new Map();
    combined.forEach(item => {
        // Защита от null значений
        if (item.value !== null && item.value !== undefined) {
            uniqueMap.set(item.time, item);
        }
    });

    // 3. Превращаем обратно в массив и сортируем (Старые -> Новые)
    return Array.from(uniqueMap.values()).sort((a, b) => a.time - b.time);
}

    // Б) Подгрузка истории (при скролле влево)
    async function loadMoreHistory() {
        if (isLoadingHistory || allData.length === 0) return;
        
        isLoadingHistory = true;
        
        // Берем время самой старой точки, которая у нас есть
        const oldestPoint = allData[0];
        const beforeTs = oldestPoint.time;

        console.log(`Подгружаем историю до: ${new Date(beforeTs * 1000).toLocaleTimeString()}`);

        try {
            // Запрашиваем 500 точек ДО этого времени
            // Используем твой НОВЫЙ эндпоинт get_chart_history
            const url = `/api/charts/linear/get_chart_history?ticker=${currentTicker}&limit=500&before_timestamp=${beforeTs}`;
            
            const response = await fetch(url);
            let newHistory = await response.json();

            // ФИЛЬТР ДУБЛИКАТОВ И NULL:
            // 1. Убираем пустые цены
            // 2. Оставляем только то, что СТРОГО меньше нашего текущего минимума
            newHistory = newHistory.filter(p => p.value !== null && p.time < oldestPoint.time);

            if (newHistory.length > 0) {
                // Склеиваем массивы: [НоваяИстория] + [ТекущиеДанные]
                allData = mergeAndSort(newHistory, allData);
                
                // Обновляем график
                areaSeries.setData(allData);
            } else {
                console.log("Истории больше нет.");
            }

        } catch (err) {
            console.error('Ошибка подгрузки истории:', err);
        } finally {
            isLoadingHistory = false;
        }
    }

    // В) Живое обновление (Real-time)
    async function updateRealtime() {
        // Добавляем timestamp, чтобы браузер не кэшировал запрос
        const apiUrl = `/api/charts/linear?ticker=${currentTicker}&limit=1&_nocache=${Date.now()}`;

        try {
            const response = await fetch(apiUrl);
            if (!response.ok) return; 

            const data = await response.json();
            
            if (data && data.length > 0) {
                const newPoint = data[data.length - 1];

                // Пропускаем, если цена null
                if (newPoint.value === null) return;

                // Обновляем график (Lightweight charts сам решит: добавить новую или обновить текущую)
                areaSeries.update(newPoint);
                
                // Обновляем наш локальный кэш allData
                if (allData.length > 0) {
                    const lastKnown = allData[allData.length - 1];
                    
                    if (newPoint.time > lastKnown.time) {
                        // Если новая секунда -> добавляем в массив
                        allData.push(newPoint);
                    } else if (newPoint.time === lastKnown.time) {
                        // Если та же секунда -> обновляем цену последней точки
                        allData[allData.length - 1] = newPoint;
                    }
                }
                
                updatePriceLabel(newPoint.value);
            }
        } catch (err) {
            console.log('Ждем связи...');
        }
    }

    // --- 3. УПРАВЛЕНИЕ ---

    function startRealtimeUpdates() {
        if (updateInterval) clearInterval(updateInterval);
        // Запускаем опрос каждые 2 секунды
        updateInterval = setInterval(updateRealtime, 2000);
    }

    // Обработчик списка тикеров
    async function loadTickersList() {
        try {
            const response = await fetch('/api/tickers_list');
            if (!response.ok) return;

            const data = await response.json();
            // Поддержка разных форматов ответа (список или объект)
            const list = data.array || data; 
            
            let html = '';
            list.forEach(item => {
                const tickerName = item.name || item; // Если объект или строка
                html += `<li><a class="dropdown-item" href="#" onclick="changeTicker('${tickerName}'); return false;">${tickerName}</a></li>`;
            });

            document.getElementById('tickers_list').innerHTML = html;
        } catch (e) {
            console.error("Ошибка списка тикеров:", e);
        }
    }

    // Смена тикера при клике
    window.changeTicker = function(newTicker) {
        if (currentTicker === newTicker) return;
        
        console.log("Меняем тикер на:", newTicker);
        currentTicker = newTicker;
        
        // Обновляем URL без перезагрузки страницы
        const newUrl = new URL(window.location);
        newUrl.searchParams.set('ticker', newTicker);
        window.history.pushState({}, '', newUrl);

        // Очищаем график и грузим новые данные
        loadInitialHistory();
    };

    function updatePriceLabel(price) {
        if (price) {
            document.getElementById('price-display').innerText = `$${price.toLocaleString()}`;
        }
    }

    // --- 4. СОБЫТИЯ ---

    // Слушаем скролл для подгрузки истории
    chart.timeScale().subscribeVisibleLogicalRangeChange(logicalRange => {
        // Если подошли к левому краю (индекс < 5) -> грузим историю
        if (logicalRange && logicalRange.from < 5) {
            loadMoreHistory();
        }
    });

    // --- ЗАПУСК ---
    // 1. Грузим список тикеров
    loadTickersList();
    // 2. Грузим график
    loadInitialHistory();
