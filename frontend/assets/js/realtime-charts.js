// frontend/assets/js/realtime-charts.js
class RealtimeCharts {
    constructor() {
        this.charts = new Map();
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeCharts();
    }

    initializeCharts() {
        // Initialize Chart.js instances for different metrics
        this.initializeSubmissionChart();
        this.initializeScoreChart();
        this.initializeCategoryChart();
    }

    initializeSubmissionChart() {
        const ctx = document.getElementById('submission-timeline');
        if (!ctx) return;

        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Отправки флагов',
                    data: [],
                    borderColor: '#EA000F',
                    backgroundColor: 'rgba(234, 0, 15, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'hour'
                        }
                    },
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });

        this.charts.set('submission-timeline', chart);
    }

    initializeScoreChart() {
        const ctx = document.getElementById('score-progression');
        if (!ctx) return;

        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Общий счет',
                    data: [],
                    borderColor: '#00FF00',
                    backgroundColor: 'rgba(0, 255, 0, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });

        this.charts.set('score-progression', chart);
    }

    initializeCategoryChart() {
        const ctx = document.getElementById('category-distribution');
        if (!ctx) return;

        const chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['WEB', 'Crypto', 'Forensics', 'Reversing', 'PWN', 'MISC'],
                datasets: [{
                    data: [0, 0, 0, 0, 0, 0],
                    backgroundColor: [
                        '#FF6384',
                        '#36A2EB',
                        '#FFCE56',
                        '#4BC0C0',
                        '#9966FF',
                        '#FF9F40'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });

        this.charts.set('category-distribution', chart);
    }

    setupEventListeners() {
        // Listen for WebSocket events
        if (window.ctfWebSocket) {
            window.ctfWebSocket.on('team_flag_submitted', (data) => {
                this.updateCharts(data);
            });

            window.ctfWebSocket.on('team_status', (data) => {
                this.updateTeamStatus(data);
            });
        }

        // Auto-refresh charts
        setInterval(() => {
            this.refreshChartData();
        }, 30000);
    }

    updateCharts(data) {
        // Update submission timeline
        const submissionChart = this.charts.get('submission-timeline');
        if (submissionChart) {
            const now = new Date();
            submissionChart.data.labels.push(now);
            submissionChart.data.datasets[0].data.push(1);
            
            // Keep only last 24 hours
            if (submissionChart.data.labels.length > 24) {
                submissionChart.data.labels.shift();
                submissionChart.data.datasets[0].data.shift();
            }
            
            submissionChart.update('none');
        }

        // Update score progression
        const scoreChart = this.charts.get('score-progression');
        if (scoreChart && data.points) {
            const now = new Date();
            scoreChart.data.labels.push(now);
            const lastScore = scoreChart.data.datasets[0].data.slice(-1)[0] || 0;
            scoreChart.data.datasets[0].data.push(lastScore + data.points);
            
            // Keep only last 50 data points
            if (scoreChart.data.labels.length > 50) {
                scoreChart.data.labels.shift();
                scoreChart.data.datasets[0].data.shift();
            }
            
            scoreChart.update('none');
        }
    }

    updateTeamStatus(data) {
        // Update category distribution
        const categoryChart = this.charts.get('category-distribution');
        if (categoryChart && data.status && data.status.category_stats) {
            const stats = data.status.category_stats;
            categoryChart.data.datasets[0].data = [
                stats.web || 0,
                stats.crypto || 0,
                stats.forensics || 0,
                stats.reversing || 0,
                stats.pwn || 0,
                stats.misc || 0
            ];
            categoryChart.update();
        }
    }

    async refreshChartData() {
        try {
            const response = await fetch('/api/analytics/team/activity');
            const data = await response.json();
            
            this.updateChartsWithHistoricalData(data);
        } catch (error) {
            console.error('Error refreshing chart data:', error);
        }
    }

    updateChartsWithHistoricalData(data) {
        // Update charts with historical data from API
        const submissionChart = this.charts.get('submission-timeline');
        if (submissionChart && data.hourly_activity) {
            data.hourly_activity.forEach(activity => {
                submissionChart.data.labels.push(new Date().setHours(activity.hour));
                submissionChart.data.datasets[0].data.push(activity.submissions);
            });
            submissionChart.update();
        }
    }

    // Public method to update specific chart
    updateChart(chartId, data) {
        const chart = this.charts.get(chartId);
        if (chart) {
            chart.data = data;
            chart.update();
        }
    }

    // Public method to add new chart
    addChart(chartId, config) {
        const ctx = document.getElementById(chartId);
        if (ctx) {
            const chart = new Chart(ctx, config);
            this.charts.set(chartId, chart);
            return chart;
        }
        return null;
    }

    // Cleanup method
    destroy() {
        this.charts.forEach(chart => {
            chart.destroy();
        });
        this.charts.clear();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.realtimeCharts = new RealtimeCharts();
});