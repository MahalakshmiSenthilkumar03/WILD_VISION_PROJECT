const express = require('express');
const { createAlert, getActiveAlerts, resolveAlert } = require('../controllers/alertController');
const router = express.Router();

router.post('/trigger', createAlert);
router.get('/active', getActiveAlerts);
router.patch('/:id/resolve', resolveAlert);

module.exports = router;
