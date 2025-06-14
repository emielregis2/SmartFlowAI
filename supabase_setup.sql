-- =====================================================
-- SmartFlowAI - Konfiguracja bazy danych Supabase
-- =====================================================

-- 1. Włączenie rozszerzeń
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Tabela użytkowników
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- 3. Tabela procesów biznesowych
CREATE TABLE IF NOT EXISTS business_processes (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    ai_analysis TEXT,
    analysis_depth VARCHAR(50) DEFAULT 'Podstawowa (szybka)',
    automation_potential INTEGER CHECK (automation_potential >= 0 AND automation_potential <= 100),
    time_savings_hours DECIMAL(10,2),
    cost_savings_annual DECIMAL(15,2),
    implementation_difficulty VARCHAR(50),
    recommended_tools TEXT,
    next_steps TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- 4. Tabela kategorii procesów (opcjonalna)
CREATE TABLE IF NOT EXISTS process_categories (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Tabela logów aktywności
CREATE TABLE IF NOT EXISTS activity_logs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    action VARCHAR(255) NOT NULL,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. Indeksy dla wydajności
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_business_processes_user_id ON business_processes(user_id);
CREATE INDEX IF NOT EXISTS idx_business_processes_created_at ON business_processes(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_activity_logs_user_id ON activity_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_created_at ON activity_logs(created_at DESC);

-- 7. Funkcja aktualizacji timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 8. Triggery dla automatycznej aktualizacji updated_at
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_business_processes_updated_at 
    BEFORE UPDATE ON business_processes 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 9. Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE business_processes ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity_logs ENABLE ROW LEVEL SECURITY;

-- 10. Polityki RLS dla users
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid() = id);

-- 11. Polityki RLS dla business_processes
CREATE POLICY "Users can view own processes" ON business_processes
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own processes" ON business_processes
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own processes" ON business_processes
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own processes" ON business_processes
    FOR DELETE USING (auth.uid() = user_id);

-- 12. Polityki RLS dla activity_logs
CREATE POLICY "Users can view own logs" ON activity_logs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own logs" ON activity_logs
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- 13. Dane testowe - użytkownicy
INSERT INTO users (id, email, password_hash, full_name) VALUES
    ('550e8400-e29b-41d4-a716-446655440001', 'test@smartflowai.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/VcSAg/9S2', 'Test User'),
    ('550e8400-e29b-41d4-a716-446655440002', 'admin@smartflowai.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/VcSAg/9S2', 'Admin User'),
    ('550e8400-e29b-41d4-a716-446655440003', 'demo@smartflowai.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/VcSAg/9S2', 'Demo User')
ON CONFLICT (email) DO NOTHING;

-- 14. Dane testowe - procesy biznesowe
INSERT INTO business_processes (user_id, title, description, ai_analysis, automation_potential, time_savings_hours, implementation_difficulty) VALUES
    ('550e8400-e29b-41d4-a716-446655440001', 
     'Proces fakturowania', 
     'Ręczne tworzenie faktur dla klientów, wysyłanie emailem i śledzenie płatności',
     'Proces ma wysoki potencjał automatyzacji. Można zaimplementować system automatycznego generowania faktur, wysyłania emaili i przypomnieć o płatnościach.',
     85,
     15.5,
     'Średnia'),
    ('550e8400-e29b-41d4-a716-446655440001',
     'Zarządzanie zapasami',
     'Cotygodniowe sprawdzanie stanów magazynowych i składanie zamówień u dostawców',
     'Proces można zautomatyzować poprzez implementację systemu automatycznego zamawiania przy osiągnięciu minimalnych stanów magazynowych.',
     75,
     8.0,
     'Łatwa')
ON CONFLICT DO NOTHING;

-- 15. Kategorie procesów
INSERT INTO process_categories (name, description) VALUES
    ('Finanse', 'Procesy związane z księgowością i finansami'),
    ('HR', 'Procesy zarządzania zasobami ludzkimi'),
    ('Sprzedaż', 'Procesy sprzedażowe i obsługi klienta'),
    ('Produkcja', 'Procesy produkcyjne i operacyjne'),
    ('IT', 'Procesy informatyczne i techniczne')
ON CONFLICT DO NOTHING;

-- 16. Widok statystyk dla użytkownika
CREATE OR REPLACE VIEW user_process_stats AS
SELECT 
    user_id,
    COUNT(*) as total_processes,
    AVG(automation_potential) as avg_automation_potential,
    SUM(time_savings_hours) as total_time_savings,
    SUM(cost_savings_annual) as total_cost_savings
FROM business_processes 
WHERE is_active = TRUE
GROUP BY user_id;

-- 17. Funkcja do wyszukiwania procesów
CREATE OR REPLACE FUNCTION search_processes(search_term TEXT, user_uuid UUID)
RETURNS TABLE (
    id UUID,
    title VARCHAR(500),
    description TEXT,
    automation_potential INTEGER,
    created_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        bp.id,
        bp.title,
        bp.description,
        bp.automation_potential,
        bp.created_at
    FROM business_processes bp
    WHERE bp.user_id = user_uuid
    AND bp.is_active = TRUE
    AND (
        bp.title ILIKE '%' || search_term || '%' OR
        bp.description ILIKE '%' || search_term || '%' OR
        bp.ai_analysis ILIKE '%' || search_term || '%'
    )
    ORDER BY bp.created_at DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 18. Funkcja do logowania aktywności
CREATE OR REPLACE FUNCTION log_activity(
    user_uuid UUID,
    action_name VARCHAR(255),
    action_details JSONB DEFAULT NULL,
    client_ip INET DEFAULT NULL,
    client_user_agent TEXT DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    log_id UUID;
BEGIN
    INSERT INTO activity_logs (user_id, action, details, ip_address, user_agent)
    VALUES (user_uuid, action_name, action_details, client_ip, client_user_agent)
    RETURNING id INTO log_id;
    
    RETURN log_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 19. Sprawdzenie poprawności konfiguracji
DO $$
BEGIN
    RAISE NOTICE 'SmartFlowAI database setup completed successfully!';
    RAISE NOTICE 'Tables created: users, business_processes, process_categories, activity_logs';
    RAISE NOTICE 'Test users created with password: test123456';
    RAISE NOTICE 'RLS policies enabled for security';
END $$; 