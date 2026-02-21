// api.ts

import axios, { AxiosError } from 'axios';

const API_URL = import.meta.env.VITE_API_URL;

export interface ApiError {
  message: string;
  status?: number;
}

interface ErrorResponse {
  error?: string;
}

export function handleApiError(error: unknown): ApiError {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<ErrorResponse>;
    
    // use backend error message if available
    const backendMessage = axiosError.response?.data?.error;
    if (backendMessage) {
      return {
        message: backendMessage,
        status: axiosError.response?.status
      };
    }
    
    // fallback for errors without backend message
    if (axiosError.response?.status === 401) {
      return { message: 'Please sign in again.', status: 401 };
    }
    
    return { 
      message: 'Something went wrong. Please try again.',
      status: axiosError.response?.status 
    };
  }
  
  return { message: 'Network error. Please check your connection.' };
}

// GET /health
export async function getHealth() {
  const res = await axios.get(`${API_URL}/health`);
  return res.data;
}

// POST /api/chat
export async function postChat(token: string, message: string) {
  const res = await axios.post(`${API_URL}/api/chat`, 
    { message },
    { headers: { Authorization: `Bearer ${token}` } }
  );
  return res.data.response;
}

// GET /api/messages
export async function getMessages(token: string) {
  const res = await axios.get(`${API_URL}/api/messages`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return res.data.messages || [];
}

// DELETE /api/data
export async function deleteData(token: string) {
  await axios.delete(`${API_URL}/api/data`, {
    headers: { Authorization: `Bearer ${token}` }
  });
}

// GET /api/analysis
export async function getAnalysis(token: string) {
  const res = await axios.get(`${API_URL}/api/analysis`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return res.data.analysis || [];
}

// POST /api/analyse
export async function postAnalyse(token: string) {
  const res = await axios.post(`${API_URL}/api/analyse`, {}, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return {
    analysis: res.data.analysis,
    summary: res.data.summary
  };
}

// DELETE /api/user
export async function deleteUser(token: string) {
  await axios.delete(`${API_URL}/api/user`, {
    headers: { Authorization: `Bearer ${token}` }
  });
}

// GET /api/usage
export async function getUsage(token: string) {
  const res = await axios.get(`${API_URL}/api/usage`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return res.data;
}

// GET /api/summary
export async function getSummary(token: string) {
  const res = await axios.get(`${API_URL}/api/summary`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return res.data.summary || null;
}

// POST /api/create-checkout
export async function postCreateCheckout(token: string, packageType: string) {
  const res = await axios.post(`${API_URL}/api/create-checkout`, 
    { packageType },
    { headers: { Authorization: `Bearer ${token}` } }
  );
  return res.data.url;
}

export { API_URL };