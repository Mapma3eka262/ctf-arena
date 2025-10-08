export function navbar() {
  return {
    user: null,
    isMenuOpen: false,
    
    init() {
      this.checkAuth();
    },
    
    checkAuth() {
      const token = localStorage.getItem('access_token');
      if (token) {
        // Verify token and get user data
        this.getUserProfile();
      }
    },
    
    async getUserProfile() {
      try {
        const response = await axios.get('/api/users/me', {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        this.user = response.data;
      } catch (error) {
        this.logout();
      }
    },
    
    logout() {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      this.user = null;
      window.location.href = '/login.html';
    },
    
    toggleMenu() {
      this.isMenuOpen = !this.isMenuOpen;
    }
  };
}