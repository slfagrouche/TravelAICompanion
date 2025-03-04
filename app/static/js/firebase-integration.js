
// Initialize Firebase
try {
  firebase.initializeApp(firebaseConfig);
  console.log("Firebase initialized successfully");
} catch (error) {
  console.error("Firebase initialization error:", error);
  showAlert("Firebase initialization failed. Authentication features are disabled.", "danger");
}

// Firebase Services
let auth = firebase.auth();
let db = firebase.firestore();
let functions = firebase.functions();
let currentUser = null;

// DOM Elements - will be initialized when document is ready
let authButtons;
let userMenu;
let userAvatar;
let userDropdown;
let loginBtn;
let signupBtn;
let logoutBtn;
let authModal;
let authClose;
let loginTab;
let signupTab;
let loginForm;
let signupForm;
let googleLoginBtn;
let forgotPasswordBtn;
let requestGuideBtn;
let emailGuideModal;
let emailGuideClose;
let emailGuideForm;
let preferenceTags;

// Initialize Firebase components when the document is ready
document.addEventListener('DOMContentLoaded', () => {
  // Initialize Firebase Auth
  initializeAuth();
  
  // Initialize DOM elements
  initializeDOMElements();
  
  // Add event listeners
  addEventListeners();
  
  // Set up auth state change listener
  setupAuthStateListener();
});

/**
 * Initialize Firebase Authentication and Firestore
 */
async function initializeAuth() {
  try {
    // Check if Firebase is already initialized
    if (!firebase.apps.length) {
      console.error('Firebase is not initialized. Make sure firebaseConfig is defined in the HTML.');
      return;
    }
    
    // Get Firebase Auth instance
    auth = firebase.auth();
    db = firebase.firestore();
    functions = firebase.functions();

    // Initialize Firestore settings
    db.settings({
      cacheSizeBytes: firebase.firestore.CACHE_SIZE_UNLIMITED
    });

    // Enable offline persistence
    await db.enablePersistence()
      .catch((err) => {
        if (err.code == 'failed-precondition') {
          console.warn('Multiple tabs open, persistence can only be enabled in one tab at a time.');
        } else if (err.code == 'unimplemented') {
          console.warn('The current browser does not support persistence.');
        }
      });

    // Create necessary collections if they don't exist
    const collections = ['users', 'preferences', 'travelGuides'];
    for (const collection of collections) {
      try {
        await db.collection(collection).get();
        console.log(`${collection} collection exists`);
      } catch (error) {
        console.error(`Error checking ${collection} collection:`, error);
      }
    }

  } catch (error) {
    console.error('Error initializing Firebase:', error);
    showAlert('Error initializing Firebase. Some features may not work properly.', 'warning');
  }
}

/**
 * Initialize DOM elements
 */
function initializeDOMElements() {
  // Auth elements
  authButtons = document.getElementById('auth-buttons');
  userMenu = document.getElementById('user-menu');
  userAvatar = document.getElementById('user-avatar');
  userDropdown = document.getElementById('user-dropdown');
  loginBtn = document.getElementById('login-btn');
  signupBtn = document.getElementById('signup-btn');
  logoutBtn = document.getElementById('logout-btn');
  authModal = document.getElementById('auth-modal');
  authClose = document.getElementById('auth-close');
  loginTab = document.getElementById('login-tab');
  signupTab = document.getElementById('signup-tab');
  loginForm = document.getElementById('login-form');
  signupForm = document.getElementById('signup-form');
  googleLoginBtn = document.getElementById('google-login');
  forgotPasswordBtn = document.getElementById('forgot-password');
  
  // Email Guide elements
  requestGuideBtn = document.getElementById('request-guide-btn');
  emailGuideModal = document.getElementById('email-guide-modal');
  emailGuideClose = document.getElementById('email-guide-close');
  emailGuideForm = document.getElementById('email-guide-form');
  preferenceTags = document.querySelectorAll('.preference-tag');
}

/**
 * Add event listeners to DOM elements
 */
