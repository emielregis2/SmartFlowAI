# -*- coding: utf-8 -*-
"""
Kompletny zestaw testów dla SmartFlowAI - Wersja Produkcyjna

Zawiera:
- Unit testy wszystkich funkcji
- Testy integracyjne
- Testy konfiguracji
- Testy bezpieczeństwa
- Testy wydajności

Autor: Claude + Dariusz
"""

import pytest
import os
import sys
import tempfile
import io
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Setup path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import funkcji z głównej aplikacji
try:
    from streamlit_app import (
        analyze_with_ai, save_process, get_processes, 
        delete_process, update_process, initialize_database
    )
except ImportError as e:
    print(f"❌ Błąd importu: {e}")
    sys.exit(1)

class TestConfiguration:
    """Testy konfiguracji aplikacji"""
    
    def test_environment_variables(self):
        """Test zmiennych środowiskowych"""
        # Test wymaganych zmiennych
        required_vars = ['OPENAI_API_KEY', 'SUPABASE_URL', 'SUPABASE_ANON_KEY']
        
        for var in required_vars:
            # Sprawdź czy zmienna jest ustawiona (może być test-value)
            value = os.getenv(var)
            assert value is not None, f"Zmienna {var} nie jest ustawiona"
            assert len(value) > 0, f"Zmienna {var} jest pusta"
    
    def test_imports(self):
        """Test importów bibliotek"""
        try:
            import streamlit
            import supabase
            import openai
            import fpdf
            assert True
        except ImportError as e:
            pytest.fail(f"Błąd importu biblioteki: {e}")

class TestAnalyzeAI:
    """Unit testy funkcji analizy AI"""
    
    def setup_method(self):
        """Setup przed każdym testem"""
        os.environ['OPENAI_API_KEY'] = 'test-key-12345'
        os.environ['SUPABASE_URL'] = 'https://test.supabase.co'
        os.environ['SUPABASE_ANON_KEY'] = 'test-anon-key-12345'
    
    @patch('streamlit_app.openai_client')
    def test_analyze_basic_success(self, mock_openai):
        """Test podstawowej analizy AI - sukces"""
        # Mock odpowiedzi OpenAI
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """
🔍 **ANALIZA:** Proces wymaga automatyzacji
🛠️ **ROZWIĄZANIE:** Zapier + Airtable
💰 **KOSZT:** 200 zł/mies
⏱️ **OSZCZĘDNOŚCI:** 10 godzin/mies
⚡ **PIERWSZE KROKI:** 1. Analiza 2. Wdrożenie 3. Test
"""
        mock_openai.chat.completions.create.return_value = mock_response
        
        # Test
        result = analyze_with_ai("Wystawianie faktur", "Ręczne tworzenie faktur w Excelu")
        
        # Sprawdzenia
        assert "🔍 **ANALIZA:**" in result
        assert "🛠️ **ROZWIĄZANIE:**" in result
        assert "💰 **KOSZT:**" in result
        assert "⏱️ **OSZCZĘDNOŚCI:**" in result
        assert "⚡ **PIERWSZE KROKI:**" in result
        mock_openai.chat.completions.create.assert_called_once()
    
    @patch('streamlit_app.openai_client')
    def test_analyze_with_context(self, mock_openai):
        """Test analizy z kontekstem firmy"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Analiza z kontekstem firmy IT"
        mock_openai.chat.completions.create.return_value = mock_response
        
        # Test z pełnym kontekstem
        result = analyze_with_ai(
            "Test Process", 
            "Test description",
            analysis_depth="Pogłębiona (z wyszukiwaniem)",
            company_size="11-50 osób",
            industry="IT/Software",
            budget="500-2000 zł/mies"
        )
        
        # Sprawdź czy wywołano z odpowiednimi parametrami
        call_args = mock_openai.chat.completions.create.call_args
        prompt = call_args[1]['messages'][0]['content']
        
        assert "11-50 osób" in prompt
        assert "IT/Software" in prompt
        assert "500-2000 zł/mies" in prompt
    
    @patch('streamlit_app.openai_client')
    def test_analyze_different_depths(self, mock_openai):
        """Test różnych głębokości analizy"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_openai.chat.completions.create.return_value = mock_response
        
        depths = ["Podstawowa (szybka)", "Pogłębiona (z wyszukiwaniem)", "Ekspercka (pełna analiza)"]
        
        for depth in depths:
            result = analyze_with_ai("Test", "Description", analysis_depth=depth)
            assert result == "Test response"
    
    @patch('streamlit_app.openai_client')
    def test_analyze_error_handling(self, mock_openai):
        """Test obsługi błędów analizy AI"""
        # Mock błędu
        mock_openai.chat.completions.create.side_effect = Exception("API Error")
        
        # Test
        result = analyze_with_ai("Test", "Description")
        
        # Sprawdzenie
        assert "Błąd analizy" in result or "Error" in result

