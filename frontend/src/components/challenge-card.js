export function challengeCard() {
  return {
    challenge: null,
    isSolved: false,
    showHint: false,
    
    init() {
      // Check if challenge is solved
      this.checkSolvedStatus();
    },
    
    async checkSolvedStatus() {
      // Implementation to check if current team has solved this challenge
    },
    
    get difficultyColor() {
      const colors = {
        easy: 'text-green-600 bg-green-100',
        medium: 'text-yellow-600 bg-yellow-100',
        hard: 'text-orange-600 bg-orange-100',
        insane: 'text-red-600 bg-red-100'
      };
      return colors[this.challenge.difficulty] || colors.easy;
    },
    
    get categoryColor() {
      const colors = {
        web: 'text-blue-600 bg-blue-100',
        crypto: 'text-purple-600 bg-purple-100',
        forensics: 'text-indigo-600 bg-indigo-100',
        pwn: 'text-red-600 bg-red-100',
        rev: 'text-pink-600 bg-pink-100',
        misc: 'text-gray-600 bg-gray-100'
      };
      return colors[this.challenge.category] || colors.misc;
    },
    
    async unlockHint(hintId) {
      try {
        const response = await axios.post(
          `/api/challenges/${this.challenge.id}/hints/${hintId}`,
          {},
          {
            headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
          }
        );
        this.showHint = true;
      } catch (error) {
        alert('Failed to unlock hint: ' + error.response.data.detail);
      }
    }
  };
}