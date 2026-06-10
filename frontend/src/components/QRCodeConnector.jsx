import React, { useState, useEffect } from 'react';
import { supabase } from '../supabaseClient';

export default function QRCodeConnector({ instanceId, status }) {
  const [qrCodeData, setQrCodeData] = useState(null);

  useEffect(() => {
    const fetchQR = async () => {
      const { data } = await supabase
        .from('whatsapp_instances')
        .select('qrcode_base64')
        .eq('id', instanceId)
        .single();
        
      if (data && data.qrcode_base64) {
        setQrCodeData(data.qrcode_base64);
      }
    };
    
    if (status === 'QRCODE') {
      fetchQR();
    }

    const channel = supabase.channel('qr-updates')
      .on('postgres_changes', { event: 'UPDATE', schema: 'public', table: 'whatsapp_instances', filter: `id=eq.${instanceId}` }, (payload) => {
        if (payload.new.status === 'QRCODE' && payload.new.qrcode_base64) {
          setQrCodeData(payload.new.qrcode_base64);
        }
      })
      .subscribe();

    return () => supabase.removeChannel(channel);
  }, [instanceId, status]);

  return (
    <div className="glass-panel p-10 rounded-2xl flex flex-col items-center w-full max-w-md text-center transform transition-all duration-500 hover:scale-[1.02]">
      <div className="w-16 h-16 bg-gradient-to-tr from-primary to-purple-500 rounded-2xl flex items-center justify-center mb-6 shadow-lg shadow-primary/20">
        <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
        </svg>
      </div>
      
      <h2 className="text-3xl font-extrabold mb-2 tracking-tight text-white">Conectar WhatsApp</h2>
      
      {status === 'DISCONNECTED' && (
        <p className="text-textMuted mb-6">Aguardando inicialização do motor. Por favor, certifique-se de que a API Python está rodando.</p>
      )}
      
      {status === 'QRCODE' && (
        <>
          <p className="text-textMuted mb-8 text-sm">Escaneie o QR Code abaixo com seu WhatsApp para conectar a instância.</p>
          <div className="bg-white p-4 rounded-xl shadow-2xl relative">
            <div className="absolute inset-0 bg-primary/10 animate-pulse rounded-xl pointer-events-none"></div>
            {qrCodeData ? (
              <img src={qrCodeData} alt="QR Code WhatsApp" className="w-64 h-64 object-contain rounded-lg" />
            ) : (
              <div className="w-64 h-64 flex items-center justify-center text-gray-400">
                <svg className="animate-spin h-8 w-8 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