class TestDatabaseOperations:
    """Unit testy operacji bazodanowych"""
    
    def setup_method(self):
        """Setup przed każdym testem"""
        os.environ['SUPABASE_URL'] = 'https://test.supabase.co'
        os.environ['SUPABASE_ANON_KEY'] = 'test-anon-key'
    
    @patch('streamlit_app.supabase')
    @patch('streamlit_app.st')
    def test_save_process_success(self, mock_st, mock_supabase):
        """Test zapisu procesu - sukces"""
        # Mock session state
        mock_st.session_state.user = "test@smartflowai.com"
        
        # Mock Supabase response
        mock_result = Mock()
        mock_result.data = [{'id': 1, 'title': 'Test Process'}]
        mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_result
        
        # Test
        result = save_process("Test Process", "Test description", "Test analysis")
        
        # Sprawdzenia
        assert result == True
        mock_supabase.table.assert_called_with('processes')
        
        # Sprawdź dane przekazane do insert
        insert_call = mock_supabase.table.return_value.insert.call_args[0][0]
        assert insert_call['user_email'] == "test@smartflowai.com"
        assert insert_call['title'] == "Test Process"
        assert insert_call['description'] == "Test description"
        assert insert_call['ai_analysis'] == "Test analysis"
    
    @patch('streamlit_app.supabase')
    @patch('streamlit_app.st')
    def test_save_process_error(self, mock_st, mock_supabase):
        """Test zapisu procesu - błąd"""
        mock_st.session_state.user = "test@smartflowai.com"
        mock_supabase.table.return_value.insert.return_value.execute.side_effect = Exception("DB Error")
        
        result = save_process("Test", "Description", "Analysis")
        assert result == False
    
    @patch('streamlit_app.supabase')
    @patch('streamlit_app.st')
    def test_get_processes_success(self, mock_st, mock_supabase):
        """Test pobierania procesów - sukces"""
        mock_st.session_state.user = "test@smartflowai.com"
        
        # Mock danych
        mock_data = [
            {
                'id': 1, 
                'title': 'Process 1', 
                'description': 'Description 1',
                'ai_analysis': 'Analysis 1',
                'user_email': 'test@smartflowai.com',
                'created_at': '2025-01-01T00:00:00Z'
            },
            {
                'id': 2, 
                'title': 'Process 2', 
                'description': 'Description 2',
                'ai_analysis': 'Analysis 2',
                'user_email': 'test@smartflowai.com',
                'created_at': '2025-01-02T00:00:00Z'
            }
        ]
        
        mock_result = Mock()
        mock_result.data = mock_data
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_result
        
        # Test
        result = get_processes()
        
        # Sprawdzenia
        assert len(result) == 2
        assert result[0]['title'] == 'Process 1'
        assert result[1]['title'] == 'Process 2'
        
        # Sprawdź wywołania Supabase
        mock_supabase.table.assert_called_with('processes')
    
    @patch('streamlit_app.supabase')
    @patch('streamlit_app.st')
    def test_get_processes_error(self, mock_st, mock_supabase):
        """Test pobierania procesów - błąd"""
        mock_st.session_state.user = "test@smartflowai.com"
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.side_effect = Exception("DB Error")
        
        result = get_processes()
        assert result == []
    
    @patch('streamlit_app.supabase')
    @patch('streamlit_app.st')
    def test_delete_process_success(self, mock_st, mock_supabase):
        """Test usuwania procesu - sukces"""
        mock_st.session_state.user = "test@smartflowai.com"
        
        # Mock sprawdzenia właściciela
        mock_check_result = Mock()
        mock_check_result.data = [{'id': 1}]
        
        # Mock usuwania
        mock_delete_result = Mock()
        
        # Konfiguracja mocków
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_check_result
        mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value = mock_delete_result
        
        # Test
        result = delete_process(1)
        
        # Sprawdzenia
        assert result == True
    
    @patch('streamlit_app.supabase')
    @patch('streamlit_app.st')
    def test_delete_process_unauthorized(self, mock_st, mock_supabase):
        """Test usuwania procesu - brak uprawnień"""
        mock_st.session_state.user = "test@smartflowai.com"
        
        # Mock braku uprawnień
        mock_check_result = Mock()
        mock_check_result.data = []  # Brak danych = brak uprawnień
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_check_result
        
        result = delete_process(1)
        assert result == False
    
    @patch('streamlit_app.supabase')
    @patch('streamlit_app.st')
    def test_update_process_success(self, mock_st, mock_supabase):
        """Test aktualizacji procesu - sukces"""
        mock_st.session_state.user = "test@smartflowai.com"
        
        # Mock sprawdzenia właściciela
        mock_check_result = Mock()
        mock_check_result.data = [{'id': 1}]
        
        # Mock aktualizacji
        mock_update_result = Mock()
        
        # Konfiguracja mocków
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_check_result
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_update_result
        
        # Test
        result = update_process(1, "Updated Title", "Updated Description", "Updated Analysis")
        
        # Sprawdzenia
        assert result == True
        
        # Sprawdź dane przekazane do update
        update_call = mock_supabase.table.return_value.update.call_args[0][0]
        assert update_call['title'] == "Updated Title"
        assert update_call['description'] == "Updated Description"
        assert update_call['ai_analysis'] == "Updated Analysis"

