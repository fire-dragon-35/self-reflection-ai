// api.ts

import axios, { AxiosError } from 'axios';

const API_URL = import.meta.env.VITE_API_URL;

export interface ApiError {
  message: string;
  status?: number;
}

export function handleApiError(error: unknown): ApiError {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError;
    
    if (axiosError.response?.status === 429) {
      return { 
        message: 'Rate limit exceeded.',
        status: 429 
      };
    }
    
    if (axiosError.response?.status === 400) {
      return { 
        message: 'Not enough conversation data. Send more messages first.',
        status: 400 
      };
    }
    
    if (axiosError.response?.status === 401) {
      return { 
        message: 'Please sign in again.',
        status: 401 
      };
    }
    
    return { 
      message: 'Something went wrong. Please try again.',
      status: axiosError.response?.status 
    };
  }
  
  return { message: 'Network error. Please check your connection.' };
}

export async function getMessages(token: string) {
  const res = await axios.get(`${API_URL}/api/messages`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return res.data.messages || [];
}

export async function sendChat(token: string, message: string) {
  const res = await axios.post(`${API_URL}/api/chat`, 
    { message },
    { headers: { Authorization: `Bearer ${token}` } }
  );
  return res.data.response;
}

export async function getAnalysis(token: string) {
  const res = await axios.get(`${API_URL}/api/analysis`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return res.data.analysis[0];
}

export async function triggerAnalysisAPI(token: string) {
  const res = await axios.post(`${API_URL}/api/analyse`, {}, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return res.data.analysis;
}

export async function clearMessages(token: string) {
  const res = await axios.delete(`${API_URL}/api/messages`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return res.data.message;
}

export { API_URL };