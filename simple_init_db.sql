-- Plik: simple_init_db.sql
-- simple_init_db.sql - Uproszczona inicjalizacja bazy danych SmartFlowAI

-- SmartFlowAI Simple Database Initialization
-- Uproszczona wersja - używaj jeśli główny skrypt ma problemy

-- 1. Utworzenie tabeli procesów (podstawowa wersja)
CREATE TABLE IF NOT EXISTS processes (
    id BIGSERIAL PRIMARY KEY,
    user_email TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    ai_analysis TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- 2. Włączenie Row Level Security
ALTER TABLE processes ENABLE ROW LEVEL SECURITY;

-- 3. Podstawowe policies RLS
CREATE POLICY "Users can manage own processes" ON processes
    FOR ALL USING (auth.email() = user_email)
    WITH CHECK (auth.email() = user_email);

-- 4. Podstawowe indeksy
CREATE INDEX IF NOT EXISTS idx_processes_user_email ON processes(user_email);
CREATE INDEX IF NOT EXISTS idx_processes_created_at ON processes(created_at DESC);

-- 5. Weryfikacja
SELECT 'Tabela processes dla SmartFlowAI utworzona pomyślnie!' as status;