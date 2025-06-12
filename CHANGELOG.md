# Changelog

Wszystkie istotne zmiany w projekcie SmartFlowAI będą dokumentowane w tym pliku.

Format oparty na [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
i projekt używa [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2025-06-12

### ✨ Dodane
- **Rejestracja nowych użytkowników**
  - Dodano zakładkę "📝 Rejestracja" w interfejsie logowania
  - Implementacja rejestracji przez Supabase Auth API
  - Walidacja formularza rejestracji:
    - Sprawdzanie czy wszystkie pola są wypełnione
    - Walidacja zgodności haseł
    - Minimalna długość hasła (6 znaków)
  - Automatyczne logowanie użytkownika po pomyślnej rejestracji
  - Wyświetlanie baloników (🎉) po udanej rejestracji
  - Obsługa błędów rejestracji z informatywnymi komunikatami

- **Funkcja inicjalizacji bazy danych**
  - Dodano `initialize_database()` sprawdzającą istnienie tabel
  - Automatyczne tworzenie tabeli `processes` jeśli nie istnieje
  - Konfiguracja Row Level Security (RLS) dla prywatności danych
  - Tworzenie polityk bezpieczeństwa dla użytkowników

- **Skrypt weryfikacji użytkowników**
  - Utworzono `check_user.py` do sprawdzania stanu użytkowników
  - Sprawdzanie istnienia użytkownika w systemie auth
  - Sprawdzanie procesów użytkownika w bazie danych
  - Szczegółowe raportowanie stanu użytkownika
  - Obsługa argumentów wiersza poleceń

### 🔧 Zmienione
- **Ulepszona funkcja logowania**
  - Przeprojektowano `show_login()` z zakładkami
  - Dodano lepszą obsługę błędów logowania
  - Poprawiono komunikaty błędów z większą ilością szczegółów
  - Zachowano kompatybilność z kontami testowymi

- **Poprawiona architektura aplikacji**
  - Dodano wywołanie `initialize_database()` w funkcji `main()`
  - Lepsze logowanie operacji rejestracji i inicjalizacji
  - Rozszerzone komentarze w kodzie

### 🐛 Naprawione
- Poprawiono obsługę błędów w procesie autentykacji
- Dodano fallback dla różnych typów błędów Supabase Auth
- Ulepszone logowanie błędów dla łatwiejszego debugowania

### 📚 Dokumentacja
- Dodano szczegółowe komentarze do nowych funkcji
- Rozszerzone docstringi z opisami parametrów
- Dodano przykłady użycia w `check_user.py`

### 🔒 Bezpieczeństwo
- Implementacja Row Level Security (RLS) dla nowych tabel
- Walidacja danych wejściowych w formularzu rejestracji
- Bezpieczne przechowywanie haseł przez Supabase Auth

### 🧪 Testowanie
- Dodano skrypt `check_user.py` do weryfikacji funkcjonalności
- Możliwość sprawdzania stanu dowolnego użytkownika
- Testowanie rejestracji użytkownika `dariusz.gasior@gmail.com`

## [1.0.0] - 2025-06-11

### ✨ Dodane
- Podstawowa aplikacja SmartFlowAI w Streamlit
- Integracja z Supabase jako baza danych
- Integracja z OpenAI GPT-4o do analizy procesów
- System logowania użytkowników
- Dodawanie i analizowanie procesów biznesowych
- Lista przeanalizowanych procesów
- Usuwanie procesów
- Konta testowe dla demonstracji
- Dark mode UI z custom CSS
- Logowanie do pliku `smartflow_debug.log`
- Podstawowe testy aplikacji
- Konfiguracja CI/CD z GitHub Actions
- Dokumentacja README.md

---

## Legenda

- ✨ **Dodane** - nowe funkcjonalności
- 🔧 **Zmienione** - zmiany w istniejących funkcjonalnościach  
- 🐛 **Naprawione** - poprawki błędów
- 🗑️ **Usunięte** - usunięte funkcjonalności
- 🔒 **Bezpieczeństwo** - poprawki bezpieczeństwa
- 📚 **Dokumentacja** - zmiany w dokumentacji
- 🧪 **Testowanie** - dodanie lub zmiany testów

## Kontakt

**Autor:** Dariusz Gąsior  
**Projekt:** SmartFlowAI - MVP w 2 dni  
**GitHub:** [SmartFlowAI Repository](https://github.com/emielregis2/SmartFlowAI) 