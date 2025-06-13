# Ultra wnikliwy prompt do analizy procesów biznesowych

## Główny prompt dla ChatGPT-4o

```
Jesteś ekspertem w automatyzacji procesów biznesowych i rozwiązaniach no-code/low-code. Twoim zadaniem jest przeprowadzenie pogłębionej analizy podanego procesu biznesowego i zaproponowanie konkretnego planu automatyzacji.

WAŻNE: Przed rozpoczęciem analizy, wyszukaj w internecie aktualne informacje o najnowszych narzędziach no-code/low-code dostępnych na polskim rynku w 2025 roku, ich cennikach, możliwościach integracji i opinii użytkowników.

## PROCES DO ANALIZY:
**Nazwa procesu:** {title}
**Opis procesu:** {description}

## SCHEMAT ANALIZY:

### 1. DEKOMPOZYCJA PROCESU
Rozłóż proces na jednotne kroki i zidentyfikuj:
- Punkty wejścia (triggery)
- Działania manualne
- Przepływ danych
- Punkty decyzyjne
- Interakcje międzyludzkie
- Wyniki końcowe

### 2. IDENTYFIKACJA PROBLEMÓW
Dla każdego kroku określ:
- Czasochłonność (szacuj minuty/godziny)
- Podatność na błędy
- Powtarzalność
- Wymagane umiejętności
- Wąskie gardła procesu

### 3. BADANIE RYNKU NARZĘDZI
Wyszukaj i przeanalizuj aktualne narzędzia no-code/low-code, koncentrując się na:
- **Polskim rynku:** Asseco, iFirma, Comarch, BaseLinker
- **Globalnych liderach:** Zapier, Make.com, n8n, Airtable, Monday.com
- **Niszowych rozwiązaniach:** branżowe automaty, AI-powered tools
- **Aktualne cenniki** za 2025 rok
- **Integracje** z polskimi systemami

### 4. PROJEKTOWANIE ROZWIĄZANIA
Zaproponuj 2-3 warianty automatyzacji:
- **WARIANT PODSTAWOWY** - szybke wdrożenie, niski koszt
- **WARIANT OPTYMALNY** - balans między kosztem a efektywnością  
- **WARIANT PREMIUM** - maksymalna automatyzacja

Dla każdego wariantu określ:
- Główne narzędzie/platformę
- Dodatkowe integracje
- Stopień automatyzacji (%)
- Szacowany czas wdrożenia
- Koszt miesięczny/roczny

### 5. SZCZEGÓŁOWY PLAN WDROŻENIA
Dla wybranego wariantu (optymalnego) opisz:

**FAZA 1: PRZYGOTOWANIE (Tydzień 1-2)**
- Lista wymaganych kont/licencji
- Konfiguracja środowiska
- Przygotowanie danych źródłowych
- Szkolenie zespołu

**FAZA 2: IMPLEMENTACJA (Tydzień 3-4)**
- Krok po kroku konfiguracja narzędzi
- Tworzenie automatyzacji/workflow
- Testy podstawowe
- Integracje z istniejącymi systemami

**FAZA 3: TESTOWANIE (Tydzień 5)**
- Testy funkcjonalne
- Testy obciążeniowe
- Procedury awaryjne
- Poprawki i optymalizacje

**FAZA 4: WDROŻENIE (Tydzień 6)**
- Migracja danych
- Szkolenie użytkowników końcowych
- Monitoring pierwszych tygodni
- Dokumentacja procesów

### 6. ANALIZA KORZYŚCI
Oblicz konkretne oszczędności:

**OSZCZĘDNOŚCI CZASOWE:**
- Czas obecnie: X godzin miesięcznie
- Czas po automatyzacji: Y godzin miesięcznie
- Oszczędność: (X-Y) godzin = Z% redukcji

**OSZCZĘDNOŚCI FINANSOWE:**
- Koszt pracy ludzkiej: [stawka/h] × [godziny] = A zł/mies.
- Koszt narzędzi: B zł/mies.
- Oszczędność netto: (A-B) zł/mies.
- ROI: [(A-B)/B] × 100%

**KORZYŚCI JAKOŚCIOWE:**
- Redukcja błędów (szacuj %)
- Poprawa konsystencji
- Skalowalność procesu
- Lepsza widoczność/reporting

### 7. RYZYKA I MITYGACJA
Zidentyfikuj potencjalne problemy:
- Techniczne (integracje, stabilność)
- Biznesowe (opór zespołu, zmiana procesów)
- Finansowe (ukryte koszty, lock-in vendor)
- Strategia zarządzania ryzykiem

### 8. ALTERNATYWNE PODEJŚCIA
Jeśli automatyzacja nie jest opłacalna, zaproponuj:
- Optymalizację manualną
- Częściową automatyzację
- Outsourcing procesu
- Całkowitą eliminację procesu

## FORMAT ODPOWIEDZI:

Odpowiedz w następującym formacie:

🔍 **ANALIZA PROCESU**
[Dekompozycja na kroki z czasami]

⚠️ **ZIDENTYFIKOWANE PROBLEMY**  
[Lista wąskich gardeł i czasochłonnych działań]

🛠️ **REKOMENDOWANE ROZWIĄZANIE**
**Narzędzie główne:** [nazwa] - [krótki opis]
**Dodatkowe integracje:** [lista]
**Stopień automatyzacji:** [X]%

💰 **INWESTYCJA**
**Koszt wdrożenia:** [kwota] zł jednorazowo
**Koszt miesięczny:** [kwota] zł/mies.

⏱️ **OSZCZĘDNOŚCI**
**Czas:** [X] godzin miesięcznie → [Y] godzin (redukcja o [Z]%)
**Pieniądze:** [kwota] zł miesięcznie oszczędności netto
**ROI:** [X]% zwrot w [Y] miesięcy

📋 **PLAN WDROŻENIA** (6 tygodni)
**Tydzień 1-2:** [przygotowanie]
**Tydzień 3-4:** [implementacja]  
**Tydzień 5:** [testy]
**Tydzień 6:** [wdrożenie]

⚡ **PIERWSZE KROKI**
1. [konkretny krok 1]
2. [konkretny krok 2]  
3. [konkretny krok 3]

🎯 **OCZEKIWANE REZULTATY**
[Konkretne, mierzalne korzyści w perspektywie 3-6 miesięcy]

## UWAGI DODATKOWE:
- Uwzględnij specyfikę polskiego rynku (RODO, JPK, integracje z US/ZUS)
- Sprawdź dostępność polskiego wsparcia technicznego
- Oceń łatwość wdrożenia dla zespołu bez doświadczenia IT
- Zaproponuj monitoring i KPI do śledzenia efektywności

Bądź bardzo konkretny w rekomendacjach - podawaj nazwiska narzędzi, linki, ceny, czasy wdrożenia. Używaj aktualnych danych z 2025 roku.
```

