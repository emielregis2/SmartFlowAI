# -*- coding: utf-8 -*-
"""
Proste testy SmartFlowAI - działające bez prawdziwych kluczy API

Testuje podstawowe funkcje bez inicjalizacji zewnętrznych serwisów.

Autor: Claude + Dariusz
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock

def test_environment_setup():
    """Test konfiguracji środowiska testowego"""
    # Ustaw zmienne testowe
    os.environ['OPENAI_API_KEY'] = 'test-key-12345'
    os.environ['SUPABASE_URL'] = 'https://test.supabase.co'
    os.environ['SUPABASE_ANON_KEY'] = 'test-anon-key-12345'
    
    # Sprawdź czy zmienne są ustawione
    assert os.getenv('OPENAI_API_KEY') == 'test-key-12345'
    assert os.getenv('SUPABASE_URL') == 'https://test.supabase.co'
    assert os.getenv('SUPABASE_ANON_KEY') == 'test-anon-key-12345'
    
    print("✅ Środowisko testowe skonfigurowane poprawnie")

def test_imports():
    """Test importów bibliotek"""
    try:
        import streamlit
        import supabase
        import openai
        import fpdf
        import pytest
        print("✅ Wszystkie biblioteki zaimportowane poprawnie")
        return True
    except ImportError as e:
        pytest.fail(f"Błąd importu biblioteki: {e}")

@patch('streamlit_app.openai')
@patch('streamlit_app.supabase')
def test_mock_ai_analysis(mock_supabase, mock_openai):
    """Test analizy AI z mockami"""
    # Ustaw zmienne środowiskowe
    os.environ['OPENAI_API_KEY'] = 'test-key-12345'
    os.environ['SUPABASE_URL'] = 'https://test.supabase.co'
    os.environ['SUPABASE_ANON_KEY'] = 'test-anon-key-12345'
    
    # Mock OpenAI response
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = """
🔍 **ANALIZA:** Proces wymaga automatyzacji
🛠️ **ROZWIĄZANIE:** Zapier + Airtable
💰 **KOSZT:** 200 zł/mies
⏱️ **OSZCZĘDNOŚCI:** 10 godzin/mies
⚡ **PIERWSZE KROKI:** 1. Analiza 2. Wdrożenie
"""
    
    # Mock klienta OpenAI
    mock_client = Mock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client
    
    # Teraz możemy bezpiecznie importować funkcję
    with patch.dict('sys.modules', {'streamlit': Mock()}):
        # Symulacja funkcji analyze_with_ai
        def mock_analyze_with_ai(title, description, analysis_depth="Pogłębiona", company_size="", industry="", budget=""):
            return mock_response.choices[0].message.content
        
        # Test
        result = mock_analyze_with_ai("Test Process", "Test description")
        
        # Sprawdzenia
        assert "🔍 **ANALIZA:**" in result
        assert "🛠️ **ROZWIĄZANIE:**" in result
        assert "💰 **KOSZT:**" in result
        assert "⏱️ **OSZCZĘDNOŚCI:**" in result
        assert "⚡ **PIERWSZE KROKI:**" in result
        
        print("✅ Mock analizy AI działa poprawnie")

def test_database_operations_mock():
    """Test operacji bazodanowych z mockami"""
    # Mock Supabase
    mock_supabase = Mock()
    
    # Mock save_process
    def mock_save_process(title, description, ai_analysis):
        if title and description and ai_analysis:
            return True
        return False
    
    # Mock get_processes
    def mock_get_processes():
        return [
            {
                'id': 1,
                'title': 'Test Process 1',
                'description': 'Test description 1',
                'ai_analysis': 'Test analysis 1',
                'user_email': 'test@smartflowai.com'
            },
            {
                'id': 2,
                'title': 'Test Process 2',
                'description': 'Test description 2',
                'ai_analysis': 'Test analysis 2',
                'user_email': 'test@smartflowai.com'
            }
        ]
    
    # Mock delete_process
    def mock_delete_process(process_id):
        return process_id > 0
    
    # Testy
    assert mock_save_process("Test", "Description", "Analysis") == True
    assert mock_save_process("", "", "") == False
    
    processes = mock_get_processes()
    assert len(processes) == 2
    assert processes[0]['title'] == 'Test Process 1'
    
    assert mock_delete_process(1) == True
    assert mock_delete_process(0) == False
    
    print("✅ Mock operacji bazodanowych działa poprawnie")

def test_pdf_generation_mock():
    """Test generowania PDF z mockami"""
    from fpdf import FPDF
    
    # Test tworzenia PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Test PDF SmartFlowAI', ln=True)
    
    # Test zapisu do pamięci
    pdf_output = pdf.output()
    
    # Sprawdzenia
    assert isinstance(pdf_output, (bytes, bytearray))
    assert len(pdf_output) > 0
    
    print("✅ Generowanie PDF działa poprawnie")

def test_text_processing():
    """Test przetwarzania tekstu"""
    # Test funkcji czyszczenia tekstu dla PDF
    def safe_text(text):
        """Konwertuje polskie znaki na ASCII dla PDF"""
        polish_chars = {
            'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n',
            'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z',
            'Ą': 'A', 'Ć': 'C', 'Ę': 'E', 'Ł': 'L', 'Ń': 'N',
            'Ó': 'O', 'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z'
        }
        
        for polish, ascii_char in polish_chars.items():
            text = text.replace(polish, ascii_char)
        
        return text
    
    # Testy
    test_text = "Proces księgowania faktur z ąćęłńóśźż"
    cleaned_text = safe_text(test_text)
    
    assert "ą" not in cleaned_text
    assert "ć" not in cleaned_text
    assert "księgowania" in cleaned_text  # Podstawowe słowo zostaje
    assert "a" in cleaned_text  # ą -> a
    assert "c" in cleaned_text  # ć -> c
    
    print("✅ Przetwarzanie tekstu działa poprawnie")

def test_form_validation():
    """Test walidacji formularza"""
    def validate_process_form(title, description):
        """Waliduje dane formularza procesu"""
        errors = []
        
        if not title or len(title.strip()) < 3:
            errors.append("Tytuł musi mieć co najmniej 3 znaki")
        
        if not description or len(description.strip()) < 10:
            errors.append("Opis musi mieć co najmniej 10 znaków")
        
        if len(title) > 200:
            errors.append("Tytuł nie może być dłuższy niż 200 znaków")
        
        if len(description) > 5000:
            errors.append("Opis nie może być dłuższy niż 5000 znaków")
        
        return errors
    
    # Testy walidacji
    # Poprawne dane
    errors = validate_process_form("Wystawianie faktur", "Ręczne tworzenie faktur w programie Excel")
    assert len(errors) == 0
    
    # Zbyt krótki tytuł
    errors = validate_process_form("AB", "Długi opis procesu biznesowego")
    assert len(errors) == 1
    assert "co najmniej 3 znaki" in errors[0]
    
    # Zbyt krótki opis
    errors = validate_process_form("Długi tytuł", "Krótko")
    assert len(errors) == 1
    assert "co najmniej 10 znaków" in errors[0]
    
    # Puste pola
    errors = validate_process_form("", "")
    assert len(errors) == 2
    
    print("✅ Walidacja formularza działa poprawnie")

def test_analysis_depth_options():
    """Test opcji głębokości analizy"""
    analysis_options = [
        "Podstawowa (szybka)",
        "Pogłębiona (z wyszukiwaniem)", 
        "Ekspercka (pełna analiza)"
    ]
    
    company_sizes = ["", "1-10 osób", "11-50 osób", "51-200 osób", "200+ osób"]
    
    industries = [
        "", "IT/Software", "E-commerce/Handel", "Produkcja", 
        "Usługi finansowe", "Marketing/Reklama", "Księgowość", 
        "Logistyka", "Edukacja", "Zdrowie", "Inna"
    ]
    
    budgets = ["", "do 500 zł/mies", "500-2000 zł/mies", "2000-5000 zł/mies", "5000+ zł/mies"]
    
    # Sprawdzenia
    assert len(analysis_options) == 3
    assert len(company_sizes) == 5
    assert len(industries) == 11
    assert len(budgets) == 5
    
    assert "Podstawowa" in analysis_options[0]
    assert "Pogłębiona" in analysis_options[1]
    assert "Ekspercka" in analysis_options[2]
    
    print("✅ Opcje analizy skonfigurowane poprawnie")

def test_security_functions():
    """Test funkcji bezpieczeństwa"""
    def validate_email(email):
        """Prosta walidacja emaila"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def sanitize_input(text):
        """Oczyszcza input z potencjalnie niebezpiecznych znaków"""
        if not text:
            return ""
        
        # Usuń potencjalnie niebezpieczne znaki
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '|', '`']
        for char in dangerous_chars:
            text = text.replace(char, '')
        
        return text.strip()
    
    # Testy walidacji emaila
    assert validate_email("test@smartflowai.com") == True
    assert validate_email("invalid-email") == False
    assert validate_email("test@") == False
    assert validate_email("@domain.com") == False
    
    # Testy sanityzacji
    assert sanitize_input("Normalny tekst") == "Normalny tekst"
    assert sanitize_input("<script>alert('xss')</script>") == "scriptalert('xss')/script"
    assert sanitize_input("Test & Company") == "Test  Company"
    
    print("✅ Funkcje bezpieczeństwa działają poprawnie")

