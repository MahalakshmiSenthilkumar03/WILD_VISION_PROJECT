const mongoose = require('mongoose');

const deliveryLogisticsSchema = new mongoose.Schema({
    orderId: {
        type: String,
        required: true,
        unique: true
    },
    foodId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'SurplusFood',
        required: true
    },
    donorId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: true
    },
    ngoId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: true
    },
    driverId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User'
    },
    pickupLocation: {
        type: {
            type: String,
            enum: ['Point'],
            default: 'Point'
        },
        coordinates: {
            type: [Number], // [longitude, latitude]
            required: true
        },
        address: String
    },
    destinationLocation: {
        type: {
            type: String,
            enum: ['Point'],
            default: 'Point'
        },
        coordinates: {
            type: [Number], // [longitude, latitude]
            required: true
        },
        address: String
    },
    routeDistance: {
        type: Number, // in km
    },
    status: {
        type: String,
        enum: ['PENDING', 'DRIVER_ASSIGNED', 'PICKUP_COMPLETED', 'IN_TRANSIT', 'DELIVERED'],
        default: 'PENDING'
    }
}, { timestamps: true });

module.exports = mongoose.model('DeliveryLogistics', deliveryLogisticsSchema);
