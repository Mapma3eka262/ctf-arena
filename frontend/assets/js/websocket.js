// frontend/assets/js/websocket.js
class CTFWebSocket {
    constructor() {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.eventHandlers = new Map();
        this.isConnected = false;
    }

    connect(token) {
        if (this.ws && this.isConnected) {
            return;
        }

        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/api/ws/arena?token=${token}`;
            
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                console.log('🔗 WebSocket connected');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.triggerEvent('connected', {});
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleMessage(data);
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };

            this.ws.onclose = (event) => {
                console.log('🔌 WebSocket disconnected');
                this.isConnected = false;
                this.triggerEvent('disconnected', { event });
                
                if (this.reconnectAttempts < this.maxReconnectAttempts) {
                    setTimeout(() => {
                        this.reconnectAttempts++;
                        this.reconnectDelay = Math.min(this.reconnectDelay * 1.5, 30000);
                        console.log(`🔄 Reconnecting... Attempt ${this.reconnectAttempts}`);
                        this.connect(token);
                    }, this.reconnectDelay);
                }
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.triggerEvent('error', { error });
            };

        } catch (error) {
            console.error('WebSocket connection error:', error);
        }
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
            this.isConnected = false;
        }
    }

    send(message) {
        if (this.ws && this.isConnected) {
            try {
                this.ws.send(JSON.stringify(message));
            } catch (error) {
                console.error('Error sending WebSocket message:', error);
            }
        }
    }

    on(event, handler) {
        if (!this.eventHandlers.has(event)) {
            this.eventHandlers.set(event, []);
        }
        this.eventHandlers.get(event).push(handler);
    }

    off(event, handler) {
        if (this.eventHandlers.has(event)) {
            const handlers = this.eventHandlers.get(event);
            const index = handlers.indexOf(handler);
            if (index > -1) {
                handlers.splice(index, 1);
            }
        }
    }

    triggerEvent(event, data) {
        if (this.eventHandlers.has(event)) {
            this.eventHandlers.get(event).forEach(handler => {
                try {
                    handler(data);
                } catch (error) {
                    console.error(`Error in event handler for ${event}:`, error);
                }
            });
        }
    }

    handleMessage(data) {
        const type = data.type;
        this.triggerEvent(type, data);
        
        // Special handling for specific message types
        switch (type) {
            case 'notification':
                this.showNotification(data.notification);
                break;
            case 'team_flag_submitted':
                this.updateTeamScore(data);
                break;
            case 'user_connected':
            case 'user_disconnected':
                this.updateOnlineUsers(data);
                break;
        }
    }

    showNotification(notification) {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 transform transition-transform duration-300 ${
            notification.type === 'success' ? 'bg-green-600' :
            notification.type === 'warning' ? 'bg-yellow-600' :
            notification.type === 'error' ? 'bg-red-600' : 'bg-blue-600'
        }`;
        
        toast.innerHTML = `
            <div class="flex items-start">
                <div class="flex-1">
                    <h4 class="font-bold text-white">${this.escapeHtml(notification.title)}</h4>
                    <p class="text-white text-sm mt-1">${this.escapeHtml(notification.message)}</p>
                </div>
                <button class="ml-4 text-white hover:text-gray-200" onclick="this.parentElement.parentElement.remove()">
                    <i data-feather="x" class="w-4 h-4"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(toast);
        feather.replace();
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 5000);
    }

    updateTeamScore(data) {
        // Update team score in real-time
        const scoreElement = document.getElementById('team-score');
        if (scoreElement) {
            const currentScore = parseInt(scoreElement.textContent) || 0;
            scoreElement.textContent = currentScore + data.points;
            
            // Add animation
            scoreElement.classList.add('score-update');
            setTimeout(() => {
                scoreElement.classList.remove('score-update');
            }, 1000);
        }
    }

    updateOnlineUsers(data) {
        // Update online users counter
        const onlineCountElement = document.getElementById('online-users-count');
        if (onlineCountElement) {
            onlineCountElement.textContent = data.connection_count;
        }
    }

    escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Utility methods for common operations
    submitFlag(challengeId, flag) {
        this.send({
            type: 'flag_submission',
            challenge_id: challengeId,
            flag: flag
        });
    }

    sendChatMessage(message) {
        this.send({
            type: 'chat_message',
            message: message
        });
    }

    requestTeamStatus() {
        this.send({
            type: 'get_team_status'
        });
    }

    ping() {
        this.send({
            type: 'ping'
        });
    }
}

// Global WebSocket instance
window.ctfWebSocket = new CTFWebSocket();