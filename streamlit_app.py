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
import tempfile

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
    
    # Pokaż poprawną informację o procesach
    col_info, col_refresh = st.columns([4, 1])
    with col_info:
        st.info(f"📊 Znaleziono {len(valid_processes)} przeanalizowanych procesów dla użytkownika: {st.session_state.user}")
    with col_refresh:
        if len(valid_processes) > 0:
            st.caption("💡 Dodałeś nowy proces? Kliknij 🔄 Odśwież")
    
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
                st.write("**Opis:**")
                st.write(process.get('description', 'Brak opisu'))
                
                st.write("**Analiza AI:**")
                st.write(process.get('ai_analysis', 'Brak analizy'))
                
                if st.button(f"🗑️ Usuń", key=f"del_{process['id']}"):
                    if delete_process(process['id']):
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
        st.write(f"**Nazwa:** {st.session_state.last_title}")
        st.write(f"**Opis:** {st.session_state.last_description}")
        
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
            
            if st.form_submit_button("🤖 Analizuj przez AI", type="primary"):
                if not title or not description:
                    st.error("Wypełnij wszystkie pola!")
                elif len(description) < 20:
                    st.error("Opis musi mieć co najmniej 20 znaków")
                else:
                    # Log dane z formularza
                    logger.info(f"FORM_SUBMIT: Dane z formularza - Title: '{title}', Desc: '{description[:50]}...'")
                    
                    with st.spinner("Analizuję przez ChatGPT-4o..."):
                        # Analiza AI
                        ai_analysis = analyze_with_ai(title, description)
                        
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

    # Podgląd danych do PDF
    st.markdown("### Podgląd danych do PDF:")
    for p in processes:
        st.markdown(f"**{p.get('title','')}:** {p.get('description','')}\n\n**Analiza AI:** {p.get('ai_analysis','')}\n---")

    if st.button("Generuj PDF", type="primary"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=14)
        pdf.multi_cell(0, 10, header)
        pdf.ln(5)
        for i, p in enumerate(processes, 1):
            pdf.set_font("Arial", style="B", size=12)
            pdf.cell(0, 10, f"{i}. {p.get('title','')}", ln=1)
            pdf.set_font("Arial", size=11)
            pdf.multi_cell(0, 8, f"Opis: {p.get('description','')}")
            pdf.multi_cell(0, 8, f"Analiza AI: {p.get('ai_analysis','')}")
            pdf.ln(2)
        pdf.set_font("Arial", size=10)
        pdf.ln(5)
        pdf.cell(0, 10, footer, ln=1, align='C')
        # Zapisz PDF do pliku tymczasowego
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            pdf.output(tmp.name)
            tmp.seek(0)
            st.success("PDF wygenerowany!")
            with open(tmp.name, "rb") as f:
                st.download_button("Pobierz PDF", f, file_name="zestawienie_procesow.pdf", mime="application/pdf")

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