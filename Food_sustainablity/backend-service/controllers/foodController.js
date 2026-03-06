const Food = require('../models/Food');

exports.uploadFood = async (req, res) => {
    try {
        const { donorId, foodName, foodType, quantityLbs, expiryDate, discountPrice, imageUrl, pickupLocation } = req.body;

        // Calculate safe hours
        const now = new Date();
        const expiry = new Date(expiryDate);
        const hoursDiff = Math.abs(expiry - now) / 36e5;

        const newFood = new Food({
            donorId,
            foodName,
            foodType,
            quantityLbs,
            expiryDate,
            discountPrice,
            imageUrl,
            pickupLocation,
            safeHoursRemaining: hoursDiff.toFixed(1)
        });

        await newFood.save();
        res.status(201).json({ message: "Food Uploaded", data: newFood });

    } catch (error) {
        console.error("Food Upload Error:", error);
        res.status(500).json({ error: "Server error uploading food" });
    }
};

exports.getAvailableFoods = async (req, res) => {
    try {
        const foods = await Food.find({ status: 'AVAILABLE' }).populate('donorId', 'profileName contactNumber');
        res.status(200).json({ data: foods });
    } catch (error) {
        console.error("Fetch Food Error:", error);
        res.status(500).json({ error: "Server error fetching active food inventory" });
    }
};
