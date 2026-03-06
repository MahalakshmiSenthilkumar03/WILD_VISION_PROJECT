const mongoose = require('mongoose');

const EmergencyAlertSchema = new mongoose.Schema({
    triggeredBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
    userModel: { type: String, enum: ['NGO', 'FoodBank'], required: true },
    profileName: { type: String, required: true },
    location: {
        lat: { type: Number, required: true },
        lng: { type: Number, required: true },
        address: { type: String, required: true }
    },
    foodQuantityNeeded: { type: String, required: true },
    urgencyLevel: { type: String, enum: ['High', 'Critical', 'Life-Threatening'], default: 'High' },
    status: { type: String, enum: ['Active', 'Resolved'], default: 'Active' },
    responders: [{ type: mongoose.Schema.Types.ObjectId, ref: 'User' }]
}, { timestamps: true });

module.exports = mongoose.model('EmergencyAlert', EmergencyAlertSchema);
