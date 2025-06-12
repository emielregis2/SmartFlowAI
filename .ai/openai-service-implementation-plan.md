# Plik: openai-service-implementation-plan.md

# SmartFlowAI - Prosta integracja ChatGPT-4o (2 dni MVP)

## Przegląd

Ultra-prosta implementacja ChatGPT-4o w 1 pliku streamlit_app.py. 
Bez klas, bez modułów - tylko funkcja `analyze_with_ai()`.

## Architektura (minimalna)

### Założenia:
- **1 funkcja:** `analyze_with_ai(title, description) -> str`
- **Model:** ChatGPT-4o (nie mini - wyższa jakość)
- **Output:** Prosty tekst (nie JSON)
- **Error handling:** Try/except + user message

### Implementacja (20 linii kodu):

```python
def analyze_with_ai(title: str, description: str) -> str:
    """Analizuje proces przez ChatGPT-4o"""
    prompt = f"""
Przeanalizuj ten proces biznesowy i podaj krótką rekomendację:

PROCES: {title}
OPIS: {description}

Odpowiedz w formacie:
OCENA: [1-10]/10
PROBLEM: [główny problem w 1 zdaniu]
ROZWIĄZANIE: [konkretne narzędzie np. Zapier, Airtable]
OSZCZĘDNOŚCI: [szacowany czas/pieniądze miesięcznie]
WDROŻENIE: [1-2 kroki implementacji]
"""
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",  # WAŻNE: gpt-4o nie mini!
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Błąd analizy: {str(e)}"
```

**To wszystko!** Żadnych klas, modułów, walidacji.

## Prompt Engineering (polski rynek)

### Prompt zoptymalizowany:
```python
prompt = f"""
Przeanalizuj ten proces biznesowy i podaj krótką rekomendację:

PROCES: {title}
OPIS: {description}

Odpowiedz w formacie:
OCENA: [1-10]/10
PROBLEM: [główny problem w 1 zdaniu]  
ROZWIĄZANIE: [konkretne narzędzie np. Zapier, Airtable]
OSZCZĘDNOŚCI: [szacowany czas/pieniądze miesięcznie]
WDROŻENIE: [1-2 kroki implementacji]
"""
```

### Dlaczego ten prompt?
- **Krótki** - szybsza odpowiedź, tańszy
- **Strukturalny** - łatwe parsowanie przez użytkownika
- **Konkretny** - nie filozofia, tylko narzędzia
- **Polski** - dla polskich firm

## Konfiguracja API

### Inicjalizacja (w streamlit_app.py):
```python
@st.cache_resource  
def init_openai():
    api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", "")
    openai.api_key = api_key
    return openai

openai_client = init_openai()
```

### Zmienne środowiskowe:
```bash
# .env
OPENAI_API_KEY=sk-twoj_klucz_openai
```

### Streamlit Cloud secrets:
```toml
# .streamlit/secrets.toml
OPENAI_API_KEY = "sk-twoj_klucz_openai"
```

## Error Handling (minimalne)

### Strategia:
- `try/except` w funkcji głównej
- User-friendly error messages
- Brak retry logic (zbyt skomplikowane)

### Implementacja:
```python
try:
    response = openai_client.chat.completions.create(...)
    return response.choices[0].message.content
except Exception as e:
    return f"Błąd analizy: {str(e)}"
```

### Możliwe błędy:
- **API key** → "Sprawdź klucz OpenAI"
- **Rate limit** → "Za dużo zapytań, spróbuj później"
- **Network** → "Problem z połączeniem"

## Użycie w aplikacji

### W formularzu (streamlit_app.py):
```python
if st.form_submit_button("🤖 Analizuj przez AI"):
    if title and description:
        with st.spinner("Analizuję przez ChatGPT-4o..."):
            # Analiza AI
            ai_analysis = analyze_with_ai(title, description)
            
            # Wyświetl wyniki
            st.success("Analiza zakończona!")
            st.write(ai_analysis)
            
            # Zapisz do bazy
            save_process(title, description, ai_analysis)
```

## Koszty (szacunkowe)

### ChatGPT-4o pricing:
- **Input:** $2.50 per 1M tokens
- **Output:** $10.00 per 1M tokens

### Szacunki dla MVP:
- **1 analiza:** ~500 input + 200 output tokens = $0.003
- **100 analiz/miesiąc:** ~$0.30
- **1000 analiz/miesiąc:** ~$3.00

**Bardzo tanie dla MVP!**

## Testowanie AI

### Test podstawowy:
```python
def test_analyze_with_ai():
    result = analyze_with_ai("Wystawianie faktur", "Ręcznie tworzę faktury...")
    assert "OCENA:" in result
    assert "PROBLEM:" in result
    assert "ROZWIĄZANIE:" in result
```

### Test manual:
```bash
python streamlit_app.py
# Dodaj proces testowy i sprawdź jakość odpowiedzi
```

## Optymalizacje (opcjonalne)

### Cache częstych zapytań:
```python
@st.cache_data(ttl=3600)  # 1 godzina cache
def analyze_with_ai_cached(title: str, description: str) -> str:
    return analyze_with_ai(title, description)
```

### Limit długości inputu:
```python
if len(description) > 2000:
    return "Opis zbyt długi - maksymalnie 2000 znaków"
```

## Harmonogram implementacji

### Godzina 1-2 (Dzień 2):
- Skopiuj funkcję `analyze_with_ai()` do streamlit_app.py
- Dodaj import `openai`
- Skonfiguruj API key

### Godzina 3-4 (Dzień 2):
- Integracja z formularzem
- Test z prawdziwymi danymi
- Poprawki prompta

### Godzina 5-6 (Dzień 2):
- Error handling
- Test edge cases
- Deploy na Streamlit Cloud

**Gotowe!** ChatGPT-4o działa w aplikacji.

## Przykłady Input/Output

### Input:
```
Tytuł: Wystawianie faktur
Opis: Każdego dnia ręcznie tworzę faktury w Excelu na podstawie 
zamówień otrzymanych mailem. Sprawdzam dane klienta, wpisuję 
pozycje, obliczam VAT, wydrukuję i wysyłam pocztą.
```

### Output:
```
OCENA: 8/10
PROBLEM: Ręczne przepisywanie danych z emaili do Excela
ROZWIĄZANIE: Zapier + InvoiceNinja + Gmail
OSZCZĘDNOŚCI: 2 godziny dziennie = 40 godzin miesięcznie
WDROŻENIE: 1. Skonfiguruj InvoiceNinja 2. Połącz przez Zapier
```

**Perfect!** Konkretna, actionable rekomendacja.

---

**Motto:** Keep it simple - 1 funkcja, 20 linii, ChatGPT-4o! ⚡