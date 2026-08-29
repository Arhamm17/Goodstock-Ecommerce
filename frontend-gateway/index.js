require('dotenv').config();
const express = require('express');
const axios = require('axios');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

const { PRODUCT_SERVICE_URL, ORDER_SERVICE_URL, USER_SERVICE_URL } = process.env;

app.get('/health', (req, res) => res.json({ status: 'ok', service: 'frontend-gateway' }));

app.get('/api/products', async (req, res) => {
  try {
    const { data } = await axios.get(`${PRODUCT_SERVICE_URL}/products`);
    res.json(data);
  } catch (err) {
    res.status(502).json({ error: 'Product service unreachable' });
  }
});

app.post('/api/orders', async (req, res) => {
  try {
    const { data } = await axios.post(`${ORDER_SERVICE_URL}/orders`, req.body);
    res.status(201).json(data);
  } catch (err) {
    res.status(502).json({ error: 'Order service unreachable' });
  }
});

app.get('/api/session/:userId', async (req, res) => {
  try {
    const { data } = await axios.get(`${USER_SERVICE_URL}/session/${req.params.userId}`);
    res.json(data);
  } catch (err) {
    res.status(502).json({ error: 'User service unreachable' });
  }
});

app.get('/api/status', async (req, res) => {
  const services = { product: PRODUCT_SERVICE_URL, order: ORDER_SERVICE_URL, user: USER_SERVICE_URL };
  const status = {};
  for (const [name, url] of Object.entries(services)) {
    try {
      await axios.get(`${url}/health`);
      status[name] = 'up';
    } catch {
      status[name] = 'down';
    }
  }
  res.json(status);
});

const PORT = process.env.PORT || 4000;
app.listen(PORT, () => console.log(`Frontend Gateway running on port ${PORT}`));