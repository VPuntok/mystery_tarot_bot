import { ApiService } from './services/api.js';
import { UI } from './ui.js';
import { marked } from 'marked';

export class TarotApp {
    constructor() {
        this.api = new ApiService();
        this.ui = new UI();
        this.currentUser = null;
        this.currentProject = null;
        
        // Настраиваем marked для безопасного рендеринга
        marked.setOptions({
            breaks: true, // Поддержка переносов строк
            gfm: true,    // GitHub Flavored Markdown
            sanitize: false // Отключаем санитизацию для эмодзи
        });
    }

    async init() {
        try {
            // Получаем данные пользователя из Telegram
            let tgUser = window.Telegram.WebApp.initDataUnsafe?.user;
            
            // Если данные не получены (локальное тестирование), используем тестовые данные
            if (!tgUser) {
                console.log('Используем тестовые данные для локального тестирования');
                tgUser = {
                    id: 123456789,
                    username: 'test_user',
                    first_name: 'Тестовый',
                    last_name: 'Пользователь'
                };
            }

            // Инициализируем приложение
            await this.initializeApp(tgUser);
            
            // Показываем главное меню
            this.showMainMenu();
            
        } catch (error) {
            console.error('Ошибка инициализации:', error);
            this.ui.showError('Ошибка загрузки приложения: ' + error.message);
        }
    }

    async initializeApp(tgUser) {
        // Получаем все проекты
        const projects = await this.api.getProjects();
        if (projects.length === 0) {
            throw new Error('Нет доступных проектов');
        }
        
        // Определяем, какой проект использовать
        this.currentProject = this.selectProject(projects);
        
        console.log(`Выбран проект: ${this.currentProject.name} (ID: ${this.currentProject.id})`);
        
        // Получаем или создаем пользователя
        this.currentUser = await this.api.getOrCreateUser({
            telegram_user_id: tgUser.id,
            username: tgUser.username,
            project: this.currentProject.id
        });

        // Загружаем и применяем настройки темы
        await this.loadAndApplyThemeSettings();
    }

    async loadAndApplyThemeSettings() {
        try {
            const response = await this.api.getThemeSettings(this.currentProject.id);
            if (response.success && response.theme_settings) {
                this.applyThemeSettings(response.theme_settings);
            }
        } catch (error) {
            console.warn('Не удалось загрузить настройки темы:', error);
            // Используем дефолтные настройки
        }
    }

    applyThemeSettings(settings) {
        const root = document.documentElement;
        
        // Применяем цвета
        if (settings.primary_color) {
            root.style.setProperty('--primary-color', settings.primary_color);
            root.style.setProperty('--primary-hover', this.adjustColor(settings.primary_color, -20));
        }
        
        if (settings.secondary_color) {
            root.style.setProperty('--secondary-color', settings.secondary_color);
        }
        
        if (settings.accent_color) {
            root.style.setProperty('--accent-color', settings.accent_color);
        }
        
        if (settings.bg_primary) {
            root.style.setProperty('--bg-primary', settings.bg_primary);
        }
        
        if (settings.bg_secondary) {
            root.style.setProperty('--bg-secondary', settings.bg_secondary);
        }
        
        if (settings.bg_card) {
            root.style.setProperty('--bg-card', settings.bg_card);
        }
        
        if (settings.text_primary) {
            root.style.setProperty('--text-primary', settings.text_primary);
        }
        
        if (settings.text_secondary) {
            root.style.setProperty('--text-secondary', settings.text_secondary);
        }
        
        if (settings.text_muted) {
            root.style.setProperty('--text-muted', settings.text_muted);
        }
        
        if (settings.border_color) {
            root.style.setProperty('--border-color', settings.border_color);
        }
        
        if (settings.font_family) {
            root.style.setProperty('--font-family', settings.font_family);
            document.body.style.fontFamily = settings.font_family;
        }
        
        if (settings.border_radius) {
            root.style.setProperty('--border-radius', settings.border_radius);
        }
        
        // Обновляем градиенты на основе новых цветов
        this.updateGradients(settings);
    }

    updateGradients(settings) {
        const root = document.documentElement;
        
        const primary = settings.primary_color || '#6366f1';
        const secondary = settings.secondary_color || '#8b5cf6';
        const accent = settings.accent_color || '#f59e0b';
        
        root.style.setProperty('--gradient-primary', `linear-gradient(135deg, ${primary} 0%, ${secondary} 100%)`);
        root.style.setProperty('--gradient-accent', `linear-gradient(135deg, ${accent} 0%, ${this.adjustColor(accent, 20)} 100%)`);
    }

