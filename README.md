# Travel Guide Application

## Project Overview

The **Travel Guide Application** is an innovative, AI-powered web platform designed to revolutionize how travelers plan and experience their journeys. Whether you're a solo adventurer, a family on vacation, or a business traveler, this app delivers personalized, real-time travel solutions tailored to your preferences, budget, and timeline. By integrating cutting-edge AI, geospatial data, news scraping, and seamless email delivery, it empowers users to:

- **Discover**: Find hidden gems, top attractions, dining options, and accommodations with detailed insights powered by Google Maps.
- **Plan**: Generate custom day-by-day itineraries using the DeepSeek AI API, enhanced with local news scraped via the Firecraler API.
- **Navigate**: Access optimized routes and directions for walking, driving, or multi-stop trips.
- **Stay Informed**: Receive beautifully formatted travel plans via email and stay updated with safety alerts and local news.

### Why It Matters

In a world where travel planning can be overwhelming, this app stands out by combining AI-driven personalization with practical, user-friendly tools. It’s not just a guide—it’s your travel companion, saving time, reducing stress, and unlocking unforgettable experiences. With scalability potential (e.g., mobile apps, multi-language support) and real-time news integration, it’s poised to capture a growing market of tech-savvy travelers seeking efficiency, inspiration, and safety.

### Goals

- **Simplify Travel Planning**: Make trip preparation effortless with AI-generated itineraries and curated recommendations.
- **Enhance User Experience**: Offer a sleek UI, real-time data, secure authentication, and local news updates.
- **Scale Globally**: Build a foundation for worldwide adoption with extensible features and robust infrastructure.

## Technical Stack

The Travel Guide Application leverages a modern, robust tech stack to deliver a seamless experience:

| Component            | Technology             | Version  | Purpose                                      |
|----------------------|------------------------|----------|----------------------------------------------|
| Backend Framework    | Flask                  | 3.1.0    | Lightweight Python web framework            |
| Frontend             | HTML/CSS/JavaScript    | N/A      | Dynamic UI with Bootstrap 5.3.0             |
| Database             | Firebase Firestore     | 9.6.10   | NoSQL storage for user data and guides      |
| Authentication       | Firebase Authentication| 9.6.10   | Secure login (Google, email/password)       |
| AI Integration       | DeepSeek API           | N/A      | Generates detailed travel itineraries       |
| News Scraping        | Firecraler API + AI    | N/A      | Scrapes and processes local news near areas |
| Geospatial API       | Google Maps API        | N/A      | Place search, routing, and mapping          |
| Email Service        | Flask-Mail (SMTP)      | 0.9.1    | Sends formatted itineraries via Gmail       |
| Deployment           | Heroku                 | N/A      | Cloud hosting with Gunicorn 20.1.0          |
| Runtime              | Python                 | 3.10.13  | Core language (specified in runtime.txt)   |
| Dependencies         | Various (see requirements.txt) | N/A | e.g., requests, python-dotenv, firebase-admin |
| Frontend Libraries   | Bootstrap              | 5.3.0    | Responsive design and UI components         |
| JavaScript Utilities | Firebase SDK           | 9.6.10   | Client-side auth and Firestore access       |

### Key Files

- `app/__init__.py`: Initializes Flask app with Firebase, Flask-Mail, and Google Maps.
- `app/main_routes.py`: Defines API endpoints for travel functionality.
- `app/static/js/firebase-integration.js`: Handles client-side Firebase auth and Firestore.
- `Procfile`: `web: gunicorn wsgi:app` for Heroku deployment.
- `requirements.txt`: Lists Python dependencies (e.g., flask, gunicorn, googlemaps).

## API Documentation

The application exposes a RESTful API for core travel planning features. Below are detailed specifications for each endpoint, including parameters, responses, and examples.

### 1. Search Places

- **Endpoint**: `GET /api/search_places`
- **Description**: Retrieves a list of nearby places based on location and type.
- **Parameters**:
  - `location` (string, required): e.g., "Paris, France"
  - `type` (string, optional, default: "tourist_attraction"): e.g., "restaurant", "hotel"
  - `radius` (int, optional, default: 5000): Search radius in meters
- **Response**:
  - **Success (200)**: JSON with place details
  - **Error (400)**: `{"error": "Location is required"}`
- **Example**:
  ```bash
  curl "http://localhost:5000/api/search_places?location=Paris,France&type=restaurant&radius=2000"
  ```
  ```json
  {
    "places": [
      {
        "name": "Le Bistro Parisien",
        "address": "123 Rue de Paris",
        "location": {"lat": 48.8566, "lng": 2.3522},
        "rating": 4.5,
        "place_id": "ChIJ123...",
        "types": ["restaurant", "food"],
        "photo": "https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference=...",
        "description": "A charming French bistro with classic cuisine."
      }
    ],
    "count": 1
  }
  ```

### 2. Place Details

- **Endpoint**: `GET /api/place/<place_id>`
- **Description**: Fetches detailed information for a specific place.
- **Parameters**:
  - `place_id` (string, required): Google Maps Place ID
