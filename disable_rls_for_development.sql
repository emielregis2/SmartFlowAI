-- Skrypt do wyłączenia RLS dla developmentu SmartFlowAI
-- UWAGA: Używaj tylko w środowisku developerskim!

-- Wyłącz RLS dla wszystkich tabel
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE business_processes DISABLE ROW LEVEL SECURITY;
ALTER TABLE activity_logs DISABLE ROW LEVEL SECURITY;
ALTER TABLE process_categories DISABLE ROW LEVEL SECURITY;

-- Usuń istniejące polityki (opcjonalnie)
DROP POLICY IF EXISTS "Users can view own profile" ON users;
DROP POLICY IF EXISTS "Users can update own profile" ON users;
DROP POLICY IF EXISTS "Users can view own processes" ON business_processes;
DROP POLICY IF EXISTS "Users can insert own processes" ON business_processes;
DROP POLICY IF EXISTS "Users can update own processes" ON business_processes;
DROP POLICY IF EXISTS "Users can delete own processes" ON business_processes;
DROP POLICY IF EXISTS "Users can view own logs" ON activity_logs;
DROP POLICY IF EXISTS "Users can insert own logs" ON activity_logs;

-- Informacja o zakończeniu
DO $$
BEGIN
    RAISE NOTICE 'RLS disabled for development. All tables are now publicly accessible.';
    RAISE NOTICE 'WARNING: Do not use this in production environment!';
END $$; 