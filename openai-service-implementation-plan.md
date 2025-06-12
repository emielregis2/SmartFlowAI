# openai-service-implementation-plan.md - Plan implementacji serwisu OpenAI dla SmartFlowAI

# SmartFlowAI - Plan implementacji serwisu OpenAI

## Przegląd

Ten dokument opisuje uproszczoną implementację serwisu OpenAI dla aplikacji SmartFlowAI. Projekt został zoptymalizowany pod kątem maksymalnej prostoty MVP z GPT-4o-mini.

## Architektura serwisu

### Główne założenia MVP
- Synchroniczna analiza procesów (użytkownik czeka na wynik)
- GPT-4o-mini model (tańszy i szybszy)
- Prosty text completion zamiast function calling
- Minimalna złożoność - wszystko w głównym pliku
- Plain text output zamiast structured JSON

### Komponenty (wszystko w streamlit_app.py)
1. **analyze_process_with_ai()** - główna funkcja analizy
2. **SYSTEM_PROMPT** - stały szablon prompta
3. **Podstawowa obsługa błędów**

## Uproszczona implementacja

### Funkcja analizy AI (w streamlit_app.py)
```python
def analyze_process_with_ai(title: str, description: str) -> str:
    """
    Analizuje proces używając OpenAI GPT-4o-mini
    
    Args:
        title: Nazwa procesu
        description: Opis procesu
        
    Returns:
        str: Analiza w formacie tekstowym
    """
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """Jesteś ekspertem od automatyzacji procesów biznesowych w Polsce. 
                    Analizuj procesy i zwracaj konkretne rekomendacje w formacie:
                    
                    OCENA POTENCJAŁU: [1-10]/10
                    GŁÓWNY PROBLEM: [krótki opis]
                    REKOMENDOWANE NARZĘDZIE: [konkretne narzędzie np. Zapier, n8n]
                    SZACOWANY CZAS OSZCZĘDNOŚCI: [godziny/miesiąc]
                    KOSZT WDROŻENIA: [w PLN]
                    
                    PLAN WDROŻENIA:
                    1. [krok pierwszy]
                    2. [krok drugi] 
                    3. [krok trzeci]
                    
                    UWAGI: [ważne zastrzeżenia]"""
                },
                {
                    "role": "user", 
                    "content": f"Przeanalizuj proces:\n\nNazwa: {title}\n\nOpis: {description}"
                }
            ],
            temperature=0.7,
            max_tokens=800,
            timeout=60
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Błąd analizy: {str(e)}"
```

## System Prompt

### Prompt zoptymalizowany dla polskiego rynku
```python
SYSTEM_PROMPT = """
Jesteś ekspertem od automatyzacji procesów biznesowych w małych firmach (5-50 osób) w Polsce. 
Analizujesz procesy pod kątem możliwości automatyzacji, uwzględniając:

KONTEKST POLSKI:
- Budżet firmy w PLN (realny dla małych firm)
- Umiejętności techniczne zespołu (podstawowe)
- Zgodność z prawem polskim (RODO, KSH)
- Zwrot z inwestycji w perspektywie 3-6 miesięcy
- Polskie narzędzia gdy dostępne

ZASADY ANALIZY:
1. Zawsze podawaj konkretne narzędzia (Zapier, n8n, Airtable, ClickUp) zamiast teorii
2. Realistyczne szacunki kosztów w PLN
3. Uwzględniaj czas na naukę dla zespołu
4. Priorytetyzuj rozwiązania no-code/low-code
5. Oceniaj realny wpływ na codzienną pracę

STRUKTURA ODPOWIEDZI:
- Ocena potencjału: 1-10 (gdzie 10 = bardzo wysoki potencjał)
- Konkretne oszczędności w godzinach i PLN miesięcznie
- Maksymalnie 3 praktyczne rekomendacje
- Plan wdrożenia 3-5 kroków
- Ważne uwagi i ograniczenia

Odpowiadaj po polsku, krótko i konkretnie.
"""
```

## Obsługa błędów

### Podstawowa strategia error handling
```python
def analyze_with_error_handling(title: str, description: str) -> str:
    """Analiza z obsługą podstawowych błędów"""
    
    # Walidacja inputu
    if not title or len(title.strip()) < 3:
        return "Błąd: Nazwa procesu musi mieć co najmniej 3 znaki"
    
    if not description or len(description.strip()) < 10:
        return "Błąd: Opis procesu musi mieć co najmniej 10 znaków"
    
    # Sprawdź długość (prosty heurystyk)
    total_length = len(title) + len(description)
    if total_length > 2000:  # Bardzo konserwatywne ograniczenie
        return "Błąd: Opis procesu zbyt długi. Skróć do maksymalnie 2000 znaków"
    
    try:
        return analyze_process_with_ai(title, description)
    except Exception as e:
        # Log błędu (opcjonalnie)
        import logging
        logging.error(f"OpenAI API error: {str(e)}")
        
        # User-friendly message
        if "rate limit" in str(e).lower():
            return "Błąd: Zbyt dużo zapytań. Spróbuj ponownie za chwilę."
        elif "api key" in str(e).lower():
            return "Błąd: Problem z konfiguracją AI. Skontaktuj się z administratorem."
        else:
            return "Błąd: Nie udało się przeanalizować procesu. Spróbuj ponownie."
```

