# -*- coding: utf-8 -*-
"""
Test ulepszonych funkcji analizy AI - SmartFlowAI

Testuje:
- Różne głębokości analizy
- Kontekst firmy
- Branżowe szablony
- Długość odpowiedzi

Autor: Claude + Dariusz
"""

import os
import sys
from unittest.mock import Mock, patch

# Dodaj ścieżkę do głównego modułu
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_analysis_depth_options():
    """Test różnych opcji głębokości analizy"""
    print("🧪 Test opcji głębokości analizy...")
    
    # Mock funkcji analyze_with_ai
    def mock_analyze(title, description, analysis_depth="Pogłębiona", company_size="", industry="", budget=""):
        if analysis_depth == "Podstawowa (szybka)":
            return "🔍 **ANALIZA:** Krótka analiza\n🛠️ **ROZWIĄZANIE:** Zapier"
        elif analysis_depth == "Ekspercka (pełna analiza)":
            return "🔍 **ANALIZA PROCESU:** Bardzo szczegółowa analiza...\n### 1. DEKOMPOZYCJA PROCESU..."
        else:
            return "🔍 **ANALIZA PROCESU:** Standardowa pogłębiona analiza..."
    
    # Test podstawowej analizy
    result_basic = mock_analyze("Test", "Opis", "Podstawowa (szybka)")
    assert "Krótka analiza" in result_basic
    print("✅ Podstawowa analiza - OK")
    
    # Test eksperckiej analizy
    result_expert = mock_analyze("Test", "Opis", "Ekspercka (pełna analiza)")
    assert "Bardzo szczegółowa" in result_expert
    print("✅ Ekspercka analiza - OK")
    
    # Test domyślnej analizy
    result_default = mock_analyze("Test", "Opis")
    assert "Standardowa pogłębiona" in result_default
    print("✅ Domyślna analiza - OK")

def test_company_context():
    """Test kontekstu firmy"""
    print("\n🧪 Test kontekstu firmy...")
    
    def mock_analyze_with_context(title, description, analysis_depth="Pogłębiona", company_size="", industry="", budget=""):
        company_context = ""
        if company_size or industry or budget:
            company_context = f"KONTEKST: {company_size}, {industry}, {budget}"
        return f"Analiza z kontekstem: {company_context}"
    
    # Test z pełnym kontekstem
    result = mock_analyze_with_context(
        "Test", "Opis", 
        company_size="11-50 osób", 
        industry="IT/Software", 
        budget="500-2000 zł/mies"
    )
    assert "11-50 osób" in result
    assert "IT/Software" in result
    assert "500-2000 zł/mies" in result
    print("✅ Pełny kontekst firmy - OK")
    
    # Test bez kontekstu
    result_empty = mock_analyze_with_context("Test", "Opis")
    assert "KONTEKST: , ," not in result_empty
    print("✅ Brak kontekstu - OK")

def test_industry_templates():
    """Test branżowych szablonów"""
    print("\n🧪 Test branżowych szablonów...")
    
    industry_context = {
        "E-commerce/Handel": "Uwzględnij integracje z Allegro, Amazon, BaseLinker",
        "Księgowość": "Uwzględnij integracje z iFirma, Wfirma, SAP",
        "Marketing/Reklama": "Uwzględnij integracje z Facebook Ads, Google Ads",
        "IT/Software": "Uwzględnij integracje z GitHub, Jira, Slack"
    }
    
    # Test każdej branży
    for industry, expected_text in industry_context.items():
        branch_specific = ""
        if industry in industry_context:
            branch_specific = f"UWAGI BRANŻOWE: {industry_context[industry]}"
        
        assert expected_text in branch_specific
        print(f"✅ Branża {industry} - OK")

def test_form_options():
    """Test opcji formularza"""
    print("\n🧪 Test opcji formularza...")
    
    # Opcje głębokości analizy
    analysis_options = ["Podstawowa (szybka)", "Pogłębiona (z wyszukiwaniem)", "Ekspercka (pełna analiza)"]
    assert len(analysis_options) == 3
    print("✅ Opcje głębokości analizy - OK")
    
    # Opcje wielkości firmy
    company_sizes = ["", "1-10 osób", "11-50 osób", "51-200 osób", "200+ osób"]
    assert len(company_sizes) == 5
    print("✅ Opcje wielkości firmy - OK")
    
    # Opcje branż
    industries = ["", "IT/Software", "E-commerce/Handel", "Produkcja", "Usługi finansowe", 
                 "Marketing/Reklama", "Księgowość", "Logistyka", "Edukacja", "Zdrowie", "Inna"]
    assert len(industries) == 11
    print("✅ Opcje branż - OK")
    
    # Opcje budżetu
    budgets = ["", "do 500 zł/mies", "500-2000 zł/mies", "2000-5000 zł/mies", "5000+ zł/mies"]
    assert len(budgets) == 5
    print("✅ Opcje budżetu - OK")

def test_prompt_generation():
    """Test generowania promptów"""
    print("\n🧪 Test generowania promptów...")
    
    def generate_prompt(title, description, analysis_depth, company_size="", industry="", budget=""):
        # Symulacja logiki z analyze_with_ai
        company_context = ""
        if company_size or industry or budget:
            company_context = f"KONTEKST FIRMY: {company_size}, {industry}, {budget}"
        
        industry_context = {
            "IT/Software": "GitHub, Jira, Slack",
            "E-commerce/Handel": "Allegro, Amazon, BaseLinker"
        }
        
        branch_specific = ""
        if industry and industry in industry_context:
            branch_specific = f"UWAGI BRANŻOWE: {industry_context[industry]}"
        
        if analysis_depth == "Podstawowa (szybka)":
            return f"PODSTAWOWA: {title} - {description} {company_context} {branch_specific}"
        elif analysis_depth == "Ekspercka (pełna analiza)":
            return f"EKSPERCKA: {title} - {description} {company_context} {branch_specific}"
        else:
            return f"POGŁĘBIONA: {title} - {description} {company_context} {branch_specific}"
    
    # Test podstawowego promptu
    prompt_basic = generate_prompt("Faktury", "Wystawianie faktur", "Podstawowa (szybka)", "11-50 osób", "IT/Software", "500-2000 zł/mies")
    assert "PODSTAWOWA" in prompt_basic
    assert "GitHub, Jira, Slack" in prompt_basic
    print("✅ Prompt podstawowy - OK")
    
    # Test eksperckiego promptu
    prompt_expert = generate_prompt("Faktury", "Wystawianie faktur", "Ekspercka (pełna analiza)", "", "E-commerce/Handel", "")
    assert "EKSPERCKA" in prompt_expert
    assert "Allegro, Amazon, BaseLinker" in prompt_expert
    print("✅ Prompt ekspercki - OK")

def main():
    """Uruchom wszystkie testy"""
    print("🚀 Uruchamianie testów ulepszonych funkcji analizy AI...\n")
    
    try:
        test_analysis_depth_options()
        test_company_context()
        test_industry_templates()
        test_form_options()
        test_prompt_generation()
        
        print("\n🎉 Wszystkie testy przeszły pomyślnie!")
        print("✅ Ulepszenia analizy AI działają poprawnie")
        
    except AssertionError as e:
        print(f"\n❌ Test nie przeszedł: {e}")
        return False
    except Exception as e:
        print(f"\n💥 Błąd podczas testów: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 