class TestSecurity:
    """Testy bezpieczeństwa"""
    
    @patch('streamlit_app.supabase')
    @patch('streamlit_app.st')
    def test_user_isolation(self, mock_st, mock_supabase):
        """Test izolacji danych użytkowników"""
        # Test że użytkownik widzi tylko swoje procesy
        mock_st.session_state.user = "user1@test.com"
        
        mock_result = Mock()
        mock_result.data = []
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_result
        
        get_processes()
        
        # Sprawdź czy filtruje po user_email
        eq_calls = mock_supabase.table.return_value.select.return_value.eq.call_args_list
        assert any('user_email' in str(call) and 'user1@test.com' in str(call) for call in eq_calls)
    
    def test_input_validation(self):
        """Test walidacji danych wejściowych"""
        # Test pustych stringów
        with patch('streamlit_app.openai_client') as mock_openai:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Test response"
            mock_openai.chat.completions.create.return_value = mock_response
            
            # Test z pustymi danymi
            result = analyze_with_ai("", "")
            assert isinstance(result, str)
            
            # Test z bardzo długimi danymi
            long_text = "A" * 10000
            result = analyze_with_ai(long_text, long_text)
            assert isinstance(result, str)

class TestPerformance:
    """Testy wydajności"""
    
    @patch('streamlit_app.openai_client')
    def test_analyze_response_time(self, mock_openai):
        """Test czasu odpowiedzi analizy AI"""
        import time
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Quick response"
        mock_openai.chat.completions.create.return_value = mock_response
        
        start_time = time.time()
        result = analyze_with_ai("Test", "Description")
        end_time = time.time()
        
        # Test powinien zakończyć się w rozsądnym czasie (< 1 sekunda dla mocka)
        assert (end_time - start_time) < 1.0
        assert result == "Quick response"

