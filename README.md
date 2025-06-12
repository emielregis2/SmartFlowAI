# Plik: README.md

# SmartFlowAI - Prosta aplikacja analizy procesów (2 dni MVP)

[![CI/CD](https://github.com/TWÓJ-USERNAME/smartflowai/actions/workflows/ci.yml/badge.svg)](https://github.com/TWÓJ-USERNAME/smartflowai/actions/workflows/ci.yml)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**SmartFlowAI** analizuje procesy biznesowe przez ChatGPT-4o i daje konkretne rekomendacje automatyzacji.

Projekt na zaliczenie kursu 10xDevs - wykonany w 2 dni.

## Quick Start (5 minut)

### 1. Klonowanie
```bash
git clone https://github.com/twoj-username/smartflowai.git
cd smartflowai
```

### 2. Instalacja
```bash
pip install -r requirements.txt
```

### 3. Konfiguracja
Skopiuj `.env.example` do `.env` i wypełnij:
```env
SUPABASE_URL=https://twoj-projekt.supabase.co
SUPABASE_ANON_KEY=twoj_anon_key
OPENAI_API_KEY=sk-twoj_openai_klucz
```

### 4. Baza danych
Wykonaj w Supabase SQL Editor:
```sql
CREATE TABLE processes (
    id BIGSERIAL PRIMARY KEY,
    user_email TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    ai_analysis TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE processes ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users manage own" ON processes 
FOR ALL USING (auth.email() = user_email);
```

### 5. Uruchomienie
```bash
streamlit run streamlit_app.py
```

Aplikacja: `http://localhost:8501`

**Konta testowe:** 
- `test@smartflowai.com` / `test123`
- `test@smatflow.pl` / `test123456`

## Funkcje

- ✅ **Logowanie** - Supabase Auth
- ✅ **Dodaj proces** - Formularz: nazwa + opis
- ✅ **Analiza AI** - ChatGPT-4o analizuje proces
- ✅ **Lista procesów** - Wszystkie procesy użytkownika
- ✅ **Usuwanie** - Usuń niepotrzebne procesy
- ✅ **CI/CD** - Automatyczne testy i deploy

**To wszystko!** Ultra-proste MVP z pełną automatyzacją.

## Technologia

- **Frontend:** Streamlit (1 plik)
- **Backend:** Python funkcje
- **Baza:** Supabase PostgreSQL
- **AI:** OpenAI ChatGPT-4o
- **Deploy:** Streamlit Cloud

## Struktura
```
smartflowai/
├── streamlit_app.py      # Cała aplikacja (200 linii)
├── requirements.txt      # 4 biblioteki
├── test_app.py          # Podstawowe testy
├── README.md            # Ta dokumentacja
├── .env.example         # Przykład konfiguracji
├── .gitignore           # Ignorowane pliki
└── .github/workflows/   # CI/CD
    ├── ci.yml           # Główny pipeline
    └── pr.yml           # Pull request checks
```

## Testowanie
```bash
pytest test_app.py -v
```

## CI/CD (GitHub Actions)

Automatyczny pipeline który:
- 🧪 Uruchamia testy na każdy commit
- 🎨 Sprawdza formatowanie kodu (Black)
- 🔍 Analizuje jakość (flake8) 
- 🔒 Skanuje bezpieczeństwo
- 🚀 Deploy na Streamlit Cloud

**Setup CI/CD:**
1. Dodaj secrets w GitHub: `OPENAI_API_KEY`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`
2. Push do `main` branch
3. GitHub Actions automatycznie uruchomi testy i deploy!

## Deploy na Streamlit Cloud

1. Push kod na GitHub
2. Połącz z Streamlit Cloud
3. Dodaj secrets:
   ```
   SUPABASE_URL = "https://..."
   SUPABASE_ANON_KEY = "..."
   OPENAI_API_KEY = "sk-..."
   ```
4. Każdy push na `main` → automatyczny deploy! 🚀

## Przykład użycia

1. **Zaloguj się:** użyj jednego z kont testowych:
   - `test@smartflowai.com` / `test123`
   - `test@smatflow.pl` / `test123456`
2. **Dodaj proces:** 
   - Nazwa: "Wystawianie faktur"
   - Opis: "Ręcznie tworzę faktury w Excelu, sprawdzam dane klientów, wysyłam mailem..."
3. **Kliknij "Analizuj przez AI"**
4. **Otrzymaj rekomendację:**
   ```
   OCENA: 8/10
   PROBLEM: Ręczne wprowadzanie danych
   ROZWIĄZANIE: Zapier + InvoiceNinja
   OSZCZĘDNOŚCI: 15 godzin miesięcznie
   WDROŻENIE: 1. Konfiguracja InvoiceNinja 2. Połączenie przez Zapier
   ```

## Rozwiązywanie problemów

**Błąd Supabase:** Sprawdź `SUPABASE_URL` i `SUPABASE_ANON_KEY`

**Błąd OpenAI:** Sprawdź `OPENAI_API_KEY` i saldo konta

**Błąd bazy:** Wykonaj SQL z sekcji "Baza danych"

## Autor

**Dariusz Gąsior** - Projekt na zaliczenie kursu 10xDevs  
GitHub: [@twoj-username](https://github.com/twoj-username)

---

**Projekt wykonany w 2 dni!** ⚡