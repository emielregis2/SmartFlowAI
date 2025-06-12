-- Fix RLS policies dla poprawnych adresów email
-- Usuwamy stare polityki i dodajemy nowe z poprawnymi emailami

-- Usuń stare polityki
DROP POLICY IF EXISTS "Users can select their own processes" ON processes;
DROP POLICY IF EXISTS "Users can insert their own processes" ON processes;
DROP POLICY IF EXISTS "Users can update their own processes" ON processes; 
DROP POLICY IF EXISTS "Users can delete their own processes" ON processes;
DROP POLICY IF EXISTS "Test users can delete their own processes" ON processes;

-- Dodaj nowe polityki z poprawnymi adresami
CREATE POLICY "Users can select their own processes" ON processes
FOR SELECT USING (
    auth.email() = user_email 
    OR (auth.email() IS NULL AND user_email IN ('test@smartflowai.com', 'test@smartflow.pl'))
);

CREATE POLICY "Users can insert their own processes" ON processes  
FOR INSERT WITH CHECK (
    auth.email() = user_email
    OR (auth.email() IS NULL AND user_email IN ('test@smartflowai.com', 'test@smartflow.pl'))
);

CREATE POLICY "Users can update their own processes" ON processes
FOR UPDATE USING (
    auth.email() = user_email
    OR (auth.email() IS NULL AND user_email IN ('test@smartflowai.com', 'test@smartflow.pl'))
);

CREATE POLICY "Users can delete their own processes" ON processes
FOR DELETE USING (
    auth.email() = user_email 
    OR (auth.email() IS NULL AND user_email IN ('test@smartflowai.com', 'test@smartflow.pl'))
);

-- Sprawdź istniejące procesy
SELECT id, user_email, title, created_at FROM processes ORDER BY created_at DESC LIMIT 10; 