const express = require('express');
const router = express.Router();
const analyticsController = require('../controllers/analyticsController');

router.get('/details', analyticsController.getImpactDetails);

module.exports = router;
