const express = require('express');
const router = express.Router();
const Notification = require('../models/Notification');
// No authParams middleware used here currently

// Get notifications for user
router.get('/', async (req, res) => {
    try {
        const userId = req.query.userId || req.user?.id;
        if (!userId) return res.status(400).json({ success: false, error: 'User ID required' });

        const notifications = await Notification.find({ userId }).sort({ createdAt: -1 }).limit(20);
        res.json({ success: true, count: notifications.length, data: notifications });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// Mark as read
router.patch('/:id/read', async (req, res) => {
    try {
        await Notification.findByIdAndUpdate(req.params.id, { isRead: true });
        res.json({ success: true, message: 'Notification marked read' });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

module.exports = router;
