const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');
const User = require('./models/User');
const Food = require('./models/Food');
const Order = require('./models/Order');
const Logistics = require('./models/Logistics');

const seedDataAuto = async () => {
    try {
        // Only seed if empty
        const count = await User.countDocuments();
        if (count > 0) return;

        console.log('Auto-Seeding In-Memory Database...');

        const salt = await bcrypt.genSalt(10);
        const hashedPassword = await bcrypt.hash('password123', salt);

        const users = [
            // ADMIN
            {
                identifier: 'admin@wasteless.com',
                passwordHash: hashedPassword,
                role: 'Admin',
                isVerified: true,
                setupComplete: true,
                profileName: 'Admin Coordinator',
                contactNumber: '1234567890'
            },
            // DRIVERS
            {
                identifier: 'ramesh@driver.com',
                passwordHash: hashedPassword,
                role: 'Delivery Partner',
                isVerified: true,
                setupComplete: true,
                profileName: 'Ramesh (Driver)',
                contactNumber: '9876543210',
                driverId: 'DRV-1001',
                driverVehicleNumber: 'TN-38-AB-1234',
                location: { lat: 11.0168, lng: 76.9558, address: 'Coimbatore' }
            },
            {
                identifier: 'suresh@driver.com',
                passwordHash: hashedPassword,
                role: 'Delivery Partner',
                isVerified: true,
                setupComplete: true,
                profileName: 'Suresh (Driver)',
                contactNumber: '9876543211',
                driverId: 'DRV-1002',
                driverVehicleNumber: 'TN-39-XY-9876',
                location: { lat: 11.1085, lng: 77.3411, address: 'Tirupur' }
            },
            // COIMBATORE HOTELS (Donors)
            {
                identifier: 'annapoorna@cbe.com',
                passwordHash: hashedPassword,
                role: 'Donor',
                isVerified: true,
                setupComplete: true,
                profileName: 'Annapoorna Hotel, Coimbatore',
                contactNumber: '8765432100',
                donorType: 'Hotel',
                location: { lat: 11.0180, lng: 76.9600, address: 'RS Puram, Coimbatore' }
            },
            {
                identifier: 'royalevents@cbe.com',
                passwordHash: hashedPassword,
                role: 'Donor',
                isVerified: true,
                setupComplete: true,
                profileName: 'Royal Events & Catering, Coimbatore',
                contactNumber: '8765432101',
                donorType: 'Event Organizer',
                location: { lat: 11.0200, lng: 76.9900, address: 'Peelamedu, Coimbatore' }
            },
            // --- COIMBATORE NGOs ---
            {
                identifier: 'helpinghearts@cbe.com',
                passwordHash: hashedPassword,
                role: 'NGO',
                isVerified: true,
                setupComplete: true,
                profileName: 'Helping Hands Orphanage, Coimbatore',
                contactNumber: '7654321000',
                ngoCertificationStatus: 'CERTIFIED',
                ngoCapacity: 500,
                location: { lat: 11.0300, lng: 76.9700, address: 'Gandhipuram, Coimbatore' }
            },
            {
                identifier: 'littleflower@cbe.com',
                passwordHash: hashedPassword,
                role: 'NGO',
                isVerified: true,
                setupComplete: true,
                profileName: 'Little Flower Home, Coimbatore',
                contactNumber: '7654321001',
                ngoCertificationStatus: 'CERTIFIED',
                ngoCapacity: 250,
                location: { lat: 11.0400, lng: 76.9800, address: 'Saravanampatti, Coimbatore' }
            },
            {
                identifier: 'sriramakrishna@cbe.com',
                passwordHash: hashedPassword,
                role: 'NGO',
                isVerified: true,
                setupComplete: true,
                profileName: 'Sri Ramakrishna Children Home, Coimbatore',
                contactNumber: '7654321002',
                ngoCertificationStatus: 'CERTIFIED',
                ngoCapacity: 600,
                location: { lat: 11.0150, lng: 76.9500, address: 'RS Puram, Coimbatore' }
            },

            // --- TIRUPUR HOTELS (Donors) ---
            {
                identifier: 'aryaas@tirupur.com',
                passwordHash: hashedPassword,
                role: 'Donor',
                isVerified: true,
                setupComplete: true,
                profileName: 'Aryaas Veg, Tirupur',
                contactNumber: '8765432102',
                donorType: 'Restaurant',
                location: { lat: 11.1100, lng: 77.3450, address: 'Avinashi Road, Tirupur' }
            },

            // --- TIRUPUR NGOs ---
            {
                identifier: 'anbuillam@tirupur.com',
                passwordHash: hashedPassword,
                role: 'NGO',
                isVerified: true,
                setupComplete: true,
                profileName: 'Anbu Illam, Tirupur',
                contactNumber: '7654321010',
                ngoCertificationStatus: 'NON_CERTIFIED',
                ngoCapacity: 150,
                location: { lat: 11.1000, lng: 77.3300, address: 'Kangeyam Road, Tirupur' }
            },
            {
                identifier: 'shanthichildren@tirupur.com',
                passwordHash: hashedPassword,
                role: 'NGO',
                isVerified: true,
                setupComplete: true,
                profileName: 'Shanthi Children Home, Tirupur',
                contactNumber: '7654321011',
                ngoCertificationStatus: 'CERTIFIED',
                ngoCapacity: 300,
                location: { lat: 11.1200, lng: 77.3600, address: 'PN Road, Tirupur' }
            },
            // CENTRAL COMMUNITY FOOD BANK
            {
                identifier: 'centralbank@wasteless.com',
                passwordHash: hashedPassword,
                role: 'Community Food Bank',
                isVerified: true,
                setupComplete: true,
                profileName: 'Central District Food Bank',
                contactNumber: '1122334455',
                location: { lat: 11.0150, lng: 76.9650, address: 'Avinashi Highway, Central Hub' }
            }
        ];

        const insertedUsers = await User.insertMany(users);

        // --- SEED MOCK TRANSACTIONS ---
        const donor = insertedUsers.find(u => u.identifier === 'annapoorna@cbe.com');
        const ngo = insertedUsers.find(u => u.identifier === 'helpinghearts@cbe.com');
        const driver = insertedUsers.find(u => u.identifier === 'ramesh@driver.com');

        const food = new Food({
            donorId: donor._id,
            foodName: 'Premium South Indian Thali',
            foodType: 'Vegetarian Meals',
            quantityLbs: 25.5,
            expiryDate: new Date(Date.now() + 5 * 3600 * 1000), // 5 hours from now
            status: 'IN_TRANSIT',
            pickupLocation: donor.location
        });
        await food.save();

        const order = new Order({
            orderIdString: '#WL-4092',
            foodId: food._id,
            donorId: donor._id,
            ngoId: ngo._id,
            driverId: driver._id,
            transportRequested: true,
            status: 'In Transit',
            distanceKm: 5.4,
            estimatedTimeMins: 18
        });
        await order.save();

        const logistics = new Logistics({
            orderId: order._id,
            driverId: driver._id,
            distanceRemainingKm: 2.1,
            etaMins: 7
        });
        await logistics.save();

        console.log('Dataset Auto-Seeded Successfully.');
    } catch (error) {
        console.error("Auto Seeder Error: ", error);
    }
};

seedDataAuto();
