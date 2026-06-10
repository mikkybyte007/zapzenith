import React, { useState, useEffect } from 'react';
import { supabase } from '../supabaseClient';

export default function ChatList({ instanceId, onSelectChat, activeChatId }) {
  const [chats, setChats] = useState([]);

  useEffect(() => {
    const fetchChats = async () => {
      const { data } = await supabase
        .from('chats')
        .select('*')
        .eq('instance_id', instanceId)
        .order('updated_at', { ascending: false });
        
      if (data) setChats(data);
    };

    fetchChats();

    const channel = supabase.channel('chats-updates')
      .on('postgres_changes', { event: '*', schema: 'public', table: 'chats', filter: `instance_id=eq.${instanceId}` }, (payload) => {
        fetchChats(); // Recarrega para manter a ordem, em um app real você atualizaria o array
      })
      .subscribe();

    return () => supabase.removeChannel(channel);
  }, [instanceId]);

  return (
    <div className="flex flex-col h-full bg-surface/40">
      {chats.length === 0 ? (
        <div className="p-6 text-center text-textMuted text-sm mt-10">
          Nenhuma conversa ativa no momento.
        </div>
      ) : (
        chats.map((chat) => (
          <div 
            key={chat.id} 
            onClick={() => onSelectChat(chat)}
            className={`p-4 border-b border-surface cursor-pointer hover:bg-surface/80 transition-colors flex items-center group relative overflow-hidden ${activeChatId === chat.id ? 'bg-surface border-l-4 border-l-primary' : ''}`}
          >
            {activeChatId === chat.id && (
              <div className="absolute inset-0 bg-gradient-to-r from-primary/10 to-transparent pointer-events-none"></div>
            )}
            
            <div className="w-12 h-12 bg-gradient-to-br from-surface to-slate-700 rounded-full flex items-center justify-center mr-4 shadow-md font-bold text-lg border border-white/5 group-hover:border-primary/50 transition-colors">
              {chat.contact_name.charAt(0).toUpperCase()}
            </div>
            
            <div className="flex-1 overflow-hidden">
              <div className="flex justify-between items-center mb-1">
                <h3 className="font-semibold text-textMain truncate pr-2">{chat.contact_name}</h3>
                <span className="text-xs text-textMuted whitespace-nowrap">
                  {new Date(chat.updated_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                </span>
              </div>
              <p className="text-sm text-textMuted truncate">{chat.last_message_preview || '...'}</p>
            </div>
          </div>
        ))
      )}
    </div>
  );
}
