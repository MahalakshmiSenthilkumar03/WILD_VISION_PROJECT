const express = require('express');
const router = express.Router();
const { createFoodRequest, getIncomingDonations, updateDonationStatus, getInventoryHistory } = require('../controllers/ngoController');
const { protect, authorize } = require('../middleware/authMiddleware');

router.post('/request', protect, authorize('NGO'), createFoodRequest);
router.get('/donations/incoming', protect, authorize('NGO'), getIncomingDonations);
router.put('/donations/:id/status', protect, authorize('NGO'), updateDonationStatus);
router.get('/inventory', protect, authorize('NGO'), getInventoryHistory);

module.exports = router;
