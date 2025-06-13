# -*- coding: utf-8 -*-
"""
test_utf8.py - Test obsługi kodowania UTF-8 w SmartFlowAI

Ten skrypt testuje czy wszystkie komponenty projektu poprawnie obsługują
polskie znaki i kodowanie UTF-8.
"""

import sys
import os
from pathlib import Path

def test_polish_characters():
    """Test polskich znaków"""
    polish_text = "Ąćęłńóśźż ĄĆĘŁŃÓŚŹŻ - test polskich znaków"
    print(f"✅ Polskie znaki: {polish_text}")
    return True

def test_file_encoding():
    """Test kodowania plików"""
    test_files = [
        "streamlit_app.py",
        "test_app.py", 
        "check_user.py",
        "quick_start.py",
        "test_simple.py",
        "test_gpt4o.py",
        "test_openai.py"
    ]
    
    for file_path in test_files:
        if Path(file_path).exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    if "# -*- coding: utf-8 -*-" in first_line:
                        print(f"✅ {file_path}: ma deklarację UTF-8")
                    else:
                        print(f"⚠️ {file_path}: brak deklaracji UTF-8")
            except UnicodeDecodeError:
                print(f"❌ {file_path}: błąd kodowania!")
        else:
            print(f"⚠️ {file_path}: plik nie istnieje")

def test_logging_utf8():
    """Test logowania z polskimi znakami"""
    import logging
    
    # Konfiguracja logowania z UTF-8
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('test_utf8.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    # Test polskich znaków w logach
    test_message = "Test logowania: ąćęłńóśźż ĄĆĘŁŃÓŚŹŻ"
    logger.info(test_message)
    print(f"✅ Logowanie UTF-8: {test_message}")
    
    return True

def test_pdf_text_processing():
    """Test przetwarzania tekstu dla PDF"""
    
    def transliterate_polish(text):
        """Zamienia polskie znaki na ASCII"""
        if not text:
            return ""
        replacements = {
            'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n', 'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z',
            'Ą': 'A', 'Ć': 'C', 'Ę': 'E', 'Ł': 'L', 'Ń': 'N', 'Ó': 'O', 'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z'
        }
        for polish, ascii_char in replacements.items():
            text = text.replace(polish, ascii_char)
        return text
    
    # Test transliteracji
    original = "Proces fakturowania: ąćęłńóśźż"
    transliterated = transliterate_polish(original)
    print(f"✅ Oryginał: {original}")
    print(f"✅ Transliteracja: {transliterated}")
    
    return True

def main():
    """Główna funkcja testowa"""
    print("🧪 Test obsługi UTF-8 w SmartFlowAI")
    print("=" * 50)
    
    # Informacje o systemie
    print(f"Python version: {sys.version}")
    print(f"Default encoding: {sys.getdefaultencoding()}")
    print(f"File system encoding: {sys.getfilesystemencoding()}")
    print()
    
    # Testy
    tests = [
        ("Polskie znaki", test_polish_characters),
        ("Kodowanie plików", test_file_encoding),
        ("Logowanie UTF-8", test_logging_utf8),
        ("Przetwarzanie tekstu PDF", test_pdf_text_processing)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Test: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Wyniki: {passed}/{total} testów przeszło pomyślnie")
    
    if passed == total:
        print("🎉 Wszystkie testy UTF-8 przeszły pomyślnie!")
        return True
    else:
        print("⚠️ Niektóre testy nie przeszły - sprawdź konfigurację")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 