# Plik: quick_start.py
#!/usr/bin/env python3
# quick_start.py - Skrypt szybkiego startu dla SmartFlowAI

"""
SmartFlowAI Quick Start Script
=============================

Ten skrypt pomoże Ci szybko skonfigurować i uruchomić SmartFlowAI.

Użycie:
    python quick_start.py [opcja]

Opcje:
    install     - Instaluje zależności
    setup       - Konfiguruje zmienne środowiskowe
    test        - Uruchamia testy
    run         - Uruchamia aplikację
    deploy      - Przygotowuje do wdrożenia
    all         - Wykonuje wszystkie kroki
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_header(text):
    """Wyświetla nagłówek"""
    print(f"\n{'='*50}")
    print(f"SmartFlowAI: {text}")
    print(f"{'='*50}")

def print_step(step, description):
    """Wyświetla krok"""
    print(f"\nKrok {step}: {description}")

def run_command(command, description=""):
    """Uruchamia komendę i obsługuje błędy"""
    if description:
        print(f"   {description}...")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(f"   {description} zakończono pomyślnie")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   Błąd: {e}")
        if e.stdout:
            print(f"   Output: {e.stdout}")
        if e.stderr:
            print(f"   Error: {e.stderr}")
        return False

def check_python_version():
    """Sprawdza wersję Pythona"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("Wymagany Python 3.8 lub wyższy!")
        print(f"   Aktualna wersja: {version.major}.{version.minor}.{version.micro}")
        sys.exit(1)
    else:
        print(f"Python {version.major}.{version.minor}.{version.micro} - OK")

def install_dependencies():
    """Instaluje zależności"""
    print_step(1, "Instalacja zależności")
    
    if not shutil.which("pip"):
        print("pip nie jest zainstalowany!")
        return False
    
    commands = [
        ("pip install --upgrade pip", "Aktualizacja pip"),
        ("pip install -r requirements.txt", "Instalacja zależności z requirements.txt"),
        ("pip install pytest pytest-cov black flake8", "Instalacja narzędzi deweloperskich")
    ]
    
    for command, desc in commands:
        if not run_command(command, desc):
            return False
    
    print("Wszystkie zależności zainstalowane!")
    return True

def setup_environment():
    """Konfiguruje zmienne środowiskowe"""
    print_step(2, "Konfiguracja środowiska")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("   Plik .env już istnieje")
        response = input("   Czy chcesz go nadpisać? (y/N): ")
        if response.lower() != 'y':
            print("   Pomijanie konfiguracji środowiska")
            return True
    
    if not env_example.exists():
        print("   Brak pliku .env.example!")
        return False
    
    shutil.copy(env_example, env_file)
    print("   Utworzono plik .env z przykładu")
    
    print("\n   Teraz musisz skonfigurować zmienne środowiskowe:")
    print("   1. Otwórz plik .env w edytorze")
    print("   2. Wypełnij swoje klucze API:")
    print("      - SUPABASE_URL (z https://app.supabase.com)")
    print("      - SUPABASE_ANON_KEY (z ustawień API)")
    print("      - OPENAI_API_KEY (z https://platform.openai.com/api-keys)")
    
    input("\n   Naciśnij Enter gdy skonfigurujesz zmienne...")
    
    try:
        with open(env_file, 'r') as f:
            content = f.read()
            if "twoj-projekt" in content or "sk-twoj" in content:
                print("   Wygląda na to, że zmienne nie zostały skonfigurowane")
                print("   Aplikacja może nie działać poprawnie")
            else:
                print("   Zmienne środowiskowe skonfigurowane")
    except Exception as e:
        print(f"   Błąd sprawdzania konfiguracji: {e}")
        return False
    
    return True

def run_tests():
    """Uruchamia testy"""
    print_step(3, "Uruchamianie testów")
    
    if not Path("test_app.py").exists():
        print("   Brak pliku test_app.py!")
        return False
    
    commands = [
        ("python -m pytest test_app.py -v", "Uruchamianie testów podstawowych"),
        ("python -m pytest test_app.py --cov=streamlit_app", "Uruchamianie testów z pokryciem kodu")
    ]
    
    for command, desc in commands:
        if not run_command(command, desc):
            print("   Niektóre testy mogły nie przejść - sprawdź konfigurację")
            return False
    
    print("   Wszystkie testy przeszły pomyślnie!")
    return True

def run_app():
    """Uruchamia aplikację"""
    print_step(4, "Uruchamianie aplikacji")
    
    if not Path("streamlit_app.py").exists():
        print("   Brak pliku streamlit_app.py!")
        return False
    
    print("   Uruchamianie SmartFlowAI...")
    print("   Aplikacja będzie dostępna pod adresem: http://localhost:8501")
    print("   Aby zatrzymać aplikację, naciśnij Ctrl+C")
    print("\n" + "="*50)
    
    try:
        subprocess.run("streamlit run streamlit_app.py", shell=True, check=True)
    except KeyboardInterrupt:
        print("\n   Aplikacja zatrzymana")
    except subprocess.CalledProcessError as e:
        print(f"   Błąd uruchamiania aplikacji: {e}")
        return False
    
    return True

def prepare_deployment():
    """Przygotowuje do wdrożenia"""
    print_step(5, "Przygotowanie do wdrożenia")
    
    required_files = [
        "streamlit_app.py",
        "requirements.txt", 
        "README.md",
        "test_app.py",
        ".env.example"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"   Brakuje plików: {', '.join(missing_files)}")
        return False
    
    if not Path(".git").exists():
        print("   Brak repozytorium git")
        response = input("   Czy chcesz zainicjalizować git? (Y/n): ")
        if response.lower() != 'n':
            commands = [
                ("git init", "Inicjalizacja git"),
                ("git