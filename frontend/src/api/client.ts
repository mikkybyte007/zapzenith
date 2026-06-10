import axios from 'axios';
import axiosRetry from 'axios-retry';

const API_URL = import.meta.env.VITE_ZAPZENITH_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // Previne que requisições fiquem penduradas
});

// Configuração do Circuit Breaker / Retry (Exponential Backoff)
axiosRetry(apiClient, {
  retries: 3, // Tenta 3 vezes
  retryDelay: (retryCount) => {
    return retryCount * 2000; // 2s, 4s, 6s
  },
  retryCondition: (error) => {
    // Tenta de novo em falhas de rede ou se a API der 429 (Rate Limit) ou 500 (Erro Interno)
    return axiosRetry.isNetworkOrIdempotentRequestError(error) || 
           error.response?.status === 429 || 
           error.response?.status >= 500;
  },
});

export const sendMessageToApi = async (number: string, text: string, chatId?: string) => {
  return apiClient.post('/send-message', {
    number,
    text,
    chat_id: chatId
  });
};
