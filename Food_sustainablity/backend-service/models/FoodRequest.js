const mongoose = require('mongoose');

const FoodRequestSchema = new mongoose.Schema({
    ngoId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
    foodId: { type: mongoose.Schema.Types.ObjectId, ref: 'Food' }, // Optional for general requests

    requestedQuantityLbs: { type: Number, required: true },
    urgencyLevel: { type: String, enum: ['Low', 'Need', 'High', 'Critical'], required: true },

    status: { type: String, enum: ['Pending', 'Approved', 'Rejected'], default: 'Pending' }
}, { timestamps: true });

module.exports = mongoose.model('FoodRequest', FoodRequestSchema);
