import axios from 'axios';

export class ApiService {
    constructor() {
        // В продакшене URL будет настраиваться через переменные окружения
        this.baseURL = 'http://localhost:8000/api';
        this.client = axios.create({
            baseURL: this.baseURL,
            timeout: 10000,
            headers: {
                'Content-Type': 'application/json',
            }
        });

        // Добавляем перехватчик для обработки ошибок
        this.client.interceptors.response.use(
            response => response,
            error => {
                console.error('API Error:', error.response?.data || error.message);
                if (error.response?.status === 404) {
                    throw new Error('API endpoint не найден. Проверьте, запущен ли бэкенд.');
                } else if (error.response?.status === 500) {
                    throw new Error('Ошибка сервера. Проверьте логи бэкенда.');
                } else if (error.code === 'ECONNREFUSED') {
                    throw new Error('Не удается подключиться к серверу. Убедитесь, что бэкенд запущен на http://localhost:8000');
                }
                throw error;
            }
        );
    }

    // Проекты
    async getProjects() {
        const response = await this.client.get('/projects/');
        return response.data.results || response.data;
    }

    // Пользователи
    async getOrCreateUser(userData) {
        try {
            // Сначала пытаемся найти пользователя
            const response = await this.client.get('/users/', {
                params: {
                    telegram_user_id: userData.telegram_user_id,
                    project: userData.project
                }
            });
            
            const users = response.data.results || response.data;
            if (users.length > 0) {
                return users[0];
            }
        } catch (error) {
            console.log('Пользователь не найден, создаем нового');
        }

        // Создаем нового пользователя
        const response = await this.client.post('/users/', userData);
        return response.data;
    }

    // Расклады
    async getSpreads(projectId) {
        const response = await this.client.get('/tarot/spreads/', {
            params: { project: projectId }
        });
        return response.data.results || response.data;
    }

    // Интерпретации
    async createInterpretation(interpretationData) {
        const response = await this.client.post('/tarot/interpretations/create_interpretation/', interpretationData);
        return response.data;
    }

    async getInterpretations(userId) {
        const response = await this.client.get('/tarot/interpretations/', {
            params: { user: userId }
        });
        return response.data.results || response.data;
    }

    // Пакеты
    async getPackages(projectId) {
        const response = await this.client.get('/packages/', {
            params: { project: projectId }
        });
        return response.data.results || response.data;
    }

    // Платежи
    async createPayment(paymentData) {
        const response = await this.client.post('/payments/', paymentData);
        return response.data;
    }

    async createTestPayment(paymentData) {
        const response = await this.client.post('/payments/test_payment/', paymentData);
        return response.data;
    }

    // Telegram Bot API (имитация)
    async sendTelegramMessage(projectId, messageData) {
        const response = await this.client.post(`/projects/${projectId}/send_message/`, messageData);
        return response.data;
    }

    async handleTelegramWebhook(projectId, messageData) {
        const response = await this.client.post('/telegram/webhook/', {
            project_id: projectId,
            message: messageData
        });
        return response.data;
    }
} 