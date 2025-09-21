// src/App.jsx
import React from 'react';
import { createBrowserRouter, RouterProvider, Link, Outlet } from 'react-router-dom';
import { useAuth0, withAuthenticationRequired } from '@auth0/auth0-react';

import HomePage from './pages/HomePage';
import HomeownerDashboard from './pages/HomeownerDashboard';

// This HOC (Higher-Order Component) protects our dashboard page
const ProtectedHomeownerDashboard = withAuthenticationRequired(HomeownerDashboard, {
  onRedirecting: () => <div>Loading...</div>, // Optional: show a loading indicator
});

// A simple layout component with navigation
const Layout = () => {
  const { isAuthenticated, loginWithRedirect, logout } = useAuth0();
  return (
    <div style={{
      width: '100vw',
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column'
    }}>
      <nav style={{
        padding: '20px 40px',
        borderBottom: '1px solid #ccc',
        display: 'flex',
        gap: '20px',
        alignItems: 'center',
        width: '100%',
        boxSizing: 'border-box'
      }}>
        <div style={{ fontWeight: 'bold', fontSize: '20px', color: '#2196F3' }}>Properly</div>
        <Link to="/">Home</Link>
        <Link to="/dashboard">Dashboard</Link>
        <div style={{ marginLeft: 'auto' }}>
          {!isAuthenticated ? (
            <button onClick={() => loginWithRedirect()}>Log In</button>
          ) : (
            <button onClick={() => logout({ logoutParams: { returnTo: window.location.origin } })}>Log Out</button>
          )}
        </div>
      </nav>
      <main style={{
        flex: 1,
        padding: '0 40px',
        width: '100%',
        boxSizing: 'border-box'
      }}>
        <Outlet /> {/* Child routes will render here */}
      </main>
    </div>
  );
};

// Define the application's routes
const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      {
        index: true,
        element: <HomePage />,
      },
      {
        path: 'dashboard',
        element: <ProtectedHomeownerDashboard />,
      },
    ],
  },
]);

function App() {
  return <RouterProvider router={router} />;
}

export default App;