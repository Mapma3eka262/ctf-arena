// frontend/assets/js/app.js
class CTFApplication {
    constructor() {
        this.websocket = null;
        this.charts = null;
        this.currentUser = null;
        this.init();
    }

    init() {
        this.checkAuthentication();
        this.initializeComponents();
        this.setupEventHandlers();
    }

    async checkAuthentication() {
        const token = localStorage.getItem('authToken');
        if (!token) {
            // Redirect to login if no token
            if (!window.location.pathname.includes('index.html') && 
                !window.location.pathname.includes('lk.html')) {
                window.location.href = '/lk.html';
            }
            return;
        }

        try {
            const response = await fetch('/api/users/me', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                this.currentUser = await response.json();
                this.initializeWebSocket(token);
            } else {
                localStorage.removeItem('authToken');
                window.location.href = '/lk.html';
            }
        } catch (error) {
            console.error('Authentication check failed:', error);
        }
    }

    initializeWebSocket(token) {
        this.websocket = window.ctfWebSocket;
        this.websocket.connect(token);
    }

    initializeComponents() {
        // Initialize real-time charts if on analytics page
        if (document.getElementById('submission-timeline')) {
            this.charts = new RealtimeCharts();
        }

        // Initialize notification bell if present
        if (document.getElementById('notification-bell')) {
            new NotificationBell();
        }

        // Initialize live arena if on live page
        if (window.location.pathname.includes('live_arena.html')) {
            new LiveArena();
        }
    }

    setupEventHandlers() {
        // Global event handlers
        document.addEventListener('logout', () => {
            this.logout();
        });

        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden && this.websocket) {
                this.websocket.ping();
            }
        });

        // Handle online/offline events
        window.addEventListener('online', () => {
            this.showNotification('Соединение восстановлено', 'success');
        });

        window.addEventListener('offline', () => {
            this.showNotification('Потеряно соединение с интернетом', 'error');
        });
    }

    logout() {
        localStorage.removeItem('authToken');
        localStorage.removeItem('refreshToken');
        
        if (this.websocket) {
            this.websocket.disconnect();
        }
        
        window.location.href = '/index.html';
    }

    showNotification(message, type = 'info') {
        // Use the WebSocket notification system or fallback
        if (this.websocket) {
            this.websocket.showNotification({
                title: type === 'error' ? 'Ошибка' : 'Уведомление',
                message: message,
                type: type
            });
        } else {
            // Fallback to simple alert
            alert(message);
        }
    }

    // Utility method for API calls
    async apiCall(endpoint, options = {}) {
        const token = localStorage.getItem('authToken');
        const defaultOptions = {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
                ...options.headers
            }
        };

        try {
            const response = await fetch(`/api${endpoint}`, {
                ...defaultOptions,
                ...options
            });

            if (response.status === 401) {
                this.logout();
                throw new Error('Authentication required');
            }

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'API request failed');
            }

            return await response.json();
        } catch (error) {
            console.error('API call failed:', error);
            throw error;
        }
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    window.ctfApp = new CTFApplication();
});