export class ApiService {
    constructor() {
        this.baseUrl = 'http://localhost:8000/api';
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    // Вспомогательный метод для обработки ответов с пагинацией
    extractResults(data) {
        // Если данные содержат пагинацию (DRF формат), извлекаем results
        if (data && typeof data === 'object' && 'results' in data) {
            return data.results;
        }
        // Иначе возвращаем данные как есть
        return data;
    }

    // Получение настроек темы для проекта
    async getThemeSettings(projectId) {
        return this.request(`/projects/${projectId}/theme_settings/`);
    }

    // Обновление настроек темы для проекта
    async updateThemeSettings(projectId, themeSettings) {
        return this.request(`/projects/${projectId}/update_theme_settings/`, {
            method: 'POST',
            body: JSON.stringify(themeSettings)
        });
    }

    // Получение проектов
    async getProjects() {
        const data = await this.request('/projects/');
        return this.extractResults(data);
    }

    // Получение или создание пользователя
    async getOrCreateUser(userData) {
        try {
            // Сначала пытаемся найти пользователя
            const searchData = await this.request(`/users/?telegram_user_id=${userData.telegram_user_id}&project=${userData.project}`);
            const users = this.extractResults(searchData);
            
            if (users && users.length > 0) {
                return users[0];
            }
        } catch (error) {
            console.log('Пользователь не найден, создаем нового');
        }

        // Создаем нового пользователя
        return this.request('/users/', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    }

    // Получение раскладов
    async getSpreads(projectId) {
        const data = await this.request(`/tarot/spreads/?project=${projectId}`);
        return this.extractResults(data);
    }

    // Получение карт для расклада
    async getSpreadCards(data) {
        return this.request('/tarot/interpretations/get_cards/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // Создание интерпретации
    async createInterpretation(data) {
        return this.request('/tarot/interpretations/create_interpretation/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // Получение интерпретаций пользователя
    async getInterpretations(userId) {
        const data = await this.request(`/tarot/interpretations/?user=${userId}`);
        return this.extractResults(data);
    }

    // Получение пакетов
    async getPackages(projectId) {
        const data = await this.request(`/packages/?project=${projectId}`);
        return this.extractResults(data);
    }

    // Создание тестового платежа
    async createTestPayment(data) {
        return this.request('/payments/test_payment/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
} 