class TestIntegration:
    """Testy integracyjne"""
    
    @patch('streamlit_app.supabase')
    @patch('streamlit_app.openai_client')
    @patch('streamlit_app.st')
    def test_full_workflow(self, mock_st, mock_openai, mock_supabase):
        """Test pełnego workflow: analiza AI + zapis + odczyt"""
        # Setup
        mock_st.session_state.user = "test@smartflowai.com"
        
        # Mock AI
        mock_ai_response = Mock()
        mock_ai_response.choices = [Mock()]
        mock_ai_response.choices[0].message.content = "🔍 **ANALIZA:** Test analysis"
        mock_openai.chat.completions.create.return_value = mock_ai_response
        
        # Mock DB save
        mock_save_result = Mock()
        mock_save_result.data = [{'id': 1}]
        mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_save_result
        
        # Mock DB get
        mock_get_result = Mock()
        mock_get_result.data = [{
            'id': 1,
            'title': 'Test Process',
            'description': 'Test description',
            'ai_analysis': '🔍 **ANALIZA:** Test analysis',
            'user_email': 'test@smartflowai.com'
        }]
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_get_result
        
        # Test workflow
        # 1. Analiza AI
        ai_result = analyze_with_ai("Test Process", "Test description")
        assert "🔍 **ANALIZA:**" in ai_result
        
        # 2. Zapis do bazy
        save_result = save_process("Test Process", "Test description", ai_result)
        assert save_result == True
        
        # 3. Odczyt z bazy
        processes = get_processes()
        assert len(processes) == 1
        assert processes[0]['title'] == 'Test Process'
        assert processes[0]['ai_analysis'] == ai_result
    
    @patch('streamlit_app.supabase')
    def test_database_initialization(self, mock_supabase):
        """Test inicjalizacji bazy danych"""
        # Mock sprawdzenia tabeli (tabela istnieje)
        mock_result = Mock()
        mock_result.data = [{'id': 1}]
        mock_supabase.table.return_value.select.return_value.limit.return_value.execute.return_value = mock_result
        
        result = initialize_database()
        assert result == True
        
        # Mock błędu (tabela nie istnieje)
        mock_supabase.table.return_value.select.return_value.limit.return_value.execute.side_effect = Exception("relation does not exist")
        mock_supabase.sql.return_value.execute.return_value = Mock()
        
        result = initialize_database()
        assert result == True

class TestEdgeCases:
    """Testy przypadków brzegowych"""
    
    @patch('streamlit_app.openai_client')
    def test_empty_ai_response(self, mock_openai):
        """Test pustej odpowiedzi AI"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = ""
        mock_openai.chat.completions.create.return_value = mock_response
        
        result = analyze_with_ai("Test", "Description")
        assert isinstance(result, str)
    
    @patch('streamlit_app.supabase')
    @patch('streamlit_app.st')
    def test_empty_database(self, mock_st, mock_supabase):
        """Test pustej bazy danych"""
        mock_st.session_state.user = "test@smartflowai.com"
        
        mock_result = Mock()
        mock_result.data = []
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_result
        
        result = get_processes()
        assert result == []
    
    def test_unicode_handling(self):
        """Test obsługi znaków Unicode"""
        with patch('streamlit_app.openai_client') as mock_openai:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Analiza z polskimi znakami: ąćęłńóśźż"
            mock_openai.chat.completions.create.return_value = mock_openai
            
            # Test z polskimi znakami
            result = analyze_with_ai("Proces z ąćęłńóśźż", "Opis zawierający ąćęłńóśźż")
            assert isinstance(result, str)

# Fixtures
@pytest.fixture
def sample_process_data():
    """Przykładowe dane procesu"""
    return {
        'title': 'Wystawianie faktur',
        'description': 'Ręczne tworzenie faktur w programie Excel, sprawdzanie danych klientów, wysyłanie mailem',
        'ai_analysis': '🔍 **ANALIZA:** Proces wymaga automatyzacji\n🛠️ **ROZWIĄZANIE:** iFirma + Zapier',
        'user_email': 'test@smartflowai.com'
    }

@pytest.fixture
def mock_environment():
    """Mock środowiska testowego"""
    with patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test-openai-key-12345',
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_ANON_KEY': 'test-supabase-key-12345'
    }):
        yield

# Uruchomienie testów
if __name__ == "__main__":
    print("🚀 Uruchamianie kompletnych testów SmartFlowAI...")
    pytest.main([__file__, "-v", "--tb=short"]) 