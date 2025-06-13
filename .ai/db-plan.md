# SmartFlowAI - Prosty plan bazy danych (2 dni MVP)

## Przegląd

Ultra-prosty schemat bazy danych PostgreSQL dla SmartFlowAI - MVP systemu analizy procesów biznesowych. Minimalna kompleksność, maksymalna skuteczność.

## Filozofia designu

### Główne założenia:
- **1 tabela** - wystarczy dla MVP
- **Proste typy** - VARCHAR, TEXT, BIGSERIAL (bez UUID)
- **RLS (Row Level Security)** - bezpieczeństwo na poziomie wiersza
- **Supabase Auth** - wykorzystujemy istniejącą auth.users

### Dlaczego tak prosto?
- ✅ **Szybka implementacja** - 5 minut setup
- ✅ **Łatwa rozbudowa** - dodawanie kolumn w przyszłości
- ✅ **Debugowanie** - proste zapytania SQL
- ✅ **MVP-first** - nie przedwczesna optymalizacja

## Schemat bazy danych

### Jedyna tabela: `processes`

```sql
CREATE TABLE processes (
    id BIGSERIAL PRIMARY KEY,
    user_email TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    ai_analysis TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**To wszystko!** 6 kolumn, żadnych relacji, enum-ów czy JSON-ów.

### Szczegóły kolumn:

| Kolumna | Typ | Opis | Wymagane |
|---------|-----|------|----------|
| `id` | BIGSERIAL | Auto-increment klucz główny | ✅ |
| `user_email` | TEXT | Email właściciela procesu | ✅ |
| `title` | TEXT | Nazwa procesu | ✅ |
| `description` | TEXT | Opis procesu | ✅ |
| `ai_analysis` | TEXT | Wyniki analizy AI | ❌ |
| `created_at` | TIMESTAMPTZ | Data utworzenia | ✅ (auto) |

### Dlaczego user_email zamiast user_id?
- Prostsze zapytania: `WHERE user_email = auth.email()`
- Brak JOIN-ów z auth.users
- Debugowanie: widzisz od razu kto to właściciel

## Row Level Security (RLS)

### Włączenie RLS:
```sql
ALTER TABLE processes ENABLE ROW LEVEL SECURITY;
```

### Policy - użytkownicy zarządzają swoimi procesami:
```sql
CREATE POLICY "Users manage own processes" ON processes 
FOR ALL USING (auth.email() = user_email);
```

**Jedna policy dla wszystkich operacji** - SELECT, INSERT, UPDATE, DELETE.

### Jak to działa?
```sql
-- Użytkownik widzi tylko swoje procesy
SELECT * FROM processes;  -- Automatycznie filtruje WHERE user_email = auth.email()

-- Może dodać tylko ze swoim email
INSERT INTO processes (user_email, title, description) 
VALUES (auth.email(), 'Nowy proces', 'Opis...');

-- Może edytować tylko swoje
UPDATE processes SET title = 'Nowa nazwa' WHERE id = 123;  -- RLS sprawdza user_email
```

## Operacje CRUD

### 🔍 READ - Lista procesów użytkownika:
```sql
SELECT id, title, description, ai_analysis, created_at 
FROM processes 
ORDER BY created_at DESC;
```

### ➕ CREATE - Dodaj nowy proces:
```sql
INSERT INTO processes (user_email, title, description) 
VALUES (auth.email(), 'Wystawianie faktur', 'Ręcznie tworzę faktury...');
```

### ✏️ UPDATE - Aktualizuj proces (🆕 dodane):
```sql
UPDATE processes 
SET title = 'Nowa nazwa', 
    description = 'Nowy opis', 
    ai_analysis = 'Nowa analiza'
WHERE id = 123;
```

### 🤖 UPDATE - Zapisz analizę AI:
```sql
UPDATE processes 
SET ai_analysis = 'OCENA: 8/10, PROBLEM: ...' 
WHERE id = 123;
```

### 🗑️ DELETE - Usuń proces:
```sql
DELETE FROM processes WHERE id = 123;
```

## Indeksy (minimalne)

### Podstawowe indeksy:
```sql
-- Auto-created dla PRIMARY KEY
-- id już ma indeks

-- Indeks dla RLS queries
CREATE INDEX idx_processes_user_email ON processes(user_email);

