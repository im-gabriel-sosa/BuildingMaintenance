// src/pages/HomeownerDashboard.jsx

import React, { useState, useEffect, useCallback } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import { getRequests, createRequest } from '../services/api';

const HomeownerDashboard = () => {
  const { user, getAccessTokenSilently } = useAuth0();
  const [requests, setRequests] = useState([]);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // A memoized function to fetch requests
  const fetchRequests = useCallback(async () => {
    try {
      const token = await getAccessTokenSilently();
      const data = await getRequests(token);
      setRequests(data);
    } catch (err) {
      setError('Failed to fetch maintenance requests.');
    } finally {
      setLoading(false);
    }
  }, [getAccessTokenSilently]);

  // Fetch requests when the component first loads
  useEffect(() => {
    fetchRequests();
  }, [fetchRequests]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title || !description) {
      alert('Please fill in both title and description.');
      return;
    }

    try {
      const token = await getAccessTokenSilently();
      const newRequestData = {
        title,
        description,
        homeowner_id: user.sub, // The user's unique ID from Auth0
      };
      await createRequest(newRequestData, token);
      // Clear form and refresh the list
      setTitle('');
      setDescription('');
      fetchRequests();
    } catch (err) {
      setError('Failed to create the request.');
    }
  };

  if (loading) return <div>Loading your requests...</div>;
  if (error) return <div style={{ color: 'red' }}>Error: {error}</div>;

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h1>My Maintenance Requests</h1>

      <div style={{ background: '#f9f9f9', padding: '20px', borderRadius: '8px', marginBottom: '30px' }}>
        <h2>Create New Request</h2>
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <input
            type="text"
            placeholder="Request Title (e.g., Leaky Faucet)"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            style={{ padding: '8px' }}
          />
          <textarea
            placeholder="Describe the issue..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            style={{ padding: '8px', minHeight: '80px' }}
          />
          <button type="submit" style={{ padding: '10px', cursor: 'pointer' }}>Submit Request</button>
        </form>
      </div>

      <div>
        <h2>Submitted Requests</h2>
        {requests.length === 0 ? (
          <p>You have not submitted any requests yet.</p>
        ) : (
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {requests.map((req) => (
              <li key={req.id} style={{ border: '1px solid #ddd', padding: '15px', borderRadius: '5px', marginBottom: '10px' }}>
                <h3 style={{ marginTop: 0 }}>{req.title}</h3>
                <p>{req.description}</p>
                <p><small>Status: {req.status}</small></p>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default HomeownerDashboard;