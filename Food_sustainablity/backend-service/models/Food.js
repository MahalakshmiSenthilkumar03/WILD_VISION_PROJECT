const mongoose = require('mongoose');

const FoodSchema = new mongoose.Schema({
    donorId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
    foodName: { type: String, required: true },
    foodType: { type: String, required: true },
    quantityLbs: { type: Number, required: true },
    expiryDate: { type: Date, required: true },
    discountPrice: { type: Number, default: 0 },
    imageUrl: { type: String }, // Optional
    safeHoursRemaining: { type: Number },
    status: { type: String, enum: ['AVAILABLE', 'REQUESTED', 'MATCHED', 'IN_TRANSIT', 'DELIVERED', 'EXPIRED'], default: 'AVAILABLE' },

    // Extracted for faster geo-queries without populating User
    pickupLocation: {
        lat: { type: Number, required: true },
        lng: { type: Number, required: true },
        address: { type: String }
    }
}, { timestamps: true });

module.exports = mongoose.model('Food', FoodSchema);
