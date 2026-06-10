-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table: whatsapp_instances
CREATE TABLE IF NOT EXISTS public.whatsapp_instances (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    instance_name TEXT NOT NULL,
    whatsapp_number TEXT,
    status TEXT DEFAULT 'DISCONNECTED' CHECK (status IN ('DISCONNECTED', 'QRCODE', 'CONNECTED')),
    qrcode_base64 TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Table: chats
CREATE TABLE IF NOT EXISTS public.chats (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    instance_id UUID REFERENCES public.whatsapp_instances(id) ON DELETE CASCADE,
    contact_name TEXT,
    contact_number TEXT NOT NULL,
    contact_avatar TEXT,
    last_message_preview TEXT,
    status TEXT DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'OPEN', 'CLOSED')),
    assigned_to UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Table: messages
CREATE TABLE IF NOT EXISTS public.messages (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    chat_id UUID REFERENCES public.chats(id) ON DELETE CASCADE,
    instance_id UUID REFERENCES public.whatsapp_instances(id) ON DELETE CASCADE,
    whatsapp_message_id TEXT,
    sender TEXT NOT NULL CHECK (sender IN ('CUSTOMER', 'ATTENDANT', 'SYSTEM')),
    content TEXT,
    media_url TEXT,
    media_type TEXT CHECK (media_type IN ('image', 'video', 'audio', 'document')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Realtime Setup
-- Supabase requires explicit publication of tables for Realtime
BEGIN;
  -- remove the supabase_realtime publication if it exists
  DROP PUBLICATION IF EXISTS supabase_realtime;
  -- re-create it
  CREATE PUBLICATION supabase_realtime;
COMMIT;
-- Add tables to the publication
ALTER PUBLICATION supabase_realtime ADD TABLE public.whatsapp_instances;
ALTER PUBLICATION supabase_realtime ADD TABLE public.chats;
ALTER PUBLICATION supabase_realtime ADD TABLE public.messages;

-- Row Level Security (RLS)
ALTER TABLE public.whatsapp_instances ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chats ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.messages ENABLE ROW LEVEL SECURITY;

-- Policies for whatsapp_instances
-- (Example: allow read/write to all authenticated users for now, or you can restrict to user_id)
CREATE POLICY "Allow all authenticated access to whatsapp_instances" ON public.whatsapp_instances
    FOR ALL USING (auth.role() = 'authenticated');

-- Policies for chats
CREATE POLICY "Allow authenticated access to chats" ON public.chats
    FOR ALL USING (auth.role() = 'authenticated');

-- Policies for messages
CREATE POLICY "Allow authenticated access to messages" ON public.messages
    FOR ALL USING (auth.role() = 'authenticated');
