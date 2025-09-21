// src/services/api.js (Updated with edit and delete)
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
 * Fetches a specific maintenance request by ID.
 */
export const getRequestById = async (requestId, token) => {
  try {
    const response = await apiClient.get(`/homeowner/requests/${requestId}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching request:', error);
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

/**
 * Updates an existing maintenance request.
 * Can update title, description, status, and image_url
 */
export const updateRequest = async (requestId, updateData, token) => {
  try {
    const response = await apiClient.put(`/homeowner/requests/${requestId}`, updateData, {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error updating request:', error);
    throw error;
  }
};

/**
 * Deletes a maintenance request.
 */
export const deleteRequest = async (requestId, token) => {
  try {
    const response = await apiClient.delete(`/homeowner/requests/${requestId}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error deleting request:', error);
    throw error;
  }
};