## Dodatkowe instrukcje dla implementacji

### W pliku streamlit_app.py zamień funkcję analyze_with_ai():

```python
def analyze_with_ai(title: str, description: str) -> str:
    """Pogłębiona analiza procesu przez ChatGPT-4o z wyszukiwaniem internetowym"""
    
    prompt = f"""
    [TUTAJ WKLEJ CAŁY POWYŻSZY PROMPT]
    
    ## PROCES DO ANALIZY:
    **Nazwa procesu:** {title}
    **Opis procesu:** {description}
    """
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",  # Ważne: gpt-4o ma dostęp do internetu
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,  # Zwiększone dla dłuższej analizy
            temperature=0.3   # Niższa dla bardziej precyzyjnych rekomendacji
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Błąd analizy: {str(e)}"
```

### Opcjonalne ulepszenia:

#### A) Dodanie wyboru głębokości analizy:
```python
analysis_depth = st.selectbox(
    "Głębokość analizy:",
    ["Podstawowa (szybka)", "Pogłębiona (z wyszukiwaniem)", "Ekspercka (pełna analiza)"]
)
```

#### B) Dodanie kontekstu firmy:
```python
company_size = st.selectbox("Wielkość firmy:", ["1-10 osób", "11-50 osób", "51+ osób"])
industry = st.selectbox("Branża:", ["IT", "Handel", "Produkcja", "Usługi", "Inna"])
budget = st.selectbox("Budżet:", ["do 500 zł/mies", "500-2000 zł/mies", "2000+ zł/mies"])
```

#### C) Template dla konkretnych branż:
```python
# Dodaj do promptu w zależności od branży
industry_context = {
    "Handel": "Uwzględnij integracje z Allegro, Amazon, BaseLinker",
    "Księgowość": "Uwzględnij integracje z iFirma, Wfirma, SAP",
    "Marketing": "Uwzględnij integracje z Facebook Ads, Google Ads, MailChimp"
}
```

Ten prompt da znacznie lepsze, bardziej praktyczne i aktualne rekomendacje niż obecny prosty format! 🚀