# db-plan.md - Plan bazy danych SmartFlowAI

# SmartFlowAI - Plan bazy danych

## Przegląd

Ten dokument opisuje uproszczony schemat bazy danych PostgreSQL dla aplikacji SmartFlowAI - systemu analizy procesów biznesowych z wykorzystaniem AI. Projekt został zoptymalizowany pod kątem ultra-prostego MVP na 2 dni.

## Architektura

### Platforma
- **Baza danych:** PostgreSQL (Supabase)
- **Autentykacja:** Supabase Auth (tabela auth.users)
- **Bezpieczeństwo:** Row Level Security (RLS)
- **Framework:** Python/Streamlit

### Główne założenia MVP
- Maksymalna prostota - tylko 1 tabela główna
- Bezpieczeństwo na poziomie wiersza (RLS)
- TEXT zamiast JSONB dla szybkości implementacji
- BIGSERIAL klucze główne
- Brak soft delete (hard delete dla prostoty)

## Schemat bazy danych

### Tabela `processes` (jedyna tabela)
Przechowuje procesy biznesowe użytkowników wraz z analizą AI.

```sql
CREATE TABLE processes (
    id BIGSERIAL PRIMARY KEY,
    user_email TEXT NOT NULL,
    title TEXT NOT NULL CHECK (length(title) >= 3 AND length(title) <= 255),
    description TEXT NOT NULL CHECK (length(description) >= 10),
    ai_analysis TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);
```

**Pola:**
- `id` - BIGSERIAL, klucz główny
- `user_email` - TEXT, email użytkownika (z auth.users)
- `title` - TEXT, nazwa procesu (3-255 znaków)
- `description` - TEXT, opis procesu (min 10 znaków)
- `ai_analysis` - TEXT, wyniki analizy AI (nullable do czasu analizy)
- `created_at` - timestamp utworzenia
- `updated_at` - timestamp ostatniej modyfikacji

## Row Level Security (RLS)

### Włączenie RLS
```sql
ALTER TABLE processes ENABLE ROW LEVEL SECURITY;
```

### Policies dla tabeli `processes`

```sql
-- Użytkownicy mogą zarządzać tylko swoimi procesami
CREATE POLICY "Users can manage own processes" ON processes
    FOR ALL USING (auth.email() = user_email)
    WITH CHECK (auth.email() = user_email);
```

## Indeksy podstawowe

```sql
-- Indeks na user_email dla szybkich zapytań użytkownika
CREATE INDEX IF NOT EXISTS idx_processes_user_email ON processes(user_email);

-- Indeks na created_at dla sortowania chronologicznego
CREATE INDEX IF NOT EXISTS idx_processes_created_at ON processes(created_at DESC);

-- Indeks full-text search z fallback dla konfiguracji językowej
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_ts_config WHERE cfgname = 'polish') THEN
        CREATE INDEX IF NOT EXISTS idx_processes_title ON processes USING GIN(to_tsvector('polish', title));
    ELSIF EXISTS (SELECT 1 FROM pg_ts_config WHERE cfgname = 'english') THEN
        CREATE INDEX IF NOT EXISTS idx_processes_title ON processes USING GIN(to_tsvector('english', title));
    ELSE
        CREATE INDEX IF NOT EXISTS idx_processes_title ON processes(title);
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        CREATE INDEX IF NOT EXISTS idx_processes_title ON processes(title);
END $$;
```

## Funkcje pomocnicze

### Trigger automatycznej aktualizacji updated_at
```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger dla processes
CREATE TRIGGER processes_updated_at
    BEFORE UPDATE ON processes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### Funkcja statystyk użytkownika
```sql
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
```

## Przykładowe zapytania

### Podstawowe operacje CRUD
```sql
-- Lista procesów użytkownika
SELECT * FROM processes 
WHERE user_email = auth.email() 
ORDER BY created_at DESC;

-- Dodanie nowego procesu
INSERT INTO processes (user_email, title, description) 
VALUES (auth.email(), 'Nazwa procesu', 'Opis procesu...');

