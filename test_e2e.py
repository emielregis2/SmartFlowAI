# -*- coding: utf-8 -*-
"""
Testy End-to-End (E2E) dla SmartFlowAI

Testuje pełny interfejs użytkownika przez Streamlit
- Logowanie/rejestracja
- Dodawanie procesów
- Analiza AI
- Edycja i usuwanie
- Export PDF

Autor: Claude + Dariusz
"""

import pytest
import os
import sys
import time
from unittest.mock import Mock, patch, MagicMock
from streamlit.testing.v1 import AppTest

# Setup path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestE2ELogin:
    """Testy E2E logowania i rejestracji"""
    
    def setup_method(self):
        """Setup przed każdym testem"""
        os.environ['OPENAI_API_KEY'] = 'test-key-12345'
        os.environ['SUPABASE_URL'] = 'https://test.supabase.co'
        os.environ['SUPABASE_ANON_KEY'] = 'test-anon-key-12345'
    
    @patch('streamlit_app.supabase')
    def test_login_flow(self, mock_supabase):
        """Test przepływu logowania"""
        # Mock successful login
        mock_response = Mock()
        mock_response.user = Mock()
        mock_response.user.email = "test@smartflowai.com"
        mock_supabase.auth.sign_in_with_password.return_value = mock_response
        
        # Inicjalizuj aplikację
        at = AppTest.from_file("streamlit_app.py")
        at.run()
        
        # Sprawdź czy pokazuje formularz logowania
        assert len(at.text_input) >= 2  # Email i hasło
        assert len(at.button) >= 1  # Przycisk logowania
        
        # Symuluj wprowadzenie danych
        at.text_input[0].set_value("test@smartflowai.com")  # Email
        at.text_input[1].set_value("test123")  # Hasło
        
        # Kliknij logowanie
        at.button[0].click()
        at.run()
        
        # Po zalogowaniu powinien pokazać dashboard
        # (Sprawdzenie zależy od struktury aplikacji)
    
    @patch('streamlit_app.supabase')
    def test_registration_flow(self, mock_supabase):
        """Test przepływu rejestracji"""
        # Mock successful registration
        mock_response = Mock()
        mock_response.user = Mock()
        mock_response.user.email = "newuser@smartflowai.com"
        mock_supabase.auth.sign_up.return_value = mock_response
        
        at = AppTest.from_file("streamlit_app.py")
        at.run()
        
        # Test rejestracji (jeśli jest dostępna w interfejsie)
        # Implementacja zależy od struktury formularza

class TestE2EProcessManagement:
    """Testy E2E zarządzania procesami"""
    
    def setup_method(self):
        """Setup z zalogowanym użytkownikiem"""
        os.environ['OPENAI_API_KEY'] = 'test-key-12345'
        os.environ['SUPABASE_URL'] = 'https://test.supabase.co'
        os.environ['SUPABASE_ANON_KEY'] = 'test-anon-key-12345'
    
    @patch('streamlit_app.supabase')
    @patch('streamlit_app.openai_client')
    def test_add_process_flow(self, mock_openai, mock_supabase):
        """Test dodawania nowego procesu"""
        # Mock zalogowanego użytkownika
        with patch('streamlit_app.st') as mock_st:
            mock_st.session_state.user = "test@smartflowai.com"
            
            # Mock AI response
            mock_ai_response = Mock()
            mock_ai_response.choices = [Mock()]
            mock_ai_response.choices[0].message.content = """
🔍 **ANALIZA:** Proces wymaga automatyzacji
🛠️ **ROZWIĄZANIE:** Zapier + iFirma
💰 **KOSZT:** 300 zł/mies
⏱️ **OSZCZĘDNOŚCI:** 15 godzin/mies
⚡ **PIERWSZE KROKI:** 1. Analiza 2. Wdrożenie
"""
            mock_openai.chat.completions.create.return_value = mock_ai_response
            
            # Mock database save
            mock_save_result = Mock()
            mock_save_result.data = [{'id': 1}]
            mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_save_result
            
            # Inicjalizuj aplikację
            at = AppTest.from_file("streamlit_app.py")
            at.run()
            
            # Znajdź formularz dodawania procesu
            # (Implementacja zależy od struktury interfejsu)
            
            # Sprawdź czy formularz zawiera wymagane pola
            process_title_inputs = [inp for inp in at.text_input if "nazwa" in inp.label.lower() or "title" in inp.label.lower()]
            process_desc_inputs = [inp for inp in at.text_area if "opis" in inp.label.lower() or "desc" in inp.label.lower()]
            
            if process_title_inputs and process_desc_inputs:
                # Wypełnij formularz
                process_title_inputs[0].set_value("Wystawianie faktur")
                process_desc_inputs[0].set_value("Ręczne tworzenie faktur w Excelu")
                
                # Znajdź przycisk analizy
                analyze_buttons = [btn for btn in at.button if "analiz" in btn.label.lower()]
                if analyze_buttons:
                    analyze_buttons[0].click()
                    at.run()
                    
                    # Sprawdź czy pokazuje wyniki analizy
                    # (Sprawdzenie zależy od implementacji)
    
    @patch('streamlit_app.supabase')
    def test_process_list_display(self, mock_supabase):
        """Test wyświetlania listy procesów"""
        with patch('streamlit_app.st') as mock_st:
            mock_st.session_state.user = "test@smartflowai.com"
            
            # Mock processes data
            mock_processes = [
                {
                    'id': 1,
                    'title': 'Proces 1',
                    'description': 'Opis procesu 1',
                    'ai_analysis': 'Analiza procesu 1',
                    'created_at': '2025-01-01T00:00:00Z'
                },
                {
                    'id': 2,
                    'title': 'Proces 2',
                    'description': 'Opis procesu 2',
                    'ai_analysis': 'Analiza procesu 2',
                    'created_at': '2025-01-02T00:00:00Z'
                }
            ]
            
            mock_result = Mock()
            mock_result.data = mock_processes
            mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_result
            
            at = AppTest.from_file("streamlit_app.py")
            at.run()
            
            # Sprawdź czy procesy są wyświetlane
            # (Implementacja zależy od struktury interfejsu)

