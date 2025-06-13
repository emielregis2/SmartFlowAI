# Plik: README.md

# SmartFlowAI - Prosta aplikacja analizy procesów (2 dni MVP)

[![CI/CD](https://github.com/emielregis2/SmartFlowAI/actions/workflows/ci.yml/badge.svg)](https://github.com/emielregis2/SmartFlowAI/actions/workflows/ci.yml)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**SmartFlowAI** analizuje procesy biznesowe przez ChatGPT-4o i daje konkretne rekomendacje automatyzacji.

Projekt na zaliczenie kursu 10xDevs - wykonany w 2 dni.

## Quick Start (5 minut)

### 1. Klonowanie
```bash
git clone https://github.com/emielregis2/SmartFlowAI.git
cd SmartFlowAI
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
- ✅ **Ultra wnikliwa analiza AI** - 3 poziomy głębokości z wyszukiwaniem internetowym
- ✅ **Kontekst firmy** - Wielkość, branża, budżet dla spersonalizowanych rekomendacji
- ✅ **Branżowe szablony** - Specjalistyczne integracje dla różnych sektorów
- ✅ **Lista procesów** - Wszystkie procesy użytkownika
- ✅ **Edycja procesów** - Modyfikuj nazwę, opis i analizę AI
- ✅ **Usuwanie** - Usuń niepotrzebne procesy
- ✅ **Export PDF** - Generuj raport z przeanalizowanymi procesami
- ✅ **Kopiuj do schowka** - Skopiuj pełny tekst raportu jednym kliknięciem
- ✅ **CI/CD** - Automatyczne testy i deploy

**To wszystko!** Ultra-proste MVP z pełną automatyzacją i zarządzaniem procesami.

## Nowe funkcjonalności

### 🤖 Ultra wnikliwa analiza AI

#### 3 poziomy głębokości analizy:
- **Podstawowa (szybka)** - Szybka rekomendacja w 5 punktach
- **Pogłębiona (z wyszukiwaniem)** - Szczegółowa analiza z aktualnym badaniem rynku
- **Ekspercka (pełna analiza)** - Najgłębsza analiza z 8-tygodniowym planem wdrożenia

#### Kontekst firmy:
- **Wielkość firmy:** 1-10, 11-50, 51-200, 200+ osób
- **Branża:** IT, E-commerce, Księgowość, Marketing, Logistyka i inne
- **Budżet:** od 500 zł/mies do 5000+ zł/mies

#### Branżowe szablony integracji:
- **E-commerce:** Allegro, Amazon, BaseLinker, Shopify
- **Księgowość:** iFirma, Wfirma, SAP, JPK, US, ZUS
- **Marketing:** Facebook Ads, Google Ads, MailChimp, HubSpot
- **IT:** GitHub, Jira, Slack, CI/CD, monitoring
- **Logistyka:** WMS, TMS, API kurierów
- I wiele innych...

### 📝 Edycja procesów
- Przycisk "✏️ Edytuj" obok każdego procesu
- Możliwość modyfikacji nazwy, opisu i analizy AI
- Intuicyjny formularz z przyciskami "Zapisz" i "Anuluj"

### 📄 Export do PDF
- Przycisk "📄 Pobierz PDF" generuje raport ze wszystkich procesów
- Zawiera szczegółowe opisy i analizy AI
- Automatyczna konwersja polskich znaków dla kompatybilności
- Nazwa pliku: `Lista_przeanalizowanych_procesow.pdf`

### 📋 Kopiowanie do schowka
- Przycisk "📋 Kopiuj do schowka" obok przycisku PDF
- Generuje pełny tekst raportu ze wszystkich procesów (nie tylko 10 jak PDF)
- Zachowuje polskie znaki i emoji w oryginalnej formie
- Dwie opcje kopiowania:
  - **st.code** - z wbudowanym przyciskiem kopiowania
  - **text_area** - zaznacz tekst i Ctrl+C
- Zawiera nagłówek, wszystkie procesy z opisami i analizami AI, stopkę i datę

## Technologia

- **Frontend:** Streamlit (1 plik)
- **Backend:** Python funkcje
- **Baza:** Supabase PostgreSQL
- **AI:** OpenAI ChatGPT-4o z dostępem do internetu
- **PDF:** fpdf2 z obsługą Unicode
- **Deploy:** Streamlit Cloud

## Struktura
```
smartflowai/
├── streamlit_app.py           # Cała aplikacja (400+ linii)
├── requirements.txt           # 5 bibliotek (dodano fpdf2)
├── test_app.py               # Podstawowe testy
├── test_utf8.py              # Testy kodowania UTF-8
├── test_enhanced_analysis.py # Testy ulepszonych funkcji AI
├── README.md                 # Ta dokumentacja
├── .env.example              # Przykład konfiguracji
├── .gitignore                # Ignorowane pliki
└── .github/workflows/        # CI/CD
    ├── ci.yml                # Główny pipeline
    └── pr.yml                # Pull request checks
```

## Testowanie
```bash
pytest test_app.py -v                    # Podstawowe testy
pytest test_utf8.py -v                   # Test kodowania UTF-8
python test_enhanced_analysis.py         # Test ulepszonych funkcji AI
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
3. **Wybierz opcje analizy:**
   - Głębokość: "Pogłębiona (z wyszukiwaniem)"
   - Wielkość firmy: "11-50 osób"
   - Branża: "Księgowość"
   - Budżet: "500-2000 zł/mies"
4. **Kliknij "Analizuj przez AI"**
5. **Otrzymaj szczegółową rekomendację:**
   ```
   🔍 ANALIZA PROCESU
   [Dekompozycja na kroki z czasami]
   
   🛠️ REKOMENDOWANE ROZWIĄZANIE
   Narzędzie główne: iFirma + Zapier
   Stopień automatyzacji: 85%
   
   💰 INWESTYCJA
   Koszt wdrożenia: 2000 zł jednorazowo
   Koszt miesięczny: 150 zł/mies.
   
   ⏱️ OSZCZĘDNOŚCI
   Czas: 20 godzin miesięcznie → 3 godziny (redukcja o 85%)
   ROI: 300% zwrot w 4 miesięcy
   
   📋 PLAN WDROŻENIA (6 tygodni)
   [Szczegółowy harmonogram]
   ```
6. **Edytuj proces:** Kliknij "✏️ Edytuj" aby zmodyfikować dane
7. **Pobierz PDF:** Kliknij "📄 Pobierz PDF" aby wygenerować raport
8. **Kopiuj do schowka:** Kliknij "📋 Kopiuj do schowka" aby skopiować pełny tekst

## Rozwiązywanie problemów

**Błąd Supabase:** Sprawdź `SUPABASE_URL` i `SUPABASE_ANON_KEY`

**Błąd OpenAI:** Sprawdź `OPENAI_API_KEY` i saldo konta

**Błąd bazy:** Wykonaj SQL z sekcji "Baza danych"

**Błąd PDF:** Sprawdź czy fpdf2 jest zainstalowane: `pip install fpdf2`

**Błąd analizy AI:** Sprawdź połączenie internetowe (GPT-4o wymaga dostępu do sieci)

## Autor

**Dariusz Gąsior** - Projekt na zaliczenie kursu 10xDevs  
GitHub: [@emielregis2](https://github.com/emielregis2/SmartFlowAI)

---

**Projekt wykonany w 2 dni!** ⚡  
**Rozszerzony o zaawansowane funkcje AI dzięki współpracy z Claude Sonnet 4** 🤖

---

**Projekt powstał z pomocą edytora [Cursor](https://www.cursor.so/) oraz AI Claude Sonnet 4.**

---