    adjustColor(color, amount) {
        // Простая функция для осветления/затемнения цвета
        const hex = color.replace('#', '');
        const num = parseInt(hex, 16);
        const r = Math.min(255, Math.max(0, (num >> 16) + amount));
        const g = Math.min(255, Math.max(0, ((num >> 8) & 0x00FF) + amount));
        const b = Math.min(255, Math.max(0, (num & 0x0000FF) + amount));
        return `#${((r << 16) | (g << 8) | b).toString(16).padStart(6, '0')}`;
    }

    selectProject(projects) {
        // 1. Проверяем URL параметры
        const urlParams = new URLSearchParams(window.location.search);
        const projectId = urlParams.get('project_id');
        const projectName = urlParams.get('project_name');
        
        // 2. Если указан project_id в URL
        if (projectId) {
            const project = projects.find(p => p.id == projectId);
            if (project) {
                console.log(`Проект выбран по ID из URL: ${project.name}`);
                return project;
            } else {
                console.warn(`Проект с ID ${projectId} не найден, используем fallback`);
            }
        }
        
        // 3. Если указан project_name в URL
        if (projectName) {
            const project = projects.find(p => p.name.toLowerCase().includes(projectName.toLowerCase()));
            if (project) {
                console.log(`Проект выбран по имени из URL: ${project.name}`);
                return project;
            } else {
                console.warn(`Проект с именем "${projectName}" не найден, используем fallback`);
            }
        }
        
        // 4. Fallback: ищем проект "Mystic Tarot Bot"
        const mysticProject = projects.find(p => p.name.includes('Mystic Tarot Bot'));
        if (mysticProject) {
            console.log(`Проект выбран по имени "Mystic Tarot Bot": ${mysticProject.name}`);
            return mysticProject;
        }
        
        // 5. Последний fallback: первый активный проект
        const activeProject = projects.find(p => p.status === 'active');
        if (activeProject) {
            console.log(`Проект выбран как первый активный: ${activeProject.name}`);
            return activeProject;
        }
        
        // 6. Если ничего не подходит, берем первый
        console.log(`Проект выбран как первый в списке: ${projects[0].name}`);
        return projects[0];
    }

    showMainMenu() {
        const content = `
            <div class="balance-header">
                <div class="balance-info">
                    💰 Баланс: ${this.currentUser.balance} раскладов
                </div>
            </div>
            
            <div class="card">
                <h1>🔮 Mystic Tarot</h1>
                <p class="text-center text-muted">Выберите действие для продолжения</p>
                
                <div class="menu-grid">
                    <div class="menu-tile card-of-day" onclick="app.showCardOfDay()">
                        <div class="menu-tile-content">
                            <span class="menu-tile-icon">🌅</span>
                            <div class="menu-tile-title">Карта дня</div>
                            <div class="menu-tile-subtitle">Ежедневное предсказание</div>
                        </div>
                    </div>
                    
                    <div class="menu-tile" onclick="app.showSpreads()">
                        <div class="menu-tile-content">
                            <span class="menu-tile-icon">🔮</span>
                            <div class="menu-tile-title">Расклады</div>
                            <div class="menu-tile-subtitle">Получить предсказание</div>
                        </div>
                    </div>
                    
                    <div class="menu-tile" onclick="app.showPackages()">
                        <div class="menu-tile-content">
                            <span class="menu-tile-icon">📦</span>
                            <div class="menu-tile-title">Пакеты</div>
                            <div class="menu-tile-subtitle">Купить расклады</div>
                        </div>
                    </div>
                    
                    <div class="menu-tile" onclick="app.showHistory()">
                        <div class="menu-tile-content">
                            <span class="menu-tile-icon">📚</span>
                            <div class="menu-tile-title">История</div>
                            <div class="menu-tile-subtitle">Предыдущие расклады</div>
                        </div>
                    </div>
                </div>
                
                <small class="text-center text-muted" style="display: block; margin-top: 16px;">
                    Проект: ${this.currentProject.name}
                </small>
            </div>
        `;
        
        this.ui.updateContent(content);
    }

