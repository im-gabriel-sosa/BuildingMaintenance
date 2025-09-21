// src/services/api.js (Production version)
import axios from 'axios';

// Use environment variable, fall back to local development URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

console.log('API Base URL:', API_BASE_URL);

// Create an Axios instance with the base URL
const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

/**
 * Fetches all maintenance requests for the authenticated user.
 */
export const getRequests = async (token) => {
  try {
    const response = await apiClient.get('/homeowner/requests', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching requests:', error);
    throw error;
  }
};

/**
 * Creates a new maintenance request.
 */
export const createRequest = async (requestData, token) => {
  try {
    const response = await apiClient.post('/homeowner/requests', requestData, {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error creating request:', error);
    throw error;
  }
};