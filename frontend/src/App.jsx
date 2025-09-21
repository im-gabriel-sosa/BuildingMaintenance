// src/App.jsx

import { useAuth0 } from '@auth0/auth0-react';

function App() {
  const { 
    isAuthenticated, 
    loginWithRedirect, 
    logout, 
    user, 
    isLoading 
  } = useAuth0();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div style={{ padding: '50px', textAlign: 'center' }}>
      <h1>Property Maintenance Platform</h1>
      {isAuthenticated ? (
        <div>
          <h2>Welcome, {user.name}!</h2>
          <p>Your email is: {user.email}</p>
          <button 
            onClick={() => logout({ logoutParams: { returnTo: window.location.origin } })}
            style={{ marginTop: '20px', padding: '10px 20px', cursor: 'pointer' }}
          >
            Log Out
          </button>
        </div>
      ) : (
        <div>
          <p>Please log in to continue.</p>
          <button 
            onClick={() => loginWithRedirect()}
            style={{ marginTop: '20px', padding: '10px 20px', cursor: 'pointer' }}
          >
            Log In
          </button>
        </div>
      )}
    </div>
  );
}

export default App;