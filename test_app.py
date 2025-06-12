# Plik: test_app.py
# test_app.py - Proste testy SmartFlowAI (2 dni MVP)

import pytest
from unittest.mock import Mock, patch
import os
import sys

# Setup path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import funkcji z głównej aplikacji
from streamlit_app import analyze_with_ai, save_process, get_processes, delete_process

class TestSmartFlowAI:
    """Proste testy podstawowych funkcji"""
    
    def setup_method(self):
        """Setup przed każdym testem"""
        os.environ['OPENAI_API_KEY'] = 'test-key'
        os.environ['SUPABASE_URL'] = 'https://test.supabase.co'
        os.environ['SUPABASE_ANON_KEY'] = 'test-key'
    
    @patch('streamlit_app.openai_client')
    def test_analyze_with_ai_success(self, mock_openai):
        """Test analizy AI - sukces"""
        # Mock odpowiedzi OpenAI
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "OCENA: 8/10\nPROBLEM: Ręczne zadania"
        mock_openai.chat.completions.create.return_value = mock_response
        
        # Test
        result = analyze_with_ai("Test Process", "Test description")
        
        # Sprawdzenia
        assert "OCENA: 8/10" in result
        assert "PROBLEM: Ręczne zadania" in result
        mock_openai.chat.completions.create.assert_called_once()
    
    @patch('streamlit_app.openai_client')
    def test_analyze_with_ai_error(self, mock_openai):
        """Test analizy AI - błąd"""
        # Mock błędu
        mock_openai.chat.completions.create.side_effect = Exception("API Error")
        
        # Test
        result = analyze_with_ai("Test", "Description")
        
        # Sprawdzenie
        assert "Błąd analizy" in result
    
    @patch('streamlit_app.supabase')
    @patch('streamlit_app.st')
    def test_save_process_success(self, mock_st, mock_supabase):
        """Test zapisu procesu - sukces"""
        # Mock session state
        mock_st.session_state.user = "test@smartflowai.com"
        
        # Mock Supabase
        mock_result = Mock()
        mock_supabase.table().insert().execute.return_value = mock_result
        
        # Test
        result = save_process("Test Process", "Test description", "Test analysis")
        
        # Sprawdzenia
        assert result == True
        mock_supabase.table.assert_called_with('processes')
    
    @patch('streamlit_app.supabase')
    @patch('streamlit_app.st')
    def test_get_processes(self, mock_st, mock_supabase):
        """Test pobierania procesów"""
        # Mock session state
        mock_st.session_state.user = "test@smartflowai.com"
        
        # Mock danych
        mock_data = [
            {'id': 1, 'title': 'Process 1', 'user_email': 'test@smartflowai.com'},
            {'id': 2, 'title': 'Process 2', 'user_email': 'test@smartflowai.com'}
        ]
        mock_result = Mock()
        mock_result.data = mock_data
        mock_supabase.table().select().eq().order().execute.return_value = mock_result
        
        # Test
        result = get_processes()
        
        # Sprawdzenia
        assert len(result) == 2
        assert result[0]['title'] == 'Process 1'
    
    @patch('streamlit_app.supabase')
    def test_delete_process(self, mock_supabase):
        """Test usuwania procesu"""
        # Mock Supabase
        mock_result = Mock()
        mock_supabase.table().delete().eq().execute.return_value = mock_result
        
        # Test
        result = delete_process(1)
        
        # Sprawdzenia
        assert result == True
        mock_supabase.table.assert_called_with('processes')

# Test integracyjny
class TestIntegration:
    """Test pełnego workflow"""
    
    @patch('streamlit_app.supabase')
    @patch('streamlit_app.openai_client')
    @patch('streamlit_app.st')
    def test_full_workflow(self, mock_st, mock_openai, mock_supabase):
        """Test: analiza AI + zapis do DB"""
        # Mock session state
        mock_st.session_state.user = "test@smartflowai.com"
        
        # Mock AI
        mock_ai_response = Mock()
        mock_ai_response.choices = [Mock()]
        mock_ai_response.choices[0].message.content = "OCENA: 8/10"
        mock_openai.chat.completions.create.return_value = mock_ai_response
        
        # Mock DB
        mock_db_result = Mock()
        mock_supabase.table().insert().execute.return_value = mock_db_result
        
        # Test workflow
        ai_result = analyze_with_ai("Test Process", "Test description")
        save_result = save_process("Test Process", "Test description", ai_result)
        
        # Sprawdzenia
        assert "OCENA: 8/10" in ai_result
        assert save_result == True

# Fixtures
@pytest.fixture
def sample_process():
    """Przykładowe dane procesu"""
    return {
        'title': 'Test Process',
        'description': 'This is a test process description for SmartFlowAI',
        'user_email': 'test@smartflowai.com'
    }

# Uruchomienie testów
if __name__ == "__main__":
    pytest.main([__file__, "-v"])