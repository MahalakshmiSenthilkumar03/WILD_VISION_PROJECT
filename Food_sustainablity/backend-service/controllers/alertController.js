const EmergencyAlert = require('../models/EmergencyAlert');
const User = require('../models/User');

exports.createAlert = async (req, res) => {
    try {
        const { userId, quantity, urgencyLevel } = req.body;

        const user = await User.findById(userId);
        if (!user || (user.role !== 'NGO' && user.role !== 'Community Food Bank')) {
            return res.status(403).json({ error: "Only NGOs or Food Banks can trigger an Emergency Alert." });
        }

        const newAlert = new EmergencyAlert({
            triggeredBy: user._id,
            userModel: user.role === 'NGO' ? 'NGO' : 'FoodBank',
            profileName: user.profileName,
            location: user.location,
            foodQuantityNeeded: quantity,
            urgencyLevel: urgencyLevel || 'High',
            status: 'Active'
        });

        await newAlert.save();

        res.status(201).json({ message: "Emergency Alert Broadcasted Successfully!", data: newAlert });

    } catch (error) {
        console.error("Create Alert Error:", error);
        res.status(500).json({ error: "Server error broadcasting alert" });
    }
};

exports.getActiveAlerts = async (req, res) => {
    try {
        const alerts = await EmergencyAlert.find({ status: 'Active' }).sort({ createdAt: -1 });
        res.status(200).json({ data: alerts });
    } catch (error) {
        console.error("Fetch Alerts Error:", error);
        res.status(500).json({ error: "Server error fetching active alerts" });
    }
};

exports.resolveAlert = async (req, res) => {
    try {
        const { id } = req.params;
        const alert = await EmergencyAlert.findById(id);

        if (!alert) return res.status(404).json({ error: "Alert not found" });

        alert.status = 'Resolved';
        await alert.save();

        res.status(200).json({ message: "Alert marked as Resolved", data: alert });
    } catch (error) {
        console.error("Resolve Alert Error:", error);
        res.status(500).json({ error: "Server error resolving alert" });
    }
};