function addEventListeners() {
  // Auth Modal
  loginBtn.addEventListener('click', () => showAuthModal('login'));
  signupBtn.addEventListener('click', () => showAuthModal('signup'));
  authClose.addEventListener('click', () => authModal.classList.remove('active'));
  
  // Auth Tabs
  loginTab.addEventListener('click', () => {
    loginTab.classList.add('active');
    signupTab.classList.remove('active');
    loginForm.classList.add('active');
    signupForm.classList.remove('active');
  });
  
  signupTab.addEventListener('click', () => {
    signupTab.classList.add('active');
    loginTab.classList.remove('active');
    signupForm.classList.add('active');
    loginForm.classList.remove('active');
  });
  
  // User Menu
  userAvatar.addEventListener('click', () => userDropdown.classList.toggle('active'));
  
  // Close dropdown when clicking outside
  document.addEventListener('click', (e) => {
    if (userMenu && !userMenu.contains(e.target)) {
      userDropdown.classList.remove('active');
    }
  });
  
  // Logout
  logoutBtn.addEventListener('click', handleLogout);
  
  // Login Form
  loginForm.addEventListener('submit', handleLogin);
  
  // Signup Form
  signupForm.addEventListener('submit', handleSignup);
  
  // Google Login
  googleLoginBtn.addEventListener('click', handleGoogleLogin);
  
  // Forgot Password
  forgotPasswordBtn.addEventListener('click', handleForgotPassword);
  
  // Email Guide Modal
  if (requestGuideBtn) {
    requestGuideBtn.addEventListener('click', handleRequestGuide);
  }
  
  if (emailGuideClose) {
    emailGuideClose.addEventListener('click', () => emailGuideModal.classList.remove('active'));
  }
  
  // Toggle preference tags
  if (preferenceTags) {
    preferenceTags.forEach(tag => {
      tag.addEventListener('click', () => tag.classList.toggle('active'));
    });
  }
  
  // Email Guide Form
  if (emailGuideForm) {
    emailGuideForm.addEventListener('submit', handleEmailGuideSubmit);
  }
}

/**
 * Set up Firebase Auth state change listener
 */
function setupAuthStateListener() {
  auth.onAuthStateChanged(async (user) => {
    currentUser = user;
    
    if (user) {
      // User is signed in
      if (authButtons) authButtons.classList.add('d-none');
      if (userMenu) userMenu.classList.remove('d-none');
      
      // Update user avatar
      if (userAvatar) {
        if (user.photoURL) {
          userAvatar.src = user.photoURL;
        } else if (user.displayName) {
          userAvatar.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(user.displayName)}&background=007bff&color=fff`;
        } else {
          userAvatar.src = `https://ui-avatars.com/api/?name=User&background=007bff&color=fff`;
        }
      }

      // Update user document with last login
      try {
        await db.collection('users').doc(user.uid).update({
          lastLogin: firebase.firestore.FieldValue.serverTimestamp()
        });
      } catch (error) {
        console.error('Error updating last login:', error);
      }
    } else {
      // User is signed out
      if (authButtons) authButtons.classList.remove('d-none');
      if (userMenu) userMenu.classList.add('d-none');
    }
  });
}

/**
 * Show the authentication modal
 * @param {string} tab - The tab to show ('login' or 'signup')
 */
function showAuthModal(tab = 'login') {
  if (tab === 'login') {
    loginTab.click();
  } else {
    signupTab.click();
  }
  authModal.classList.add('active');
}

/**
 * Handle login form submission
 * @param {Event} e - The form submit event
 */
async function handleLogin(e) {
  e.preventDefault();
  
  const email = document.getElementById('login-email').value;
  const password = document.getElementById('login-password').value;
  
  try {
    const userCredential = await auth.signInWithEmailAndPassword(email, password);
    
    // Update user's last login time
    await db.collection('users').doc(userCredential.user.uid).update({
      lastLogin: firebase.firestore.FieldValue.serverTimestamp()
    });
    
    authModal.classList.remove('active');
    showAlert('Logged in successfully!', 'success');
  } catch (error) {
    console.error('Login error:', error);
    if (error.code === 'auth/user-not-found') {
      showAlert('No account found with this email. Please sign up.', 'warning');
    } else if (error.code === 'auth/wrong-password') {
      showAlert('Incorrect password. Please try again.', 'warning');
    } else {
      showAlert(`Login failed: ${error.message}`, 'danger');
    }
  }
}

/**
 * Handle signup form submission
 * @param {Event} e - The form submit event
 */
