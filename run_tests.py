# -*- coding: utf-8 -*-
"""
Test Runner dla SmartFlowAI - Wersja Produkcyjna

Uruchamia wszystkie testy:
- Unit testy
- Testy integracyjne  
- Testy E2E
- Testy wydajności

Autor: Claude + Dariusz
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def setup_test_environment():
    """Konfiguruje środowisko testowe"""
    print("🔧 Konfiguracja środowiska testowego...")
    
    # Ustaw zmienne środowiskowe dla testów
    test_env = {
        'OPENAI_API_KEY': 'test-openai-key-12345',
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_ANON_KEY': 'test-supabase-anon-key-12345',
        'PYTHONPATH': str(Path(__file__).parent)
    }
    
    for key, value in test_env.items():
        os.environ[key] = value
    
    print("✅ Środowisko testowe skonfigurowane")

def run_unit_tests():
    """Uruchamia testy jednostkowe"""
    print("\n🧪 Uruchamianie testów jednostkowych...")
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            'test_comprehensive.py',
            '-v',
            '--tb=short',
            '--durations=10'
        ], capture_output=True, text=True, timeout=300)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print("✅ Testy jednostkowe przeszły pomyślnie")
            return True
        else:
            print("❌ Testy jednostkowe nie przeszły")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Timeout - testy jednostkowe trwały zbyt długo")
        return False
    except Exception as e:
        print(f"💥 Błąd podczas testów jednostkowych: {e}")
        return False

def run_enhanced_tests():
    """Uruchamia testy ulepszonych funkcji"""
    print("\n🤖 Uruchamianie testów ulepszonych funkcji AI...")
    
    try:
        result = subprocess.run([
            sys.executable, 'test_enhanced_analysis.py'
        ], capture_output=True, text=True, timeout=120)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print("✅ Testy ulepszonych funkcji przeszły pomyślnie")
            return True
        else:
            print("❌ Testy ulepszonych funkcji nie przeszły")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Timeout - testy ulepszonych funkcji trwały zbyt długo")
        return False
    except Exception as e:
        print(f"💥 Błąd podczas testów ulepszonych funkcji: {e}")
        return False

def run_utf8_tests():
    """Uruchamia testy kodowania UTF-8"""
    print("\n🔤 Uruchamianie testów kodowania UTF-8...")
    
    try:
        result = subprocess.run([
            sys.executable, 'test_utf8.py'
        ], capture_output=True, text=True, timeout=60)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print("✅ Testy kodowania UTF-8 przeszły pomyślnie")
            return True
        else:
            print("❌ Testy kodowania UTF-8 nie przeszły")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Timeout - testy UTF-8 trwały zbyt długo")
        return False
    except Exception as e:
        print(f"💥 Błąd podczas testów UTF-8: {e}")
        return False

def run_basic_tests():
    """Uruchamia podstawowe testy"""
    print("\n📋 Uruchamianie podstawowych testów...")
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            'test_app.py',
            '-v',
            '--tb=short'
        ], capture_output=True, text=True, timeout=180)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print("✅ Podstawowe testy przeszły pomyślnie")
            return True
        else:
            print("❌ Podstawowe testy nie przeszły")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Timeout - podstawowe testy trwały zbyt długo")
        return False
    except Exception as e:
        print(f"💥 Błąd podczas podstawowych testów: {e}")
        return False

def run_e2e_tests():
    """Uruchamia testy E2E (opcjonalne)"""
    print("\n🌐 Uruchamianie testów End-to-End...")
    
    try:
        # Sprawdź czy streamlit.testing jest dostępne
        import streamlit.testing
        
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            'test_e2e.py',
            '-v',
            '--tb=short',
            '-x'  # Stop on first failure
        ], capture_output=True, text=True, timeout=600)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print("✅ Testy E2E przeszły pomyślnie")
            return True
        else:
            print("❌ Testy E2E nie przeszły")
            return False
            
    except ImportError:
        print("⚠️ Streamlit testing nie jest dostępne - pomijam testy E2E")
        return True
    except subprocess.TimeoutExpired:
        print("⏰ Timeout - testy E2E trwały zbyt długo")
        return False
    except Exception as e:
        print(f"💥 Błąd podczas testów E2E: {e}")
        return False

def check_code_quality():
    """Sprawdza jakość kodu"""
    print("\n🔍 Sprawdzanie jakości kodu...")
    
    # Sprawdź składnię
    try:
        result = subprocess.run([
            sys.executable, '-m', 'py_compile', 'streamlit_app.py'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Składnia kodu poprawna")
        else:
            print("❌ Błędy składni:", result.stderr)
            return False
    except Exception as e:
        print(f"💥 Błąd sprawdzania składni: {e}")
        return False
    
    # Sprawdź importy
    try:
        import streamlit_app
        print("✅ Importy działają poprawnie")
    except Exception as e:
        print(f"❌ Błąd importów: {e}")
        return False
    
    return True

def generate_test_report(results):
    """Generuje raport z testów"""
    print("\n📊 RAPORT Z TESTÓW")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    failed_tests = total_tests - passed_tests
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<30} {status}")
    
    print("=" * 50)
    print(f"Łącznie testów: {total_tests}")
    print(f"Przeszło: {passed_tests}")
    print(f"Nie przeszło: {failed_tests}")
    print(f"Sukces: {passed_tests/total_tests*100:.1f}%")
    
    if failed_tests == 0:
        print("\n🎉 WSZYSTKIE TESTY PRZESZŁY POMYŚLNIE!")
        print("🚀 Aplikacja gotowa do wdrożenia produkcyjnego")
    else:
        print(f"\n⚠️ {failed_tests} testów nie przeszło")
        print("🔧 Wymagane poprawki przed wdrożeniem")
    
    return failed_tests == 0

def main():
    """Główna funkcja test runnera"""
    print("🚀 SmartFlowAI Test Runner - Wersja Produkcyjna")
    print("=" * 60)
    
    start_time = time.time()
    
    # Setup
    setup_test_environment()
    
    # Sprawdź jakość kodu
    if not check_code_quality():
        print("❌ Problemy z jakością kodu - przerywam testy")
        return False
    
    # Uruchom wszystkie testy
    results = {}
    
    results["Testy podstawowe"] = run_basic_tests()
    results["Testy jednostkowe"] = run_unit_tests()
    results["Testy ulepszonych funkcji"] = run_enhanced_tests()
    results["Testy kodowania UTF-8"] = run_utf8_tests()
    results["Testy E2E"] = run_e2e_tests()
    
    # Generuj raport
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"\n⏱️ Całkowity czas testów: {total_time:.2f} sekund")
    
    success = generate_test_report(results)
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Testy przerwane przez użytkownika")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Nieoczekiwany błąd: {e}")
        sys.exit(1) 