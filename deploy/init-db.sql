-- deploy/init-db.sql
-- Initial database setup for CyberCTF Arena

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Set timezone
SET timezone = 'Europe/Moscow';

-- Create additional indexes for performance
CREATE INDEX IF NOT EXISTS idx_submissions_team_challenge ON submissions(team_id, challenge_id);
CREATE INDEX IF NOT EXISTS idx_submissions_status ON submissions(status);
CREATE INDEX IF NOT EXISTS idx_submissions_submitted_at ON submissions(submitted_at DESC);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_team ON users(team_id);
CREATE INDEX IF NOT EXISTS idx_challenges_category ON challenges(category);
CREATE INDEX IF NOT EXISTS idx_challenges_difficulty ON challenges(difficulty);
CREATE INDEX IF NOT EXISTS idx_challenges_points ON challenges(points);
CREATE INDEX IF NOT EXISTS idx_teams_score ON teams(score DESC);

-- Create function for updating updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_teams_updated_at ON teams;
CREATE TRIGGER update_teams_updated_at
    BEFORE UPDATE ON teams
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_challenges_updated_at ON challenges;
CREATE TRIGGER update_challenges_updated_at
    BEFORE UPDATE ON challenges
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create function for leaderboard calculation
CREATE OR REPLACE FUNCTION get_team_leaderboard(limit_count INTEGER DEFAULT 10)
RETURNS TABLE(
    position INTEGER,
    team_id INTEGER,
    team_name VARCHAR,
    score INTEGER,
    total_solved INTEGER,
    last_submission TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    WITH team_stats AS (
        SELECT 
            t.id as team_id,
            t.name as team_name,
            t.score,
            COUNT(DISTINCT s.challenge_id) as total_solved,
            MAX(s.submitted_at) as last_submission,
            ROW_NUMBER() OVER (ORDER BY t.score DESC, MAX(s.submitted_at) ASC) as position
        FROM teams t
        LEFT JOIN submissions s ON t.id = s.team_id AND s.status = 'accepted'
        GROUP BY t.id, t.name, t.score
    )
    SELECT 
        ts.position,
        ts.team_id,
        ts.team_name,
        ts.score,
        ts.total_solved,
        ts.last_submission
    FROM team_stats ts
    ORDER BY ts.position
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Create function for user activity stats
CREATE OR REPLACE FUNCTION get_user_activity_stats(days_back INTEGER DEFAULT 7)
RETURNS TABLE(
    user_id INTEGER,
    username VARCHAR,
    submissions_count BIGINT,
    accepted_count BIGINT,
    success_rate DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        u.id as user_id,
        u.username,
        COUNT(s.id) as submissions_count,
        COUNT(CASE WHEN s.status = 'accepted' THEN 1 END) as accepted_count,
        CASE 
            WHEN COUNT(s.id) = 0 THEN 0
            ELSE ROUND(COUNT(CASE WHEN s.status = 'accepted' THEN 1 END) * 100.0 / COUNT(s.id), 2)
        END as success_rate
    FROM users u
    LEFT JOIN submissions s ON u.id = s.user_id 
        AND s.submitted_at >= CURRENT_TIMESTAMP - (days_back || ' days')::INTERVAL
    GROUP BY u.id, u.username
    ORDER BY submissions_count DESC;
END;
$$ LANGUAGE plpgsql;

-- Insert default services for monitoring
INSERT INTO services (name, type, host, port, check_endpoint, expected_status, is_active) VALUES
('CTF API', 'web', 'localhost', 8000, '/api/health', 200, true),
('CTF WebSocket', 'web', 'localhost', 8001, '/health', 200, true),
('PostgreSQL', 'database', 'localhost', 5432, NULL, NULL, true),
('Redis', 'database', 'localhost', 6379, NULL, NULL, true),
('Nginx', 'web', 'localhost', 80, '/', 200, true)
ON CONFLICT DO NOTHING;

-- Create admin user (password: admin123)
INSERT INTO users (username, email, hashed_password, is_admin, is_captain, is_active) VALUES
('admin', 'admin@ctf-arena.local', '$2b$12$LQv3c1yqBWVHxkd0L6k0u.LdA6Y2ZQ3cZ3jJZkQ8Q3b5dYvXrYbXa', true, true, true)
ON CONFLICT (username) DO NOTHING;

-- Create test competition
INSERT INTO competitions (name, description, start_time, end_time, is_active, max_team_size) VALUES
('Demo CTF Competition', 'Тестовое соревнование для демонстрации возможностей платформы', 
 CURRENT_TIMESTAMP + INTERVAL '1 hour', 
 CURRENT_TIMESTAMP + INTERVAL '25 hours', 
 true, 5)
ON CONFLICT DO NOTHING;

-- Create sample challenges
INSERT INTO challenges (title, description, category, difficulty, points, flag, is_active) VALUES
('Welcome Challenge', 'Простое задание для знакомства с платформой', 'MISC', 'easy', 50, 'CTF{w3lc0m3_t0_ctf_4r3n4}', true),
('Web Security 101', 'Базовое задание по веб-безопасности', 'WEB', 'easy', 100, 'CTF{w3b_s3cur1ty_b4s1c5}', true),
('Crypto Challenge', 'Задание по криптографии для начинающих', 'CRYPTO', 'easy', 100, 'CTF{cryp70_b4s1c5}', true),
('Forensics Investigation', 'Расследование цифровых улик', 'FORENSICS', 'medium', 200, 'CTF{f0r3ns1c5_m4st3r}', true),
('Reverse Engineering', 'Обратная разработка приложения', 'REVERSING', 'hard', 300, 'CTF{r3v3rs3_3ng1n33r1ng}', true),
('PWN Challenge', 'Эксплуатация уязвимостей в бинарных файлах', 'PWN', 'hard', 400, 'CTF{pwn_m4st3r}', true)
ON CONFLICT DO NOTHING;

-- Create indexes for better performance
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_submissions_team_status ON submissions(team_id, status);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_submissions_challenge_status ON submissions(challenge_id, status);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_last_login ON users(last_login);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_notifications_user_created ON notifications(user_id, created_at DESC);

-- Create materialized view for leaderboard (for better performance)
CREATE MATERIALIZED VIEW IF NOT EXISTS leaderboard_mv AS
SELECT 
    t.id as team_id,
    t.name as team_name,
    t.score,
    COUNT(DISTINCT s.challenge_id) as solved_challenges,
    COUNT(s.id) as total_submissions,
    MAX(s.submitted_at) as last_solve
FROM teams t
LEFT JOIN submissions s ON t.id = s.team_id AND s.status = 'accepted'
GROUP BY t.id, t.name, t.score;

CREATE UNIQUE INDEX IF NOT EXISTS idx_leaderboard_mv_team ON leaderboard_mv(team_id);
REFRESH MATERIALIZED VIEW CONCURRENTLY leaderboard_mv;

-- Create function to refresh materialized views
CREATE OR REPLACE FUNCTION refresh_materialized_views()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY leaderboard_mv;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ctfuser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ctfuser;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO ctfuser;

-- Create read-only user for monitoring (optional)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'ctf_monitor') THEN
        CREATE USER ctf_monitor WITH PASSWORD 'monitor_password';
        GRANT CONNECT ON DATABASE ctfarena TO ctf_monitor;
        GRANT USAGE ON SCHEMA public TO ctf_monitor;
        GRANT SELECT ON ALL TABLES IN SCHEMA public TO ctf_monitor;
    END IF;
END $$;

COMMENT ON DATABASE ctfarena IS 'CyberCTF Arena - CTF Platform Database';