async function handleSignup(e) {
  e.preventDefault();
  
  const name = document.getElementById('signup-name').value;
  const email = document.getElementById('signup-email').value;
  const password = document.getElementById('signup-password').value;
  
  try {
    // Create user with email and password
    const userCredential = await auth.createUserWithEmailAndPassword(email, password);
    
    // Update user profile with display name
    await userCredential.user.updateProfile({
      displayName: name
    });
    
    // Create user document in Firestore with retry mechanism
    const createUserDoc = async (retries = 3) => {
      try {
        await db.collection('users').doc(userCredential.user.uid).set({
          name: name,
          email: email,
          createdAt: firebase.firestore.FieldValue.serverTimestamp(),
          lastLogin: firebase.firestore.FieldValue.serverTimestamp(),
          preferences: [],
          accountStatus: 'active'
        });
        console.log('User document created successfully');
      } catch (error) {
        if (retries > 0 && (error.code === 'unavailable' || error.code === 'resource-exhausted')) {
          console.log(`Retrying user document creation. Attempts left: ${retries-1}`);
          await new Promise(resolve => setTimeout(resolve, 1000));
          return createUserDoc(retries - 1);
        }
        throw error;
      }
    };
    
    await createUserDoc();
    
    authModal.classList.remove('active');
    showAlert('Account created successfully!', 'success');
  } catch (error) {
    console.error('Signup error:', error);
    if (error.code === 'auth/email-already-in-use') {
      showAlert('This email is already registered. Please try logging in.', 'warning');
    } else if (error.code === 'auth/weak-password') {
      showAlert('Please choose a stronger password (at least 6 characters).', 'warning');
    } else {
      showAlert(`Signup failed: ${error.message}`, 'danger');
    }
  }
}

/**
 * Handle Google login
 */
async function handleGoogleLogin() {
  const provider = new firebase.auth.GoogleAuthProvider();
  
  try {
    const result = await auth.signInWithPopup(provider);
    
    // Check if this is a new user
    const isNewUser = result.additionalUserInfo.isNewUser;
    
    if (isNewUser) {
      // Create user document in Firestore
      await db.collection('users').doc(result.user.uid).set({
        name: result.user.displayName,
        email: result.user.email,
        createdAt: firebase.firestore.FieldValue.serverTimestamp(),
        lastLogin: firebase.firestore.FieldValue.serverTimestamp(),
        preferences: [],
        accountStatus: 'active'
      });
    } else {
      // Update last login time
      await db.collection('users').doc(result.user.uid).update({
        lastLogin: firebase.firestore.FieldValue.serverTimestamp()
      });
    }
    
    authModal.classList.remove('active');
    showAlert('Logged in with Google successfully!', 'success');
  } catch (error) {
    console.error('Google login error:', error);
    let errorMessage = 'Failed to sign in with Google. Please try again.';
    
    switch (error.code) {
      case 'auth/cancelled-popup-request':
        errorMessage = 'Sign-in was cancelled. Please try again and keep the popup window open.';
        break;
      case 'auth/popup-blocked':
        errorMessage = 'Sign-in popup was blocked by your browser. Please allow popups for this site and try again.';
        break;
      case 'auth/popup-closed-by-user':
        errorMessage = 'Sign-in was cancelled. Please keep the popup window open until sign-in is complete.';
        break;
      case 'auth/account-exists-with-different-credential':
        errorMessage = 'An account already exists with the same email address but different sign-in credentials. Try signing in using the original method.';
        break;
      case 'auth/network-request-failed':
        errorMessage = 'Network error occurred. Please check your internet connection and try again.';
        break;
      case 'auth/user-disabled':
        errorMessage = 'This account has been disabled. Please contact support for assistance.';
        break;
      case 'auth/operation-not-allowed':
        errorMessage = 'Google sign-in is not enabled for this application. Please contact support.';
        break;
    }
    
    showAlert(errorMessage, 'danger');
  }
}

/**
 * Handle logout
 */
async function handleLogout() {
  try {
    if (currentUser) {
      // Update last logout time
      await db.collection('users').doc(currentUser.uid).update({
        lastLogout: firebase.firestore.FieldValue.serverTimestamp()
      });
    }
    await auth.signOut();
    showAlert('Logged out successfully!', 'success');
  } catch (error) {
    console.error('Logout error:', error);
    showAlert(`Logout failed: ${error.message}`, 'danger');
  }
}

/**
 * Handle forgot password
 */
