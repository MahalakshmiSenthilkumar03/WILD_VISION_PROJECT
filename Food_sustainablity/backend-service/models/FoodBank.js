const mongoose = require('mongoose');

const FoodBankSchema = new mongoose.Schema({
    userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
    profileName: { type: String, required: true },
    location: {
        lat: { type: Number, required: true },
        lng: { type: Number, required: true },
        address: { type: String, required: true }
    },
    capacity: { type: Number, default: 0 },
    inventory: [{
        foodType: String,
        quantity: String,
        addedAt: { type: Date, default: Date.now }
    }],
    isActive: { type: Boolean, default: true }
}, { timestamps: true });

module.exports = mongoose.model('FoodBank', FoodBankSchema);
