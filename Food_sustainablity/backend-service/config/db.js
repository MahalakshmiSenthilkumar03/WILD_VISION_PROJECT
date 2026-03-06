const mongoose = require('mongoose');
const { MongoMemoryServer } = require('mongodb-memory-server');

const connectDB = async () => {
    try {
        let uri = process.env.MONGO_URI;

        // Use in-memory DB for quick setup without requiring MongoDB installation
        if (uri.includes('localhost')) {
            console.log('Starting In-Memory MongoDB Server...');
            const mongoServer = await MongoMemoryServer.create();
            uri = mongoServer.getUri();
        }

        const conn = await mongoose.connect(uri);
        console.log(`MongoDB Connected: ${conn.connection.host}`);

        // Auto-seed data on startup if using memory server
        if (uri.includes('127.0.0.1')) {
            require('../seeder-auto'); // We'll create a module version of seeder
        }
    } catch (error) {
        console.error(`Error: ${error.message}`);
        process.exit(1);
    }
};

module.exports = connectDB;
