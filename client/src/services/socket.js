import io from 'socket.io-client';

const SOCKET_URL = process.env.NODE_ENV === 'production' 
  ? process.env.REACT_APP_SOCKET_URL 
  : 'http://localhost:4001';

export const socket = io(SOCKET_URL, {
  transports: ['websocket', 'polling'],
  path: '/socket.io',
  reconnection: true,
  reconnectionAttempts: 5,
  reconnectionDelay: 1000,
});

// Socket event listeners for connection status
socket.on('connect', () => {
  console.log('Socket connected');
});

socket.on('disconnect', () => {
  console.log('Socket disconnected');
});

socket.on('connect_error', (error) => {
  console.error('Socket connection error:', error);
});

// Export socket instance
export default socket;
