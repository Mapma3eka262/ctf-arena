export function leaderboard() {
  return {
    teams: [],
    loading: false,
    updateInterval: null,
    
    init() {
      this.loadLeaderboard();
      // Auto-update every 30 seconds
      this.updateInterval = setInterval(() => {
        this.loadLeaderboard();
      }, 30000);
    },
    
    async loadLeaderboard() {
      this.loading = true;
      try {
        const response = await axios.get('/api/submissions/leaderboard');
        this.teams = response.data;
      } catch (error) {
        console.error('Failed to load leaderboard:', error);
      } finally {
        this.loading = false;
      }
    },
    
    destroy() {
      if (this.updateInterval) {
        clearInterval(this.updateInterval);
      }
    }
  };
}