    async showSpreads() {
        try {
            this.ui.showLoading('Загрузка раскладов...');
            
            const spreads = await this.api.getSpreads(this.currentProject.id);
            
            if (spreads.length === 0) {
                this.ui.showError('Нет доступных раскладов');
                return;
            }

            // Фильтруем расклады, убирая карту дня
            const filteredSpreads = spreads.filter(spread => 
                !spread.name.toLowerCase().includes('карта дня')
            );

            if (filteredSpreads.length === 0) {
                this.ui.showError('Нет доступных раскладов');
                return;
            }

            // Сохраняем расклады для использования в других методах
            this.currentSpreads = filteredSpreads;

            const spreadsHtml = filteredSpreads.map(spread => `
                <div class="spread-tile" onclick="app.selectSpread(${spread.id})">
                    <div class="spread-tile-content">
                        <span class="spread-tile-icon">🔮</span>
                        <div class="spread-tile-title">${spread.name}</div>
                        <div class="spread-tile-subtitle">${spread.description || 'Описание отсутствует'}</div>
                        <div class="spread-tile-cards">Карт: ${spread.num_cards}</div>
                    </div>
                </div>
            `).join('');

            const content = `
                <div class="balance-header">
                    <div class="balance-info">
                        💰 Баланс: ${this.currentUser.balance} раскладов
                    </div>
                    <a href="#" class="back-button" onclick="app.showMainMenu()">
                        ← Назад
                    </a>
                </div>
                
                <div class="card">
                    <h2>🔮 Выберите расклад</h2>
                    <div class="spreads-grid">
                        ${spreadsHtml}
                    </div>
                </div>
            `;
            
            this.ui.updateContent(content);
            
        } catch (error) {
            console.error('Ошибка загрузки раскладов:', error);
            this.ui.showError('Ошибка загрузки раскладов');
        }
    }

    async selectSpread(spreadId) {
        try {
            // Показываем страницу для ввода вопроса
            this.showQuestionInput(spreadId);
        } catch (error) {
            console.error('Ошибка загрузки расклада:', error);
            this.ui.showError('Ошибка загрузки расклада');
        }
    }

    showQuestionInput(spreadId) {
        // Находим информацию о раскладе
        const spread = this.currentSpreads.find(s => s.id === spreadId);
        if (!spread) {
            this.ui.showError('Расклад не найден');
            return;
        }

        const content = `
            <div class="balance-header">
                <div class="balance-info">
                    💰 Баланс: ${this.currentUser.balance} раскладов
                </div>
                <a href="#" class="back-button" onclick="app.showSpreads()">
                    ← Назад к раскладам
                </a>
            </div>
            
            <div class="spread-page">
                <h2>🔮 ${spread.name}</h2>
                <div class="spread-description">
                    <p>${spread.description || 'Описание отсутствует'}</p>
                    <p><strong>Количество карт:</strong> ${spread.num_cards}</p>
                </div>
                <div class="question-section">
                    <label for="user-question"><strong>На какой вопрос делаем расклад?</strong></label>
                    <textarea id="user-question" class="question-textarea" rows="3" placeholder="Введите ваш вопрос..." autofocus></textarea>
                </div>
                <div class="action-buttons-row">
                    <button class="button primary" onclick="app.saveUserQuestionAndDealCards(${spreadId})">
                        🎴 Продолжить
                    </button>
                </div>
            </div>
        `;
        this.ui.updateContent(content);
    }

    saveUserQuestionAndDealCards(spreadId) {
        const question = document.getElementById('user-question')?.value?.trim() || '';
        this.currentUserQuestion = question;
        this.dealCards(spreadId);
    }

    async dealCards(spreadId) {
        try {
            if (this.currentUser.balance <= 0) {
                this.ui.showError('Недостаточно раскладов. Пополните баланс.');
                return;
            }
            this.ui.showLoading('Раздаем карты...');
            // Получаем карты для расклада, передаем user_context
            const cardsData = await this.api.getSpreadCards({
                user: this.currentUser.id,
                spread: spreadId,
                user_context: this.currentUserQuestion || ''
            });
            this.currentUser.balance -= 1;
            this.showCardsResult(cardsData, spreadId);
        } catch (error) {
            console.error('Ошибка раздачи карт:', error);
            this.ui.showError('Ошибка раздачи карт: ' + (error.response?.data?.error || error.message));
        }
    }

