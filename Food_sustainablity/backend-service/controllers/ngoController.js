const FoodRequest = require('../models/FoodRequest');
const DeliveryLogistics = require('../models/DeliveryLogistics');

// @desc    Create a food request
// @route   POST /api/ngo/request
// @access  Private (NGO)
const createFoodRequest = async (req, res) => {
    try {
        const { foodType, quantityNeeded, urgencyLevel } = req.body;

        const request = await FoodRequest.create({
            ngoId: req.user.id,
            foodType,
            quantityNeeded,
            urgencyLevel
        });

        res.status(201).json(request);
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Server error creating request' });
    }
};

// @desc    Get incoming donations (Logistics assigned to this NGO)
// @route   GET /api/ngo/donations/incoming
// @access  Private (NGO)
const getIncomingDonations = async (req, res) => {
    try {
        const logistics = await DeliveryLogistics.find({
            ngoId: req.user.id,
            status: { $in: ['PENDING', 'DRIVER_ASSIGNED', 'PICKUP_COMPLETED', 'IN_TRANSIT'] }
        }).populate('foodId donorId driverId', '-password');

        res.json(logistics);
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Server error fetching incoming donations' });
    }
};

// @desc    Accept/Reject donation (Logistics record)
// @route   PUT /api/ngo/donations/:id/status
// @access  Private (NGO)
const updateDonationStatus = async (req, res) => {
    try {
        const { id } = req.params;
        const { action } = req.body; // 'ACCEPT' or 'REJECT'

        const logistics = await DeliveryLogistics.findById(id);

        if (!logistics || logistics.ngoId.toString() !== req.user.id) {
            return res.status(404).json({ message: 'Donation logistics not found' });
        }

        if (action === 'REJECT') {
            // Cancel logistics and reset food status
            // Depending on business logic, maybe reassign to another NGO?
            res.status(200).json({ message: 'Donation rejected' });
            // Implementation specific logic...
        } else if (action === 'ACCEPT') {
            res.status(200).json({ message: 'Donation accepted', logistics });
        } else {
            res.status(400).json({ message: 'Invalid action' });
        }

    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Server error updating donation' });
    }
};

// @desc    Get Inventory History (Delivered objects)
// @route   GET /api/ngo/inventory
// @access  Private (NGO)
const getInventoryHistory = async (req, res) => {
    try {
        const logistics = await DeliveryLogistics.find({
            ngoId: req.user.id,
            status: 'DELIVERED'
        }).populate('foodId donorId', '-password');

        res.json(logistics);
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Server error fetching inventory history' });
    }
};

module.exports = {
    createFoodRequest,
    getIncomingDonations,
    updateDonationStatus,
    getInventoryHistory
};
