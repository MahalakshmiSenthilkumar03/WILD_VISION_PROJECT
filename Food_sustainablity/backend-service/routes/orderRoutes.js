const express = require('express');
const router = express.Router();
const orderController = require('../controllers/orderController');

router.post('/create', orderController.createOrder);
router.get('/list', orderController.getRoleOrders);
router.patch('/:id/status', orderController.updateOrderStatus);
router.patch('/:id/accept', orderController.acceptOrder);
router.patch('/:id/claim', orderController.claimOrder);

module.exports = router;
