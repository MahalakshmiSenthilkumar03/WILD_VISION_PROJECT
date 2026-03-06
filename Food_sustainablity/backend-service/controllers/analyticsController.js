const User = require('../models/User');
const Order = require('../models/Order');
const Food = require('../models/Food');

exports.getImpactDetails = async (req, res) => {
    try {
        const { type } = req.query; // 'donors', 'ngos', 'meals', 'saved'

        if (type === 'donors') {
            const donors = await User.find({ role: 'Donor', isVerified: true }).select('profileName location contactNumber donorType');
            return res.status(200).json({ data: donors });
        }

        if (type === 'ngos') {
            const ngos = await User.find({ role: 'NGO', isVerified: true }).select('profileName location contactNumber ngoCapacity');
            return res.status(200).json({ data: ngos });
        }

        if (type === 'meals') {
            // Meals provided translates to Completed Orders
            const orders = await Order.find({ status: { $in: ['Completed', 'Delivered'] } })
                .populate('donorId', 'profileName')
                .populate('ngoId', 'profileName')
                .populate('foodId', 'foodName quantityLbs')
                .sort({ createdAt: -1 });
            return res.status(200).json({ data: orders });
        }

        if (type === 'saved') {
            // Foods saved translates to all Foods uploaded that are not Expired/Wasted
            const foods = await Food.find()
                .populate('donorId', 'profileName')
                .sort({ createdAt: -1 });
            return res.status(200).json({ data: foods });
        }

        return res.status(400).json({ error: "Invalid type requested" });

    } catch (error) {
        console.error("Impact Analytics Error:", error);
        res.status(500).json({ error: "Server error fetching analytics data" });
    }
};
