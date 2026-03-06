const express = require('express');
const router = express.Router();
const { getAssignedOrders, updateOrderStatus, updateLocation } = require('../controllers/driverController');
const { protect, authorize } = require('../middleware/authMiddleware');

router.get('/orders', protect, authorize('DRIVER'), getAssignedOrders);
router.put('/orders/:id/status', protect, authorize('DRIVER'), updateOrderStatus);
router.put('/location', protect, authorize('DRIVER'), updateLocation);

module.exports = router;
