const mongoose = require('mongoose');

const LogisticsSchema = new mongoose.Schema({
    orderId: { type: mongoose.Schema.Types.ObjectId, ref: 'Order', required: true },
    driverId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },

    // Arrays containing coordinates tracked over time to draw the UI map route
    routeCoordinates: [{
        lat: Number,
        lng: Number,
        timestamp: { type: Date, default: Date.now }
    }],

    currentLocation: {
        lat: Number,
        lng: Number,
    },

    // Snapshot metrics updated dynamically by the routing engine
    distanceRemainingKm: { type: Number },
    etaMins: { type: Number },
    lastUpdated: { type: Date, default: Date.now }

}, { timestamps: true });

module.exports = mongoose.model('Logistics', LogisticsSchema);
