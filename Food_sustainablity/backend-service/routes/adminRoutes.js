const express = require('express');
const router = express.Router();
const { getUsers, getLogistics, getAnalytics } = require('../controllers/adminController');
const { protect, authorize } = require('../middleware/authMiddleware');

router.get('/users', protect, authorize('ADMIN'), getUsers);
router.get('/logistics', protect, authorize('ADMIN'), getLogistics);
router.get('/analytics', protect, authorize('ADMIN'), getAnalytics);

module.exports = router;