    showCardsResult(cardsData, spreadId) {
        // Находим информацию о раскладе
        const spread = this.currentSpreads.find(s => s.id === spreadId);
        // Формируем HTML для карт (сразу лицевой стороной вверх)
        const cardsHtml = (cardsData.cards_names || []).map((cardName, idx) => {
            const imgUrl = cardsData.cards_images && cardsData.cards_images[idx];
            const isReversed = cardsData.cards_used && cardsData.cards_used[idx] && cardsData.cards_used[idx].is_reversed;
            return `
                <div class="card-item${isReversed ? ' reversed' : ''}">
                    ${imgUrl ? `<img src="${imgUrl}" alt="${cardName}" class="card-image"/>` : ''}
                    <div class="card-name">${cardName}</div>
                    ${isReversed ? '<div class="card-status">🔄 Перевернутая</div>' : '<div class="card-status">⬆️ Прямая</div>'}
                </div>
            `;
        }).join('');

        const questionBlock = this.currentUserQuestion ? `
            <div class="user-question-block">
                <strong>Вопрос пользователя:</strong><br>
                <span>${this.currentUserQuestion}</span>
            </div>
        ` : '';

        const content = `
            <div class="balance-header">
                <div class="balance-info">
                    💰 Осталось раскладов: ${this.currentUser.balance}
                </div>
                <a href="#" class="back-button" onclick="app.showMainMenu()">
                    ← Вернуться в меню
                </a>
            </div>
            
            <div class="cards-result">
                ${questionBlock}
                <div class="spread-info">
                    <h3>Расклад: ${spread ? spread.name : 'Неизвестный расклад'}</h3>
                </div>
                <div class="cards-section">
                    <h4>Выпавшие карты:</h4>
                    <div class="cards-list">
                        ${cardsHtml}
                    </div>
                </div>
                <div class="action-buttons-row">
                    <button class="button primary" onclick="app.getInterpretation(${spreadId}, ${cardsData.interpretation_id})">
                        🔮 Получить интерпретацию
                    </button>
                </div>
            </div>
        `;
        this.ui.updateContent(content);
        this.currentCardsData = cardsData;
    }

    async getInterpretation(spreadId, interpretationId) {
        try {
            this.showInterpretationLoading();
            // Получаем интерпретацию, передаем user_context
            const interpretation = await this.api.createInterpretation({
                user: this.currentUser.id,
                spread: spreadId,
                interpretation_id: interpretationId,
                user_context: this.currentUserQuestion || ''
            });
            this.addInterpretationToPage(interpretation);
        } catch (error) {
            console.error('Ошибка получения интерпретации:', error);
            this.ui.showError('Ошибка получения интерпретации: ' + (error.response?.data?.error || error.message));
        }
    }

    showInterpretationLoading() {
        // Находим секцию action-buttons и заменяем её на индикатор загрузки
        const actionButtons = document.querySelector('.action-buttons-row');
        if (actionButtons) {
            actionButtons.innerHTML = `
                <div class="interpretation-loading">
                    <div class="loading-spinner"></div>
                    <p>🔮 Получаем интерпретацию...</p>
                </div>
            `;
        }
    }

    addInterpretationToPage(interpretation) {
        // Рендерим интерпретацию в Markdown
        const interpretationHtml = interpretation.ai_response 
            ? marked.parse(interpretation.ai_response)
            : '<p class="text-muted">Интерпретация не найдена</p>';
        // Находим секцию action-buttons и заменяем её на интерпретацию
        const actionButtons = document.querySelector('.action-buttons-row');
        if (actionButtons) {
            actionButtons.innerHTML = `
                <div class="interpretation-section">
                    <h4>📖 Интерпретация:</h4>
                    <div class="markdown-content">
                        ${interpretationHtml}
                    </div>
                </div>
                <div class="interpretation-footer">
                    <div class="ai-status">
                        🤖 AI статус: ${interpretation.ai_service_status || 'active'}
                    </div>
                </div>
            `;
        }
    }

