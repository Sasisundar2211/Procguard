'use client';

import React from 'react';

const OfflineScreen = () => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
      <h1>Backend Offline</h1>
      <p>The backend service is currently unavailable. Please try again later.</p>
    </div>
  );
};

export default OfflineScreen;