const mongoose = require('mongoose');

const surplusFoodSchema = new mongoose.Schema({
    donorId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: true
    },
    foodName: {
        type: String,
        required: true
    },
    quantity: {
        type: Number, // in kg/portions
        required: true
    },
    expiryDateTime: {
        type: Date,
        required: true
    },
    imageUrl: {
        type: String
    },
    price: {
        type: Number,
        default: 0 // Free or discounted price
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
    predictedSurplus: {
        score: Number,
        reason: String
    },
    status: {
        type: String,
        enum: ['AVAILABLE', 'REQUESTED', 'ASSIGNED', 'PICKED_UP', 'DELIVERED', 'EXPIRED'],
        default: 'AVAILABLE'
    }
}, { timestamps: true });

surplusFoodSchema.index({ pickupLocation: '2dsphere' });

module.exports = mongoose.model('SurplusFood', surplusFoodSchema);
