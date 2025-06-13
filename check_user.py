#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_user.py - Skrypt do sprawdzania użytkowników w bazie danych

Użycie:
python check_user.py [email]
"""

import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ładuj zmienne środowiskowe
load_dotenv()

def init_supabase():
    """Inicjalizuje klienta Supabase"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("❌ Brak konfiguracji Supabase! Sprawdź .env")
        sys.exit(1)
    
    return create_client(url, key)

def check_user_in_auth(supabase, email):
    """Sprawdza czy użytkownik istnieje w systemie auth"""
    try:
        # Próba logowania z niepoprawnym hasłem, aby sprawdzić czy użytkownik istnieje
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": "fake_password_to_check_existence"
        })
        return True
    except Exception as e:
        error_msg = str(e).lower()
        if "invalid login credentials" in error_msg or "invalid" in error_msg:
            print(f"✅ Użytkownik {email} ISTNIEJE w systemie auth (błędne hasło)")
            return True
        elif "user not found" in error_msg or "email not confirmed" in error_msg:
            print(f"❌ Użytkownik {email} NIE ISTNIEJE w systemie auth")
            return False
        else:
            print(f"⚠️ Nieznany błąd przy sprawdzaniu {email}: {e}")
            # Zakładamy że istnieje jeśli dostajemy błąd 400 (Bad Request)
            if "400" in str(e):
                print(f"✅ Prawdopodobnie użytkownik {email} ISTNIEJE (błąd 400)")
                return True
            return False

def check_user_processes(supabase, email):
    """Sprawdza procesy użytkownika w bazie danych"""
    try:
        result = supabase.table('processes').select('*').eq('user_email', email).execute()
        count = len(result.data)
        print(f"📊 Użytkownik {email} ma {count} procesów w bazie danych")
        
        if count > 0:
            print("   Ostatnie procesy:")
            for process in result.data[:3]:  # Pokaż 3 ostatnie
                title = process.get('title', 'Brak tytułu')
                created = process.get('created_at', 'Brak daty')[:10]
                print(f"   - {title} ({created})")
        
        return count > 0
    except Exception as e:
        print(f"❌ Błąd sprawdzania procesów dla {email}: {e}")
        return False

def main():
    """Główna funkcja"""
    if len(sys.argv) != 2:
        print("Użycie: python check_user.py [email]")
        print("Przykład: python check_user.py dariusz.gasior@gmail.com")
        sys.exit(1)
    
    email = sys.argv[1]
    print(f"🔍 Sprawdzam użytkownika: {email}")
    print("="*50)
    
    # Inicjalizuj Supabase
    supabase = init_supabase()
    
    # Sprawdź w systemie auth
    auth_exists = check_user_in_auth(supabase, email)
    
    # Sprawdź procesy w bazie
    has_processes = check_user_processes(supabase, email)
    
    print("="*50)
    print("📋 PODSUMOWANIE:")
    print(f"   Auth system: {'✅ ISTNIEJE' if auth_exists else '❌ NIE ISTNIEJE'}")
    print(f"   Procesy w DB: {'✅ MA PROCESY' if has_processes else '❌ BRAK PROCESÓW'}")
    
    if auth_exists:
        print(f"\n💡 Użytkownik {email} może się zalogować do aplikacji")
    else:
        print(f"\n⚠️ Użytkownik {email} musi się zarejestrować w aplikacji")

if __name__ == "__main__":
    main() 