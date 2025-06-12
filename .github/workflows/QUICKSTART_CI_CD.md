# Plik: QUICKSTART_CI_CD.md

# 🚀 SmartFlowAI CI/CD - Quickstart (5 minut)

## ⚡ Szybki Setup CI/CD

### 1. **Skopiuj pliki CI/CD** (2 minuty)
```bash
# Utwórz strukturę
mkdir -p .github/workflows

# Skopiuj pliki CI/CD (gotowe w artifacts powyżej):
# - .github/workflows/ci.yml
# - .github/workflows/pr.yml  
# - .gitignore
```

### 2. **Dodaj Secrets w GitHub** (2 minuty)
W swoim repo → Settings → Secrets and variables → Actions:

```
OPENAI_API_KEY = sk-twój_openai_klucz
SUPABASE_URL = https://twój-projekt.supabase.co
SUPABASE_ANON_KEY = twój_anon_key_z_supabase
```

### 3. **Test CI/CD** (1 minuta)
```bash
# Commit wszystko
git add .
git commit -m "feat: add CI/CD pipeline"
git push origin main

# Sprawdź w GitHub → Actions tab
# Powinieneś zobaczyć uruchomiony workflow! ✅
```

## 🎯 **Co się dzieje automatycznie:**

### **Na każdy commit:**
- ✅ Testy (pytest)
- ✅ Formatowanie (black)
- ✅ Linting (flake8)
- ✅ Security scan

### **Na push do main:**
- ✅ Wszystko powyżej +
- ✅ Deploy notification
- ✅ Gotowość do Streamlit Cloud deploy

## 🔧 **Troubleshooting**

### ❌ **CI fails:**
```bash
# Sprawdź lokalnie
black .
flake8 .
pytest test_app.py

# Jeśli OK, sprawdź secrets w GitHub
```

### ❌ **Tests fail:**
```bash
# Sprawdź czy masz poprawne zmienne
cat .env.example

# Sprawdź czy baza działa
# Test connection w Supabase dashboard
```

## ✅ **Ready for 10xDevs!**

Teraz masz **wszystkie wymagania kursu 10xDevs:**

1. ✅ **Auth** (Supabase)
2. ✅ **Logika biznesowa** (ChatGPT-4o)  
3. ✅ **CRUD** (procesy)
4. ✅ **Testy** (pytest)
5. ✅ **CI/CD** (GitHub Actions) 🎉

**Śmiało wysyłaj na zaliczenie!** 🚀

### 📝 **Formularz zaliczeniowy:**
https://airtable.com/appJmaxL3gbDV0Qcv/pagLn96rJGZklZ0A4/form

---

*SmartFlowAI - From 0 to Production in 2 days!* ⚡