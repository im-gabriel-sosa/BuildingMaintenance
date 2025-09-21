import React from 'https://esm.sh/react@18.2.0';
import { createRoot } from 'https://esm.sh/react-dom@18.2.0/client';
import { Auth0Provider, useAuth0 } from 'https://esm.sh/@auth0/auth0-react@2.2.4';
import useSWR from 'https://esm.sh/swr@2.2.4';

const MainApp = () => {
  const {
    isAuthenticated,
    user,
    loginWithRedirect,
    logout,
    getAccessTokenSilently,
  } = useAuth0();

  const { data: accessToken, error } = useSWR(
    isAuthenticated ? ['/api/token', 'access_token'] : null,
    async () => {
      const token = await getAccessTokenSilently();
      return token;
    }
  );

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
      <div className="bg-white p-8 rounded-xl shadow-lg w-full max-w-2xl text-center">
        <h1 className="text-3xl font-bold mb-6 text-gray-800">Property Maintenance Platform</h1>
        {!isAuthenticated ? (
          <div className="space-y-4">
            <p className="text-gray-600">Please log in to continue.</p>
            <button
              onClick={() => loginWithRedirect()}
              className="w-full px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 transition-colors"
            >
              Log In
            </button>
          </div>
        ) : (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-gray-700">Welcome, {user.name}!</h2>
            {accessToken ? (
              <div className="bg-gray-50 p-4 rounded-lg shadow-inner break-all">
                <p className="font-medium text-gray-900 mb-2">Your JWT Access Token:</p>
                <code className="text-sm text-gray-600 select-all">{accessToken}</code>
              </div>
            ) : (
              <p className="text-gray-500">Loading token...</p>
            )}
            <button
              onClick={() => logout({ returnTo: window.location.origin })}
              className="w-full px-6 py-3 bg-red-600 text-white font-semibold rounded-lg shadow-md hover:bg-red-700 transition-colors"
            >
              Log Out
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

// Replace with your Auth0 credentials
const AUTH0_DOMAIN = 'dev-5sxkcuwmv28osx0h.us.auth0.com';
const AUTH0_CLIENT_ID = 'pImKWWsPIePIaGUi5vi0NAEayHJI11ji';  // Replace with your real client ID
const AUTH0_AUDIENCE = 'https://property-maintenance-api';

const container = document.getElementById('root');
const root = createRoot(container);
root.render(
  <Auth0Provider
    domain={AUTH0_DOMAIN}
    clientId={AUTH0_CLIENT_ID}
    authorizationParams={{
      redirect_uri: window.location.origin,
      audience: AUTH0_AUDIENCE,
      scope: 'openid profile email'
    }}
  >
    <MainApp />
  </Auth0Provider>
);
