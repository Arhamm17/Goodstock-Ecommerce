require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

const productSchema = new mongoose.Schema({
  name: { type: String, required: true },
  price: { type: Number, required: true },
  stock: { type: Number, default: 0 },
});

const Product = mongoose.model('Product', productSchema);

app.get('/health', (req, res) => {
  if (mongoose.connection.readyState !== 1) {
    return res.status(503).json({
      status: 'unhealthy',
      service: 'product-service',
      database: 'disconnected',
    });
  }

  return res.json({
    status: 'ok',
    service: 'product-service',
    database: 'connected',
  });
});

app.get('/products', async (req, res) => {
  try {
    const products = await Product.find();
    res.json(products);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Could not fetch products' });
  }
});

app.post('/products', async (req, res) => {
  try {
    const { name, price, stock } = req.body || {};
    const productName = typeof name === 'string' ? name.trim() : '';
    const parsedPrice = Number(price);
    const parsedStock = Number(stock);

    if (!productName || !Number.isFinite(parsedPrice) || !Number.isFinite(parsedStock)) {
      return res.status(400).json({
        error: 'Name, price, and stock are required',
      });
    }

    if (parsedPrice < 0 || parsedStock < 0) {
      return res.status(400).json({
        error: 'Price and stock cannot be negative',
      });
    }

    const product = new Product({
      name: productName,
      price: parsedPrice,
      stock: parsedStock,
    });

    await product.save();
    res.status(201).json(product);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Could not create product' });
  }
});

app.get('/products/:id', async (req, res) => {
  try {
    const product = await Product.findById(req.params.id);

    if (!product) {
      return res.status(404).json({ error: 'Not found' });
    }

    res.json(product);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Could not fetch product' });
  }
});

app.patch('/products/:id/stock', async (req, res) => {
  try {
    const product = await Product.findById(req.params.id);

    if (!product) {
      return res.status(404).json({ error: 'Product not found' });
    }

    const delta = Number(req.body?.delta);

    if (!Number.isFinite(delta) || delta === 0) {
      return res.status(400).json({
        error: 'delta must be a non-zero number',
      });
    }

    const currentStock = Number(product.stock || 0);
    const newStock = currentStock + delta;

    if (newStock < 0) {
      return res.status(400).json({
        error: `Insufficient stock. Available stock: ${currentStock}`,
      });
    }

    product.stock = newStock;
    await product.save();

    return res.json(product);
  } catch (error) {
    console.error(error);
    return res.status(500).json({
      error: 'Could not update product stock',
    });
  }
});

app.delete('/products/:id', async (req, res) => {
  try {
    const product = await Product.findByIdAndDelete(req.params.id);

    if (!product) {
      return res.status(404).json({ error: 'Not found' });
    }

    res.json({
      deleted: true,
      product,
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Could not delete product' });
  }
});

const PORT = process.env.PORT || 4001;

async function startServer() {
  try {
    await mongoose.connect(process.env.MONGO_URI);

    console.log('Product Service: MongoDB connected');

    app.listen(PORT, '0.0.0.0', () => {
      console.log(`Product Service running on port ${PORT}`);
    });
  } catch (error) {
    console.error('Mongo connection error:', error);
    process.exit(1);
  }
}

startServer();