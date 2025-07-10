export class UI {
    constructor() {
        this.appContainer = document.getElementById('app');
    }

    updateContent(html) {
        this.appContainer.innerHTML = html;
        this.appContainer.classList.add('fade-in');
        
        // Убираем класс анимации через некоторое время
        setTimeout(() => {
            this.appContainer.classList.remove('fade-in');
        }, 300);
    }

    showLoading(message = 'Загрузка...') {
        this.appContainer.innerHTML = `
            <div class="loading">
                <div>${message}</div>
            </div>
        `;
    }

    showError(message) {
        this.appContainer.innerHTML = `
            <div class="error">
                <h3>❌ Ошибка</h3>
                <p>${message}</p>
                <button class="button" onclick="location.reload()">
                    Обновить страницу
                </button>
            </div>
        `;
    }

    showSuccess(message) {
        this.appContainer.innerHTML = `
            <div class="success">
                <h3>✅ Успешно</h3>
                <p>${message}</p>
            </div>
        `;
    }

    showConfirm(message, onConfirm, onCancel) {
        this.appContainer.innerHTML = `
            <div class="card">
                <h3>Подтверждение</h3>
                <p>${message}</p>
                <button class="button" onclick="window.confirmAction()">
                    Подтвердить
                </button>
                <button class="button" onclick="window.cancelAction()" style="background: var(--tg-theme-destructive-text-color, #ff4444);">
                    Отмена
                </button>
            </div>
        `;

        window.confirmAction = onConfirm;
        window.cancelAction = onCancel;
    }
} 