-- Aktualizacja analizy AI
UPDATE processes 
SET ai_analysis = 'Wyniki analizy...'
WHERE id = $1 AND user_email = auth.email();

-- Usunięcie procesu
DELETE FROM processes 
WHERE id = $1 AND user_email = auth.email();
```

### Zapytania analityczne
```sql
-- Statystyki użytkownika
SELECT 
    COUNT(*) as total_processes,
    COUNT(ai_analysis) as analyzed_processes,
    MAX(created_at) as last_process_date
FROM processes 
WHERE user_email = auth.email();

-- Wyszukiwanie procesów
SELECT * FROM processes 
WHERE user_email = auth.email() 
  AND (title ILIKE '%' || $1 || '%' OR description ILIKE '%' || $1 || '%')
ORDER BY created_at DESC;
```

## Bezpieczeństwo

### Ochrona danych
- **RLS policies** - izolacja danych między użytkownikami
- **Check constraints** - walidacja długości pól
- **Foreign key** przez email (Supabase Auth)

### Audit trail
- `created_at` - kiedy rekord został utworzony
- `updated_at` - kiedy ostatnio modyfikowany
- `user_email` - kto jest właścicielem

## Backup i recovery
- Supabase automatyczne backupy
- Prosta struktura ułatwia eksport/import
- Point-in-time recovery przez Supabase

## Migracja z pliku

### Struktura migracji dla SmartFlowAI:
1. `001_create_processes_table.sql` - główna tabela
2. `002_enable_rls.sql` - Row Level Security
3. `003_create_indexes.sql` - indeksy wydajnościowe
4. `004_create_functions.sql` - funkcje pomocnicze

### Przykład pełnej migracji
```sql
-- SmartFlowAI - Pełna migracja bazy danych

-- 1. Tworzenie tabeli
CREATE TABLE IF NOT EXISTS processes (
    id BIGSERIAL PRIMARY KEY,
    user_email TEXT NOT NULL,
    title TEXT NOT NULL CHECK (length(title) >= 3 AND length(title) <= 255),
    description TEXT NOT NULL CHECK (length(description) >= 10),
    ai_analysis TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- 2. RLS
ALTER TABLE processes ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage own processes" ON processes
    FOR ALL USING (auth.email() = user_email)
    WITH CHECK (auth.email() = user_email);

-- 3. Indeksy
CREATE INDEX IF NOT EXISTS idx_processes_user_email ON processes(user_email);
CREATE INDEX IF NOT EXISTS idx_processes_created_at ON processes(created_at DESC);

-- 4. Funkcje
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER processes_updated_at
    BEFORE UPDATE ON processes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

## Optymalizacje MVP

### Co zostało uproszczone względem pełnego SmartFlowAI:
- Brak tabeli `profiles` - dane firmy w session state
- Brak enumeracji - proste stringi
- Brak JSONB - prosty TEXT dla AI analysis
- Brak soft delete - zwykłe DELETE
- Brak partycjonowania - niepotrzebne dla MVP
- Brak zaawansowanych indeksów GIN

### Dlaczego to wystarczy dla MVP:
- Obsługa do 1000 procesów bez problemów wydajnościowych
- Prosta struktura = szybsza implementacja
- Łatwe debugowanie i maintenance
- Możliwość rozbudowy w przyszłości

## Metryki dla MVP

### Założenia wydajnościowe:
- **Liczba użytkowników:** do 100 jednocześnie
- **Procesy na użytkownika:** do 50
- **Całkowite procesy:** do 5000
- **Czas zapytania:** < 100ms dla basic CRUD
- **Backup:** automatyczny przez Supabase

### Monitoring:
- Supabase Dashboard
- Query performance w SQL Editor
- Storage usage

---

**Autor:** Dariusz Gąsior - SmartFlowAI MVP  
**Data:** 11 czerwca 2025  
**Status:** Gotowy do 2-dniowego sprintu