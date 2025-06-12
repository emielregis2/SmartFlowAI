# Plik: prd.md

# SmartFlowAI - Ultra-prosta specyfikacja na 2 dni (kurs 10X)

## Cel aplikacji

**Problem:** Małe firmy nie wiedzą, które procesy warto zautomatyzować.

**Rozwiązanie:** SmartFlowAI - prosta aplikacja analizująca procesy przez ChatGPT-4o.

---

## Funkcje (TYLKO 4 podstawowe!)

### 1. Logowanie ✅
- Email + hasło (Supabase Auth)
- Brak rejestracji (użyj gotowego konta)

### 2. Dodaj proces ✅
- Formularz: Nazwa procesu + Opis
- Button "Analizuj" → ChatGPT-4o

### 3. Analiza AI ✅
- ChatGPT-4o analizuje proces
- Zwraca prostą rekomendację (tekst)
- Zapisuje do bazy danych

### 4. Lista procesów ✅
- Tabela: Nazwa | Data | Analiza AI
- Opcja usuwania procesu

**TO WSZYSTKO!** Żadnych dodatkowych funkcji.

---

## Technologia (ultra-minimalna)

### Stack:
- **1 plik:** `streamlit_app.py` (150-200 linii)
- **Baza:** Supabase (1 tabela)
- **AI:** OpenAI ChatGPT-4o 
- **Deploy:** Streamlit Cloud

### Baza danych (1 tabela):
```sql
-- TYLKO TA TABELA!
CREATE TABLE processes (
    id BIGSERIAL PRIMARY KEY,
    user_email TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    ai_analysis TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS
ALTER TABLE processes ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users manage own" ON processes 
FOR ALL USING (auth.email() = user_email);
```

### Pliki projektu:
```
smartflowai/
├── streamlit_app.py      # CAŁA APLIKACJA (200 linii max)
├── requirements.txt      # 4 biblioteki
├── README.md            # Jak uruchomić
└── .env.example         # Klucze API
```

---

## Plan na 2 dni

### Dzień 1 (6 godzin):
- **Godzina 1-2:** Setup Supabase + baza danych
- **Godzina 3-4:** Podstawowy Streamlit + logowanie
- **Godzina 5-6:** Formularz procesu + zapis do bazy

### Dzień 2 (6 godzin):
- **Godzina 1-2:** Integracja ChatGPT-4o
- **Godzina 3-4:** Lista procesów + usuwanie
- **Godzina 5-6:** Deploy + testy

---

## Wymagania (minimum do zaliczenia)

### ✅ Logowanie
- Jeden użytkownik może się zalogować
- Session state w Streamlit

### ✅ Logika biznesowa  
- Dodawanie procesu
- Analiza przez ChatGPT-4o
- Zapis do bazy danych

### ✅ Operacje na danych
- CREATE: Nowy proces
- READ: Lista procesów
- DELETE: Usuwanie procesu

### ✅ Testy
- 3 podstawowe testy funkcji
- Test logowania
- Test analizy AI

### ✅ Automatyzacja
- GitHub repo
- Deploy na Streamlit Cloud
- 1 workflow CI/CD

---

## ChatGPT-4o Integration

### Prompt dla AI:
```python
PROMPT = """
Przeanalizuj proces biznesowy i podaj krótką rekomendację:

PROCES: {title}
OPIS: {description}

Odpowiedz w formacie:
OCENA: [1-10]/10
PROBLEM: [główny problem]
ROZWIĄZANIE: [konkretne narzędzie]
OSZCZĘDNOŚCI: [czas/pieniądze]
"""
```

### Kod AI (w streamlit_app.py):
```python
def analyze_with_ai(title, description):
    response = openai.chat.completions.create(
        model="gpt-4o",  # WAŻNE: gpt-4o nie mini!
        messages=[{"role": "user", "content": PROMPT.format(...)}],
        max_tokens=300
    )
    return response.choices[0].message.content
```

---

## UI Flow (ultra-prosty)

```
Login Page
    ↓
Dashboard: [Lista procesów] [Nowy proces]
    ↓
Nowy proces: [Nazwa] [Opis] [Analizuj]
    ↓
Wyniki: [Analiza AI] [Zapisz] [Powrót]
    ↓
Dashboard: [Zaktualizowana lista]
```

---

## Definicja "gotowe" 

Aplikacja jest gotowa gdy:
1. ✅ Można się zalogować
2. ✅ Można dodać proces
3. ✅ ChatGPT-4o analizuje proces
4. ✅ Proces zapisuje się do bazy
5. ✅ Lista procesów się wyświetla
6. ✅ Można usunąć proces
7. ✅ Działa na Streamlit Cloud
8. ✅ Kod jest na GitHub

**Deadline:** 48 godzin od startu!

---

## Ograniczenia (rzeczy których NIE robimy)

❌ Rejestracja użytkowników (użyj test account)
❌ Edycja procesów 
❌ Eksport PDF
❌ Zaawansowane UI
❌ Walidacja formularzy
❌ Error handling
❌ Zaawansowane testy
❌ Dokumentacja API
❌ Multiple users
❌ Backup bazy danych

**Motto:** "Make it work, then make it better" - ale mamy tylko 2 dni na "make it work"!