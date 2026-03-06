const mongoose = require('mongoose');

const OrderSchema = new mongoose.Schema({
    orderIdString: { type: String, required: true, unique: true }, // e.g., #WL-9012
    foodId: { type: mongoose.Schema.Types.ObjectId, ref: 'Food', required: true },
    donorId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
    ngoId: { type: mongoose.Schema.Types.ObjectId, ref: 'User' }, // Optional for broadcast
    driverId: { type: mongoose.Schema.Types.ObjectId, ref: 'User' }, // Can be null if transport not requested

    transportRequested: { type: Boolean, default: false },
    status: {
        type: String,
        enum: ['Pending', 'Accepted', 'Rejected', 'Driver Assigned', 'Pickup Completed', 'In Transit', 'Completed', 'Cancelled'],
        default: 'Pending'
    },

    // Cached for routing engine
    distanceKm: { type: Number },
    estimatedTimeMins: { type: Number },

}, { timestamps: true });

module.exports = mongoose.model('Order', OrderSchema);
