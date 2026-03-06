const express = require('express');
const router = express.Router();
const { uploadFood, getNearbyNGOs, createDeliveryRequest } = require('../controllers/donorController');
const { protect, authorize } = require('../middleware/authMiddleware');

router.post('/food', protect, authorize('DONOR'), uploadFood);
router.get('/ngos', protect, authorize('DONOR'), getNearbyNGOs);
router.post('/delivery', protect, authorize('DONOR'), createDeliveryRequest);

module.exports = router;
