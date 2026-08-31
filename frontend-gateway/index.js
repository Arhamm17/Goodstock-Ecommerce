require('dotenv').config();
const express = require('express');
const axios = require('axios');
const cors = require('cors');
const path = require('path');

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

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

app.post('/api/products', async (req, res) => {
  try {
    const { data } = await axios.post(`${PRODUCT_SERVICE_URL}/products`, req.body);
    res.status(201).json(data);
  } catch (err) {
    res.status(502).json({ error: 'Product service unreachable' });
  }
});

app.patch('/api/products/:id/stock', async (req, res) => {
  try {
    const { data } = await axios.patch(`${PRODUCT_SERVICE_URL}/products/${req.params.id}/stock`, req.body);
    res.json(data);
  } catch (err) {
    res.status(502).json({ error: 'Product service unreachable' });
  }
});

app.delete('/api/products/:id', async (req, res) => {
  try {
    const { data } = await axios.delete(`${PRODUCT_SERVICE_URL}/products/${req.params.id}`);
    res.json(data);
  } catch (err) {
    res.status(502).json({ error: 'Product service unreachable' });
  }
});

app.get('/api/orders', async (req, res) => {
  try {
    const { data } = await axios.get(`${ORDER_SERVICE_URL}/orders`);
    res.json(data);
  } catch (err) {
    res.status(502).json({ error: 'Order service unreachable' });
  }
});

app.post('/api/orders', async (req, res) => {
  try {
    const { data: products } = await axios.get(`${PRODUCT_SERVICE_URL}/products`);
    const product = products.find(item => String(item._id) === String(req.body.product_id));

    if (!product) {
      return res.status(404).json({ error: 'Product not found' });
    }

    const requestedQty = Number(req.body.quantity);
    if (!Number.isFinite(requestedQty) || requestedQty < 1 || requestedQty > Number(product.stock || 0)) {
      return res.status(400).json({ error: `Only ${product.stock} item(s) available in stock` });
    }

    const { data } = await axios.post(`${ORDER_SERVICE_URL}/orders`, req.body);
    res.status(201).json(data);
  } catch (err) {
    if (err.response && err.response.status === 400) {
      return res.status(400).json(err.response.data);
    }

    res.status(502).json({ error: 'Order service unreachable' });
  }
});

app.put('/api/orders/:id', async (req, res) => {
  try {
    const { data: products } = await axios.get(`${PRODUCT_SERVICE_URL}/products`);
    const product = products.find(item => String(item._id) === String(req.body.product_id));

    if (!product) {
      return res.status(404).json({ error: 'Product not found' });
    }

    const requestedQty = Number(req.body.quantity);
    if (!Number.isFinite(requestedQty) || requestedQty < 1 || requestedQty > Number(product.stock || 0)) {
      return res.status(400).json({ error: `Only ${product.stock} item(s) available in stock` });
    }

    const { data } = await axios.put(`${ORDER_SERVICE_URL}/orders/${req.params.id}`, req.body);
    res.json(data);
  } catch (err) {
    if (err.response && err.response.status === 400) {
      return res.status(400).json(err.response.data);
    }

    res.status(502).json({ error: 'Order service unreachable' });
  }
});

app.delete('/api/orders/:id', async (req, res) => {
  try {
    const { data } = await axios.delete(`${ORDER_SERVICE_URL}/orders/${req.params.id}`);
    res.json(data);
  } catch (err) {
    res.status(502).json({ error: 'Order service unreachable' });
  }
});

app.post('/api/session', async (req, res) => {
  try {
    const { data } = await axios.post(`${USER_SERVICE_URL}/session`, req.body);
    res.status(201).json(data);
  } catch (err) {
    res.status(502).json({ error: 'User service unreachable' });
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