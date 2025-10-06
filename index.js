const express = require('express');
const mongoose = require('mongoose');
const multer = require('multer');
const cors = require('cors');
const path = require('path');
const fs = require('fs');
require('dotenv').config();

const app = express();
app.use(cors());
app.use(express.json());

// Ensure 'uploads' directory exists
const uploadsDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir, { recursive: true });
}

app.use('/uploads', express.static(uploadsDir));

// MongoDB Connection
const uri = process.env.MONGODB_URI || "mongodb+srv://kiranmanupati7557_db_user:obIMXeWZ6Myi8L19@cluster0.vxzic6e.mongodb.net/demo?retryWrites=true&w=majority";

mongoose.connect(uri, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
})
.then(() => console.log('MongoDB connected'))
.catch(err => console.error('MongoDB connection error:', err));

// Define schema and model
const postSchema = new mongoose.Schema({
  title: String,
  content: String,
  image: String,
});

const Post = mongoose.model('Post', postSchema);

// Multer setup for image upload
const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, uploadsDir),
  filename: (req, file, cb) => {
    cb(null, Date.now() + '-' + file.originalname);
  }
});
const upload = multer({ storage });

// Get all posts
app.get('/posts', async (req, res) => {
  try {
    const posts = await Post.find().sort({ _id: -1 });
    posts.forEach(post => {
      if (post.image && !post.image.startsWith('http')) {
        post.image = `${req.protocol}://${req.get('host')}/` + post.image;
      }
    });
    res.json(posts);
  } catch (err) {
    res.status(500).json({ error: 'Failed to get posts' });
  }
});

// Create post
app.post('/posts', upload.single('image'), async (req, res) => {
  try {
    let imageUrl = '';
    if (req.file) {
      imageUrl = 'uploads/' + req.file.filename;
      imageUrl = `${req.protocol}://${req.get('host')}/` + imageUrl;
    }
    const { title, content } = req.body;
    const post = new Post({ title, content, image: imageUrl });
    await post.save();
    res.json(post);
  } catch (err) {
    res.status(500).json({ error: 'Failed to create post' });
  }
});

// Update post
app.put('/posts/:id', upload.single('image'), async (req, res) => {
  try {
    const { id } = req.params;
    let imageUrl;
    if (req.file) {
      imageUrl = 'uploads/' + req.file.filename;
      imageUrl = `${req.protocol}://${req.get('host')}/` + imageUrl;
    }
    const { title, content } = req.body;
    const update = { title, content };
    if (imageUrl) update.image = imageUrl;
    const post = await Post.findByIdAndUpdate(id, update, { new: true });
    res.json(post);
  } catch (err) {
    res.status(500).json({ error: 'Failed to update post' });
  }
});

// Listen to port from environment variable or 3000
const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
