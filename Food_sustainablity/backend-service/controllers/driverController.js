const DeliveryLogistics = require('../models/DeliveryLogistics');
const User = require('../models/User');

// @desc    Get assigned delivery orders
// @route   GET /api/driver/orders
// @access  Private (DRIVER)
const getAssignedOrders = async (req, res) => {
    try {
        const orders = await DeliveryLogistics.find({
            driverId: req.user.id,
            status: { $in: ['DRIVER_ASSIGNED', 'PICKUP_COMPLETED', 'IN_TRANSIT'] }
        }).populate('foodId donorId ngoId', '-password');

        res.json(orders);
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Server error fetching orders' });
    }
};

// @desc    Update order status
// @route   PUT /api/driver/orders/:id/status
// @access  Private (DRIVER)
const updateOrderStatus = async (req, res) => {
    try {
        const { status } = req.body;
        // status options: 'PICKUP_COMPLETED', 'IN_TRANSIT', 'DELIVERED', 'REJECTED'

        const order = await DeliveryLogistics.findById(req.params.id);

        if (!order || order.driverId.toString() !== req.user.id) {
            return res.status(404).json({ message: 'Order not found or not assigned to you' });
        }

        if (status === 'REJECTED') {
            order.status = 'PENDING';
            order.driverId = null;
            await order.save();
            await User.findByIdAndUpdate(req.user.id, { deliveryStatus: 'AVAILABLE' });
            return res.json({ message: 'Order rejected. It is back to pending.' });
        }

        order.status = status;
        await order.save();

        if (status === 'DELIVERED') {
            await User.findByIdAndUpdate(req.user.id, { deliveryStatus: 'AVAILABLE' });
        }

        res.json(order);
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Server error updating order' });
    }
};

// @desc    Update live location of driver
// @route   PUT /api/driver/location
// @access  Private (DRIVER)
const updateLocation = async (req, res) => {
    try {
        const { lng, lat } = req.body;

        const driver = await User.findById(req.user.id);
        if (driver) {
            driver.location = {
                type: 'Point',
                coordinates: [lng, lat]
            };
            await driver.save();
            res.json({ message: 'Location updated', location: driver.location });
        } else {
            res.status(404).json({ message: 'Driver not found' });
        }
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Server error updating location' });
    }
};

module.exports = {
    getAssignedOrders,
    updateOrderStatus,
    updateLocation
};
