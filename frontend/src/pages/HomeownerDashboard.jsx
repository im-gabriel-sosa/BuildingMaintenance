// src/pages/HomeownerDashboard.jsx
import React, { useState, useEffect, useCallback } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import { getRequests, createRequest, updateRequest, deleteRequest } from '../services/api';

const HomeownerDashboard = () => {
  const { user, getAccessTokenSilently } = useAuth0();
  const [requests, setRequests] = useState([]);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editingRequest, setEditingRequest] = useState(null);
  const [editTitle, setEditTitle] = useState('');
  const [editDescription, setEditDescription] = useState('');
  const [editStatus, setEditStatus] = useState('');
  const [editImageUrl, setEditImageUrl] = useState('');

  // Status options
  const statusOptions = [
    { value: 'open', label: 'Open' },
    { value: 'in_progress', label: 'In Progress' },
    { value: 'completed', label: 'Completed' },
    { value: 'canceled', label: 'Canceled' }
  ];

  // A memoized function to fetch requests
  const fetchRequests = useCallback(async () => {
    try {
      const token = await getAccessTokenSilently();
      const data = await getRequests(token);
      setRequests(data);
    } catch (err) {
      setError('Failed to fetch maintenance requests.');
      console.error('Fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, [getAccessTokenSilently]);

  // Fetch requests when the component first loads
  useEffect(() => {
    fetchRequests();
  }, [fetchRequests]);

  // DEBUG: Log requests state whenever it changes
  useEffect(() => {
    if (requests.length > 0) {
      console.log('=== REQUESTS STATE DEBUG ===');
      requests.forEach((req, index) => {
        console.log(`Request ${index}:`, {
          id: req.id,
          idType: typeof req.id,
          title: req.title,
          fullObject: req
        });
      });
    }
  }, [requests]);

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

      // DEBUG LOGS:
      console.log('=== FRONTEND DEBUG ===');
      console.log('User object:', user);
      console.log('User.sub:', user.sub);
      console.log('Title:', title, 'Length:', title.length);
      console.log('Description:', description, 'Length:', description.length);
      console.log('Full payload:', JSON.stringify(newRequestData, null, 2));
      console.log('Token preview:', token.substring(0, 50) + '...');

      const newRequest = await createRequest(newRequestData, token);

      // DEBUG CREATE RESPONSE:
      console.log('=== CREATE RESPONSE DEBUG ===');
      console.log('New request returned:', newRequest);
      console.log('New request ID:', newRequest.id);
      console.log('ID type:', typeof newRequest.id);
      console.log('Full new request object:', JSON.stringify(newRequest, null, 2));

      // Clear form and refresh the list
      setTitle('');
      setDescription('');
      fetchRequests();
    } catch (err) {
      setError('Failed to create the request.');
      console.error('Create error:', err);
      console.error('Error response:', err.response?.data);
      console.error('Validation details:', err.response?.data?.detail);
    }
  };

  const handleEdit = (request) => {
    console.log('=== EDIT DEBUG ===');
    console.log('Editing request:', request);
    console.log('Request ID being edited:', request.id);
    console.log('Request ID type:', typeof request.id);

    setEditingRequest(request.id);
    setEditTitle(request.title);
    setEditDescription(request.description);
    setEditStatus(request.status);
    setEditImageUrl(request.image_url || '');
  };

  const handleCancelEdit = () => {
    setEditingRequest(null);
    setEditTitle('');
    setEditDescription('');
    setEditStatus('');
    setEditImageUrl('');
  };

  const handleUpdateSubmit = async (e) => {
    e.preventDefault();
    if (!editTitle || !editDescription) {
      alert('Please fill in both title and description.');
      return;
    }

    try {
      const token = await getAccessTokenSilently();
      const updateData = {
        title: editTitle,
        description: editDescription,
        status: editStatus,
        image_url: editImageUrl || null,
      };

      console.log('=== UPDATE DEBUG ===');
      console.log('Updating request ID:', editingRequest);
      console.log('Update data:', updateData);
      console.log('Request ID type:', typeof editingRequest);

      await updateRequest(editingRequest, updateData, token);
      // Clear edit state and refresh the list
      setEditingRequest(null);
      setEditTitle('');
      setEditDescription('');
      setEditStatus('');
      setEditImageUrl('');
      fetchRequests();
    } catch (err) {
      setError('Failed to update the request.');
      console.error('Update error:', err);
      console.error('Update error response:', err.response?.data);
    }
  };

  const handleDelete = async (requestId) => {
    if (!window.confirm('Are you sure you want to delete this request?')) {
      return;
    }

    try {
      console.log('=== DELETE DEBUG ===');
      console.log('Deleting request ID:', requestId);
      console.log('Request ID type:', typeof requestId);

      const token = await getAccessTokenSilently();
      await deleteRequest(requestId, token);
      fetchRequests(); // Refresh the list
    } catch (err) {
      setError('Failed to delete the request.');
      console.error('Delete error:', err);
      console.error('Delete error response:', err.response?.data);
    }
  };

  if (loading) return <div>Loading your requests...</div>;
  if (error) return <div style={{ color: 'red' }}>Error: {error}</div>;

  return (
    <div style={{ padding: '20px 0', maxWidth: '800px', margin: '0 auto', width: '100%' }}>
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
                {editingRequest === req.id ? (
                  // Edit form
                  <div>
                    <form onSubmit={handleUpdateSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                      <input
                        type="text"
                        value={editTitle}
                        onChange={(e) => setEditTitle(e.target.value)}
                        style={{ padding: '8px', fontSize: '16px', fontWeight: 'bold' }}
                      />
                      <textarea
                        value={editDescription}
                        onChange={(e) => setEditDescription(e.target.value)}
                        style={{ padding: '8px', minHeight: '60px' }}
                      />
                      <select
                        value={editStatus}
                        onChange={(e) => setEditStatus(e.target.value)}
                        style={{ padding: '8px' }}
                      >
                        {statusOptions.map(option => (
                          <option key={option.value} value={option.value}>
                            {option.label}
                          </option>
                        ))}
                      </select>
                      <input
                        type="url"
                        placeholder="Image URL (optional)"
                        value={editImageUrl}
                        onChange={(e) => setEditImageUrl(e.target.value)}
                        style={{ padding: '8px' }}
                      />
                      <div style={{ display: 'flex', gap: '10px' }}>
                        <button type="submit" style={{ padding: '8px 12px', cursor: 'pointer', backgroundColor: '#4CAF50', color: 'white', border: 'none', borderRadius: '4px' }}>
                          Save Changes
                        </button>
                        <button type="button" onClick={handleCancelEdit} style={{ padding: '8px 12px', cursor: 'pointer', backgroundColor: '#f44336', color: 'white', border: 'none', borderRadius: '4px' }}>
                          Cancel
                        </button>
                      </div>
                    </form>
                  </div>
                ) : (
                  // Display mode
                  <div>
                    <h3 style={{ marginTop: 0 }}>{req.title}</h3>
                    <p>{req.description}</p>
                    {req.image_url && (
                      <div style={{ marginBottom: '10px' }}>
                        <img
                          src={req.image_url}
                          alt="Request"
                          style={{ maxWidth: '300px', maxHeight: '200px', objectFit: 'cover', borderRadius: '4px' }}
                          onError={(e) => { e.target.style.display = 'none'; }}
                        />
                      </div>
                    )}
                    <p><small>Status: <span style={{
                      fontWeight: 'bold',
                      color: req.status === 'open' ? '#FFA500' :
                             req.status === 'completed' ? '#4CAF50' :
                             req.status === 'in_progress' ? '#2196F3' :
                             req.status === 'canceled' ? '#f44336' : '#666'
                    }}>{req.status.replace('_', ' ').toUpperCase()}</span></small></p>
                    <p><small>ID: {req.id} (Debug info)</small></p>
                    {/* Action buttons - available for all requests */}
                    <div style={{ marginTop: '10px', display: 'flex', gap: '10px' }}>
                      <button
                        onClick={() => handleEdit(req)}
                        style={{
                          padding: '8px 12px',
                          cursor: 'pointer',
                          backgroundColor: '#2196F3',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px'
                        }}
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDelete(req.id)}
                        style={{
                          padding: '8px 12px',
                          cursor: 'pointer',
                          backgroundColor: '#f44336',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px'
                        }}
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default HomeownerDashboard;