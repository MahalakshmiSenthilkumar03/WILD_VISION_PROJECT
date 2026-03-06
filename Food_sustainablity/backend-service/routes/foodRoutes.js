const express = require('express');
const router = express.Router();
const foodController = require('../controllers/foodController');

router.post('/upload', foodController.uploadFood);
router.get('/available', foodController.getAvailableFoods);

module.exports = router;
