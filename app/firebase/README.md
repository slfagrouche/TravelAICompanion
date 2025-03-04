# Firebase Integration for Personal Travel Guide

This directory contains the Firebase configuration for the Personal Travel Guide application, including:

- Authentication (email/password and Google sign-in)
- Firestore database for user data and email guide requests
- Cloud Functions for sending personalized travel guide emails

## Setup Instructions

### Prerequisites

1. Install Firebase CLI:
   ```
   npm install -g firebase-tools
   ```

2. Log in to Firebase:
   ```
   firebase login
   ```

3. Create a new Firebase project in the [Firebase Console](https://console.firebase.google.com/)

### Configuration

1. Initialize Firebase in this directory:
   ```
   cd app/firebase
   firebase init
   ```
   - Select Firestore, Functions, and Hosting
   - Choose your Firebase project
   - Use existing files when prompted

2. Update the Firebase configuration in the HTML file with your project's configuration:
   ```javascript
   const firebaseConfig = {
     apiKey: "YOUR_API_KEY",
     authDomain: "YOUR_PROJECT_ID.firebaseapp.com",
     projectId: "YOUR_PROJECT_ID",
     storageBucket: "YOUR_PROJECT_ID.appspot.com",
     messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
     appId: "YOUR_APP_ID"
   };
   ```

3. Set up email configuration for the Cloud Function:
   ```
   firebase functions:config:set email.user="your-email@gmail.com" email.password="your-app-password"
   ```
   Note: For Gmail, you'll need to use an "App Password" rather than your regular password. See [Google Account Help](https://support.google.com/accounts/answer/185833) for instructions.

### Deployment

1. Deploy Firestore rules and indexes:
   ```
   firebase deploy --only firestore
   ```

2. Deploy Cloud Functions:
   ```
   firebase deploy --only functions
   ```

3. Deploy Hosting (if needed):
   ```
   firebase deploy --only hosting
   ```

## Features

### Authentication

The application supports:
- Email/password authentication
- Google sign-in
- Password reset functionality

### Firestore Database

The database structure includes:
- `users` collection: Stores user profiles and preferences
- `emailGuides` collection: Logs of requested travel guides

### Cloud Functions

- `sendTravelGuide`: Generates and sends personalized travel guide emails based on user preferences

## Security

- Firestore security rules ensure users can only access their own data
- Authentication is required for all sensitive operations
- Cloud Functions validate user authentication before processing requests

## Local Development

1. Start Firebase emulators:
   ```
   firebase emulators:start
   ```

2. Use the emulator UI at http://localhost:4000 to view and manage your local Firebase resources

## Troubleshooting

- If you encounter CORS issues with Cloud Functions, ensure your Firebase project has the appropriate CORS configuration
- For authentication issues, check the Firebase Authentication console for error logs
- For Cloud Function deployment failures, check the Firebase CLI output for detailed error messages
