// src/services/api.js (Debug version)
import axios from 'axios';

// Temporarily hardcode the API URL to test
const API_BASE_URL = 'http://127.0.0.1:8000';

console.log('API Base URL:', API_BASE_URL); // Debug log

// Create an Axios instance with the base URL
const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

/**
 * Fetches all maintenance requests for the authenticated user.
 * @param {string} token - The JWT access token.
 * @returns {Promise<Array>} A promise that resolves to an array of requests.
 */
export const getRequests = async (token) => {
  try {
    console.log('Making GET request to:', `${API_BASE_URL}/homeowner/requests`);
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
 * @param {Object} requestData - The data for the new request (e.g., { title, description, homeowner_id }).
 * @param {string} token - The JWT access token.
 * @returns {Promise<Object>} A promise that resolves to the newly created request object.
 */
export const createRequest = async (requestData, token) => {
  try {
    console.log('Making POST request to:', `${API_BASE_URL}/homeowner/requests`);
    console.log('Request data:', requestData);

    const response = await apiClient.post('/homeowner/requests', requestData, {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error creating request:', error);
    console.error('Response data:', error.response?.data);
    console.error('Response status:', error.response?.status);
    throw error;
  }
};