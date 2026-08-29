require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

mongoose.connect(process.env.MONGO_URI)
  .then(() => console.log('Product Service: MongoDB connected'))
  .catch(err => console.error('Mongo connection error:', err));

const productSchema = new mongoose.Schema({
  name: { type: String, required: true },
  price: { type: Number, required: true },
  stock: { type: Number, default: 0 },
});
const Product = mongoose.model('Product', productSchema);

app.get('/health', (req, res) => res.json({ status: 'ok', service: 'product-service' }));

app.get('/products', async (req, res) => {
  const products = await Product.find();
  res.json(products);
});

app.post('/products', async (req, res) => {
  const product = new Product(req.body);
  await product.save();
  res.status(201).json(product);
});

app.get('/products/:id', async (req, res) => {
  const product = await Product.findById(req.params.id);
  if (!product) return res.status(404).json({ error: 'Not found' });
  res.json(product);
});

const PORT = process.env.PORT || 4001;
app.listen(PORT, () => console.log(`Product Service running on port ${PORT}`));