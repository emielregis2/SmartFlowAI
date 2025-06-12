# Plik: db-plan.md

# SmartFlowAI - Plan bazy danych

## Przegląd

Ten dokument opisuje schemat bazy danych PostgreSQL dla aplikacji SmartFlowAI - systemu analizy procesów biznesowych z wykorzystaniem AI. Projekt został zoptymalizowany pod kątem MVP przy zachowaniu możliwości przyszłej rozbudowy.

## Architektura

### Platforma
- **Baza danych:** PostgreSQL 15+ (Supabase)
- **Autentykacja:** Supabase Auth (tabela auth.users)
- **Bezpieczeństwo:** Row Level Security (RLS)
- **Framework:** Python/Streamlit

### Główne założenia
- Prostota MVP przy zachowaniu elastyczności
- Bezpieczeństwo na poziomie wiersza (RLS)
- JSONB dla elastycznego przechowywania danych AI
- UUID klucze główne dla bezpieczeństwa
- Soft delete dla zachowania historii

## Schemat bazy danych

### 1. Tabela `profiles`
Przechowuje informacje o firmie użytkownika w relacji 1:1 z auth.users.

```sql
CREATE TABLE profiles (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE NOT NULL,
    company_size company_size_enum NOT NULL,
    industry industry_enum NOT NULL,
    budget_range budget_range_enum NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);
```

**Pola:**
- `id` - UUID, klucz główny
- `user_id` - UUID, referencja do auth.users, UNIQUE (relacja 1:1)
- `company_size` - enum, wielkość firmy
- `industry` - enum, branża
- `budget_range` - enum, zakres budżetu
- `created_at` - timestamp utworzenia
- `updated_at` - timestamp ostatniej modyfikacji

### 2. Tabela `processes`
Przechowuje procesy biznesowe użytkowników wraz z danymi analizy.

```sql
CREATE TABLE processes (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    form_data JSONB NOT NULL,
    ai_analysis JSONB,
    potential_score INTEGER CHECK (potential_score >= 1 AND potential_score <= 10),
    status process_status_enum DEFAULT 'draft' NOT NULL,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);
```

**Pola:**
- `id` - UUID, klucz główny
- `user_id` - UUID, właściciel procesu
- `title` - VARCHAR(255), nazwa procesu (NOT NULL)
- `description` - TEXT, opis procesu (nullable)
- `form_data` - JSONB, dane z formularza analizy
- `ai_analysis` - JSONB, wyniki analizy AI (nullable do czasu analizy)
- `potential_score` - INTEGER (1-10), ocena potencjału z AI
- `status` - enum, status procesu
- `deleted_at` - TIMESTAMPTZ, soft delete (nullable)
- `created_at` - timestamp utworzenia
- `updated_at` - timestamp ostatniej modyfikacji

## Enumeracje

### company_size_enum
```sql
CREATE TYPE company_size_enum AS ENUM (
    '5-10 osób',
    '11-25 osób', 
    '26-50 osób'
);
```

### industry_enum
```sql
CREATE TYPE industry_enum AS ENUM (
    'Marketing',
    'Księgowość',
    'Handel',
    'Produkcja',
    'Usługi'
);
```

### budget_range_enum
```sql
CREATE TYPE budget_range_enum AS ENUM (
    'do 500 zł/miesiąc',
    '500-2000 zł/miesiąc',
    'powyżej 2000 zł/miesiąc'
);
```

### process_status_enum
```sql
CREATE TYPE process_status_enum AS ENUM (
    'draft',
    'analyzed', 
    'implemented'
);
```

## Struktura JSONB

### form_data (processes.form_data)
```json
{
    "company": {
        "size": "11-25 osób",
        "industry": "Marketing",
        "budget": "500-2000 zł/miesiąc"
    },
    "process": {
        "name": "Wystawianie faktur",
        "frequency": "raz w tygodniu",
        "participants": "2-3 osoby", 
        "duration": 4.0,
        "description": "Proces tworzenia i wysyłania faktur do klientów..."
    },
    "improvement_goal": ["szybkość", "mniej błędów"]
}
```

### ai_analysis (processes.ai_analysis)
```json
{
    "ocena_potencjalu": 8,
    "mozliwe_oszczednosci": {
        "czas_godziny_miesiecznie": 16,
        "oszczednosci_pieniadze_miesiecznie": 2400
    },
    "rekomendacje": [
        {
            "narzedzie": "Zapier + InvoiceNinja",
            "czas_wdrozenia": "1 tydzień",
            "koszt_miesiecznie": 400,
            "opis": "Automatyczne tworzenie faktur z danych klientów"
        }
    ],
    "plan_wdrozenia": [
        "Tydzień 1: Konfiguracja InvoiceNinja",
        "Tydzień 2: Połączenie przez Zapier"
    ],
    "uwagi": [
        "Wymaga zgodę klientów na automatyczne faktury"
    ],
    "generated_at": "2025-06-08T10:30:00Z",
    "model_used": "gpt-4"
}
```

## Indeksy

### Indeksy podstawowe
```sql
-- Indeks na user_id dla szybkich zapytań użytkownika
CREATE INDEX idx_profiles_user_id ON profiles(user_id);
CREATE INDEX idx_processes_user_id ON processes(user_id);

-- Indeks na created_at dla sortowania chronologicznego
CREATE INDEX idx_processes_created_at ON processes(created_at DESC);

-- Indeks na status dla filtrowania
CREATE INDEX idx_processes_status ON processes(status) WHERE deleted_at IS NULL;

-- Indeks na soft delete
CREATE INDEX idx_processes_active ON processes(user_id, created_at) WHERE deleted_at IS NULL;
```

### Indeksy JSONB
```sql
-- GIN indeks dla zapytań po form_data
CREATE INDEX idx_processes_form_data ON processes USING GIN(form_data);

-- GIN indeks dla zapytań po ai_analysis  
CREATE INDEX idx_processes_ai_analysis ON processes USING GIN(ai_analysis);

-- Indeks na ocenę potencjału
CREATE INDEX idx_processes_potential_score ON processes(potential_score) WHERE potential_score IS NOT NULL;
```

## Row Level Security (RLS)

### Włączenie RLS
```sql
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE processes ENABLE ROW LEVEL SECURITY;
```

### Policies dla tabeli `profiles`

```sql
-- Użytkownicy mogą widzieć tylko swój profil
CREATE POLICY "profiles_select_own" ON profiles
    FOR SELECT USING (auth.uid() = user_id);

-- Użytkownicy mog