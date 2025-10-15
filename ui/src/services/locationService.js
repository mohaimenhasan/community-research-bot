// Location service for detecting user location and finding nearby cities
class LocationService {
  constructor() {
    this.currentLocation = null;
    this.nearbyCities = [];
  }

  // Calculate distance between two coordinates in miles
  calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 3959; // Earth's radius in miles
    const dLat = this.toRadians(lat2 - lat1);
    const dLon = this.toRadians(lon2 - lon1);
    const a =
      Math.sin(dLat/2) * Math.sin(dLat/2) +
      Math.cos(this.toRadians(lat1)) * Math.cos(this.toRadians(lat2)) *
      Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
  }

  toRadians(degrees) {
    return degrees * (Math.PI/180);
  }

  // Major global cities database for geolocation fallback
  getAllCities() {
    return [
      // Bosnia and Herzegovina
      { city: 'Sarajevo', country: 'Bosnia and Herzegovina', coordinates: [43.8563, 18.4131] },
      { city: 'Banja Luka', country: 'Bosnia and Herzegovina', coordinates: [44.7666, 17.1736] },
      { city: 'Tuzla', country: 'Bosnia and Herzegovina', coordinates: [44.5386, 18.6708] },
      { city: 'Zenica', country: 'Bosnia and Herzegovina', coordinates: [44.2035, 17.9061] },
      { city: 'Mostar', country: 'Bosnia and Herzegovina', coordinates: [43.3438, 17.8078] },

      // Australia
      { city: 'Sydney', state: 'NSW', country: 'Australia', coordinates: [-33.8688, 151.2093] },
      { city: 'Melbourne', state: 'VIC', country: 'Australia', coordinates: [-37.8136, 144.9631] },
      { city: 'Brisbane', state: 'QLD', country: 'Australia', coordinates: [-27.4698, 153.0251] },
      { city: 'Perth', state: 'WA', country: 'Australia', coordinates: [-31.9505, 115.8605] },
      { city: 'Adelaide', state: 'SA', country: 'Australia', coordinates: [-34.9285, 138.6007] },
      { city: 'Canberra', state: 'ACT', country: 'Australia', coordinates: [-35.2809, 149.1300] },
      { city: 'Newcastle', state: 'NSW', country: 'Australia', coordinates: [-32.9283, 151.7817] },
      { city: 'Wollongong', state: 'NSW', country: 'Australia', coordinates: [-34.4278, 150.8931] },
      { city: 'Gold Coast', state: 'QLD', country: 'Australia', coordinates: [-28.0167, 153.4000] },

      // United States
      { city: 'New York', state: 'NY', country: 'USA', coordinates: [40.7128, -74.0060] },
      { city: 'Los Angeles', state: 'CA', country: 'USA', coordinates: [34.0522, -118.2437] },
      { city: 'Chicago', state: 'IL', country: 'USA', coordinates: [41.8781, -87.6298] },
      { city: 'Houston', state: 'TX', country: 'USA', coordinates: [29.7604, -95.3698] },
      { city: 'Phoenix', state: 'AZ', country: 'USA', coordinates: [33.4484, -112.0740] },
      { city: 'Philadelphia', state: 'PA', country: 'USA', coordinates: [39.9526, -75.1652] },
      { city: 'San Antonio', state: 'TX', country: 'USA', coordinates: [29.4241, -98.4936] },
      { city: 'San Diego', state: 'CA', country: 'USA', coordinates: [32.7157, -117.1611] },
      { city: 'Dallas', state: 'TX', country: 'USA', coordinates: [32.7767, -96.7970] },
      { city: 'San Jose', state: 'CA', country: 'USA', coordinates: [37.3382, -121.8863] },
      { city: 'Austin', state: 'TX', country: 'USA', coordinates: [30.2672, -97.7431] },
      { city: 'Jacksonville', state: 'FL', country: 'USA', coordinates: [30.3322, -81.6557] },
      { city: 'Fort Worth', state: 'TX', country: 'USA', coordinates: [32.7555, -97.3308] },
      { city: 'Columbus', state: 'OH', country: 'USA', coordinates: [39.9612, -82.9988] },
      { city: 'San Francisco', state: 'CA', country: 'USA', coordinates: [37.7749, -122.4194] },
      { city: 'Charlotte', state: 'NC', country: 'USA', coordinates: [35.2271, -80.8431] },
      { city: 'Indianapolis', state: 'IN', country: 'USA', coordinates: [39.7684, -86.1581] },
      { city: 'Seattle', state: 'WA', country: 'USA', coordinates: [47.6062, -122.3321] },
      { city: 'Denver', state: 'CO', country: 'USA', coordinates: [39.7392, -104.9903] },
      { city: 'Washington', state: 'DC', country: 'USA', coordinates: [38.9072, -77.0369] },
      { city: 'Boston', state: 'MA', country: 'USA', coordinates: [42.3601, -71.0589] },
      { city: 'Nashville', state: 'TN', country: 'USA', coordinates: [36.1627, -86.7816] },
      { city: 'Baltimore', state: 'MD', country: 'USA', coordinates: [39.2904, -76.6122] },
      { city: 'Portland', state: 'OR', country: 'USA', coordinates: [45.5152, -122.6784] },

      // Canada
      { city: 'Toronto', province: 'ON', country: 'Canada', coordinates: [43.6532, -79.3832] },
      { city: 'Vancouver', province: 'BC', country: 'Canada', coordinates: [49.2827, -123.1207] },
      { city: 'Montreal', province: 'QC', country: 'Canada', coordinates: [45.5017, -73.5673] },
      { city: 'Calgary', province: 'AB', country: 'Canada', coordinates: [51.0447, -114.0719] },
      { city: 'Edmonton', province: 'AB', country: 'Canada', coordinates: [53.5461, -113.4938] },
      { city: 'Ottawa', province: 'ON', country: 'Canada', coordinates: [45.4215, -75.6972] },
      { city: 'Winnipeg', province: 'MB', country: 'Canada', coordinates: [49.8951, -97.1384] },
      { city: 'Quebec City', province: 'QC', country: 'Canada', coordinates: [46.8139, -71.2080] },

      // United Kingdom
      { city: 'London', country: 'United Kingdom', coordinates: [51.5074, -0.1278] },
      { city: 'Birmingham', country: 'United Kingdom', coordinates: [52.4862, -1.8904] },
      { city: 'Manchester', country: 'United Kingdom', coordinates: [53.4808, -2.2426] },
      { city: 'Liverpool', country: 'United Kingdom', coordinates: [53.4084, -2.9916] },
      { city: 'Leeds', country: 'United Kingdom', coordinates: [53.8008, -1.5491] },
      { city: 'Sheffield', country: 'United Kingdom', coordinates: [53.3811, -1.4701] },
      { city: 'Bristol', country: 'United Kingdom', coordinates: [51.4545, -2.5879] },
      { city: 'Glasgow', country: 'Scotland', coordinates: [55.8642, -4.2518] },
      { city: 'Edinburgh', country: 'Scotland', coordinates: [55.9533, -3.1883] },

      // Germany
      { city: 'Berlin', country: 'Germany', coordinates: [52.5200, 13.4050] },
      { city: 'Hamburg', country: 'Germany', coordinates: [53.5511, 9.9937] },
      { city: 'Munich', country: 'Germany', coordinates: [48.1351, 11.5820] },
      { city: 'Cologne', country: 'Germany', coordinates: [50.9375, 6.9603] },
      { city: 'Frankfurt', country: 'Germany', coordinates: [50.1109, 8.6821] },

      // France
      { city: 'Paris', country: 'France', coordinates: [48.8566, 2.3522] },
      { city: 'Marseille', country: 'France', coordinates: [43.2965, 5.3698] },
      { city: 'Lyon', country: 'France', coordinates: [45.7640, 4.8357] },
      { city: 'Toulouse', country: 'France', coordinates: [43.6047, 1.4442] },
      { city: 'Nice', country: 'France', coordinates: [43.7102, 7.2620] },

      // Other Balkans
      { city: 'Belgrade', country: 'Serbia', coordinates: [44.7866, 20.4489] },
      { city: 'Zagreb', country: 'Croatia', coordinates: [45.8150, 15.9819] },
      { city: 'Ljubljana', country: 'Slovenia', coordinates: [46.0569, 14.5058] },
      { city: 'Skopje', country: 'North Macedonia', coordinates: [41.9973, 21.4280] },
      { city: 'Podgorica', country: 'Montenegro', coordinates: [42.4304, 19.2594] },

      // Other major cities
      { city: 'Vienna', country: 'Austria', coordinates: [48.2082, 16.3738] },
      { city: 'Amsterdam', country: 'Netherlands', coordinates: [52.3676, 4.9041] },
      { city: 'Brussels', country: 'Belgium', coordinates: [50.8503, 4.3517] },
      { city: 'Copenhagen', country: 'Denmark', coordinates: [55.6761, 12.5683] },
      { city: 'Stockholm', country: 'Sweden', coordinates: [59.3293, 18.0686] },
      { city: 'Oslo', country: 'Norway', coordinates: [59.9139, 10.7522] },
      { city: 'Helsinki', country: 'Finland', coordinates: [60.1699, 24.9384] },
      { city: 'Prague', country: 'Czech Republic', coordinates: [50.0755, 14.4378] },
      { city: 'Budapest', country: 'Hungary', coordinates: [47.4979, 19.0402] },
      { city: 'Warsaw', country: 'Poland', coordinates: [52.2297, 21.0122] }
    ];
  }

  // Get user's current location using geolocation API
  async getCurrentLocation() {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('Geolocation is not supported by this browser'));
        return;
      }

      navigator.geolocation.getCurrentPosition(
        async (position) => {
          const { latitude, longitude } = position.coords;

          try {
            // Try to reverse geocode to get city name
            const cityName = await this.reverseGeocode(latitude, longitude);
            const location = {
              coordinates: [latitude, longitude],
              city: cityName.city || 'Unknown City',
              state: cityName.state || cityName.province,
              country: cityName.country || 'USA',
              detected: true
            };

            this.currentLocation = location;
            resolve(location);
          } catch (error) {
            // If reverse geocoding fails, still return coordinates
            const location = {
              coordinates: [latitude, longitude],
              city: 'Current Location',
              state: '',
              country: '',
              detected: true
            };

            this.currentLocation = location;
            resolve(location);
          }
        },
        (error) => {
          console.error('Geolocation error:', error);
          reject(error);
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 300000 // 5 minutes
        }
      );
    });
  }

  // Simple reverse geocoding - in production you'd use a real service
  async reverseGeocode(lat, lon) {
    // For demo, find the closest city in our database
    const cities = this.getAllCities();
    let closestCity = null;
    let minDistance = Infinity;

    cities.forEach(city => {
      const distance = this.calculateDistance(lat, lon, city.coordinates[0], city.coordinates[1]);
      if (distance < minDistance) {
        minDistance = distance;
        closestCity = city;
      }
    });

    return closestCity || { city: 'Unknown', state: '', country: '' };
  }

  // Get cities within specified radius (in miles)
  getCitiesWithinRadius(centerLat, centerLon, radiusMiles = 100) {
    const cities = this.getAllCities();
    const nearbyCities = [];

    cities.forEach(city => {
      const distance = this.calculateDistance(
        centerLat, centerLon,
        city.coordinates[0], city.coordinates[1]
      );

      if (distance <= radiusMiles) {
        nearbyCities.push({
          ...city,
          distance: Math.round(distance)
        });
      }
    });

    // Sort by distance
    nearbyCities.sort((a, b) => a.distance - b.distance);

    this.nearbyCities = nearbyCities;
    return nearbyCities;
  }

  // Search cities by name
  searchCities(query) {
    if (!query || query.length < 2) return [];

    const cities = this.getAllCities();
    const lowerQuery = query.toLowerCase();

    return cities.filter(city =>
      city.city.toLowerCase().includes(lowerQuery) ||
      (city.state && city.state.toLowerCase().includes(lowerQuery)) ||
      (city.province && city.province.toLowerCase().includes(lowerQuery))
    ).slice(0, 10); // Limit to 10 results
  }

  // Format location for display
  formatLocation(location) {
    if (location.state) {
      return `${location.city}, ${location.state}`;
    } else if (location.province) {
      return `${location.city}, ${location.province}`;
    }
    return location.city;
  }

  // Get popular locations for the area
  getPopularLocationsForArea(lat, lon) {
    // Get cities within 200 miles and pick the most populous/important ones
    const nearby = this.getCitiesWithinRadius(lat, lon, 200);

    // Define important cities based on population/significance
    const importantCities = [];

    const popular = nearby.filter(city =>
      importantCities.includes(city.city)
    ).slice(0, 8);

    // If we don't have enough popular cities, add closest ones
    if (popular.length < 8) {
      const additional = nearby
        .filter(city => !popular.find(p => p.city === city.city))
        .slice(0, 8 - popular.length);
      popular.push(...additional);
    }

    return popular;
  }
}

export default new LocationService();