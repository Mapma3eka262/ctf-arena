// frontend/assets/js/notifications.js
class NotificationSystem {
    constructor() {
        this.notifications = [];
        this.isInitialized = false;
        this.init();
    }

    init() {
        if (this.isInitialized) return;
        
        this.createNotificationContainer();
        this.setupEventListeners();
        this.isInitialized = true;
        
        console.log('🔔 Notification System initialized');
    }

    createNotificationContainer() {
        // Create main notification container
        const container = document.createElement('div');
        container.id = 'notification-system';
        container.className = 'fixed top-4 right-4 z-50 space-y-2 max-w-sm';
        
        document.body.appendChild(container);
    }

    setupEventListeners() {
        // Listen for custom notification events
        document.addEventListener('ctf-notification', (event) => {
            this.showNotification(event.detail);
        });

        // Listen for WebSocket notifications if available
        if (window.ctfWebSocket) {
            window.ctfWebSocket.on('notification', (data) => {
                this.showNotification(data.notification);
            });
        }

        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                this.checkPendingNotifications();
            }
        });
    }

    showNotification(notificationData) {
        const notification = {
            id: this.generateId(),
            type: notificationData.type || 'info',
            title: notificationData.title || 'Уведомление',
            message: notificationData.message,
            duration: notificationData.duration || 5000,
            action: notificationData.action,
            timestamp: new Date()
        };

        this.notifications.push(notification);
        this.renderNotification(notification);

        // Auto-remove after duration
        if (notification.duration > 0) {
            setTimeout(() => {
                this.removeNotification(notification.id);
            }, notification.duration);
        }

        return notification.id;
    }

    renderNotification(notification) {
        const container = document.getElementById('notification-system');
        const notificationElement = document.createElement('div');
        
        notificationElement.id = `notification-${notification.id}`;
        notificationElement.className = `notification-toast p-4 rounded-lg shadow-lg transform transition-all duration-300 toast-enter ${
            this.getNotificationClass(notification.type)
        }`;
        
        notificationElement.innerHTML = `
            <div class="flex items-start">
                <div class="flex-shrink-0 mt-0.5">
                    ${this.getNotificationIcon(notification.type)}
                </div>
                <div class="ml-3 flex-1">
                    <div class="flex justify-between items-start">
                        <h4 class="font-semibold text-white">${this.escapeHtml(notification.title)}</h4>
                        <button class="text-white hover:text-gray-200 transition-colors" 
                                onclick="window.notificationSystem.removeNotification('${notification.id}')">
                            <i data-feather="x" class="w-4 h-4"></i>
                        </button>
                    </div>
                    <p class="mt-1 text-sm text-white">${this.escapeHtml(notification.message)}</p>
                    ${notification.action ? `
                        <div class="mt-2">
                            <button class="text-xs bg-white bg-opacity-20 hover:bg-opacity-30 text-white px-2 py-1 rounded transition-colors"
                                    onclick="${notification.action.handler}">
                                ${notification.action.text}
                            </button>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
        
        container.appendChild(notificationElement);
        feather.replace();
        
        // Trigger animation
        setTimeout(() => {
            notificationElement.classList.add('opacity-100');
        }, 10);
    }

    removeNotification(notificationId) {
        const notificationElement = document.getElementById(`notification-${notificationId}`);
        if (notificationElement) {
            notificationElement.classList.add('toast-exit');
            notificationElement.classList.remove('toast-enter');
            
            setTimeout(() => {
                if (notificationElement.parentElement) {
                    notificationElement.remove();
                }
            }, 300);
        }

        // Remove from array
        this.notifications = this.notifications.filter(n => n.id !== notificationId);
    }

    removeAllNotifications() {
        this.notifications.forEach(notification => {
            this.removeNotification(notification.id);
        });
    }

    getNotificationClass(type) {
        const classes = {
            info: 'bg-blue-600',
            success: 'bg-green-600',
            warning: 'bg-yellow-600',
            error: 'bg-red-600'
        };
        return classes[type] || classes.info;
    }

    getNotificationIcon(type) {
        const icons = {
            info: 'info',
            success: 'check-circle',
            warning: 'alert-triangle',
            error: 'x-circle'
        };
        const iconName = icons[type] || 'info';
        
        return `<i data-feather="${iconName}" class="w-5 h-5 text-white"></i>`;
    }

    generateId() {
        return `notification_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    checkPendingNotifications() {
        // Check if there are any notifications that should be shown
        // when the page becomes visible
        const now = new Date();
        const recentNotifications = this.notifications.filter(
            n => (now - n.timestamp) < 300000 // 5 minutes
        );
        
        recentNotifications.forEach(notification => {
            this.renderNotification(notification);
        });
    }

    // Public API methods
    info(message, title = 'Информация') {
        return this.showNotification({
            type: 'info',
            title,
            message
        });
    }

    success(message, title = 'Успех') {
        return this.showNotification({
            type: 'success',
            title,
            message
        });
    }

    warning(message, title = 'Предупреждение') {
        return this.showNotification({
            type: 'warning',
            title,
            message
        });
    }

    error(message, title = 'Ошибка') {
        return this.showNotification({
            type: 'error',
            title,
            message,
            duration: 8000 // Longer duration for errors
        });
    }

    escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Method to show notification with action
    showActionNotification(config) {
        return this.showNotification(config);
    }

    // Method to update existing notification
    updateNotification(notificationId, updates) {
        const notificationIndex = this.notifications.findIndex(n => n.id === notificationId);
        if (notificationIndex !== -1) {
            this.notifications[notificationIndex] = {
                ...this.notifications[notificationIndex],
                ...updates
            };
            
            // Re-render the notification
            this.removeNotification(notificationId);
            this.renderNotification(this.notifications[notificationIndex]);
        }
    }
}

// Initialize notification system
document.addEventListener('DOMContentLoaded', () => {
    window.notificationSystem = new NotificationSystem();
});

// Global helper function for quick notifications
window.showNotification = (message, type = 'info', title = null) => {
    if (window.notificationSystem) {
        const notificationTitle = title || 
            (type === 'success' ? 'Успех' :
             type === 'warning' ? 'Предупреждение' :
             type === 'error' ? 'Ошибка' : 'Информация');
        
        return window.notificationSystem[type](message, notificationTitle);
    } else {
        // Fallback to alert if notification system not ready
        alert(`${type.toUpperCase()}: ${message}`);
    }
};