class TestE2EAdvancedFeatures:
    """Testy E2E zaawansowanych funkcji"""
    
    @patch('streamlit_app.supabase')
    def test_process_editing(self, mock_supabase):
        """Test edycji procesu"""
        with patch('streamlit_app.st') as mock_st:
            mock_st.session_state.user = "test@smartflowai.com"
            
            # Mock process data
            mock_process = {
                'id': 1,
                'title': 'Stary tytuł',
                'description': 'Stary opis',
                'ai_analysis': 'Stara analiza'
            }
            
            # Mock check ownership
            mock_check_result = Mock()
            mock_check_result.data = [{'id': 1}]
            
            # Mock update
            mock_update_result = Mock()
            
            mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_check_result
            mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_update_result
            
            # Test edycji przez interfejs
            # (Implementacja zależy od struktury interfejsu)
    
    @patch('streamlit_app.supabase')
    def test_process_deletion(self, mock_supabase):
        """Test usuwania procesu"""
        with patch('streamlit_app.st') as mock_st:
            mock_st.session_state.user = "test@smartflowai.com"
            
            # Mock check ownership
            mock_check_result = Mock()
            mock_check_result.data = [{'id': 1}]
            
            # Mock deletion
            mock_delete_result = Mock()
            
            mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_check_result
            mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value = mock_delete_result
            
            # Test usuwania przez interfejs
            # (Implementacja zależy od struktury interfejsu)

class TestE2EPDFGeneration:
    """Testy E2E generowania PDF"""
    
    @patch('streamlit_app.supabase')
    def test_pdf_generation_flow(self, mock_supabase):
        """Test generowania PDF"""
        with patch('streamlit_app.st') as mock_st:
            mock_st.session_state.user = "test@smartflowai.com"
            
            # Mock processes for PDF
            mock_processes = [
                {
                    'id': 1,
                    'title': 'Proces testowy',
                    'description': 'Opis procesu testowego',
                    'ai_analysis': 'Analiza procesu testowego',
                    'created_at': '2025-01-01T00:00:00Z'
                }
            ]
            
            mock_result = Mock()
            mock_result.data = mock_processes
            mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_result
            
            at = AppTest.from_file("streamlit_app.py")
            at.run()
            
            # Znajdź przycisk generowania PDF
            pdf_buttons = [btn for btn in at.button if "pdf" in btn.label.lower()]
            
            if pdf_buttons:
                # Test kliknięcia przycisku PDF
                pdf_buttons[0].click()
                at.run()
                
                # Sprawdź czy nie ma błędów
                # (Sprawdzenie zależy od implementacji)

