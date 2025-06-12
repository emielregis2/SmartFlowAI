-- disable_rls_for_testing.sql - Tymczasowe wyłączenie RLS dla testów

-- UWAGA: To wyłącza bezpieczeństwo! Używaj tylko do testów lokalnych!
ALTER TABLE processes DISABLE ROW LEVEL SECURITY;

-- Sprawdzenie statusu
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE tablename = 'processes';

-- Aby przywrócić RLS później:
-- ALTER TABLE processes ENABLE ROW LEVEL SECURITY; 