- **Response**:
  - **Success (200)**: JSON with place details
  - **Error (404)**: `{"error": "Place not found"}`
- **Example**:
  ```bash
  curl "http://localhost:5000/api/place/ChIJ123..."
  ```
  ```json
  {
    "name": "Eiffel Tower",
    "formatted_address": "Champ de Mars, Paris",
    "rating": 4.7,
    "photos": [{"photo_reference": "..."}],
    "editorial_summary": {"overview": "Iconic Parisian landmark."}
  }
  ```

### 3. Generate Travel Guide

- **Endpoint**: `POST /api/generate-travel-guide`
- **Description**: Creates a personalized travel itinerary using AI, enriched with local news scraped via Firecraler API, and emails it to the user.
- **Parameters** (JSON body):
  - `destination` (string, required): e.g., "Tokyo, Japan"
  - `start_date` (string, optional, format: YYYY-MM-DD): e.g., "2025-04-01"
  - `end_date` (string, optional, format: YYYY-MM-DD): e.g., "2025-04-07"
  - `travelers` (int, required): e.g., 2
  - `budget` (string, required): e.g., "Moderate"
  - `interests` (string, optional): e.g., "Food, Culture"
  - `email` (string, optional): Recipient email
  - `special_requests` (string, optional): e.g., "Vegetarian options"
- **Response**:
  - **Success (200)**: JSON with itinerary details
  - **Error (400)**: `{"success": false, "message": "Missing required fields"}`
- **Example**:
  ```bash
  curl -X POST "http://localhost:5000/api/generate-travel-guide" \
  -H "Content-Type: application/json" \
  -d '{"destination": "Tokyo, Japan", "start_date": "2025-04-01", "end_date": "2025-04-07", "travelers": 2, "budget": "Moderate", "interests": "Food, Culture", "email": "user@example.com"}'
  ```
  ```json
  {
    "success": true,
    "message": "Travel guide generated successfully!",
    "data": {
      "destination": "Tokyo, Japan",
      "start_date": "2025-04-01",
      "end_date": "2025-04-07",
      "number_of_days": 7,
      "travelers": 2,
      "budget": "Moderate",
      "interests": "Food, Culture",
      "itinerary": "## Day 1: Arrival\n- Check into hotel\n- Visit Shibuya Crossing...",
      "local_news": "Recent safety advisory issued for Shibuya area due to crowds.",
      "email": "user@example.com",
      "generated_at": "2025-03-03T20:19:40Z"
    }
  }
  ```

### 4. Get Route

- **Endpoint**: `GET /api/route`
- **Description**: Calculates directions between two points with optional waypoints.
- **Parameters**:
  - `origin` (string, required): e.g., "Tokyo Station"
  - `destination` (string, required): e.g., "Akihabara"
  - `waypoints` (array, optional): e.g., ["Shinjuku"]
  - `mode` (string, optional, default: "walking"): e.g., "driving"
- **Response**:
  - **Success (200)**: JSON with route details
  - **Error (400)**: `{"error": "Origin and destination are required"}`
- **Example**:
  ```bash
  curl "http://localhost:5000/api/route?origin=Tokyo Station&destination=Akihabara&mode=walking"
  ```
  ```json
  {
    "total_distance": "2.1 km",
    "total_duration": "25 mins",
    "steps": [{"instructions": "Head east...", "distance": "200 m"}],
    "polyline": "abcd123..."
  }
  ```

## Installation Instructions

### Prerequisites

- **Python**: 3.10.13 (specified in `runtime.txt`)
- **Heroku CLI**: For deployment
- **Firebase Project**: For authentication and Firestore
- **Google Cloud Account**: For Maps API key
- **DeepSeek API Key**: For AI itinerary generation
- **Firecraler API Key**: For news scraping
- **Gmail Account**: For email service (with app-specific password)

### Local Setup

1. **Clone the Repository**:
   ```bash
   git clone <your-repo-url>
   cd travel_guide
   ```

2. **Create Virtual Environment**:
   - **Linux/macOS**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
   - **Windows**:
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**:
   Create a `.env` file in the root directory:
   ```bash
   GOOGLE_MAPS_API_KEY=your_google_maps_api_key
   DEEPSEEK_API_KEY=your_deepseek_api_key
   FIRECRALER_API_KEY=your_firecraler_api_key
   FIREBASE_API_KEY=your_firebase_api_key
   FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
   FIREBASE_PROJECT_ID=your_project_id
   FIREBASE_STORAGE_BUCKET=your_project.appspot.com
   FIREBASE_MESSAGING_SENDER_ID=your_sender_id
   FIREBASE_APP_ID=your_app_id
   FIREBASE_MEASUREMENT_ID=your_measurement_id
   MAIL_DEFAULT_SENDER=your_email@gmail.com
   MAIL_USERNAME=your_email@gmail.com
   MAIL_PASSWORD=your_app_specific_password
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   ```

