const mongoose = require('mongoose');
const dotenv = require('dotenv');
const bcrypt = require('bcryptjs');
const User = require('./models/User');

dotenv.config();

const seedData = async () => {
    try {
        await mongoose.connect(process.env.MONGO_URI);

        console.log('MongoDB Connected for Seeding...');

        // Clear existing data
        await User.deleteMany();

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
            // COIMBATORE NGO
            {
                identifier: 'helpinghearts@cbe.com',
                passwordHash: hashedPassword,
                role: 'NGO',
                isVerified: true,
                setupComplete: true,
                profileName: 'Helping Hearts NGO, Coimbatore',
                contactNumber: '7654321000',
                ngoCertificationStatus: 'CERTIFIED',
                ngoCapacity: 500,
                location: { lat: 11.0300, lng: 76.9700, address: 'Gandhipuram, Coimbatore' }
            },
            // TIRUPUR HOTELS (Donors)
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
            // TIRUPUR ORPHANAGE
            {
                identifier: 'littleangels@tirupur.com',
                passwordHash: hashedPassword,
                role: 'NGO',
                isVerified: true,
                setupComplete: true,
                profileName: 'Little Angels Orphanage, Tirupur',
                contactNumber: '7654321001',
                ngoCertificationStatus: 'NON_CERTIFIED',
                ngoCapacity: 200,
                location: { lat: 11.1000, lng: 77.3300, address: 'Kangeyam Road, Tirupur' }
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

        await User.insertMany(users);
        console.log('Dataset Imported Successfully!');
        process.exit();
    } catch (error) {
        console.error(error);
        process.exit(1);
    }
};

seedData();