-- Indeks dla sortowania
CREATE INDEX idx_processes_created_at ON processes(created_at DESC);
```

**3 indeksy wystarczą** dla tysięcy procesów.

## Przykładowe dane

### Test data:
```sql
INSERT INTO processes (user_email, title, description, ai_analysis) VALUES
('test@smartflowai.com', 
 'Wystawianie faktur', 
 'Ręcznie tworzę faktury w Excelu, sprawdzam dane klientów, wysyłam mailem.',
 'OCENA: 8/10
PROBLEM: Ręczne wprowadzanie danych
ROZWIĄZANIE: Zapier + InvoiceNinja
OSZCZĘDNOŚCI: 15 godzin miesięcznie
WDROŻENIE: 1. Konfiguracja InvoiceNinja 2. Połączenie przez Zapier'),

('test@smartflowai.com',
 'Księgowanie dokumentów',
 'Drukuję dokumenty, segreguję do teczek, ręcznie wpisuję do księgi.',
 'OCENA: 9/10
PROBLEM: Papierowy obieg dokumentów
ROZWIĄZANIE: iFirma + skanowanie
OSZCZĘDNOŚCI: 20 godzin miesięcznie
WDROŻENIE: 1. iFirma setup 2. Skaner dokumentów');
```

## Backup & Recovery

### Supabase automatyczne:
- ✅ **Daily backups** - automatyczne
- ✅ **Point-in-time recovery** - 7 dni
- ✅ **Replication** - multiple zones

### Manual backup:
```sql
-- Export całej tabeli
\copy processes TO 'processes_backup.csv' CSV HEADER;

-- Import z backup
\copy processes FROM 'processes_backup.csv' CSV HEADER;
```

## Performance

### Dla MVP wystarczy:
- **1000 procesów** - instant queries
- **10,000 procesów** - <100ms queries  
- **100,000 procesów** - potrzeba optymalizacji

### Monitoring:
```sql
-- Sprawdź slow queries
SELECT query, mean_time, calls 
FROM pg_stat_statements 
WHERE query LIKE '%processes%'
ORDER BY mean_time DESC;
```

## Ewolucja schematu

### Przyszłe rozszerzenia (gdy będzie potrzeba):

#### Faza 2 - Kategoryzacja:
```sql
ALTER TABLE processes ADD COLUMN category TEXT;
ALTER TABLE processes ADD COLUMN priority INTEGER DEFAULT 1;
```

#### Faza 3 - Metadata:
```sql
ALTER TABLE processes ADD COLUMN tags TEXT[];
ALTER TABLE processes ADD COLUMN estimated_savings DECIMAL;
```

#### Faza 4 - Audit trail:
```sql
ALTER TABLE processes ADD COLUMN updated_at TIMESTAMPTZ DEFAULT NOW();
ALTER TABLE processes ADD COLUMN updated_by TEXT;
```

### Enterprise upgrade (w przyszłości):
```sql
-- Normalizacja gdy będzie 10+ tabel
CREATE TABLE users (...);
CREATE TABLE categories (...);
CREATE TABLE ai_analyses (...);
-- etc.
```

## Deployment SQL

### Supabase SQL Editor - skopiuj i uruchom:
```sql
-- 1. Utwórz tabelę
CREATE TABLE processes (
    id BIGSERIAL PRIMARY KEY,
    user_email TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    ai_analysis TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Włącz RLS
ALTER TABLE processes ENABLE ROW LEVEL SECURITY;

-- 3. Dodaj policy
CREATE POLICY "Users manage own processes" ON processes 
FOR ALL USING (auth.email() = user_email);

-- 4. Dodaj indeksy
CREATE INDEX idx_processes_user_email ON processes(user_email);
CREATE INDEX idx_processes_created_at ON processes(created_at DESC);

-- 5. Test data (opcjonalne)
INSERT INTO processes (user_email, title, description) VALUES
('test@smartflowai.com', 'Test proces', 'Test opis procesu');
```

**5 minut i baza gotowa!**

## Troubleshooting

### Częste problemy:

#### RLS nie działa:
```sql
-- Sprawdź czy RLS jest włączone
SELECT schemaname, tablename, rowsecurity 
FROM pg_tables 
WHERE tablename = 'processes';

-- Sprawdź policies
SELECT * FROM pg_policies WHERE tablename = 'processes';
```

#### Brak dostępu do danych:
```sql
-- Sprawdź auth.email()
SELECT auth.email();

-- Sprawdź user_email w rekordach
SELECT user_email, count(*) FROM processes GROUP BY user_email;
```

#### Performance issues:
```sql
-- Sprawdź execution plan
EXPLAIN ANALYZE SELECT * FROM processes WHERE user_email = auth.email();
```

## Testowanie

### Test RLS:
```sql
-- Zaloguj jako test@smartflowai.com
SELECT count(*) FROM processes;  -- Powinien pokazać tylko procesy tego użytkownika

-- Spróbuj edytować cudzy proces
UPDATE processes SET title = 'hack' WHERE user_email != auth.email();  -- Powinien dać 0 rows affected
```

### Load testing:
```sql
-- Insert 1000 test records
INSERT INTO processes (user_email, title, description)
SELECT 
    'test@smartflowai.com',
    'Test proces ' || i,
    'Test opis procesu ' || i
FROM generate_series(1, 1000) AS i;

-- Check performance
\timing
SELECT * FROM processes ORDER BY created_at DESC LIMIT 10;
```

---

**Motto:** "Start simple, scale when needed" - jedna tabela może obsłużyć cały MVP! ⚡

**Design principle:** Premature optimization is the root of all evil - zaczynamy od najprostszego działającego rozwiązania! 🚀