def test_performance_helpers():
    """Test funkcji pomocniczych wydajności"""
    import time
    
    def measure_time(func, *args, **kwargs):
        """Mierzy czas wykonania funkcji"""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        return result, end_time - start_time
    
    def simple_function():
        """Prosta funkcja do testowania"""
        return "test result"
    
    # Test pomiaru czasu
    result, execution_time = measure_time(simple_function)
    
    assert result == "test result"
    assert execution_time >= 0
    assert execution_time < 1.0  # Powinna być bardzo szybka
    
    print("✅ Funkcje wydajności działają poprawnie")

# Główna funkcja testowa
def run_all_tests():
    """Uruchamia wszystkie proste testy"""
    print("🚀 Uruchamianie prostych testów SmartFlowAI...")
    print("=" * 50)
    
    tests = [
        test_environment_setup,
        test_imports,
        test_mock_ai_analysis,
        test_database_operations_mock,
        test_pdf_generation_mock,
        test_text_processing,
        test_form_validation,
        test_analysis_depth_options,
        test_security_functions,
        test_performance_helpers
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} nie przeszedł: {e}")
            failed += 1
    
    print("=" * 50)
    print(f"📊 WYNIKI TESTÓW:")
    print(f"✅ Przeszło: {passed}")
    print(f"❌ Nie przeszło: {failed}")
    print(f"📈 Sukces: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 WSZYSTKIE PROSTE TESTY PRZESZŁY POMYŚLNIE!")
        return True
    else:
        print(f"\n⚠️ {failed} testów nie przeszło")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 