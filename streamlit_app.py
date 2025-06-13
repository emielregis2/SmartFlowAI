# -*- coding: utf-8 -*-
# Plik: streamlit_app.py
# streamlit_app.py - Ultra-prosta aplikacja SmartFlowAI (2 dni MVP)
# UWAGA: Projekt powstał z pomocą edytora Cursor oraz AI Claude Sonnet 4.

import streamlit as st
import openai
import os
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv
import logging
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import tempfile
import io

# Konfiguracja logowania do pliku
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('smartflow_debug.log', encoding='utf-8'),
        logging.StreamHandler()  # Też na konsoli dla development
    ]
)
logger = logging.getLogger(__name__)

# Ładuj zmienne środowiskowe z .env
load_dotenv()

# Konfiguracja strony
st.set_page_config(page_title="SmartFlowAI", page_icon="🤖")

# Custom CSS dla Dark Mode
st.markdown("""
<style>
    /* Dark Mode Custom Styling */
    .stApp {
        background: linear-gradient(135deg, #0E1117 0%, #1e2328 100%);
    }
    
    /* Poprawki dla ekspanderów w dark mode */
    .streamlit-expanderHeader {
        background-color: #262730 !important;
        border: 1px solid #3e4147 !important;
    }
    
    /* Styling dla success/error messages */
    .stAlert > div {
        border-radius: 10px;
        border: none;
    }
    
    /* Custom styling dla przycisków */
    .stButton > button {
        border-radius: 20px;
        border: 2px solid #00D4AA;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 212, 170, 0.3);
    }
    
    /* Styling dla form elements */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 1px solid #3e4147;
        background-color: #262730;
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 10px;
        border: 1px solid #3e4147;
        background-color: #262730;
    }
    
    /* Dark mode tabs styling */
    .stTabs [data-baseweb="tab"] {
        background-color: #262730;
        border-radius: 10px 10px 0 0;
    }
    
    /* Title glow effect */
    h1 {
        text-shadow: 0 0 10px rgba(0, 212, 170, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Inicjalizacja klientów
@st.cache_resource
def init_supabase():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    
    # Fallback do secrets jeśli .env nie ma wartości
    if not url or not key:
        try:
            url = url or st.secrets.get("SUPABASE_URL", "")
            key = key or st.secrets.get("SUPABASE_ANON_KEY", "")
        except:
            pass
    
    if not url or not key:
        st.error("❌ Brak konfiguracji Supabase! Sprawdź .env lub secrets.toml")
        st.stop()
    
    return create_client(url, key)

@st.cache_resource  
def init_openai():
    api_key = os.getenv("OPENAI_API_KEY")
    
    # Fallback do secrets jeśli .env nie ma wartości
    if not api_key:
        try:
            api_key = st.secrets.get("OPENAI_API_KEY", "")
        except:
            pass
    
    if not api_key:
        st.error("❌ Brak klucza OpenAI! Sprawdź .env lub secrets.toml")
        st.stop()
    
    openai.api_key = api_key
    return openai

# Globalne zmienne
supabase = init_supabase()
openai_client = init_openai()

# Session state
if 'user' not in st.session_state:
    st.session_state.user = None

# FUNKCJE POMOCNICZE

def analyze_with_ai(title: str, description: str, analysis_depth: str = "Pogłębiona", company_size: str = "", industry: str = "", budget: str = "") -> str:
    """Ultra wnikliwa analiza procesu przez ChatGPT-4o z wyszukiwaniem internetowym"""
    
    # Dodatkowy kontekst firmy
    company_context = ""
    if company_size or industry or budget:
        company_context = f"""
## KONTEKST FIRMY:
**Wielkość firmy:** {company_size}
**Branża:** {industry}
**Budżet na automatyzację:** {budget}
"""
    
    # Branżowe szablony kontekstu
    industry_context = {
        "E-commerce/Handel": "Uwzględnij integracje z Allegro, Amazon, BaseLinker, Shopify, WooCommerce, systemy magazynowe i płatności online.",
        "Księgowość": "Uwzględnij integracje z iFirma, Wfirma, SAP, Comarch ERP, JPK, US, ZUS, systemy bankowe.",
        "Marketing/Reklama": "Uwzględnij integracje z Facebook Ads, Google Ads, MailChimp, HubSpot, analytics, CRM.",
        "IT/Software": "Uwzględnij integracje z GitHub, Jira, Slack, CI/CD, monitoring, ticketing systems.",
        "Logistyka": "Uwzględnij integracje z systemami WMS, TMS, śledzenie przesyłek, API kurierów.",
        "Usługi finansowe": "Uwzględnij integracje z systemami bankowymi, KNF, AML, RODO, systemy płatności.",
        "Produkcja": "Uwzględnij integracje z systemami ERP, MES, IoT, kontrola jakości, planowanie produkcji.",
        "Edukacja": "Uwzględnij integracje z systemami LMS, e-learning, zarządzanie studentami, certyfikaty.",
        "Zdrowie": "Uwzględnij integracje z systemami medycznymi, RODO w ochronie zdrowia, NFZ, e-recepty."
    }
    
    # Dodaj branżowy kontekst jeśli wybrano branżę
    branch_specific = ""
    if industry and industry in industry_context:
        branch_specific = f"\n\n**UWAGI BRANŻOWE:** {industry_context[industry]}"
    
    # Modyfikacja promptu w zależności od głębokości analizy
    if analysis_depth == "Podstawowa (szybka)":
        prompt = f"""
Przeanalizuj ten proces biznesowy i podaj krótką rekomendację:

PROCES: {title}
OPIS: {description}
{company_context}{branch_specific}

Odpowiedz w formacie:
🔍 **ANALIZA:** [główny problem w 2-3 zdaniach]
🛠️ **ROZWIĄZANIE:** [konkretne narzędzie np. Zapier, Airtable]
💰 **KOSZT:** [szacowany koszt miesięczny]
⏱️ **OSZCZĘDNOŚCI:** [szacowany czas/pieniądze miesięcznie]
⚡ **PIERWSZE KROKI:** [2-3 konkretne kroki]
"""
    elif analysis_depth == "Ekspercka (pełna analiza)":
        prompt = f"""
Jesteś ekspertem w automatyzacji procesów biznesowych z 15-letnim doświadczeniem. Przeprowadź najgłębszą możliwą analizę tego procesu.

WAŻNE: Wyszukaj w internecie najnowsze informacje o narzędziach, cennikach, case studies i opiniach użytkowników z 2025 roku.

## PROCES DO ANALIZY:
**Nazwa procesu:** {title}
**Opis procesu:** {description}
{company_context}{branch_specific}

## ULTRA SZCZEGÓŁOWA ANALIZA:

### 1. DEKOMPOZYCJA PROCESU (szczegółowa)
- Mapowanie każdego kroku z czasami
- Identyfikacja wszystkich touchpointów
- Analiza przepływu danych i dokumentów
- Punkty integracji z innymi systemami

### 2. ANALIZA PROBLEMÓW (pogłębiona)
- Koszty ukryte i jawne
- Analiza ryzyka błędów
- Wpływ na inne procesy
- Bottlenecki i wąskie gardła

### 3. BADANIE RYNKU (aktualne dane 2025)
- Porównanie 5-7 najlepszych narzędzi
- Aktualne cenniki i promocje
- Opinie użytkowników z ostatnich 6 miesięcy
- Integracje z polskimi systemami (US, ZUS, JPK)

### 4. WARIANTY ROZWIĄZAŃ (3 opcje)
- BASIC: Minimum viable automation
- STANDARD: Optymalne rozwiązanie
- PREMIUM: Maksymalna automatyzacja

### 5. SZCZEGÓŁOWY PLAN WDROŻENIA (8 tygodni)
- Harmonogram tygodniowy
- Zasoby i kompetencje
- Punkty kontrolne i KPI
- Plan zarządzania ryzykiem

### 6. ANALIZA FINANSOWA (ROI)
- Szczegółowe kalkulacje kosztów
- Analiza zwrotu z inwestycji
- Scenariusze optymistyczny/pesymistyczny
- Ukryte koszty i oszczędności

### 7. MONITORING I OPTYMALIZACJA
- KPI do śledzenia
- Narzędzia monitoringu
- Plan ciągłego doskonalenia

Odpowiedz w pełnym formacie z wszystkimi sekcjami, bądź bardzo konkretny w rekomendacjach.
"""
    else:  # Pogłębiona (domyślna)
        prompt = f"""
Jesteś ekspertem w automatyzacji procesów biznesowych i rozwiązaniach no-code/low-code. Twoim zadaniem jest przeprowadzenie pogłębionej analizy podanego procesu biznesowego i zaproponowanie konkretnego planu automatyzacji.

WAŻNE: Przed rozpoczęciem analizy, wyszukaj w internecie aktualne informacje o najnowszych narzędziach no-code/low-code dostępnych na polskim rynku w 2025 roku, ich cennikach, możliwościach integracji i opinii użytkowników.

## PROCES DO ANALIZY:
**Nazwa procesu:** {title}
**Opis procesu:** {description}
{company_context}{branch_specific}

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
"""
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",  # WAŻNE: gpt-4o ma dostęp do internetu
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000 if analysis_depth == "Podstawowa (szybka)" else 3000,  # Więcej tokenów dla głębszej analizy
            temperature=0.3   # Niższa dla bardziej precyzyjnych rekomendacji
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Błąd analizy: {str(e)}"

def save_process(title: str, description: str, ai_analysis: str):
    """Zapisuje proces do bazy"""
    try:
        data_to_insert = {
            'user_email': st.session_state.user,
            'title': title,
            'description': description,
            'ai_analysis': ai_analysis,
            'created_at': datetime.now().isoformat()
        }
        
        logger.info(f"SAVE_PROCESS: Zapisuję dane - Title: '{title}', Desc: '{description[:50]}...', User: {st.session_state.user}")
        
        result = supabase.table('processes').insert(data_to_insert).execute()
        
        logger.info(f"SAVE_PROCESS: Wynik zapisu: {result.data}")
        
        # Sprawdź czy rzeczywiście się zapisało
        if result.data and len(result.data) > 0:
            st.success(f"✅ Proces '{title}' został zapisany!")
            return True
        else:
            st.error(f"❌ Proces się nie zapisał - brak danych w odpowiedzi")
            return False
            
    except Exception as e:
        st.error(f"❌ Błąd zapisu: {str(e)}")
        return False

def get_processes():
    """Pobiera procesy użytkownika - BEZ CACHE!"""
    try:
        result = supabase.table('processes').select('*').eq('user_email', st.session_state.user).order('created_at', desc=True).execute()
        logger.info(f"GET_PROCESSES: Pobrano {len(result.data)} procesów dla {st.session_state.user}")
        return result.data
    except Exception as e:
        logger.error(f"GET_PROCESSES: Błąd pobierania dla {st.session_state.user}: {str(e)}")
        st.error(f"❌ Błąd pobierania: {str(e)}")
        return []

def delete_process(process_id: int):
    """Usuwa proces"""
    try:
        # Najpierw sprawdź czy proces istnieje
        existing = supabase.table('processes').select('id').eq('id', process_id).eq('user_email', st.session_state.user).execute()
        
        if not existing.data:
            st.warning("⚠️ Proces nie został znaleziony lub brak uprawnień")
            return False
        
        # Usuń proces
        result = supabase.table('processes').delete().eq('id', process_id).execute()
        logger.info(f"DELETE_PROCESS: Usunięto proces ID {process_id}")
        st.success("✅ Proces został usunięty!")
        st.session_state.processes_updated = True  # Odśwież listę po usunięciu
        return True
        
    except Exception as e:
        logger.error(f"DELETE_PROCESS: Błąd usuwania procesu ID {process_id}: {str(e)}")
        st.error(f"❌ Błąd usuwania: {str(e)}")
        return False

def update_process(process_id: int, title: str, description: str, ai_analysis: str):
    """Aktualizuje proces w bazie danych"""
    try:
        # Najpierw sprawdź czy proces istnieje
        existing = supabase.table('processes').select('id').eq('id', process_id).eq('user_email', st.session_state.user).execute()
        
        if not existing.data:
            st.warning("⚠️ Proces nie został znaleziony lub brak uprawnień")
            return False
        
        # Aktualizuj proces
        result = supabase.table('processes').update({
            'title': title,
            'description': description,
            'ai_analysis': ai_analysis
        }).eq('id', process_id).execute()
        
        logger.info(f"UPDATE_PROCESS: Zaktualizowano proces ID {process_id}")
        st.success("✅ Proces został zaktualizowany!")
        st.session_state.processes_updated = True  # Odśwież listę po aktualizacji
        return True
        
    except Exception as e:
        logger.error(f"UPDATE_PROCESS: Błąd aktualizacji procesu ID {process_id}: {str(e)}")
        st.error(f"❌ Błąd aktualizacji: {str(e)}")
        return False

# STRONY APLIKACJI

def show_login():
    """Strona logowania i rejestracji"""
    st.title("SmartFlowAI")
    
    # Zakładki logowanie / rejestracja
    login_tab, register_tab = st.tabs(["🔑 Logowanie", "📝 Rejestracja"])
    
    # Zakładka logowania
    with login_tab:
        st.subheader("Zaloguj się")
        
        # Informacja o kontach testowych
        with st.expander("👥 Konta testowe", expanded=False):
            st.info("""
            **Dostępne konta testowe:**
            
            📧 **test@smartflowai.com** / test123
            📧 **test@smartflow.pl** / test123456
            """)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            with st.form("login"):
                email = st.text_input("Email")
                password = st.text_input("Hasło", type="password")
                if st.form_submit_button("Zaloguj"):
                    if email and password:
                        try:
                            # Próba logowania przez Supabase
                            response = supabase.auth.sign_in_with_password({
                                "email": email,
                                "password": password
                            })
                            if response.user:
                                st.session_state.user = email
                                st.rerun()
                        except Exception as e:
                            # Fallback - użytkownicy testowi
                            test_users = {
                                "test@smartflowai.com": "test123",
                                "test@smartflow.pl": "test123456"
                            }
                            
                            if email in test_users and test_users[email] == password:
                                st.session_state.user = email
                                st.success(f"✅ Zalogowano jako {email}")
                                st.rerun()
                            else:
                                st.error(f"❌ Błędne dane logowania: {str(e)}")
                    else:
                        st.error("Wypełnij wszystkie pola")
    
    # Zakładka rejestracji
    with register_tab:
        st.subheader("Utwórz konto")
        
        with st.form("register"):
            new_email = st.text_input("Email")
            new_password = st.text_input("Hasło", type="password")
            confirm_password = st.text_input("Potwierdź hasło", type="password")
            
            if st.form_submit_button("Zarejestruj"):
                if not new_email or not new_password or not confirm_password:
                    st.error("❌ Wypełnij wszystkie pola!")
                elif new_password != confirm_password:
                    st.error("❌ Hasła nie są identyczne!")
                elif len(new_password) < 6:
                    st.error("❌ Hasło musi mieć co najmniej 6 znaków!")
                else:
                    try:
                        # Rejestracja w Supabase
                        logger.info(f"REGISTER: Próba rejestracji użytkownika: {new_email}")
                        response = supabase.auth.sign_up({
                            "email": new_email,
                            "password": new_password
                        })
                        
                        if response.user:
                            logger.info(f"REGISTER: Zarejestrowano użytkownika: {new_email}")
                            st.success(f"✅ Konto utworzone! Możesz się teraz zalogować jako {new_email}")
                            
                            # Opcjonalnie: automatycznie zaloguj użytkownika
                            st.session_state.user = new_email
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("❌ Błąd rejestracji - sprawdź dane i spróbuj ponownie")
                    except Exception as e:
                        logger.error(f"REGISTER: Błąd rejestracji użytkownika {new_email}: {str(e)}")
                        st.error(f"❌ Błąd rejestracji: {str(e)}")
                        
                        # Informacja dla użytkownika, że może email jest już zajęty
                        if "already registered" in str(e) or "already exists" in str(e):
                            st.warning("⚠️ Ten email jest już zarejestrowany. Spróbuj się zalogować.")

def show_dashboard():
    """Dashboard główny"""
    st.title("SmartFlowAI Dashboard")
    st.write(f"Zalogowany: {st.session_state.user}")
    
    if st.button("Wyloguj"):
        st.session_state.user = None
        st.rerun()
    
    # Menu
    tab1, tab2, tab3 = st.tabs(["➕ Nowy Proces", "📋 Przeanalizowane procesy", "📄 Zestawienie w PDF"])
    
    with tab1:
        show_new_process_form()
    
    with tab2:
        show_processes_list()
    
    with tab3:
        show_pdf_summary_tab()

def show_processes_list():
    """Lista procesów"""
    st.subheader("Przeanalizowane procesy")
    
    # Sprawdź czy lista wymaga odświeżenia po dodaniu nowego procesu
    if st.session_state.get('processes_updated', False):
        st.session_state.processes_updated = False  # Wyczyść flagę
        logger.info("PROCESSES_LIST: Auto-odświeżenie listy po dodaniu nowego procesu")
        st.rerun()
    
    # Przycisk odświeżania
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Odśwież listę", type="secondary"):
            logger.info("PROCESSES_LIST: Ręczne odświeżenie listy")
            st.rerun()
    
    processes = get_processes()
    
    # Sprawdź każdy proces i policz które można wyrenderować
    valid_processes = []
    invalid_processes = []
    
    for i, process in enumerate(processes):
        title = process.get('title')
        created_at = process.get('created_at')
        
        # Sprawdź czy proces ma wszystkie wymagane dane
        if title and created_at and len(title.strip()) > 0:
            valid_processes.append(process)
        else:
            invalid_processes.append({
                'id': process.get('id', 'BRAK'),
                'title': title,
                'created_at': created_at,
                'description': process.get('description', '')[:50] + '...' if process.get('description') else 'BRAK'
            })
    
    # Pokaż procesy z błędnymi danymi jeśli istnieją
    if invalid_processes:
        with st.expander(f"⚠️ Procesy z błędnymi danymi ({len(invalid_processes)})", expanded=False):
            for proc in invalid_processes:
                st.write(f"**ID:** {proc['id']}, **Title:** '{proc['title']}', **Created:** '{proc['created_at']}', **Desc:** {proc['description']}")
                if st.button(f"🗑️ Usuń proces ID {proc['id']}", key=f"del_invalid_{proc['id']}"):
                    if delete_process(proc['id']):
                        st.rerun()
    
    if not valid_processes:
        st.info("Brak przeanalizowanych procesów. Dodaj pierwszy proces w zakładce 'Nowy Proces'!")
        return
    
    # Renderuj tylko procesy z poprawnymi danymi
    for i, process in enumerate(valid_processes):
        try:
            title = process['title']
            created_date = process['created_at'][:10]
            
            with st.expander(f"{title} ({created_date})", expanded=False):
                st.write("Opis:")
                st.write(process.get('description', 'Brak opisu'))
                
                st.write("Analiza AI:")
                st.write(process.get('ai_analysis', 'Brak analizy'))
                
                # Przyciski akcji - Edytuj po lewej, Usuń maksymalnie po prawej
                col1, col2, col3 = st.columns([1, 2, 1])
                with col1:
                    if st.button(f"✏️ Edytuj", key=f"edit_{process['id']}"):
                        st.session_state[f"editing_{process['id']}"] = True
                        st.rerun()
                with col3:  # Maksymalnie po prawej stronie
                    if st.button(f"🗑️ Usuń", key=f"del_{process['id']}"):
                        if delete_process(process['id']):
                            st.rerun()
                
                # Formularz edycji (jeśli aktywny)
                if st.session_state.get(f"editing_{process['id']}", False):
                    st.markdown("---")
                    st.subheader("✏️ Edytuj proces")
                    
                    with st.form(f"edit_form_{process['id']}"):
                        edit_title = st.text_input(
                            "Nazwa procesu", 
                            value=process.get('title', ''),
                            key=f"edit_title_{process['id']}"
                        )
                        edit_description = st.text_area(
                            "Opis procesu", 
                            value=process.get('description', ''),
                            height=150,
                            key=f"edit_desc_{process['id']}"
                        )
                        edit_analysis = st.text_area(
                            "Analiza AI", 
                            value=process.get('ai_analysis', ''),
                            height=100,
                            key=f"edit_analysis_{process['id']}"
                        )
                        
                        col_save, col_space, col_cancel = st.columns([1, 2, 1])
                        with col_save:
                            if st.form_submit_button("💾 Zapisz zmiany", type="primary"):
                                if edit_title and edit_description and edit_analysis:
                                    if update_process(process['id'], edit_title, edit_description, edit_analysis):
                                        st.session_state[f"editing_{process['id']}"] = False
                                        st.rerun()
                                else:
                                    st.error("Wypełnij wszystkie pola!")
                        with col_cancel:  # Maksymalnie po prawej stronie
                            if st.form_submit_button("❌ Anuluj"):
                                st.session_state[f"editing_{process['id']}"] = False
                        st.rerun()
                        
        except Exception as e:
            st.error(f"❌ Błąd renderowania procesu ID {process.get('id', 'BRAK')}: {str(e)}")

def show_new_process_form():
    """Formularz nowego procesu"""
    st.subheader("Dodaj Nowy Proces")
    
    # Informacja o logach debugowania
    with st.expander("🔍 Debugging", expanded=False):
        st.info("Logi debugowania są zapisywane w pliku: `smartflow_debug.log`")
        if st.button("📄 Pokaż ostatnie 10 linii logów"):
            try:
                with open('smartflow_debug.log', 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    last_lines = lines[-10:] if len(lines) >= 10 else lines
                    st.code(''.join(last_lines))
            except FileNotFoundError:
                st.warning("Plik logów jeszcze nie istnieje")
    
    # Session state do przechowywania stanu analizy i formularza
    if 'analysis_completed' not in st.session_state:
        st.session_state.analysis_completed = False
    if 'last_analysis' not in st.session_state:
        st.session_state.last_analysis = ""
    if 'last_title' not in st.session_state:
        st.session_state.last_title = ""
    if 'last_description' not in st.session_state:
        st.session_state.last_description = ""
    if 'form_key' not in st.session_state:
        st.session_state.form_key = 0
    if 'balloons_shown' not in st.session_state:
        st.session_state.balloons_shown = False
    
    # Jeśli analiza została zakończona, pokaż wyniki i przycisk
    if st.session_state.analysis_completed and st.session_state.last_analysis:
        st.success("Analiza zakończona!")
        
        # Pokaż baloniki tylko przy pierwszym renderowaniu
        if not st.session_state.balloons_shown:
            st.balloons()  # 🎉 Baloniki po udanej analizie!
            st.session_state.balloons_shown = True
        
        # Pokaż wprowadzone dane
        st.subheader("📋 Wprowadzony proces:")
        st.write(f"Nazwa: {st.session_state.last_title}")
        st.write(f"Opis: {st.session_state.last_description}")
        
        # Pokaż analizę AI
        st.subheader("🤖 Analiza AI:")
        st.write(st.session_state.last_analysis)
        
        st.info("💡 **Przeczytaj analizę powyżej, a następnie kliknij przycisk aby przejść do następnego procesu.**")
        
        if st.button("➡️ Następny proces do analizy", type="primary"):
            logger.info(f"NEXT_PROCESS: Użytkownik kliknął 'Następny proces', resetuję stan, form_key: {st.session_state.form_key} -> {st.session_state.form_key + 1}")
            # Wyczyść stan analizy i wymuś nowy formularz
            st.session_state.analysis_completed = False
            st.session_state.last_title = ""
            st.session_state.last_description = ""
            st.session_state.last_analysis = ""
            st.session_state.balloons_shown = False  # Reset baloników na następną analizę
            st.session_state.processes_updated = True  # Odśwież listę gdy użytkownik przejdzie do zakładki
            st.session_state.form_key += 1
            st.rerun()
    else:
        # Pokaż formularz tylko gdy nie ma aktywnej analizy
        logger.info(f"FORM: Renderuję formularz z kluczem: new_process_{st.session_state.form_key}")
        with st.form(f"new_process_{st.session_state.form_key}"):
            title = st.text_input(
                "Nazwa procesu *", 
                placeholder="np. Wystawianie faktur"
            )
            description = st.text_area(
                "Opis procesu *", 
                placeholder="Opisz krok po kroku jak wygląda ten proces...",
                height=150
            )
            
            # Opcje analizy
            st.markdown("### ⚙️ Opcje analizy")
            
            col1, col2 = st.columns(2)
            with col1:
                analysis_depth = st.selectbox(
                    "Głębokość analizy:",
                    ["Podstawowa (szybka)", "Pogłębiona (z wyszukiwaniem)", "Ekspercka (pełna analiza)"],
                    index=1  # Domyślnie pogłębiona
                )
            
            with col2:
                company_size = st.selectbox(
                    "Wielkość firmy:", 
                    ["", "1-10 osób", "11-50 osób", "51-200 osób", "200+ osób"]
                )
            
            col3, col4 = st.columns(2)
            with col3:
                industry = st.selectbox(
                    "Branża:", 
                    ["", "IT/Software", "E-commerce/Handel", "Produkcja", "Usługi finansowe", 
                     "Marketing/Reklama", "Księgowość", "Logistyka", "Edukacja", "Zdrowie", "Inna"]
                )
            
            with col4:
                budget = st.selectbox(
                    "Budżet na automatyzację:", 
                    ["", "do 500 zł/mies", "500-2000 zł/mies", "2000-5000 zł/mies", "5000+ zł/mies"]
            )
            
            if st.form_submit_button("🤖 Analizuj przez AI", type="primary"):
                if not title or not description:
                    st.error("Wypełnij wszystkie pola!")
                elif len(description) < 20:
                    st.error("Opis musi mieć co najmniej 20 znaków")
                else:
                    # Log dane z formularza
                    logger.info(f"FORM_SUBMIT: Dane z formularza - Title: '{title}', Desc: '{description[:50]}...', Depth: {analysis_depth}")
                    
                    with st.spinner("Analizuję przez ChatGPT-4o..."):
                        # Analiza AI z dodatkowymi parametrami
                        ai_analysis = analyze_with_ai(title, description, analysis_depth, company_size, industry, budget)
                        
                        logger.info(f"FORM_SUBMIT: Analiza AI: '{ai_analysis[:50]}...'")
                        
                        # Zapisz do bazy
                        if save_process(title, description, ai_analysis):
                            logger.info(f"FORM_SUBMIT: Zapisano do bazy - Title: '{title}'")
                            
                            # Zapisz dane w session state
                            st.session_state.analysis_completed = True
                            st.session_state.last_title = title
                            st.session_state.last_description = description
                            st.session_state.last_analysis = ai_analysis
                            st.session_state.processes_updated = True  # Flaga do odświeżenia listy
                            st.rerun()
                        else:
                            st.error("Błąd zapisu do bazy danych")

def show_pdf_summary_tab():
    """Zakładka: Zestawienie w PDF"""
    st.subheader("Zestawienie procesów w PDF")
    processes = get_processes()
    if not processes:
        st.info("Brak procesów do zestawienia.")
        return

    # Edytowalny tekst nagłówka
    header = st.text_input("Nagłówek raportu", value="Zestawienie przeanalizowanych procesów SmartFlowAI")
    # Edytowalny tekst stopki
    footer = st.text_input("Stopka raportu", value="Wygenerowano przez SmartFlowAI")

    # Funkcja do generowania tekstu do kopiowania
    def generate_text_content():
        """Generuje pełny tekst raportu do kopiowania"""
        text_content = f"{header}\n{'='*50}\n\n"
        
        # Dodaj wszystkie procesy (nie tylko 10 jak w PDF)
        for i, p in enumerate(processes, 1):
            text_content += f"{i}. {p.get('title','')}\n"
            text_content += f"{'='*30}\n"
            text_content += f"OPIS:\n{p.get('description','')}\n\n"
            text_content += f"ANALIZA AI:\n{p.get('ai_analysis','')}\n\n"
            text_content += f"{'-'*50}\n\n"
        
        text_content += f"\n{footer}\n"
        text_content += f"Wygenerowano: {processes[0].get('created_at', '')[:10] if processes else ''}"
        
        return text_content

    # Podgląd danych do PDF
    st.markdown("### Podgląd danych do PDF:")
    for p in processes:
        st.write(f"{p.get('title','')}: {p.get('description','')}")
        st.write(f"Analiza AI: {p.get('ai_analysis','')}")
        st.write("---")

    # Przyciski w dwóch kolumnach
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Generuj PDF", type="primary"):
            try:
                # Funkcja pomocnicza do przygotowania tekstu dla PDF
                def prepare_text_for_pdf(text, max_length=2000):  # Zwiększone z 500 do 2000
                    """Przygotowuje tekst dla PDF zachowując polskie znaki"""
                    if not text:
                        return ""
                    
                    # Zachowaj polskie znaki, tylko wyczyść formatowanie
                    clean_text = str(text)
                    
                    # Usuń znaki specjalne które mogą powodować problemy z formatowaniem
                    clean_text = clean_text.replace('\n', ' ').replace('\r', ' ')
                    clean_text = clean_text.replace('\t', ' ')  # Usuń tabulatory
                    clean_text = ' '.join(clean_text.split())  # Usuń wielokrotne spacje
                    
                    # Skróć tekst jeśli jest za długi (ale z większym limitem)
                    if len(clean_text) > max_length:
                        clean_text = clean_text[:max_length] + "..."
                    
                    return clean_text

                # Funkcja pomocnicza do bezpiecznego tekstu
                def safe_text(text):
                    """Zwraca tekst bezpieczny dla wybranej czcionki - usuwa polskie znaki i emoji, ale zachowuje treść"""
                    if not text:
                        return ""
                    
                    # Konwersja polskich znaków na ASCII
                    replacements = {
                        'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n', 'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z',
                        'Ą': 'A', 'Ć': 'C', 'Ę': 'E', 'Ł': 'L', 'Ń': 'N', 'Ó': 'O', 'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z'
                    }
                    
                    clean_text = str(text)
                    
                    # Zamień polskie znaki
                    for polish, ascii_char in replacements.items():
                        clean_text = clean_text.replace(polish, ascii_char)
                    
                    # Zamień emoji na tekst opisowy (zamiast je usuwać)
                    emoji_replacements = {
                        '🔍': ' [ANALIZA] ',
                        '⚠️': ' [PROBLEMY] ',
                        '🛠️': ' [ROZWIAZANIE] ',
                        '💰': ' [INWESTYCJA] ',
                        '⏱️': ' [OSZCZEDNOSCI] ',
                        '📋': ' [PLAN] ',
                        '⚡': ' [KROKI] ',
                        '🎯': ' [REZULTATY] ',
                        '🤖': ' [AI] ',
                        '✅': ' [OK] ',
                        '❌': ' [BLAD] ',
                        '📄': ' [PDF] ',
                        '✏️': ' [EDYTUJ] ',
                        '🗑️': ' [USUN] ',
                        '💾': ' [ZAPISZ] ',
                        '🚀': ' [START] ',
                        '📊': ' [DANE] ',
                        '🔧': ' [NARZEDZIA] ',
                        '📈': ' [WZROST] ',
                        '💡': ' [POMYSL] ',
                        '🎉': ' [SUKCES] '
                    }
                    
                    # Zamień znane emoji na tekst
                    for emoji, replacement in emoji_replacements.items():
                        clean_text = clean_text.replace(emoji, replacement)
                    
                    # Usuń pozostałe znaki spoza ASCII 32-126, ale zachowaj podstawowe znaki białe
                    safe_chars = []
                    for char in clean_text:
                        char_code = ord(char)
                        if 32 <= char_code <= 126:  # Podstawowe znaki ASCII (spacja do ~)
                            safe_chars.append(char)
                        elif char in ['\n', '\r', '\t']:  # Zachowaj podstawowe znaki białe
                            safe_chars.append(' ')  # Zamień na spację
                        # Inne znaki specjalne pomijamy (ale główne emoji już zostały zamienione)
                    
                    return ''.join(safe_chars)
                
                # Tworzymy PDF z obsługą Unicode
                pdf = FPDF()
                pdf.add_page()
                pdf.set_auto_page_break(auto=True, margin=15)
                
                # fpdf2 nie ma wbudowanej obsługi polskich znaków - używamy konwersji
                font_family = 'Helvetica'
                unicode_support = False
                
                def fallback_clean_polish(text):
                    """Konwersja polskich znaków na ASCII"""
                    replacements = {
                        'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n', 'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z',
                        'Ą': 'A', 'Ć': 'C', 'Ę': 'E', 'Ł': 'L', 'Ń': 'N', 'Ó': 'O', 'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z'
                    }
                    for polish, ascii_char in replacements.items():
                        text = text.replace(polish, ascii_char)
                    return text
                
                # Nagłówek
                pdf.set_font(font_family, "B", size=14)
                header_text = safe_text(prepare_text_for_pdf(header, 100))
                pdf.cell(0, 10, header_text, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
                pdf.ln(5)
                
                # Procesy - ograniczamy do pierwszych 10 dla lepszego przeglądu
                display_processes = processes[:10] if len(processes) > 10 else processes
                
                for i, p in enumerate(display_processes, 1):
                    # Sprawdź czy mamy miejsce na stronie
                    if pdf.get_y() > 250:  # Jeśli jesteśmy blisko końca strony
                        pdf.add_page()
                    
                    # Tytuł procesu
                    pdf.set_font(font_family, "B", size=11)
                    title_text = safe_text(prepare_text_for_pdf(f"{i}. {p.get('title','')}", 80))
                    pdf.cell(0, 8, title_text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    
                    # Opis procesu - pełny tekst z wieloma liniami (zwiększony limit)
                    pdf.set_font(font_family, "", size=9)
                    description = safe_text(prepare_text_for_pdf(p.get('description',''), 1500))  # Zwiększone z 500 do 1500
                    pdf.cell(0, 6, "Opis:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.multi_cell(0, 5, description)  # multi_cell dla długich tekstów
                    pdf.ln(2)
                    
                    # Analiza AI - pełny tekst z wieloma liniami (zwiększony limit)
                    analysis = safe_text(prepare_text_for_pdf(p.get('ai_analysis',''), 2000))  # Zwiększone z 500 do 2000
                    pdf.cell(0, 6, "Analiza AI:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.multi_cell(0, 5, analysis)  # multi_cell dla długich tekstów
                    pdf.ln(3)
                
                # Informacja o ograniczeniu
                if len(processes) > 10:
                    pdf.ln(5)
                    pdf.set_font(font_family, "I", size=8)
                    limit_text = safe_text(f"Pokazano 10 z {len(processes)} procesów. Pełna lista dostępna w aplikacji.")
                    pdf.cell(0, 6, limit_text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
                # Stopka
                pdf.ln(5)
                pdf.set_font(font_family, "", size=8)
                footer_text = safe_text(prepare_text_for_pdf(footer, 100))
                pdf.cell(0, 6, footer_text, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
                
                # Generujemy PDF do pamięci
                pdf_output = io.BytesIO()
                pdf_bytes = pdf.output()  # Nowa wersja fpdf2 zwraca bytes bezpośrednio
                pdf_output.write(pdf_bytes)
                pdf_output.seek(0)
                
                st.success("✅ PDF wygenerowany pomyślnie!")
                
                # Przycisk do pobrania
                st.download_button(
                    "📄 Pobierz PDF", 
                    pdf_output.getvalue(), 
                    file_name="Lista_przeanalizowanych_procesow.pdf", 
                    mime="application/pdf"
                )
                
            except Exception as e:
                st.error(f"❌ Błąd generowania PDF: {str(e)}")
                logger.error(f"PDF_ERROR: {str(e)}")
                
                # Fallback - prosty tekst
                st.info("💡 Alternatywnie możesz skopiować dane jako tekst:")
                text_content = f"{header}\n\n"
                for i, p in enumerate(processes, 1):
                    text_content += f"{i}. {p.get('title','')}\n"
                    text_content += f"Opis: {p.get('description','')[:200]}...\n"
                    text_content += f"Analiza AI: {p.get('ai_analysis','')[:200]}...\n\n"
                text_content += f"\n{footer}"
                
                st.text_area("Zawartość raportu:", text_content, height=300)
    
    with col2:
        # Uproszczona sekcja kopiowania do schowka - tylko przyciski
        text_to_copy = generate_text_content()
        
        # Przycisk do pokazania tekstu
        if st.button("📋 Pokaż tekst do skopiowania", help="Wyświetl pełny tekst raportu"):
            # CSS do kontroli szerokości pola tekstowego
            st.markdown("""
            <style>
            .stTextArea > div > div > textarea {
                font-family: 'Source Code Pro', monospace;
                font-size: 12px;
                line-height: 1.4;
                white-space: pre-wrap;
                word-wrap: break-word;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Pole tekstowe z pełnym tekstem - bez dodatkowych instrukcji
            st.text_area(
                "Tekst raportu:",
                text_to_copy,
                height=400,
                key="copy_text_area"
            )
        
        # Przycisk pobierania jako plik tekstowy - bez nagłówka
        st.download_button(
            "📄 Pobierz jako .txt",
            text_to_copy,
            file_name="Lista_przeanalizowanych_procesow.txt",
            mime="text/plain"
        )

def initialize_database():
    """Inicjalizuje bazę danych, jeśli tabele nie istnieją"""
    try:
        logger.info("DB_INIT: Sprawdzanie i inicjalizacja bazy danych")
        
        # Sprawdź czy tabela processes istnieje
        # Uwaga: to jest bardzo uproszczone sprawdzenie, w prawdziwym środowisku
        # powinno się użyć bardziej zaawansowanych metod
        try:
            supabase.table('processes').select('id').limit(1).execute()
            logger.info("DB_INIT: Tabela 'processes' już istnieje")
        except Exception as e:
            if "relation" in str(e) and "does not exist" in str(e):
                logger.warning("DB_INIT: Tabela 'processes' nie istnieje, tworzę...")
                
                # SQL do utworzenia tabeli
                sql = """
                CREATE TABLE IF NOT EXISTS processes (
                    id BIGSERIAL PRIMARY KEY,
                    user_email TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    ai_analysis TEXT,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
                
                -- Dodaj Row Level Security dla prywatności danych
                ALTER TABLE processes ENABLE ROW LEVEL SECURITY;
                
                -- Polityka - użytkownicy widzą tylko swoje procesy
                CREATE POLICY IF NOT EXISTS "Users manage own" ON processes 
                FOR ALL USING (auth.email() = user_email);
                """
                
                # Wykonaj SQL (w prawdziwym środowisku powinno się używać migracji)
                supabase.sql(sql).execute()
                logger.info("DB_INIT: Utworzono tabelę 'processes' z Row Level Security")
            else:
                raise e
                
        return True
        
    except Exception as e:
        logger.error(f"DB_INIT: Błąd inicjalizacji bazy danych: {str(e)}")
        return False

# MAIN APP
def main():
    # Inicjalizacja bazy danych
    initialize_database()
    
    # Routing
    if not st.session_state.user:
        show_login()
    else:
        show_dashboard()

if __name__ == "__main__":
    main()