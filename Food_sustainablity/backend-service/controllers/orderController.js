const Order = require('../models/Order');
const User = require('../models/User');
const Logistics = require('../models/Logistics');
const Notification = require('../models/Notification');

// Complex routing match algorithm workflow
exports.createOrder = async (req, res) => {
    try {
        const { foodId, donorId, ngoId, transportRequested } = req.body;

        // 1. Generate human readable ID
        const orderIdString = `#WL-${Math.floor(1000 + Math.random() * 9000)}`;

        const newOrder = new Order({
            orderIdString,
            foodId,
            donorId,
            ngoId: ngoId === 'ALL' || !ngoId ? undefined : ngoId,
            driverId: null,
            transportRequested: false,
            status: 'Pending',
            distanceKm: (Math.random() * 15).toFixed(1), // Mock engine
            estimatedTimeMins: Math.floor(Math.random() * 45) + 10
        });

        await newOrder.save();

        // Trigger Notifications for NGOs
        if (ngoId && ngoId !== 'ALL') {
            await new Notification({
                userId: ngoId,
                title: 'New Donation Request',
                message: `A new donation ${orderIdString} has been assigned to your organization.`,
                type: 'New Request'
            }).save();
        } else {
            // Broadcast to all NGOs (mock broadcast)
            const ngos = await User.find({ role: 'NGO' }).limit(5);
            for (let ngo of ngos) {
                await new Notification({
                    userId: ngo._id,
                    title: 'New Available Donation',
                    message: `A new public donation ${orderIdString} is available near you.`,
                    type: 'New Request'
                }).save();
            }
        }

        res.status(201).json({
            message: "Workflow Order generated and notifications sent.",
            data: newOrder
        });

    } catch (error) {
        console.error("Order Creation Error:", error);
        res.status(500).json({ error: "Server error executing order route" });
    }
};

exports.getRoleOrders = async (req, res) => {
    try {
        const { userId, role, available } = req.query; // Admin gets all

        let query = {};
        if (role === 'Donor') query.donorId = userId;
        if (role === 'NGO' || role === 'Community Food Bank') {
            query.$or = [
                { ngoId: userId },
                { ngoId: { $exists: false } },
                { ngoId: null }
            ];
        }
        if (role === 'Delivery Partner' || role === 'DRIVER') {
            if (available === 'true') {
                query.status = 'Accepted';
                query.transportRequested = true;
                query.driverId = null;
            } else {
                query.driverId = userId;
            }
        }

        const orders = await Order.find(query)
            .populate('donorId', 'profileName location')
            .populate('ngoId', 'profileName location')
            .populate('driverId', 'profileName driverVehicleNumber')
            .populate('foodId');

        res.status(200).json({ data: orders });
    } catch (error) {
        console.error("Fetch Orders Error:", error);
        res.status(500).json({ error: "Server error fetching logistics list" });
    }
};

exports.updateOrderStatus = async (req, res) => {
    try {
        const { id } = req.params;
        const { status } = req.body;

        const order = await Order.findById(id);
        if (!order) return res.status(404).json({ error: "Order not found" });

        // Fallback Logic: If NGO Rejects, gracefully route to a Food Bank
        if (status === 'Rejected') {
            const foodBank = await User.findOne({ role: 'Community Food Bank' });
            if (foodBank) {
                order.ngoId = foodBank._id;
                order.status = 'Pending';
                await order.save();
                return res.status(200).json({ message: "Order gracefully routed to Community Food Bank fallback", data: order });
            }
        }

        order.status = status;
        await order.save();

        res.status(200).json({ message: "Order updated successfully", data: order });
    } catch (error) {
        console.error("Update Order Status Error:", error);
        res.status(500).json({ error: "Server error updating order status" });
    }
};

exports.acceptOrder = async (req, res) => {
    try {
        const { id } = req.params;
        const { ngoId, transportRequested } = req.body;

        const order = await Order.findById(id);
        if (!order) return res.status(404).json({ error: "Order not found" });

        if (order.status !== 'Pending' && order.ngoId && order.ngoId.toString() !== ngoId) {
            return res.status(400).json({ error: "Order already accepted by another organization." });
        }

        order.ngoId = ngoId;
        order.transportRequested = transportRequested;
        order.status = 'Accepted'; // Now just "Accepted", awaiting driver if transportRequested is true

        await order.save();
        res.status(200).json({ message: "Order successfully claimed. Awaiting transport if requested.", data: order });

    } catch (error) {
        console.error("Accept Order Error:", error);
        res.status(500).json({ error: "Server error locking order to NGO" });
    }
};

exports.claimOrder = async (req, res) => {
    try {
        const { id } = req.params;
        const { driverId } = req.body;

        const order = await Order.findById(id);
        if (!order) return res.status(404).json({ error: "Order not found" });

        if (order.status !== 'Accepted' || order.driverId) {
            return res.status(400).json({ error: "Order is no longer available for claiming." });
        }

        order.driverId = driverId;
        order.status = 'Driver Assigned';
        await order.save();

        // Create Logistics Entry
        await new Logistics({
            orderId: order._id,
            driverId: driverId,
            distanceRemainingKm: order.distanceKm || 5.0,
            etaMins: order.estimatedTimeMins || 15
        }).save();

        res.status(200).json({ message: "Delivery successfully claimed!", data: order });

    } catch (error) {
        console.error("Claim Order Error:", error);
        res.status(500).json({ error: "Server error claiming delivery" });
    }
};
