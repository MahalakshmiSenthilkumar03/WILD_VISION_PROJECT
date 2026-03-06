const User = require('../models/User');
const DeliveryLogistics = require('../models/DeliveryLogistics');
const SurplusFood = require('../models/SurplusFood');

// @desc    Get all users based on role query
// @route   GET /api/admin/users?role=NGO
// @access  Private (ADMIN)
const getUsers = async (req, res) => {
    try {
        const query = req.query.role ? { role: req.query.role } : {};
        const users = await User.find(query).select('-password');
        res.json(users);
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Server error fetching users' });
    }
};

// @desc    Get all logistics
// @route   GET /api/admin/logistics
// @access  Private (ADMIN)
const getLogistics = async (req, res) => {
    try {
        const logistics = await DeliveryLogistics.find()
            .populate('foodId donorId ngoId driverId', '-password')
            .sort({ createdAt: -1 });
        res.json(logistics);
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Server error fetching logistics' });
    }
};

// @desc    Get dashboard analytics
// @route   GET /api/admin/analytics
// @access  Private (ADMIN)
const getAnalytics = async (req, res) => {
    try {
        const totalDonors = await User.countDocuments({ role: 'DONOR' });
        const totalNGOs = await User.countDocuments({ role: 'NGO' });
        const totalDrivers = await User.countDocuments({ role: 'DRIVER' });

        const totalFoodDonatedCount = await SurplusFood.countDocuments({});

        const totalDelivered = await DeliveryLogistics.countDocuments({ status: 'DELIVERED' });

        // Aggregate total quantity of food delivered
        const deliveredFoods = await DeliveryLogistics.find({ status: 'DELIVERED' }).populate('foodId');
        const totalKgsDelivered = deliveredFoods.reduce((acc, curr) => acc + (curr.foodId ? curr.foodId.quantity : 0), 0);

        res.json({
            users: {
                donors: totalDonors,
                ngos: totalNGOs,
                drivers: totalDrivers
            },
            food: {
                totalListings: totalFoodDonatedCount,
                completedDeliveries: totalDelivered,
                totalQuantityDelivered: totalKgsDelivered
            }
        });

    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Server error fetching analytics' });
    }
};

module.exports = {
    getUsers,
    getLogistics,
    getAnalytics
};
