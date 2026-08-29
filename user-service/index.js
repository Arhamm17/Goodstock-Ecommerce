require('dotenv').config();
const express = require('express');
const { createClient } = require('redis');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

const redisClient = createClient({ url: process.env.REDIS_URL });
redisClient.on('error', (err) => console.error('Redis error:', err));

(async () => {
  await redisClient.connect();
  console.log('User Service: Redis connected');
})();

app.get('/health', (req, res) => res.json({ status: 'ok', service: 'user-service' }));

app.post('/session', async (req, res) => {
  const { userId, data } = req.body;
  await redisClient.set(`session:${userId}`, JSON.stringify(data), { EX: 3600 });
  res.status(201).json({ message: 'Session created', userId });
});

app.get('/session/:userId', async (req, res) => {
  const session = await redisClient.get(`session:${req.params.userId}`);
  if (!session) return res.status(404).json({ error: 'No session found' });
  res.json(JSON.parse(session));
});

const PORT = process.env.PORT || 4003;
app.listen(PORT, () => console.log(`User Service running on port ${PORT}`));