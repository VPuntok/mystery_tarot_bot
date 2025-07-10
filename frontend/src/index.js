import './styles.css';
import { TarotApp } from './app.js';

// Инициализация Telegram WebApp
window.Telegram.WebApp.ready();
window.Telegram.WebApp.expand();

// Запуск приложения
document.addEventListener('DOMContentLoaded', () => {
    const app = new TarotApp();
    window.app = app; // Делаем приложение доступным глобально
    app.init();
}); 