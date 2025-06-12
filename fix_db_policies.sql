-- fix_db_policies.sql - Naprawa polityk RLS dla testowych użytkowników SmartFlowAI

-- Usunięcie starych polityk
DROP POLICY IF EXISTS "Users can view own processes" ON processes;
DROP POLICY IF EXISTS "Users can insert own processes" ON processes;
DROP POLICY IF EXISTS "Users can update own processes" ON processes;
DROP POLICY IF EXISTS "Users can delete own processes" ON processes;

-- Dodanie polityk dla testowych użytkowników
DROP POLICY IF EXISTS "Test users can view processes" ON processes;
DROP POLICY IF EXISTS "Test users can insert processes" ON processes;
DROP POLICY IF EXISTS "Test users can update processes" ON processes;
DROP POLICY IF EXISTS "Test users can delete processes" ON processes;

-- 1. Polityki dla prawdziwych użytkowników Supabase (gdy auth.email() istnieje)
CREATE POLICY "Authenticated users can view own processes" ON processes
    FOR SELECT USING (
        (auth.email() IS NOT NULL AND auth.email() = user_email)
    );

CREATE POLICY "Authenticated users can insert own processes" ON processes
    FOR INSERT WITH CHECK (
        (auth.email() IS NOT NULL AND auth.email() = user_email)
    );

CREATE POLICY "Authenticated users can update own processes" ON processes
    FOR UPDATE USING (
        (auth.email() IS NOT NULL AND auth.email() = user_email)
    ) WITH CHECK (
        (auth.email() IS NOT NULL AND auth.email() = user_email)
    );

CREATE POLICY "Authenticated users can delete own processes" ON processes
    FOR DELETE USING (
        (auth.email() IS NOT NULL AND auth.email() = user_email)
    );

-- 2. Polityki dla testowych użytkowników (gdy auth.email() jest NULL)
CREATE POLICY "Test users can view processes" ON processes
    FOR SELECT USING (
        auth.email() IS NULL 
        AND user_email IN ('test@smartflowai.com', 'test@smatflow.pl')
    );

CREATE POLICY "Test users can insert processes" ON processes
    FOR INSERT WITH CHECK (
        auth.email() IS NULL 
        AND user_email IN ('test@smartflowai.com', 'test@smatflow.pl')
    );

CREATE POLICY "Test users can update processes" ON processes
    FOR UPDATE USING (
        auth.email() IS NULL 
        AND user_email IN ('test@smartflowai.com', 'test@smatflow.pl')
    ) WITH CHECK (
        auth.email() IS NULL 
        AND user_email IN ('test@smartflowai.com', 'test@smatflow.pl')
    );

CREATE POLICY "Test users can delete processes" ON processes
    FOR DELETE USING (
        auth.email() IS NULL 
        AND user_email IN ('test@smartflowai.com', 'test@smatflow.pl')
    );

-- Sprawdzenie utworzonych polityk
SELECT schemaname, tablename, policyname, permissive, cmd 
FROM pg_policies 
WHERE tablename = 'processes'
ORDER BY policyname; 