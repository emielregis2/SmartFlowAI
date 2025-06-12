# Plik: GITHUB_ACTIONS_SETUP.md

# GitHub Actions CI/CD Setup dla SmartFlowAI

## 🚀 Automatyczne CI/CD już skonfigurowane!

SmartFlowAI ma kompletny CI/CD pipeline który automatycznie:

### ✅ **Na każdy commit/PR:**
- 🧪 Uruchamia testy
- 🎨 Sprawdza formatowanie kodu (Black)
- 🔍 Analizuje jakość kodu (flake8)
- 🔒 Skanuje bezpieczeństwo
- 📊 Generuje coverage report

### ✅ **Na merge do main:**
- 🚀 Automatyczny deploy na Streamlit Cloud
- 📧 Powiadomienia o deployment

## 📋 Setup (jednorazowo)

### 1. **Dodaj Secrets w GitHub**
W repozytorium → Settings → Secrets and variables → Actions:

```
OPENAI_API_KEY = sk-twój_openai_klucz
SUPABASE_URL = https://twój-projekt.supabase.co  
SUPABASE_ANON_KEY = twój_anon_key
```

### 2. **Włącz GitHub Actions**
- Idź do zakładki "Actions" w repozytorium
- Kliknij "I understand my workflows, go ahead and enable them"

### 3. **Sprawdź czy działa**
```bash
# Zrób jakąś zmianę i commit
echo "# Test CI/CD" >> README.md
git add .
git commit -m "test: sprawdzenie CI/CD"
git push
```

### 4. **Dodaj badge do README**
```markdown
[![CI/CD](https://github.com/TWÓJ-USERNAME/smartflowai/actions/workflows/ci.yml/badge.svg)](https://github.com/TWÓJ-USERNAME/smartflowai/actions/workflows/ci.yml)
```

## 🔧 **Pliki CI/CD**

Struktura dodana do projektu:
```
.github/
├── workflows/
│   ├── ci.yml          # Główny CI/CD (testy + deploy)
│   └── pr.yml          # Sprawdzanie Pull Requestów
├── .gitignore          # Ignorowane pliki
└── GITHUB_ACTIONS_SETUP.md  # Te instrukcje
```

## 🧪 **Lokalne testowanie przed commit**

Przed push sprawdź lokalnie:
```bash
# Formatowanie kodu
black .

# Linting
flake8 .

# Testy
pytest test_app.py -v

# Wszystko naraz
black . && flake8 . && pytest test_app.py
```

## 🚨 **Troubleshooting**

### **CI fails na testach:**
- Sprawdź czy masz poprawnie ustawione secrets
- Sprawdź czy wszystkie testy przechodzą lokalnie

### **Deploy nie działa:**
- Upewnij się że pushuje na branch `main`
- Sprawdź czy Streamlit Cloud jest podłączony do repo

### **Secrets nie działają:**
- Sprawdź pisownię nazw secrets (case-sensitive)
- Sprawdź czy masz uprawnienia admin w repo

## 📱 **Deploy na Streamlit Cloud**

### Automatyczny deployment:
1. Idź na https://streamlit.io/cloud
2. Podłącz swoje GitHub repo
3. Ustaw main branch jako deployment branch
4. Dodaj swoje secrets w Streamlit Cloud
5. Każdy push na main → automatyczny deploy!

### 🔗 **Twoja aplikacja będzie dostępna pod:**
```
https://TWOJA-NAZWA-REPO-NAZWISKO.streamlit.app
```

## ✅ **Gotowe do zaliczenia kursu 10xDevs!**

Teraz masz kompletny project z:
- ✅ Auth (Supabase)
- ✅ Logika biznesowa (ChatGPT-4o)
- ✅ CRUD (procesy)
- ✅ Testy (pytest)
- ✅ **CI/CD (GitHub Actions)** 🎉

**Możesz wysyłać na zaliczenie!** 🚀