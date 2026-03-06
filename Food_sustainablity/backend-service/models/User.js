const mongoose = require('mongoose');

const UserSchema = new mongoose.Schema({
    identifier: { type: String, required: true, unique: true }, // Phone or Email
    role: { type: String, enum: ['Admin', 'Donor', 'NGO', 'Delivery Partner', 'Community Food Bank'], required: true },
    passwordHash: { type: String }, // Present only if they finished setup
    otpSecret: { type: String },
    isVerified: { type: Boolean, default: false },
    setupComplete: { type: Boolean, default: false },

    // Dynamic embedding instead of complex lookups 
    profileName: { type: String }, // Hotel Name, NGO Name, Driver Name
    contactNumber: { type: String },
    location: {
        lat: { type: Number },
        lng: { type: Number },
        address: { type: String }
    },

    // Role-specific fields tightly coupled to authentication flow
    donorType: { type: String, enum: ['Hotel', 'Event Organizer', 'Restaurant', null] },
    ngoCertificationStatus: { type: String, enum: ['CERTIFIED', 'NON_CERTIFIED', null] },
    ngoCapacity: { type: Number }, // Meals they can accept
    driverId: { type: String },
    driverVehicleNumber: { type: String },

}, { timestamps: true });

module.exports = mongoose.model('User', UserSchema);
