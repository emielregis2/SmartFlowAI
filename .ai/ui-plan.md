# Plik: ui-plan.md

# SmartFlowAI - Prosty plan UI (2 dni MVP)

## Przegląd

Ultra-prosty UI w 1 pliku streamlit_app.py. Brak komponenetów, folderów, CSS. 
Tylko podstawowe Streamlit widgets.

## Architektura UI (minimalna)

### Założenia:
- **1 plik:** streamlit_app.py (wszystko tutaj)
- **3 funkcje:** show_login(), show_dashboard(), show_new_process_form()
- **Session state:** tylko `st.session_state.user`
- **Routing:** if/else na user login status

### Flow aplikacji:
```
Login Page → Dashboard → [New Process | Process List]
     ↑         ↓              ↓
  Logout    Processes    AI Analysis + Save
```

## Struktura UI

### 1. Login Page (show_login)
```python
def show_login():
    st.title("SmartFlowAI")
    with st.form("login"):
        email = st.text_input("Email")
        password = st.text_input("Hasło", type="password") 
        if st.form_submit_button("Zaloguj"):
            # auth logic
```

**Komponenty:**
- Title
- Email input
- Password input  
- Submit button

### 2. Dashboard (show_dashboard)
```python
def show_dashboard():
    st.title("SmartFlowAI Dashboard")
    
    tab1, tab2 = st.tabs(["📋 Moje Procesy", "➕ Nowy Proces"])
    
    with tab1:
        show_processes_list()
    
    with tab2:
        show_new_process_form()
```

**Komponenty:**
- Title z user email
- Logout button
- Tabs (2 zakładki)

### 3. Process List (show_processes_list)
```python
def show_processes_list():
    for process in processes:
        with st.expander(f"{process['title']}"):
            st.write(process['description'])
            st.write(process['ai_analysis'])
            if st.button("🗑️ Usuń"):
                delete_process(process['id'])
```

**Komponenty:**
- Loop przez procesy
- Expander dla każdego procesu
- Delete button

### 4. New Process Form (show_new_process_form)
```python
def show_new_process_form():
    with st.form("new_process"):
        title = st.text_input("Nazwa procesu")
        description = st.text_area("Opis procesu")
        
        if st.form_submit_button("🤖 Analizuj przez AI"):
            # AI analysis + save
```

**Komponenty:**
- Text input (title)
- Text area (description)  
- Submit button
- Spinner podczas AI analysis
- Success message

## Session State (ultra-prosty)

```python
# Tylko 1 zmienna!
if 'user' not in st.session_state:
    st.session_state.user = None

# Użycie
if st.session_state.user:
    show_dashboard()
else:
    show_login()
```

**To wszystko!** Żadnych kompleksowych state management.

## Routing (if/else)

```python
def main():
    if not st.session_state.user:
        show_login()    # Nie zalogowany
    else:
        show_dashboard() # Zalogowany

if __name__ == "__main__":
    main()
```

**Prosty routing** - 1 if statement.

## Error Handling (minimalne)

### User feedback:
```python
# Success
st.success("Proces zapisany!")
st.balloons()

# Error  
st.error("Wypełnij wszystkie pola!")

# Info
st.info("Brak procesów. Dodaj pierwszy!")

# Warning
st.warning("Opis zbyt krótki")
```

### Loading states:
```python
with st.spinner("Analizuję przez ChatGPT-4o..."):
    ai_analysis = analyze_with_ai(title, description)
```

## Styling (zero custom CSS)

### Konfiguracja strony:
```python
st.set_page_config(
    page_title="SmartFlowAI",
    page_icon="🤖"
)
```

### Używamy domyślny Streamlit theme:
- ✅ Responsive design (automatyczny)
- ✅ Dark/light mode (automatyczny)  
- ✅ Mobile friendly (automatyczny)
- ✅ Accessibility (automatyczny)

**Brak custom CSS!** Streamlit domyślnie wygląda dobrze.

## Komponenty Streamlit

### Używane widgets:
- `st.title()` - nagłówki
- `st.text_input()` - pola tekstowe
- `st.text_area()` - większe pola tekstowe
- `st.form()` - formularze
- `st.form_submit_button()` - przyciski submit
- `st.button()` - zwykłe przyciski
- `st.tabs()` - zakładki
- `st.expander()` - rozwijane sekcje
- `st.write()` - wyświetlanie tekstu
- `st.spinner()` - loading
- `st.success/error/info()` - komunikaty

### NIE używane (za skomplikowane):
- `st.sidebar` - niepotrzebne
- `st.columns` - za skomplikowane
- `st.metric` - nice to have
- `st.chart` - brak wykresów
- `st.file_uploader` - brak plików

## Layout (prosty)

### Mobile-first:
```
[Title]
[Login Form]
[Button]
```

### Desktop:
```
[Title]           
[Tab 1] [Tab 2]
[Content Area]
[Action Buttons]
```

**Responsive automatycznie** przez Streamlit.

## User Experience Flow

### 1. First Visit:
```
Landing Page → Login Form → Test Credentials → Dashboard
```

### 2. Returning User:
```
Auto-login → Dashboard → View Processes
```

### 3. Adding Process:
```
New Process Tab → Fill Form → AI Analysis → Results → Save
```

### 4. Managing Processes:
```
Process List → Expand → View Details → Delete (optional)
```

## Testowanie UI

### Manual testing:
1. **Login flow:** Test credentials work
2. **Form validation:** Empty fields show errors
3. **AI integration:** Analysis appears correctly
4. **Data persistence:** Processes save and load
5. **Mobile responsive:** Works on phone

### User testing:
- **Task:** "Dodaj nowy proces i przeanalizuj go"
- **Success criteria:** Użytkownik kończy zadanie w < 2 minuty

## Performance (zero optimization)

### Streamlit cache:
```python
@st.cache_resource
def init_supabase():
    # Connection caching
    
@st.cache_data(ttl=300)  
def get_processes():
    # Data caching (5 min)
```

**Wystarczy dla MVP!** Brak zaawansowanych optymalizacji.

## Deployment UI

### Streamlit Cloud:
- Automatyczny responsive design
- HTTPS out of the box
- Sharing URL
- Analytics dashboard

### Brak konfiguracji serwera!

## Harmonogram UI (Dzień 1)

### Godzina 1-2:
- Setup streamlit_app.py
- Basic page config
- Login form

### Godzina 3-4:
- Dashboard tabs
- Session state management
- Basic routing

### Godzina 5-6:
- Process form
- Process list
- Error handling

**UI gotowy!** Następny dzień: AI integration.

## Przykłady

### Login Page:
```
🤖 SmartFlowAI
━━━━━━━━━━━━━

Email: [test@smartflowai.com]
Hasło: [••••••••]

[Zaloguj]
```

### Dashboard:
```
🤖 SmartFlowAI Dashboard
Zalogowany: test@smartflowai.com [Wyloguj]

[📋 Moje Procesy] [➕ Nowy Proces]

▼ Wystawianie faktur (2025-06-11)
  Opis: Ręcznie tworzę faktury...
  Analiza: OCENA: 8/10, PROBLEM: ...
  [🗑️ Usuń]
```

---

**Motto:** Prostota = szybkość development! ⚡