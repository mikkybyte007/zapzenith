import { createClient } from '@supabase/supabase-js'

// Variáveis de ambiente devem ser configuradas no arquivo .env localmente
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://sua-url.supabase.co'
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'sua-anon-key'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
