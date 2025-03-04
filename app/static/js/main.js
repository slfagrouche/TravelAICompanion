let map;
let markers = [];
let directionsService;
let directionsRenderer;
let selectedPlaces = [];

function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: 0, lng: 0 },
        zoom: 2
    });
    
    directionsService = new google.maps.DirectionsService();
    directionsRenderer = new google.maps.DirectionsRenderer();
    directionsRenderer.setMap(map);
}

async function searchPlaces() {
    const location = document.getElementById('location').value;
    const placeType = document.getElementById('place-type').value;
    
    const response = await fetch(`/search_places?location=${location}&type=${placeType}`);
    const data = await response.json();
    
    displayPlaces(data.places);
}

function displayPlaces(places) {
    // Clear existing markers
    markers.forEach(marker => marker.setMap(null));
    markers = [];
    
    // Clear places list
    const placesList = document.getElementById('places-list');
    placesList.innerHTML = '';
    
    places.forEach((place, index) => {
        // Add marker
        const marker = new google.maps.Marker({
            position: place.location,
            map: map,
            title: place.name,
            label: (index + 1).toString()
        });
        
        markers.push(marker);
        
        // Add to list
        const placeDiv = document.createElement('div');
        placeDiv.className = 'place-item';
        placeDiv.innerHTML = `
            <h3>${index + 1}. ${place.name}</h3>
            <p>${place.address}</p>
            <p>Rating: ${place.rating || 'N/A'}</p>
            <p class="description">${place.description || 'No description available.'}</p>
            <button onclick='addToRoute(${JSON.stringify(place)})'>Add to Route</button>
        `;
        placesList.appendChild(placeDiv);
    });
    
    // Center map on first result
    if (places.length > 0) {
        map.setCenter(places[0].location);
        map.setZoom(13);
    }
}

function addToRoute(place) {
    selectedPlaces.push(place);
    if (selectedPlaces.length >= 2) {
        calculateAndDisplayRoute();
    }
}

function calculateAndDisplayRoute() {
    if (selectedPlaces.length < 2) return;
    
    const origin = selectedPlaces[0].location;
    const destination = selectedPlaces[selectedPlaces.length - 1].location;
    
    let waypoints = [];
    if (selectedPlaces.length > 2) {
        waypoints = selectedPlaces.slice(1, -1).map(place => ({
            location: place.location,
            stopover: true
        }));
    }
    
    directionsService.route(
        {
            origin: origin,
            destination: destination,
            waypoints: waypoints,
            optimizeWaypoints: true,
            travelMode: 'WALKING'
        },
        function(response, status) {
            if (status === 'OK') {
                directionsRenderer.setDirections(response);
            } else {
                console.error('Directions request failed:', status);
            }
        }
    );
}

function clearRoute() {
    selectedPlaces = [];
    directionsRenderer.setDirections({routes: []});
}

async function translateDescriptions() {
    const descriptions = document.querySelectorAll('.description');
    for (const desc of descriptions) {
        const text = desc.innerText;
        const response = await fetch(`/translate?text=${encodeURIComponent(text)}&target_lang=en`);
        const data = await response.json();
        desc.innerText = data.translated_text || text;
    }
}

// Handle tag clicks
document.querySelectorAll(".side-tags .tag").forEach((tag) => {
    tag.addEventListener("click", (e) => {
      e.preventDefault();
  
      // Remove active class from all tags
      document.querySelectorAll(".side-tags .tag").forEach((t) => t.classList.remove("active"));
  
      // Add active class to the clicked tag
      tag.classList.add("active");
  
      // Trigger search with the selected tag's type
      searchPlaces();
    });
  });
  
  // Updated searchPlaces function
  async function searchPlaces() {
    const location = document.getElementById("location").value;
    const placeType = document.querySelector(".side-tags .tag.active").dataset.type;
  
    // Show loading spinner
    document.getElementById("loadingSpinner").style.display = "block";
  
    try {
      const response = await fetch(
        `/search_places?location=${encodeURIComponent(location)}&type=${placeType}`
      );
      const data = await response.json();
  
      // Display places
      displayPlaces(data.places);
    } catch (error) {
      console.error("Error searching places:", error);
    } finally {
      // Hide loading spinner
      document.getElementById("loadingSpinner").style.display = "none";
    }
  }