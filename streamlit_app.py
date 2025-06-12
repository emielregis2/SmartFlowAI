# Plik: streamlit_app.py
# streamlit_app.py - Ultra-prosta aplikacja SmartFlowAI (2 dni MVP)

import streamlit as st
import openai
import os
from datetime import datetime
from supabase import create_client, Client

# Konfiguracja strony
st.set_page_config(page_title="SmartFlowAI", page_icon="🤖")

# Inicjalizacja klientów
@st.cache_resource
def init_supabase():
    url = os.getenv("SUPABASE_URL") or st.secrets.get("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_ANON_KEY") or st.secrets.get("SUPABASE_ANON_KEY", "")
    return create_client(url, key)

@st.cache_resource  
def init_openai():
    api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", "")
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
                        # Fallback - do testów
                        if email == "test@smartflowai.com" and password == "test123":
                            st.session_state.user = email
                            st.rerun()
                        else:
                            st.error("Błędne dane logowania")
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