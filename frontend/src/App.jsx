import React, { useState, useEffect } from 'react';
import { supabase } from './supabaseClient';
import QRCodeConnector from './components/QRCodeConnector';
import ChatList from './components/ChatList';
import ChatArea from './components/ChatArea';

// Substitua pelo ID da instância que você configurou no backend
const INSTANCE_ID = import.meta.env.VITE_INSTANCE_ID || '123e4567-e89b-12d3-a456-426614174000';

function App() {
  const [connectionStatus, setConnectionStatus] = useState('DISCONNECTED');
  const [activeChat, setActiveChat] = useState(null);

  useEffect(() => {
    // Busca o status inicial
    const fetchStatus = async () => {
      const { data, error } = await supabase
        .from('whatsapp_instances')
        .select('status')
        .eq('id', INSTANCE_ID)
        .single();
      
      if (data) setConnectionStatus(data.status);
    };
    
    fetchStatus();

    // Inscreve-se em mudanças na tabela de instâncias
    const channel = supabase.channel('schema-db-changes')
      .on(
        'postgres_changes',
        {
          event: 'UPDATE',
          schema: 'public',
          table: 'whatsapp_instances',
          filter: `id=eq.${INSTANCE_ID}`
        },
        (payload) => {
          console.log('Status updated!', payload);
          setConnectionStatus(payload.new.status);
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, []);

  if (connectionStatus !== 'CONNECTED') {
    return (
      <div className="flex items-center justify-center h-screen bg-background text-textMain">
        <QRCodeConnector instanceId={INSTANCE_ID} status={connectionStatus} />
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-background overflow-hidden text-textMain">
      <div className="w-1/3 border-r border-surface/50 h-full flex flex-col bg-surface/30">
        <div className="p-4 bg-surface/80 shadow-md">
          <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-purple-400">
            Verthos Zenith
          </h1>
          <p className="text-xs text-messageSent mt-1 flex items-center">
            <span className="w-2 h-2 rounded-full bg-messageSent mr-2 inline-block"></span>
            Conectado
          </p>
        </div>
        <div className="flex-1 overflow-y-auto">
          <ChatList instanceId={INSTANCE_ID} onSelectChat={setActiveChat} activeChatId={activeChat?.id} />
        </div>
      </div>
      
      <div className="flex-1 flex flex-col h-full bg-background relative">
        {activeChat ? (
          <ChatArea chat={activeChat} instanceId={INSTANCE_ID} />
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-textMuted p-8 text-center glass-panel m-auto rounded-xl w-1/2">
            <div className="w-24 h-24 mb-6 rounded-full bg-surface flex items-center justify-center border border-white/10 shadow-inner">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 text-primary/60" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-textMain mb-2">Selecione uma conversa</h2>
            <p>Clique em um chat ao lado para visualizar as mensagens e começar a atender.</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