## Integracja ze Streamlit

### Użycie w głównej aplikacji
```python
# W show_new_process() w streamlit_app.py

if submitted:
    if not title or not description:
        st.error("Wypełnij wszystkie wymagane pola (*)")
    elif len(description) < 50:
        st.error("Opis musi mieć co najmniej 50 znaków")
    else:
        with st.spinner("Analizuję proces za pomocą AI..."):
            # Analiza AI
            ai_analysis = analyze_process_with_ai(title, description)
            
            # Zapisz do bazy
            result = save_process(st.session_state.user, title, description, ai_analysis)
            
            if result:
                st.success("Proces przeanalizowany i zapisany!")
                
                # Wyświetl wyniki
                st.markdown("### Wyniki analizy")
                st.markdown(ai_analysis)
```

## Konfiguracja

### Zmienne środowiskowe
```bash
# .env
OPENAI_API_KEY=sk-twoj_klucz_openai
OPENAI_MODEL=gpt-4o-mini  # Tańszy niż gpt-4o
```

### Inicjalizacja w Streamlit
```python
@st.cache_resource  
def init_openai():
    api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", "")
    if not api_key:
        st.error("Brak klucza OpenAI! Sprawdź zmienne środowiskowe.")
        st.stop()
    
    client = openai.OpenAI(api_key=api_key)
    return client

# Użycie
openai_client = init_openai()
```

## Testowanie

### Test podstawowej funkcjonalności
```python
def test_analyze_process_basic():
    """Test podstawowej analizy procesu"""
    
    # Mock OpenAI response
    with patch('streamlit_app.openai_client') as mock_client:
        mock_response = Mock()
        mock_response.choices[0].message.content = "OCENA POTENCJAŁU: 8/10\nGŁÓWNY PROBLEM: Ręczne zadania"
        mock_client.chat.completions.create.return_value = mock_response
        
        # Test
        result = analyze_process_with_ai("Test Process", "Test description of a business process")
        
        # Assertions
        assert "OCENA POTENCJAŁU: 8/10" in result
        assert "GŁÓWNY PROBLEM: Ręczne zadania" in result

def test_error_handling():
    """Test obsługi błędów"""
    
    # Test pustego tytułu
    result = analyze_with_error_handling("", "Valid description")
    assert "Błąd:" in result
    
    # Test pustego opisu
    result = analyze_with_error_handling("Valid title", "")
    assert "Błąd:" in result
    
    # Test zbyt długiego inputu
    long_description = "x" * 3000
    result = analyze_with_error_handling("Title", long_description)
    assert "zbyt długi" in result
```

## Optymalizacje kosztów

### Strategia oszczędzania na OpenAI API
1. **Model gpt-4o-mini** zamiast gpt-4o (10x tańszy)
2. **Krótkie prompty** - maksymalnie konkretne
3. **Ograniczenie max_tokens** do 800
4. **Proste text completion** zamiast function calling
5. **Walidacja inputu** przed wysłaniem do API

### Szacowane koszty miesięczne
- **100 analiz/miesiąc:** ~$2-5 USD
- **500 analiz/miesiąc:** ~$10-25 USD
- **1000 analiz/miesiąc:** ~$20-50 USD

## Monitoring prostej wersji

### Podstawowe metryki
- Liczba zapytań dziennie (przez Streamlit analytics)
- Success rate (ile % analiz się powiodło)
- Średnia długość odpowiedzi
- Najczęstsze błędy w logach

### Logowanie w Streamlit
```python
import logging

# Podstawowe logowanie
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - SmartFlowAI - %(levelname)s - %(message)s'
)

def log_analysis_attempt(title: str, success: bool, error: str = None):
    """Loguje próby analizy dla monitoringu"""
    if success:
        logging.info(f"Analysis successful for process: {title[:50]}")
    else:
        logging.error(f"Analysis failed for process: {title[:50]} - Error: {error}")
```

## Przykłady użycia

### Input/Output dla różnych branż

**Input - Księgowość:**
```
Tytuł: Wystawianie faktur VAT
Opis: Każdego dnia ręcznie tworzę faktury w programie księgowym na podstawie 
zamówień z emaili. Sprawdzam dane klienta, wpisuję pozycje, obliczam VAT, 
drukuję i wysyłam pocztą. Zajmuje mi to 2-3 godziny dziennie.
```

**Output:**
```
OCENA POTENCJAŁU: 9/10
GŁÓWNY PROBLEM: Ręczne przepisywanie danych z emaili
REKOMENDOWANE NARZĘDZIE: Zapier + InvoiceNinja + Gmail
SZACOWANY CZAS OSZCZĘDNOŚCI: 40 godzin/miesiąc
KOSZT WDROŻENIA: 200 PLN/miesiąc

PLAN WDROŻENIA:
1. Konfiguracja InvoiceNinja (darmowy plan)
2. Połączenie Gmail z Zapier (automatyczne rozpoznawanie zamówień)
3. Automatyczne generowanie faktur z danych email
4. Testowanie przez tydzień z ręczną kontrolą

UWAGI: Wymaga standaryzacji formatu zamówień w emailach
```

---

**Autor:** Dariusz Gąsior - SmartFlowAI MVP  
**Data:** 11 czerwca 2025  
**Status:** Gotowy do 2-dniowego sprintu