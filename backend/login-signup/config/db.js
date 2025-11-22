const mongoose = require('mongoose');

const connectDB = async () => {
  try {
    const mongoOptions = {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    };

    if (process.env.MONGODB_DB) {
      mongoOptions.dbName = process.env.MONGODB_DB;
    }

    await mongoose.connect(process.env.MONGO_URI, mongoOptions);
    console.log(`✅ MongoDB connected${mongoOptions.dbName ? ` (${mongoOptions.dbName})` : ''}`);
  } catch (err) {
    console.error('❌ MongoDB connection failed', err);
    process.exit(1);
  }
};

module.exports = connectDB;
