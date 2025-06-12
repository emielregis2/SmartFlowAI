-- Plik: init_db.sql
-- init_db.sql - Inicjalizacja bazy danych SmartFlowAI

-- SmartFlowAI Database Initialization
-- Wykonaj ten skrypt w Supabase SQL Editor

-- 1. Utworzenie tabeli procesów
CREATE TABLE IF NOT EXISTS processes (
    id BIGSERIAL PRIMARY KEY,
    user_email TEXT NOT NULL,
    title TEXT NOT NULL CHECK (length(title) >= 3 AND length(title) <= 255),
    description TEXT NOT NULL CHECK (length(description) >= 10),
    ai_analysis TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- 2. Dodanie komentarzy do tabeli
COMMENT ON TABLE processes IS 'Tabela przechowująca procesy biznesowe użytkowników SmartFlowAI';
COMMENT ON COLUMN processes.id IS 'Unikalny identyfikator procesu';
COMMENT ON COLUMN processes.user_email IS 'Email użytkownika (z auth.users)';
COMMENT ON COLUMN processes.title IS 'Nazwa procesu (3-255 znaków)';
COMMENT ON COLUMN processes.description IS 'Szczegółowy opis procesu (min 10 znaków)';
COMMENT ON COLUMN processes.ai_analysis IS 'Wynik analizy AI (może być NULL)';
COMMENT ON COLUMN processes.created_at IS 'Data utworzenia procesu';
COMMENT ON COLUMN processes.updated_at IS 'Data ostatniej modyfikacji';

-- 3. Włączenie Row Level Security (RLS)
ALTER TABLE processes ENABLE ROW LEVEL SECURITY;

-- 4. Usunięcie istniejących policies (jeśli istnieją)
DROP POLICY IF EXISTS "Users can view own processes" ON processes;
DROP POLICY IF EXISTS "Users can insert own processes" ON processes;
DROP POLICY IF EXISTS "Users can update own processes" ON processes;
DROP POLICY IF EXISTS "Users can delete own processes" ON processes;

-- 5. Tworzenie policies RLS
-- Użytkownicy mogą przeglądać tylko swoje procesy
CREATE POLICY "Users can view own processes" ON processes
    FOR SELECT USING (auth.email() = user_email);

-- Użytkownicy mogą dodawać procesy tylko dla siebie
CREATE POLICY "Users can insert own processes" ON processes
    FOR INSERT WITH CHECK (auth.email() = user_email);

-- Użytkownicy mogą edytować tylko swoje procesy
CREATE POLICY "Users can update own processes" ON processes
    FOR UPDATE USING (auth.email() = user_email)
    WITH CHECK (auth.email() = user_email);

-- Użytkownicy mogą usuwać tylko swoje procesy
CREATE POLICY "Users can delete own processes" ON processes
    FOR DELETE USING (auth.email() = user_email);

-- 6. Indeksy dla wydajności
CREATE INDEX IF NOT EXISTS idx_processes_user_email ON processes(user_email);
CREATE INDEX IF NOT EXISTS idx_processes_created_at ON processes(created_at DESC);

-- Indeks full-text search z fallback dla konfiguracji językowej
DO $$
BEGIN
    -- Sprawdź czy konfiguracja 'polish' istnieje
    IF EXISTS (SELECT 1 FROM pg_ts_config WHERE cfgname = 'polish') THEN
        CREATE INDEX IF NOT EXISTS idx_processes_title ON processes USING GIN(to_tsvector('polish', title));
        RAISE NOTICE 'Utworzono indeks full-text z konfiguracją polish';
    ELSIF EXISTS (SELECT 1 FROM pg_ts_config WHERE cfgname = 'english') THEN
        CREATE INDEX IF NOT EXISTS idx_processes_title ON processes USING GIN(to_tsvector('english', title));
        RAISE NOTICE 'Utworzono indeks full-text z konfiguracją english (fallback)';
    ELSE
        CREATE INDEX IF NOT EXISTS idx_processes_title ON processes USING GIN(to_tsvector('simple', title));
        RAISE NOTICE 'Utworzono indeks full-text z konfiguracją simple (fallback)';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        -- Jeśli wszystko zawiedzie, utwórz zwykły indeks B-tree
        CREATE INDEX IF NOT EXISTS idx_processes_title ON processes(title);
        RAISE NOTICE 'Utworzono zwykły indeks B-tree na title (fallback)';
END $$;

-- 7. Trigger dla automatycznej aktualizacji updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_processes_updated_at ON processes;
CREATE TRIGGER update_processes_updated_at
    BEFORE UPDATE ON processes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 8. Funkcja do sprawdzenia liczby procesów użytkownika
CREATE OR REPLACE FUNCTION get_user_processes_count()
RETURNS INTEGER AS $$
BEGIN
    RETURN (
        SELECT COUNT(*)::INTEGER 
        FROM processes 
        WHERE user_email = auth.email()
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 9. Widok dla statystyk użytkownika
CREATE OR REPLACE VIEW user_process_stats AS
SELECT 
    user_email,
    COUNT(*) as total_processes,
    COUNT(ai_analysis) as analyzed_processes,
    MAX(created_at) as last_process_date,
    DATE_TRUNC('month', created_at) as month_created,
    COUNT(*) as processes_per_month
FROM processes
WHERE user_email = auth.email()
GROUP BY user_email, DATE_TRUNC('month', created_at);

-- 10. Przykładowe dane testowe (opcjonalne - usuń po testach)
-- INSERT INTO processes (user_email, title, description, ai_analysis) VALUES
-- ('dariusz.gasior@gmail.com', 'Proces testowy 1', 'To jest przykładowy proces do testowania aplikacji SmartFlowAI', 'OCENA POTENCJAŁU: 8/10\nGŁÓWNY PROBLEM: Ręczne zadania\nREKOMENDOWANE NARZĘDZIE: Zapier');

-- 11. Weryfikacja konfiguracji
DO $$
BEGIN
    -- Sprawdź czy tabela została utworzona
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'processes') THEN
        RAISE NOTICE 'Tabela processes została utworzona pomyślnie';
    ELSE
        RAISE EXCEPTION 'Błąd: Tabela processes nie została utworzona';
    END IF;
    
    -- Sprawdź czy RLS jest włączone
    IF EXISTS (SELECT FROM pg_tables WHERE tablename = 'processes' AND rowsecurity = true) THEN
        RAISE NOTICE 'Row Level Security jest włączone';
    ELSE
        RAISE EXCEPTION 'Błąd: Row Level Security nie jest włączone';
    END IF;
    
    -- Sprawdź liczbę policies
    IF (SELECT COUNT(*) FROM pg_policies WHERE tablename = 'processes') >= 4 THEN
        RAISE NOTICE 'Policies RLS zostały utworzone pomyślnie';
    ELSE
        RAISE EXCEPTION 'Błąd: Nie wszystkie policies zostały utworzone';
    END IF;
    
    RAISE NOTICE 'Inicjalizacja bazy danych SmartFlowAI zakończona pomyślnie!';
END $$;