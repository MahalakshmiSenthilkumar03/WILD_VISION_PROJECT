const express = require('express');
const router = express.Router();
const authController = require('../controllers/authController');

router.post('/send-otp', authController.sendOTP);
router.post('/verify-otp', authController.verifyOTP);
router.post('/complete-setup', authController.completeSetup);

router.post('/login', authController.login);
router.post('/update-profile', authController.updateProfile);
router.get('/nearby-ngos', authController.getNearbyNGOs);

module.exports = router;
