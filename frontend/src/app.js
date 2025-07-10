import { ApiService } from './services/api.js';
import { UI } from './ui.js';

export class TarotApp {
    constructor() {
        this.api = new ApiService();
        this.ui = new UI();
        this.currentUser = null;
        this.currentProject = null;
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
            <div class="balance">
                💰 Баланс: ${this.currentUser.balance} раскладов
            </div>
            
            <div class="card">
                <small style="color: var(--tg-theme-hint-color, #6c757d); margin-bottom: 16px; display: block;">
                    Проект: ${this.currentProject.name} (ID: ${this.currentProject.id})
                </small>
                
                <button class="button" onclick="app.showSpreads()">
                    🔮 Получить предсказание
                </button>
                
                <button class="button" onclick="app.showPackages()">
                    📦 Купить пакет
                </button>
                
                <button class="button" onclick="app.showHistory()">
                    📚 История раскладов
                </button>
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

            const spreadsHtml = spreads.map(spread => `
                <div class="spread-card" onclick="app.selectSpread(${spread.id})">
                    <h3>${spread.name}</h3>
                    <p>${spread.description || 'Описание отсутствует'}</p>
                    <small>Карт в раскладе: ${spread.num_cards}</small>
                </div>
            `).join('');

            const content = `
                <div class="card">
                    <h2>Выберите расклад</h2>
                    ${spreadsHtml}
                </div>
                
                <button class="button" onclick="app.showMainMenu()">
                    ← Назад
                </button>
            `;
            
            this.ui.updateContent(content);
            
        } catch (error) {
            console.error('Ошибка загрузки раскладов:', error);
            this.ui.showError('Ошибка загрузки раскладов');
        }
    }

    async selectSpread(spreadId) {
        try {
            this.ui.showLoading('Создание интерпретации...');
            
            // Создаем интерпретацию
            const interpretation = await this.api.createInterpretation({
                user: this.currentUser.id,
                spread: spreadId,
                cards: [] // Карты будут выбраны автоматически на бэкенде
            });
            
            // Обновляем баланс пользователя
            this.currentUser.balance -= 1;
            
            this.showInterpretationResult(interpretation);
            
        } catch (error) {
            console.error('Ошибка создания интерпретации:', error);
            this.ui.showError('Ошибка создания интерпретации');
        }
    }

    showInterpretationResult(interpretation) {
        // Если есть изображения, используем их, иначе fallback на название
        const cardsHtml = (interpretation.cards_names || []).map((cardName, idx) => {
            const imgUrl = interpretation.cards_images && interpretation.cards_images[idx];
            return `
                <div class="card-item">
                    ${imgUrl ? `<img src="${imgUrl}" alt="${cardName}" class="card-image" style="max-width:120px;max-height:200px;display:block;margin:0 auto 8px;"/>` : ''}
                    <div>${cardName}</div>
                </div>
            `;
        }).join('');

        const content = `
            <div class="interpretation-result">
                <h2>🔮 Ваше предсказание</h2>
                
                <h3>Расклад: ${interpretation.spread_name}</h3>
                
                <div class="cards-list">
                    ${cardsHtml}
                </div>
                
                <h3>Интерпретация:</h3>
                <p>${interpretation.ai_response}</p>
                
                <div class="balance">
                    💰 Осталось раскладов: ${this.currentUser.balance}
                </div>
            </div>
            
            <button class="button" onclick="app.showMainMenu()">
                ← Вернуться в меню
            </button>
        `;
        
        this.ui.updateContent(content);
    }

    async showPackages() {
        try {
            this.ui.showLoading('Загрузка пакетов...');
            
            const packages = await this.api.getPackages(this.currentProject.id);
            
            if (packages.length === 0) {
                this.ui.showError('Нет доступных пакетов');
                return;
            }

            const packagesHtml = packages.map(pkg => `
                <div class="package-item">
                    <h3>${pkg.name}</h3>
                    <div class="package-price">${pkg.price}₽</div>
                    <div class="package-description">
                        ${pkg.package_type === 'one_time' 
                            ? `${pkg.num_readings} раскладов`
                            : `Подписка на ${pkg.subscription_days} дней`
                        }
                    </div>
                    <button class="button" onclick="app.buyPackage(${pkg.id})">
                        Купить
                    </button>
                </div>
            `).join('');

            const content = `
                <div class="card">
                    <h2>Доступные пакеты</h2>
                    ${packagesHtml}
                </div>
                
                <button class="button" onclick="app.showMainMenu()">
                    ← Назад
                </button>
            `;
            
            this.ui.updateContent(content);
            
        } catch (error) {
            console.error('Ошибка загрузки пакетов:', error);
            this.ui.showError('Ошибка загрузки пакетов');
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

            const historyHtml = interpretations.map(interpretation => {
                const cardsHtml = (interpretation.cards_names || []).map((cardName, idx) => {
                    const imgUrl = interpretation.cards_images && interpretation.cards_images[idx];
                    return `
                        <div class="card-item">
                            ${imgUrl ? `<img src="${imgUrl}" alt="${cardName}" class="card-image" style="max-width:80px;max-height:120px;display:block;margin:0 auto 4px;"/>` : ''}
                            <div>${cardName}</div>
                        </div>
                    `;
                }).join('');
                return `
                    <div class="history-item">
                        <div class="history-date">
                            ${new Date(interpretation.created_at).toLocaleDateString('ru-RU')}
                        </div>
                        <strong>${interpretation.spread_name}</strong>
                        <div class="cards-list">
                            ${cardsHtml}
                        </div>
                    </div>
                `;
            }).join('');

            const content = `
                <div class="card">
                    <h2>История раскладов</h2>
                    ${historyHtml}
                </div>
                
                <button class="button" onclick="app.showMainMenu()">
                    ← Назад
                </button>
            `;
            
            this.ui.updateContent(content);
            
        } catch (error) {
            console.error('Ошибка загрузки истории:', error);
            this.ui.showError('Ошибка загрузки истории');
        }
    }
}

// Делаем приложение доступным глобально для обработчиков событий
window.app = null; 