5. **Run Locally**:
   ```bash
   python run.py
   ```
   Access at `http://localhost:5000`.

## Deployment Process

### Heroku Deployment

1. **Create Heroku App**:
   ```bash
   heroku create your-app-name
   ```

2. **Set Config Vars**:
   Set all required variables:
   ```bash
   heroku config:set GOOGLE_MAPS_API_KEY=your_key
   heroku config:set DEEPSEEK_API_KEY=your_key
   heroku config:set FIRECRALER_API_KEY=your_key
   heroku config:set FIREBASE_API_KEY=your_key
   heroku config:set FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
   heroku config:set FIREBASE_PROJECT_ID=your_project_id
   heroku config:set FIREBASE_STORAGE_BUCKET=your_project.appspot.com
   heroku config:set FIREBASE_MESSAGING_SENDER_ID=your_sender_id
   heroku config:set FIREBASE_APP_ID=your_app_id
   heroku config:set FIREBASE_MEASUREMENT_ID=your_measurement_id
   heroku config:set MAIL_DEFAULT_SENDER=your_email@gmail.com
   heroku config:set MAIL_USERNAME=your_email@gmail.com
   heroku config:set MAIL_PASSWORD=your_app_specific_password
   heroku config:set MAIL_SERVER=smtp.gmail.com
   heroku config:set MAIL_PORT=587
   heroku config:set MAIL_USE_TLS=True
   ```

3. **Deploy Code**:
   ```bash
   git push heroku master
   ```

4. **Scale Dynos**:
   - **For Basic ($7/month)**:
     ```bash
     heroku ps:scale web=1 -a your-app-name
     ```
   - **For Eco ($5/month, 1000 hours)**:
     Subscribe via Dashboard, then:
     ```bash
     heroku ps:scale web=1 -a your-app-name
     ```

5. **Verify Deployment**:
   ```bash
   heroku logs --tail -a your-app-name
   heroku open -a your-app-name
   ```

## Challenges and Solutions

| Challenge            | Impact                     | Solution                                    |
|----------------------|----------------------------|---------------------------------------------|
| Heroku Dyno Scaling  | App offline without plan   | Subscribe to Eco ($5/month) or Basic ($7/month); scale with `heroku ps:scale web=1`. |
| Firebase Config Errors | Auth/Firestore fails     | Verify all `FIREBASE_*` vars match Firebase Console settings. |
| Email Delivery Failures | Itineraries not sent    | Use Gmail app-specific password; ensure `MAIL_*` vars are correct. |
| API Rate Limits      | Google Maps/DeepSeek/Firecraler throttled | Implement caching (e.g., Redis); monitor usage via API dashboards. |
| Missing Procfile     | Deployment fails on Heroku | Create `Procfile`: `echo "web: gunicorn wsgi:app" > Procfile`. |
| Dependency Conflicts | App crashes on start       | Pin versions in `requirements.txt` (e.g., `flask==3.1.0`); test locally. |

## Usage Guide

### Web Interface

1. **Visit**: `http://localhost:5000` (or your deployed URL)
2. **Sign In**: Use Google or email/password via Firebase Auth.
3. **Search Places**: Enter a location (e.g., "Rome, Italy") and select a category (e.g., "Museums").
4. **Generate Itinerary**: Fill out the "Request Guide" form with trip details and receive an email with local news.
5. **View Routes**: Add places to your route and see directions on the map.

### API Usage

- **Search Places**:
  ```bash
  curl "http://localhost:5000/api/search_places?location=Tokyo&type=park"
  ```
- **Generate Guide**:
  ```bash
  curl -X POST "http://localhost:5000/api/generate-travel-guide" -d '{"destination": "Paris", "email": "user@example.com"}'
  ```

## Future Enhancements

- **User Profiles**: Store preferences and past trips in Firestore.
- **Mobile App**: Extend to iOS/Android with React Native.
- **Multi-Language Support**: Add real-time translation for itineraries.
- **Offline Mode**: Cache maps and guides for offline access.
- **Social Features**: Share itineraries with friends via links or QR codes.
- **Enhanced News Integration**: Use Firecraler API with AI to summarize and prioritize local news.

## Author

**Said Lfagrouche** | [Website](https://saidlfagrouche.com/) | [LinkedIn](https://www.linkedin.com/in/saidlfagrouche/)

## 🤝 **Contributing**

We welcome contributions! Follow these steps:
1. Fork the repository.
2. Create your feature branch:
   ```sh
   git checkout -b feature/AmazingFeature
   ```
3. Commit your changes:
   ```sh
   git commit -m "Add some AmazingFeature"
   ```
4. Push to your branch:
   ```sh
   git push origin feature/AmazingFeature
   ```
5. Open a **Pull Request**.

---

## 📄 **License**

Distributed under the **MIT License**. See the `LICENSE` file for more information.

---

For further assistance, reach out via [GitHub Issues](https://github.com/slfagrouche/TravelAICompanion/issues).

Happy Coding! :)