async function handleForgotPassword() {
  const email = document.getElementById('login-email').value;
  
  if (!email) {
    showAlert('Please enter your email address first.', 'warning');
    return;
  }
  
  try {
    await auth.sendPasswordResetEmail(email);
    showAlert('Password reset email sent. Check your inbox.', 'success');
  } catch (error) {
    console.error('Password reset error:', error);
    if (error.code === 'auth/user-not-found') {
      showAlert('No account found with this email.', 'warning');
    } else {
      showAlert(`Password reset failed: ${error.message}`, 'danger');
    }
  }
}

/**
 * Handle request guide button click
 */
function handleRequestGuide() {
  if (!currentUser) {
    showAlert('Please log in to request a personalized travel guide.', 'warning');
    showAuthModal('login');
    return;
  }
  
  // Pre-fill email if user is logged in
  document.getElementById('guide-email').value = currentUser.email;
  
  // Pre-fill destination if one is selected
  const location = document.getElementById('location').value;
  if (location) {
    document.getElementById('guide-destination').value = location;
  }
  
  emailGuideModal.classList.add('active');
}

/**
 * Handle email guide form submission
 * @param {Event} e - The form submit event
 */
async function handleEmailGuideSubmit(e) {
  e.preventDefault();
  console.log('Form submitted - Starting travel guide generation process');

  if (!currentUser) {
    console.warn('No current user - Prompting login');
    showAlert('Please log in to request a personalized travel guide.', 'warning');
    emailGuideModal.classList.remove('active');
    showAuthModal('login');
    return;
  }

  try {
    const destination = document.getElementById('guide-destination').value;
    const startDate = document.getElementById('guide-start-date').value;
    const endDate = document.getElementById('guide-end-date').value;
    const travelers = document.getElementById('guide-travelers').value;
    const budget = document.getElementById('guide-budget').value;
    const interests = document.getElementById('guide-interests').value;
    const email = document.getElementById('guide-email').value;
    const specialRequests = document.getElementById('guide-special-requests').value;

    console.log('Form data collected:', { destination, startDate, endDate, travelers, budget, interests, email, specialRequests });

    const start = new Date(startDate);
    const end = new Date(endDate);
    const numberOfDays = Math.ceil((end - start) / (1000 * 60 * 60 * 24));
    if (numberOfDays < 1) {
      throw new Error('End date must be after start date');
    }

    console.log('Initiating API request to /api/generate-travel-guide');
    const response = await fetch('http://localhost:5000/api/generate-travel-guide', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({
        destination,
        start_date: startDate,
        end_date: endDate,
        travelers: parseInt(travelers),
        budget,
        interests,
        special_requests: specialRequests,
        email  // Ensure email is included
      })
    });

    console.log('API response status:', response.status);
    const result = await response.json();
    console.log('API response data:', result);

    if (!response.ok) {
      throw new Error(result.message || 'Failed to generate travel guide');
    }

    emailGuideModal.classList.remove('active');
    showAlert('Your personalized travel guide has been generated and sent to your email!', 'success');
  } catch (error) {
    console.error('Error in handleEmailGuideSubmit:', error.stack);
    showAlert(`Failed to generate travel guide: ${error.message}`, 'danger');
  }
}

/**
 * Show an alert message
 * @param {string} message - The message to display
 * @param {string} type - The alert type ('success', 'danger', 'warning', 'info')
 */
function showAlert(message, type = 'info') {
  // Create alert element
  const alertDiv = document.createElement('div');
  alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-4`;
  alertDiv.style.zIndex = '9999';
  alertDiv.style.maxWidth = '90%';
  alertDiv.style.width = '500px';
  alertDiv.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
  alertDiv.style.border = type === 'danger' ? '1px solid #dc3545' : '1px solid rgba(0,0,0,0.1)';
  
  // Add icon based on alert type
  const icon = type === 'success' ? '✓' :
               type === 'danger' ? '⚠' :
               type === 'warning' ? '!' : 'ℹ';
               
  alertDiv.innerHTML = `
    <div class="d-flex align-items-center">
      <div class="me-3" style="font-size: 1.2em;">${icon}</div>
      <div class="flex-grow-1">${message}</div>
      <button type="button" class="btn-close ms-2" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>
  `;
  
  // Add to document
  document.body.appendChild(alertDiv);
  
  // Auto-dismiss after 5 seconds
  setTimeout(() => {
    alertDiv.classList.remove('show');
    setTimeout(() => alertDiv.remove(), 150);
  }, 5000);
}
