// src/supabaseClient.js
import { createClient } from '@supabase/supabase-js';

// Ganti dengan URL dan kunci ANON (publik) Supabase Anda
const supabaseUrl = 'https://ambmnezomkgksdcbzbqb.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFtYm1uZXpvbWtna3NkY2J6YnFiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEzODM3NDgsImV4cCI6MjA3Njk1OTc0OH0.1P7zL-5cN4uzpEqPZR4Z18nMoFNuxdgTReCUbN28scE';

export const supabase = createClient(supabaseUrl, supabaseKey);