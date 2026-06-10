import React, { useState, useEffect, useRef } from 'react';
import { supabase } from '../supabaseClient';

export default function ChatArea({ chat, instanceId }) {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    const fetchMessages = async () => {
      const { data } = await supabase
        .from('messages')
        .select('*')
        .eq('chat_id', chat.id)
        .order('created_at', { ascending: true });
        
      if (data) setMessages(data);
    };

    fetchMessages();

    const channel = supabase.channel(`messages-${chat.id}`)
      .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'messages', filter: `chat_id=eq.${chat.id}` }, (payload) => {
        setMessages(prev => [...prev, payload.new]);
      })
      .subscribe();

    return () => supabase.removeChannel(channel);
  }, [chat.id]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || isSending) return;

    setIsSending(true);
    try {
      // O FastAPI Backend está rodando na porta 8000 localmente (ou via Ngrok)
      // Ajuste a URL base conforme necessário
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      
      const response = await fetch(`${apiUrl}/send-message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          number: chat.contact_number,
          text: newMessage,
          chat_id: chat.id
        })
      });

      if (!response.ok) throw new Error('Falha ao enviar mensagem');
      
      setNewMessage('');
    } catch (error) {
      console.error('Erro ao enviar:', error);
      alert('Erro ao enviar mensagem.');
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-background relative">
      {/* Header */}
      <div className="h-16 border-b border-surface/50 bg-surface/80 flex items-center px-6 shadow-sm z-10">
        <div className="w-10 h-10 bg-gradient-to-br from-primary to-purple-600 rounded-full flex items-center justify-center mr-4 text-white font-bold shadow-md">
          {chat.contact_name.charAt(0).toUpperCase()}
        </div>
        <div>
          <h2 className="font-bold text-textMain text-lg leading-tight">{chat.contact_name}</h2>
          <p className="text-xs text-textMuted">{chat.contact_number}</p>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((msg) => {
          const isCustomer = msg.sender === 'CUSTOMER';
          return (
            <div key={msg.id} className={`flex ${isCustomer ? 'justify-start' : 'justify-end'}`}>
              <div 
                className={`max-w-[70%] rounded-2xl px-5 py-3 shadow-md ${
                  isCustomer 
                    ? 'bg-messageReceived text-textMain rounded-tl-sm' 
                    : 'bg-primary text-white rounded-tr-sm'
                }`}
              >
                <p className="whitespace-pre-wrap">{msg.content}</p>
                <div className={`text-[10px] mt-1 text-right opacity-70`}>
                  {new Date(msg.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                </div>
              </div>
            </div>
          );
        })}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 bg-surface/90 border-t border-white/5 backdrop-blur-md">
        <form onSubmit={handleSendMessage} className="flex gap-2 relative">
          <input 
            type="text" 
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Digite sua mensagem..." 
            className="flex-1 bg-background border border-white/10 rounded-full px-6 py-3 text-textMain focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-all"
            disabled={isSending}
          />
          <button 
            type="submit"
            disabled={!newMessage.trim() || isSending}
            className="bg-primary hover:bg-primaryHover text-white rounded-full w-12 h-12 flex items-center justify-center transition-transform hover:scale-105 active:scale-95 disabled:opacity-50 disabled:hover:scale-100 shadow-lg shadow-primary/30"
          >
            {isSending ? (
              <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 ml-1" viewBox="0 0 20 20" fill="currentColor">
                <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
              </svg>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