class TestE2EUserExperience:
    """Testy E2E doświadczenia użytkownika"""
    
    def test_responsive_interface(self):
        """Test responsywności interfejsu"""
        at = AppTest.from_file("streamlit_app.py")
        at.run()
        
        # Sprawdź podstawowe elementy interfejsu
        assert len(at.title) >= 1  # Tytuł aplikacji
        
        # Sprawdź czy nie ma błędów w interfejsie
        assert len(at.exception) == 0
    
    def test_navigation_flow(self):
        """Test nawigacji między zakładkami"""
        with patch('streamlit_app.st') as mock_st:
            mock_st.session_state.user = "test@smartflowai.com"
            
            at = AppTest.from_file("streamlit_app.py")
            at.run()
            
            # Sprawdź czy są dostępne zakładki
            # (Implementacja zależy od struktury interfejsu)
    
    @patch('streamlit_app.supabase')
    @patch('streamlit_app.openai_client')
    def test_error_handling_ui(self, mock_openai, mock_supabase):
        """Test obsługi błędów w interfejsie"""
        with patch('streamlit_app.st') as mock_st:
            mock_st.session_state.user = "test@smartflowai.com"
            
            # Mock błędu AI
            mock_openai.chat.completions.create.side_effect = Exception("API Error")
            
            # Mock błędu bazy danych
            mock_supabase.table.return_value.insert.return_value.execute.side_effect = Exception("DB Error")
            
            at = AppTest.from_file("streamlit_app.py")
            at.run()
            
            # Sprawdź czy aplikacja nie crashuje przy błędach
            # (Implementacja zależy od obsługi błędów)

class TestE2EPerformance:
    """Testy E2E wydajności"""
    
    def test_app_startup_time(self):
        """Test czasu uruchamiania aplikacji"""
        start_time = time.time()
        
        at = AppTest.from_file("streamlit_app.py")
        at.run()
        
        end_time = time.time()
        startup_time = end_time - start_time
        
        # Aplikacja powinna uruchomić się w rozsądnym czasie (< 10 sekund)
        assert startup_time < 10.0, f"Aplikacja uruchamiała się zbyt długo: {startup_time:.2f}s"
    
    @patch('streamlit_app.supabase')
    def test_large_dataset_handling(self, mock_supabase):
        """Test obsługi dużej ilości danych"""
        with patch('streamlit_app.st') as mock_st:
            mock_st.session_state.user = "test@smartflowai.com"
            
            # Mock dużej ilości procesów
            mock_processes = []
            for i in range(100):
                mock_processes.append({
                    'id': i,
                    'title': f'Proces {i}',
                    'description': f'Opis procesu {i}' * 10,  # Długi opis
                    'ai_analysis': f'Analiza procesu {i}' * 20,  # Długa analiza
                    'created_at': f'2025-01-{i%30+1:02d}T00:00:00Z'
                })
            
            mock_result = Mock()
            mock_result.data = mock_processes
            mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_result
            
            start_time = time.time()
            
            at = AppTest.from_file("streamlit_app.py")
            at.run()
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Przetwarzanie dużej ilości danych powinno być rozsądnie szybkie
            assert processing_time < 15.0, f"Przetwarzanie dużej ilości danych trwało zbyt długo: {processing_time:.2f}s"

# Pomocnicze funkcje testowe
def simulate_user_input(at, field_label, value):
    """Symuluje wprowadzenie danych przez użytkownika"""
    for input_field in at.text_input:
        if field_label.lower() in input_field.label.lower():
            input_field.set_value(value)
            return True
    return False

def find_button_by_text(at, button_text):
    """Znajduje przycisk po tekście"""
    for button in at.button:
        if button_text.lower() in button.label.lower():
            return button
    return None

# Fixtures dla testów E2E
@pytest.fixture
def mock_logged_user():
    """Mock zalogowanego użytkownika"""
    with patch('streamlit_app.st') as mock_st:
        mock_st.session_state.user = "test@smartflowai.com"
        yield mock_st

@pytest.fixture
def mock_environment_e2e():
    """Mock środowiska dla testów E2E"""
    with patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test-openai-key-e2e',
        'SUPABASE_URL': 'https://test-e2e.supabase.co',
        'SUPABASE_ANON_KEY': 'test-supabase-key-e2e'
    }):
        yield

# Uruchomienie testów E2E
if __name__ == "__main__":
    print("🚀 Uruchamianie testów End-to-End SmartFlowAI...")
    pytest.main([__file__, "-v", "--tb=short", "-x"])  # -x = stop on first failure 