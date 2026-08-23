/**
 * TRACE Frontend API Client
 * Configurable HTTP client targeting VITE_API_BASE_URL (default: http://127.0.0.1:8000)
 */

const getBaseUrl = () => {
  const envUrl = import.meta.env.VITE_API_BASE_URL;
  if (envUrl === undefined || envUrl === null) {
    return 'http://127.0.0.1:8000';
  }
  return envUrl.replace(/\/$/, '');
};

const BASE_URL = getBaseUrl();

export async function fetchApi(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
  
  const defaultHeaders = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
  };

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    });

    if (!response.ok) {
      const errorBody = await response.text();
      let errorMessage = `HTTP Error ${response.status}: ${response.statusText}`;
      try {
        const parsed = JSON.parse(errorBody);
        if (parsed.detail) {
          errorMessage = typeof parsed.detail === 'string' ? parsed.detail : JSON.stringify(parsed.detail);
        }
      } catch {
        // use raw message
      }
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error) {
    if (error.name === 'TypeError' || error.message.toLowerCase().includes('fetch') || error.message.toLowerCase().includes('network')) {
      throw new Error('Backend unreachable. Make sure the TRACE backend server is running at ' + BASE_URL);
    }
    throw error;
  }
}
