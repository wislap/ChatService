import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:25578',
  timeout: 10000, // 10-second timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;
