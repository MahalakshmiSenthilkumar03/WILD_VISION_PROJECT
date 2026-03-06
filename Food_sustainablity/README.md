# 🌍 WasteLess Grid (Food Sustainability App)

**WasteLess Grid** is a modern, AI-powered food rescue and redistribution application designed to bridge the gap between food surplus (from restaurants, events, and individuals) and food scarcity (orphanges, NGOs, community banks). 

Inspired by sustainability and smart logistics, the platform enables real-time tracking, AI-driven surplus prediction, an emergency SOS system, and end-to-end transparency.

---

## 🚀 Key Features

*   **Donor Dashboard & ML Surplus Prediction**: Donors can easily list surplus food and get AI predictions on potential food waste based on weather, trends, and historical data.
*   **Advanced NGO Acceptance Flow**: NGOs can view incoming food donation broadcasts and *explicitly* **Accept** or **Reject** orders. They are not forced to receive orders they don't need or cannot accommodate.
*   **Integrated Logistics**: NGOs have the option to trigger a need for a delivery driver when accepting an order. Real-time mapping tracks the food from donor to recipient.
*   **Smart Routing Engine**: Backend system intelligently routes the closest available driver to the donation pickup and tracks remaining distance/ETA.
*   **Reporting & Analytics Dashboard**: Keep track of the carbon redirected and meals secured through interactive history and charts.

---

## 🛠 Tech Stack

### Frontend (Mobile App)
*   **Flutter** (Dart) for UI & Mobile experience
*   Beautiful, native-feeling UI with `fl_chart` for analytics and custom theming (using `AppTheme` colors).

### Backend Service (Node.js)
*   **Node.js / Express.js** API Server
*   **MongoDB** for Database (Mongoose Schemas for `Order`, `Food`, `User`, `DeliveryLogistics`)
*   **Socket.io** integration for Live Tracking.

### ML Service (Python)
*   **FastAPI / Python** server
*   Scikit-Learn models for predictive waste analytics.

---

## 📂 Project Structure

```text
/Food_sustainablity
│
├── /mobile-app          # Flutter application codebase
│   ├── /lib/screens     # UI Screens (Dashboards, Map Tracking, Add Food, etc.)
│   └── pubspec.yaml     # Flutter dependencies
│
├── /backend-service     # Node.js REST API
│   ├── /controllers     # Application logic (orders, logic, users, foods)
│   ├── /models          # MongoDB Data schemas
│   └── /routes          # API endpoints mapping
│
└── /ml-service          # Python Machine Learning microservice
    └── app.py           # FastAPI prediction endpoints
```

---

## 💡 How The Updated NGO Order Flow Works

1. **Donation Broadcast**: A donor posts food. If no specific NGO is selected, nearby NGOs are pinged.
2. **Reviewing the Request**: The NGO sees the request in their *Incoming Requests* section.
3. **Reject/Accept Decision**: 
    *   **Reject**: The NGO can reject the order, which gracefully updates the order status (potentially rerouting to a community food bank default).
    *   **Accept**: The NGO accepts the order and is immediately prompted: *"Do you need a delivery partner to transport this food directly to your facility?"*.
4. **Driver Allocation**: If the NGO requests transport, the order enters an `Accepted` (Awaiting Driver) status until a driver claims it. Otherwise, it simply assigns the order to the NGO for manual pickup.

---

## 📜 Setup Instructions

**Backend (`/backend-service`)**
1. Run `npm install`
2. Configure `.env` with your `MONGO_URI`.
3. Run `npm run dev` or `node index.js`. (API runs on port `5001`)

**Mobile App (`/mobile-app`)**
1. Navigate to `/mobile-app`.
2. Run `flutter pub get`.
3. Run `flutter run` on an emulator or connected device.

**ML Service (`/ml-service`)**
1. Ensure Python is installed.
2. Run `pip install -r requirements.txt`. (or install `fastapi`, `uvicorn`, `scikit-learn`, `pandas`)
3. Use the `start_ml.bat` script or run `uvicorn app:app --reload --port 8000`.

---

Developed with ❤️ for food sustainability and hunger alleviation.
