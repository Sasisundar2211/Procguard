'use client';

import { createContext, useState, useEffect, ReactNode, useContext } from 'react';

// Define the shape of the context data
interface ApiHealth {
  healthy: boolean;
}

const ApiHealthContext = createContext<ApiHealth>({ healthy: false });

// Custom hook to use the API health context
export const useApiHealth = () => useContext(ApiHealthContext);

// A placeholder loading component
const MinimalBootLoader = () => (
  <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
    <p>Loading...</p>
  </div>
);


export function ApiHealthProvider({ children }: { children: ReactNode }) {
  const [healthy, setHealthy] = useState(false);
  const [checked, setChecked] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    // 3 second timeout for the health check
    const timeout = setTimeout(() => {
      controller.abort();
    }, 3000);

    const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
    fetch(`${API_URL}/health`, {
      signal: controller.signal,
      cache: "no-store", // Ensure fresh check
    })
      .then(res => {
        if (res.ok) {
          setHealthy(true);
        } else {
          setHealthy(false);
        }
      })
      .catch(() => {
        setHealthy(false);
      })
      .finally(() => {
        clearTimeout(timeout);
        setChecked(true);
      });

    // Cleanup function to abort fetch on unmount
    return () => {
      controller.abort();
      clearTimeout(timeout);
    };
  }, []);

  if (!checked) {
    return <MinimalBootLoader />;
  }

  return (
    <ApiHealthContext.Provider value={{ healthy }}>
      {children}
    </ApiHealthContext.Provider>
  );
}