    async showPackages() {
        try {
            this.ui.showLoading('Загрузка подписок и пакетов...');
            
            const packages = await this.api.getPackages(this.currentProject.id);
            
            if (packages.length === 0) {
                this.ui.showError('Нет доступных подписок и пакетов');
                return;
            }

            const packagesHtml = packages.map(pkg => `
                <div class="package-tile" onclick="app.buyPackage(${pkg.id})">
                    <div class="package-tile-content">
                        <span class="package-tile-icon">📦</span>
                        <div class="package-tile-title">${pkg.name}</div>
                        <div class="package-tile-price">${pkg.price}₽</div>
                        <div class="package-tile-description">
                            ${pkg.package_type === 'one_time' 
                                ? `${pkg.num_readings} раскладов`
                                : `Подписка на ${pkg.subscription_days} дней`
                            }
                        </div>
                    </div>
                </div>
            `).join('');

            const content = `
                <div class="balance-header">
                    <div class="balance-info">
                        💰 Баланс: ${this.currentUser.balance} раскладов
                    </div>
                    <a href="#" class="back-button" onclick="app.showMainMenu()">
                        ← Назад
                    </a>
                </div>
                
                <div class="card">
                    <h2>📦 Подписки и пакеты раскладов</h2>
                    <p class="text-center text-muted">Выберите подписку или пакет для пополнения баланса</p>
                    <div class="packages-grid">
                        ${packagesHtml}
                    </div>
                </div>
            `;
            
            this.ui.updateContent(content);
            
        } catch (error) {
            console.error('Ошибка загрузки пакетов:', error);
            this.ui.showError('Ошибка загрузки подписок и пакетов');
        }
    }

    async buyPackage(packageId) {
        try {
            this.ui.showLoading('Создание платежа...');
            
            // Запрашиваем PIN-код у пользователя
            const pinCode = prompt('Введите PIN-код для тестового платежа (8712):');
            
            if (!pinCode) {
                this.ui.showError('PIN-код не введен');
                return;
            }
            
            // Создаем тестовый платеж
            const response = await this.api.createTestPayment({
                user: this.currentUser.id,
                project: this.currentProject.id,
                package: packageId,
                pin_code: pinCode
            });
            
            // Обновляем баланс пользователя
            this.currentUser.balance = response.new_balance;
            if (response.subscription_end) {
                this.currentUser.subscription_end = response.subscription_end;
            }
            
            this.ui.showSuccess(`Платеж успешно выполнен! Новый баланс: ${response.new_balance} раскладов`);
            
            setTimeout(() => {
                this.showMainMenu();
            }, 2000);
            
        } catch (error) {
            console.error('Ошибка создания платежа:', error);
            this.ui.showError('Ошибка создания платежа: ' + (error.response?.data?.error || error.message));
        }
    }

    async showHistory() {
        try {
            this.ui.showLoading('Загрузка истории...');
            
            const interpretations = await this.api.getInterpretations(this.currentUser.id);
            
            if (interpretations.length === 0) {
                this.ui.showError('История раскладов пуста');
                return;
            }

            // Сохраняем интерпретации для использования в других методах
            this.currentHistory = interpretations;

            const historyHtml = interpretations.map((interpretation, index) => {
                const date = new Date(interpretation.created_at);
                const formattedDate = date.toLocaleDateString('ru-RU');
                const formattedTime = date.toLocaleTimeString('ru-RU', { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                });
                
                return `
                    <div class="history-tile" onclick="app.openHistoryItem(${index})">
                        <div class="history-tile-content">
                            <span class="history-tile-icon">🔮</span>
                            <div class="history-tile-title">${interpretation.spread_name || 'Неизвестный расклад'}</div>
                            <div class="history-tile-date">${formattedDate}</div>
                            <div class="history-tile-time">${formattedTime}</div>
                        </div>
                    </div>
                `;
            }).join('');

            const content = `
                <div class="balance-header">
                    <div class="balance-info">
                        💰 Баланс: ${this.currentUser.balance} раскладов
                    </div>
                    <a href="#" class="back-button" onclick="app.showMainMenu()">
                        ← Назад
                    </a>
                </div>
                
                <div class="card">
                    <h2>📚 История раскладов</h2>
                    <div class="history-grid">
                        ${historyHtml}
                    </div>
                </div>
            `;
            
            this.ui.updateContent(content);
            
        } catch (error) {
            console.error('Ошибка загрузки истории:', error);
            this.ui.showError('Ошибка загрузки истории');
        }
    }

    openHistoryItem(index) {
        const interpretation = this.currentHistory[index];
        if (!interpretation) {
            this.ui.showError('Расклад не найден');
            return;
        }

        const date = new Date(interpretation.created_at);
        const formattedDate = date.toLocaleDateString('ru-RU');
        const formattedTime = date.toLocaleTimeString('ru-RU', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });

