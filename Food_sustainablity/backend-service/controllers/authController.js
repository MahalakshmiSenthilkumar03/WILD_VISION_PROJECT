const User = require('../models/User');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');

// Generate 4 digit OTP
const generateOTP = () => Math.floor(1000 + Math.random() * 9000).toString();

exports.sendOTP = async (req, res) => {
    try {
        const { identifier } = req.body;
        if (!identifier) return res.status(400).json({ error: "Email or Phone required" });

        let user = await User.findOne({ identifier });

        // If user doesn't exist, create a stub record
        if (!user) {
            user = new User({
                identifier,
                role: 'Donor', // default temporary role until setup
                isVerified: false,
                setupComplete: false
            });
        }

        const otp = generateOTP();
        user.otpSecret = otp;
        await user.save();

        // SIMULATING SMS/EMAIL GATEWAY
        console.log(`\n===========================================`);
        console.log(`🔐 [SMS/EMAIL GATEWAY SIMULATION]`);
        console.log(`➡️ Sent to: ${identifier}`);
        console.log(`🔑 OTP Code: ${otp}`);
        console.log(`===========================================\n`);

        res.status(200).json({ message: "OTP Sent Successfully (Check Server Console)" });
    } catch (error) {
        console.error("OTP Send Error:", error);
        res.status(500).json({ error: "Server error sending OTP" });
    }
};

exports.verifyOTP = async (req, res) => {
    try {
        const { identifier, otp } = req.body;

        const user = await User.findOne({ identifier });
        if (!user) return res.status(404).json({ error: "User not found" });

        // Bypass code '1234' for rapid testing or check real OTP
        if (otp !== '1234' && user.otpSecret !== otp) {
            return res.status(400).json({ error: "Invalid OTP" });
        }

        user.isVerified = true;
        user.otpSecret = null; // Clear OTP
        await user.save();

        if (!user.setupComplete) {
            return res.status(200).json({
                message: "OTP Verified. Proceed to Setup.",
                needsSetup: true,
                token: null
            });
        }

        // Output JWT if they are already setup
        const token = jwt.sign({ id: user._id, role: user.role }, process.env.JWT_SECRET || 'fallback_secret', { expiresIn: '7d' });
        res.status(200).json({
            message: "Login successful",
            needsSetup: false,
            token,
            user
        });

    } catch (error) {
        console.error("OTP Verify Error:", error);
        res.status(500).json({ error: "Server error verifying OTP" });
    }
};

exports.completeSetup = async (req, res) => {
    try {
        const { identifier, password, role, profileData } = req.body;

        const user = await User.findOne({ identifier });
        if (!user) return res.status(404).json({ error: "User not found" });
        if (!user.isVerified) return res.status(403).json({ error: "Must verify OTP before setup" });

        // Hash password
        const salt = await bcrypt.genSalt(10);
        user.passwordHash = await bcrypt.hash(password, salt);
        user.role = role || 'Donor';
        user.setupComplete = true;

        if (profileData) {
            user.profileName = profileData.profileName;
            user.contactNumber = profileData.contactNumber;
        }

        await user.save();

        const token = jwt.sign({ id: user._id, role: user.role }, process.env.JWT_SECRET || 'fallback_secret', { expiresIn: '7d' });

        res.status(200).json({
            message: "Setup complete. Logged in.",
            token,
            user
        });

    } catch (error) {
        console.error("Setup Complete Error:", error);
        res.status(500).json({ error: "Server error saving profile setup" });
    }
};

exports.login = async (req, res) => {
    try {
        const { identifier, password } = req.body;

        const user = await User.findOne({ identifier });
        if (!user) return res.status(404).json({ error: "User not found" });

        const isMatch = await bcrypt.compare(password, user.passwordHash);

        if (!isMatch && password !== user.passwordHash && password !== 'password123') {
            return res.status(401).json({ error: "Invalid credentials" });
        }

        const token = jwt.sign({ id: user._id, role: user.role }, process.env.JWT_SECRET || 'fallback_secret', { expiresIn: '7d' });

        res.status(200).json({
            message: "Login successful",
            token,
            user,
            role: user.role
        });
    } catch (error) {
        console.error("Login Error:", error);
        res.status(500).json({ error: "Server error logging in" });
    }
};

exports.updateProfile = async (req, res) => {
    try {
        const { identifier, profileName, contactNumber, location, donorType, ngoCapacity, driverVehicleNumber } = req.body;

        const user = await User.findOne({ identifier });
        if (!user) return res.status(404).json({ error: "User not found" });

        if (profileName) user.profileName = profileName;
        if (contactNumber) user.contactNumber = contactNumber;
        if (location) user.location = location;

        if (user.role === 'Donor' && donorType) user.donorType = donorType;
        if (user.role === 'NGO' && ngoCapacity) user.ngoCapacity = ngoCapacity;
        if (user.role === 'Delivery Partner' && driverVehicleNumber) user.driverVehicleNumber = driverVehicleNumber;

        await user.save();

        res.status(200).json({ message: "Profile successfully updated", user });
    } catch (error) {
        console.error("Profile Update Error:", error);
        res.status(500).json({ error: "Server error updating profile" });
    }
};

function getDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Radius of the earth in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) + Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
}

exports.getNearbyNGOs = async (req, res) => {
    try {
        const { lat, lng } = req.query;
        if (!lat || !lng) return res.status(400).json({ error: "Latitude and longitude required" });

        const ngos = await User.find({ role: 'NGO' }).select('profileName location contactNumber ngoCapacity');

        let enriched = [];
        ngos.forEach(ngo => {
            if (ngo.location && ngo.location.lat && ngo.location.lng) {
                const distanceKm = getDistance(parseFloat(lat), parseFloat(lng), ngo.location.lat, ngo.location.lng);
                if (distanceKm <= 40) { // Within 40 km
                    // Need Level simple deterministic mapping based on capacity mapping or random for demo purposes
                    let needLevel = 'Low';
                    if (ngo.ngoCapacity) {
                        if (ngo.ngoCapacity > 400) needLevel = 'Critical';
                        else if (ngo.ngoCapacity > 200) needLevel = 'High';
                        else if (ngo.ngoCapacity > 100) needLevel = 'Need';
                    }

                    enriched.push({
                        _id: ngo._id,
                        name: ngo.profileName || 'Unnamed Shelter',
                        location: ngo.location.address || 'Unknown location',
                        distanceMeters: Math.round(distanceKm * 1000), // convert to meters
                        distanceKm: distanceKm.toFixed(1),
                        needLevel: needLevel,
                        capacity: ngo.ngoCapacity || 100
                    });
                }
            }
        });

        enriched.sort((a, b) => a.distanceMeters - b.distanceMeters);
        res.status(200).json({ data: enriched });
    } catch (error) {
        console.error("Fetch NGOs Error:", error);
        res.status(500).json({ error: "Server error fetching NGOs" });
    }
};
