# Plik: streamlit_app.py
# streamlit_app.py - Ultra-prosta aplikacja SmartFlowAI (2 dni MVP)

import streamlit as st
import openai
import os
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

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
        result = supabase.table('processes').insert({
            'user_email': st.session_state.user,
            'title': title,
            'description': description,
            'ai_analysis': ai_analysis,
            'created_at': datetime.now().isoformat()
        }).execute()
        return True
    except Exception as e:
        st.error(f"Błąd zapisu: {str(e)}")
        return False

def get_processes():
    """Pobiera procesy użytkownika"""
    try:
        result = supabase.table('processes').select('*').eq('user_email', st.session_state.user).order('created_at', desc=True).execute()
        return result.data
    except Exception as e:
        st.error(f"Błąd: {str(e)}")
        return []

def delete_process(process_id: int):
    """Usuwa proces"""
    try:
        supabase.table('processes').delete().eq('id', process_id).execute()
        return True
    except Exception as e:
        st.error(f"Błąd usuwania: {str(e)}")
        return False

# STRONY APLIKACJI

def show_login():
    """Strona logowania"""
    st.title("SmartFlowAI")
    st.subheader("Zaloguj się")
    
    # Informacja o kontach testowych
    with st.expander("👥 Konta testowe", expanded=False):
        st.info("""
        **Dostępne konta testowe:**
        
        📧 **test@smartflowai.com** / test123
        📧 **test@smatflow.pl** / test123456
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
                    except:
                        # Fallback - użytkownicy testowi
                        test_users = {
                            "test@smartflowai.com": "test123",
                            "test@smatflow.pl": "test123456"
                        }
                        
                        if email in test_users and test_users[email] == password:
                            st.session_state.user = email
                            st.success(f"✅ Zalogowano jako {email}")
                            st.rerun()
                        else:
                            st.error("❌ Błędne dane logowania")
                else:
                    st.error("Wypełnij wszystkie pola")

def show_dashboard():
    """Dashboard główny"""
    st.title("SmartFlowAI Dashboard")
    st.write(f"Zalogowany: {st.session_state.user}")
    
    if st.button("Wyloguj"):
        st.session_state.user = None
        st.rerun()
    
    # Menu
    tab1, tab2 = st.tabs(["📋 Moje Procesy", "➕ Nowy Proces"])
    
    with tab1:
        show_processes_list()
    
    with tab2:
        show_new_process_form()

def show_processes_list():
    """Lista procesów"""
    st.subheader("Moje Procesy")
    
    processes = get_processes()
    
    if not processes:
        st.info("Brak procesów. Dodaj pierwszy proces w zakładce 'Nowy Proces'!")
        return
    
    for process in processes:
        with st.expander(f"{process['title']} ({process['created_at'][:10]})", expanded=False):
            st.write("**Opis:**")
            st.write(process['description'])
            
            st.write("**Analiza AI:**")
            st.write(process.get('ai_analysis', 'Brak analizy'))
            
            if st.button(f"🗑️ Usuń", key=f"del_{process['id']}"):
                if delete_process(process['id']):
                    st.success("Proces usunięty!")
                    st.rerun()

def show_new_process_form():
    """Formularz nowego procesu"""
    st.subheader("Dodaj Nowy Proces")
    
    with st.form("new_process"):
        title = st.text_input("Nazwa procesu *", placeholder="np. Wystawianie faktur")
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
                with st.spinner("Analizuję przez ChatGPT-4o..."):
                    # Analiza AI
                    ai_analysis = analyze_with_ai(title, description)
                    
                    # Wyświetl wyniki
                    st.success("Analiza zakończona!")
                    st.subheader("Wyniki analizy:")
                    st.write(ai_analysis)
                    
                    # Zapisz do bazy
                    if save_process(title, description, ai_analysis):
                        st.success("Proces zapisany w bazie danych!")
                        st.balloons()
                        # Odśwież aplikację żeby pokazać nowy proces w liście
                        st.rerun()
                    else:
                        st.error("Błąd zapisu do bazy danych")

# MAIN APP
def main():
    if not st.session_state.user:
        show_login()
    else:
        show_dashboard()

if __name__ == "__main__":
    main()