        // Формируем HTML для карт
        const cardsHtml = (interpretation.cards_names || []).map((cardName, idx) => {
            const imgUrl = interpretation.cards_images && interpretation.cards_images[idx];
            const isReversed = interpretation.cards_used && interpretation.cards_used[idx] && interpretation.cards_used[idx].is_reversed;
            return `
                <div class="card-item${isReversed ? ' reversed' : ''}">
                    ${imgUrl ? `<img src="${imgUrl}" alt="${cardName}" class="card-image"/>` : ''}
                    <div class="card-name">${cardName}</div>
                    ${isReversed ? '<div class="card-status">🔄 Перевернутая</div>' : '<div class="card-status">⬆️ Прямая</div>'}
                </div>
            `;
        }).join('');

        // Рендерим интерпретацию в Markdown
        const interpretationHtml = interpretation.ai_response 
            ? marked.parse(interpretation.ai_response)
            : '<p class="text-muted">Интерпретация не найдена</p>';

        // Блок с вопросом пользователя (если есть)
        const questionBlock = interpretation.user_question ? `
            <div class="user-question-block">
                <strong>Вопрос пользователя:</strong><br>
                <span>${interpretation.user_question}</span>
            </div>
        ` : '';

        const content = `
            <div class="balance-header">
                <div class="balance-info">
                    💰 Баланс: ${this.currentUser.balance} раскладов
                </div>
                <a href="#" class="back-button" onclick="app.showHistory()">
                    ← Назад к истории
                </a>
            </div>
            
            <div class="history-detail">
                <div class="history-detail-header">
                    <h2>🔮 ${interpretation.spread_name || 'Неизвестный расклад'}</h2>
                    <div class="history-detail-date">
                        📅 ${formattedDate} в ${formattedTime}
                    </div>
                </div>
                
                ${questionBlock}
                
                <div class="cards-section">
                    <h4>Выпавшие карты:</h4>
                    <div class="cards-list">
                        ${cardsHtml}
                    </div>
                </div>
                
                <div class="interpretation-section">
                    <h4>📖 Интерпретация:</h4>
                    <div class="markdown-content">
                        ${interpretationHtml}
                    </div>
                </div>
            </div>
        `;
        
