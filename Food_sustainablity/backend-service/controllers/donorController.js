const SurplusFood = require('../models/SurplusFood');
const User = require('../models/User');
const DeliveryLogistics = require('../models/DeliveryLogistics');

// @desc    Upload surplus food
// @route   POST /api/donor/food
// @access  Private (DONOR)
const uploadFood = async (req, res) => {
    try {
        const { foodName, quantity, expiryDateTime, imageUrl, price, pickupLocation } = req.body;

        const food = await SurplusFood.create({
            donorId: req.user.id,
            foodName,
            quantity,
            expiryDateTime,
            imageUrl,
            price,
            pickupLocation,
            // later we can call prediction service here to set predictedSurplus
        });

        res.status(201).json(food);
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Server error uploading food' });
    }
};

// @desc    Get nearby NGOs (within 40km)
// @route   GET /api/donor/ngos?lng=...&lat=...&radius=40
// @access  Private (DONOR)
const getNearbyNGOs = async (req, res) => {
    try {
        const lng = parseFloat(req.query.lng);
        const lat = parseFloat(req.query.lat);
        const radiusInKm = req.query.radius ? parseFloat(req.query.radius) : 40;

        if (!lng || !lat) {
            return res.status(400).json({ message: 'Please provide lng and lat' });
        }

        const radiusInRadians = radiusInKm / 6378.1; // Earth radius in km

        const ngos = await User.find({
            role: 'NGO',
            location: {
                $geoWithin: {
                    $centerSphere: [[lng, lat], radiusInRadians]
                }
            }
        }).select('-password');

        res.json(ngos);
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Server error finding NGOs' });
    }
};

const { calculateDistance } = require('../utils/routingEngine');

// @desc    Select NGO & Create delivery request
// @route   POST /api/donor/delivery
// @access  Private (DONOR)
const createDeliveryRequest = async (req, res) => {
    try {
        const { foodId, ngoId } = req.body;

        const food = await SurplusFood.findById(foodId);
        const ngo = await User.findById(ngoId);

        if (!food || !ngo) {
            return res.status(404).json({ message: 'Food or NGO not found' });
        }

        if (food.donorId.toString() !== req.user.id) {
            return res.status(403).json({ message: 'Not authorized for this food item' });
        }

        // Find nearest available driver using geospatial search
        const pickupLoc = food.pickupLocation.coordinates; // [lng, lat]
        const availableDrivers = await User.find({
            role: 'DRIVER',
            deliveryStatus: 'AVAILABLE',
            location: {
                $near: {
                    $geometry: {
                        type: 'Point',
                        coordinates: pickupLoc
                    },
                    $maxDistance: 20000 // 20km search radius
                }
            }
        });

        let assignedDriverId = null;
        if (availableDrivers.length > 0) {
            assignedDriverId = availableDrivers[0]._id;
            // Update driver status
            await User.findByIdAndUpdate(assignedDriverId, { deliveryStatus: 'IN_TRANSIT' });
        }

        // calculate route distance (Haversine simple distance for now, or Dijkstra if mapping graph exists)
        const dist = calculateDistance(
            pickupLoc[1], pickupLoc[0],
            ngo.location.coordinates[1], ngo.location.coordinates[0]
        );

        const logistics = await DeliveryLogistics.create({
            foodId,
            donorId: req.user.id,
            ngoId,
            driverId: assignedDriverId,
            pickupLocation: food.pickupLocation,
            destinationLocation: ngo.location,
            routeDistance: dist,
            status: assignedDriverId ? 'DRIVER_ASSIGNED' : 'PENDING'
        });

        // Update food status
        food.status = assignedDriverId ? 'ASSIGNED' : 'REQUESTED';
        await food.save();

        res.status(201).json(logistics);

    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Server error creating delivery' });
    }
};

module.exports = {
    uploadFood,
    getNearbyNGOs,
    createDeliveryRequest
};
