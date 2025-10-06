import os
from pathlib import Path

# Backend structure based on your screenshot
files = {
    '.env': 'PORT=5000\nMONGO_URL=your_mongodb_url_here\n',
    'index.js': '''const express = require('express');
const mongoose = require('mongoose');
const multer = require('multer');
const cors = require('cors');
const path = require('path');
require('dotenv').config();

const app = express();
app.use(cors());
app.use(express.json());
app.use('/uploads', express.static('uploads'));

// MongoDB Connection
mongoose.connect(process.env.MONGO_URL, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
});

const postSchema = new mongoose.Schema({
  title: String,
  content: String,
  image: String,
});

const Post = mongoose.model('Post', postSchema);

// Multer setup for image uploading
const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, 'uploads/'),
  filename: (req, file, cb) => {
    cb(null, Date.now() + '-' + file.originalname)
  }
});
const upload = multer({ storage });

// Get all posts
app.get('/posts', async (req, res) => {
  const posts = await Post.find().sort({ _id: -1 });
  posts.forEach(post => {
    if (post.image && !post.image.startsWith('http')) {
      post.image = `${req.protocol}://${req.get('host')}/` + post.image;
    }
  });
  res.json(posts);
});

// Create post
app.post('/posts', upload.single('image'), async (req, res) => {
  let imageUrl = '';
  if (req.file) {
    imageUrl = 'uploads/' + req.file.filename;
    imageUrl = `${req.protocol}://${req.get('host')}/` + imageUrl;
  }
  const { title, content } = req.body;
  const post = new Post({ title, content, image: imageUrl });
  await post.save();
  res.json(post);
});

// Update post (PUT)
app.put('/posts/:id', upload.single('image'), async (req, res) => {
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
});

const port = process.env.PORT || 5000;
app.listen(port, () => console.log('Backend running on port', port));
'''
}

# Add example package.json
files['package.json'] = '''{
  "name": "backend",
  "version": "1.0.0",
  "main": "index.js",
  "license": "MIT",
  "scripts": {
    "start": "node index.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "cors": "^2.8.5",
    "dotenv": "^16.1.4",
    "mongoose": "^7.0.0",
    "multer": "^1.4.5"
  }
}
'''

# Write files
def write_backend_files(base_dir, files):
    for path, content in files.items():
        fp = Path(base_dir) / path
        fp.parent.mkdir(parents=True, exist_ok=True)
        with fp.open('w', encoding='utf8') as f:
            f.write(content)
    # Also touch uploads folder to ensure it exists
    Path(base_dir, 'uploads').mkdir(parents=True, exist_ok=True)

backend_dir = 'backend-social-app'
write_backend_files(backend_dir, files)

import shutil
shutil.make_archive('backend-social-app', 'zip', backend_dir)