        this.ui.updateContent(content);
    }

    async showCardOfDay() {
        try {
            // Проверяем, есть ли уже карта дня для сегодня
            const today = new Date().toDateString();
            const storedCardOfDay = localStorage.getItem(`cardOfDay_${this.currentUser.id}_${today}`);
            
            if (storedCardOfDay) {
                // Показываем сохраненную карту дня
                const cardData = JSON.parse(storedCardOfDay);
                this.showCardOfDayResult(cardData);
                
                // Проверяем, есть ли сохраненная интерпретация
                const storedInterpretation = localStorage.getItem(`cardOfDayInterpretation_${this.currentUser.id}_${today}`);
                if (storedInterpretation) {
                    const interpretation = JSON.parse(storedInterpretation);
                    this.addCardOfDayInterpretation(interpretation);
                } else {
                    // Если интерпретации нет, запрашиваем её
                    this.getCardOfDayInterpretation();
                }
            } else {
                // Создаем новую карту дня
                if (this.currentUser.balance <= 0) {
                    this.ui.showError('Недостаточно раскладов для карты дня. Пополните баланс.');
                    return;
                }
                
                // Показываем лоадер с текстом
                this.showCardOfDayLoading();
                
                // Находим расклад "Карта дня" для текущего проекта
                const spreads = await this.api.getSpreads(this.currentProject.id);
                const cardOfDaySpread = spreads.find(s => s.name.toLowerCase().includes('карта дня'));
                
                if (!cardOfDaySpread) {
                    this.ui.showError('Расклад "Карта дня" не найден');
                    return;
                }
                
                // Создаем специальный расклад "Карта дня" (1 карта)
                const cardData = await this.api.getSpreadCards({
                    user: this.currentUser.id,
                    spread: cardOfDaySpread.id,
                    user_context: 'Карта дня - ежедневное предсказание'
                });
                
                this.currentUser.balance -= 1;
                
                // Сохраняем карту дня в localStorage
                localStorage.setItem(`cardOfDay_${this.currentUser.id}_${today}`, JSON.stringify(cardData));
                
                // Показываем результат с задержкой
                setTimeout(() => {
                    this.showCardOfDayResult(cardData);
                    // Автоматически запрашиваем интерпретацию
                    this.getCardOfDayInterpretation();
                }, 1500);
            }
        } catch (error) {
            console.error('Ошибка получения карты дня:', error);
            this.ui.showError('Ошибка получения карты дня: ' + (error.response?.data?.error || error.message));
        }
    }

    showCardOfDayLoading() {
        const content = `
            <div class="card">
                <div class="card-of-day-loading">
                    <div class="loading-spinner"></div>
                    <h3>🌅 Выбираем карту дня</h3>
                    <p class="text-muted">Подождите, мы выбираем ваше предсказание на сегодня...</p>
                </div>
            </div>
        `;
        this.ui.updateContent(content);
    }

    showCardOfDayResult(cardData) {
        const cardName = cardData.cards_names && cardData.cards_names[0];
        const imgUrl = cardData.cards_images && cardData.cards_images[0];
        const isReversed = cardData.cards_used && cardData.cards_used[0] && cardData.cards_used[0].is_reversed;
        
        const cardHtml = `
            <div class="card-of-day-item${isReversed ? ' reversed' : ''}">
                ${imgUrl ? `<img src="${imgUrl}" alt="${cardName}" class="card-of-day-image"/>` : ''}
                <div class="card-of-day-name">${cardName}</div>
                ${isReversed ? '<div class="card-of-day-status">🔄 Перевернутая</div>' : '<div class="card-of-day-status">⬆️ Прямая</div>'}
            </div>
        `;

        const content = `
            <div class="balance-header">
                <div class="balance-info">
                    💰 Баланс: ${this.currentUser.balance} раскладов
                </div>
                <a href="#" class="back-button" onclick="app.showMainMenu()">
                    ← Назад
                </a>
            </div>
            
            <div class="card">
                <h2>🌅 Карта дня</h2>
                <p class="text-center text-muted">Ваше предсказание на сегодня</p>
                
                <div class="card-of-day-content">
                    <div class="card-of-day-left">
                        ${cardHtml}
                    </div>
                    <div class="card-of-day-right">
                        <div class="interpretation-loading">
                            <div class="loading-spinner"></div>
                            <p>🔮 Получаем интерпретацию...</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        this.ui.updateContent(content);
        this.currentCardOfDayData = cardData;
    }

    async getCardOfDayInterpretation() {
        try {
            // Находим расклад "Карта дня" для текущего проекта
            const spreads = await this.api.getSpreads(this.currentProject.id);
            const cardOfDaySpread = spreads.find(s => s.name.toLowerCase().includes('карта дня'));
            
            if (!cardOfDaySpread) {
                this.ui.showError('Расклад "Карта дня" не найден');
                return;
            }
            
            // Получаем интерпретацию для карты дня
            const interpretation = await this.api.createInterpretation({
                user: this.currentUser.id,
                spread: cardOfDaySpread.id,
                interpretation_id: this.currentCardOfDayData.interpretation_id,
                user_context: 'Карта дня - ежедневное предсказание'
            });
            
            // Сохраняем интерпретацию в localStorage
            const today = new Date().toDateString();
            localStorage.setItem(`cardOfDayInterpretation_${this.currentUser.id}_${today}`, JSON.stringify(interpretation));
            
            this.addCardOfDayInterpretation(interpretation);
        } catch (error) {
            console.error('Ошибка получения интерпретации карты дня:', error);
            this.ui.showError('Ошибка получения интерпретации: ' + (error.response?.data?.error || error.message));
        }
    }

    addCardOfDayInterpretation(interpretation) {
        // Рендерим интерпретацию в Markdown
        const interpretationHtml = interpretation.ai_response 
            ? marked.parse(interpretation.ai_response)
            : '<p class="text-muted">Интерпретация не найдена</p>';
        
        // Находим правую часть и заменяем её на интерпретацию
        const rightSection = document.querySelector('.card-of-day-right');
        if (rightSection) {
            rightSection.innerHTML = `
                <div class="interpretation-section">
                    <h4>📖 Интерпретация:</h4>
                    <div class="markdown-content">
                        ${interpretationHtml}
                    </div>
                </div>
            `;
        }
    }
}

// Делаем приложение доступным глобально для обработчиков событий
window.app = null;