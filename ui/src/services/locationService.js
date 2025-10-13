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

  // Major North American cities with coordinates
  getAllCities() {
    return [
      // Pacific Northwest - Major cities only
      { city: 'Seattle', state: 'WA', country: 'USA', coordinates: [47.6062, -122.3321] },
      { city: 'Portland', state: 'OR', country: 'USA', coordinates: [45.5152, -122.6784] },
      { city: 'Vancouver', province: 'BC', country: 'Canada', coordinates: [49.2827, -123.1207] },
      { city: 'Tacoma', state: 'WA', country: 'USA', coordinates: [47.2529, -122.4443] },
      { city: 'Spokane', state: 'WA', country: 'USA', coordinates: [47.6588, -117.4260] },
      { city: 'Eugene', state: 'OR', country: 'USA', coordinates: [44.0521, -123.0868] },
      { city: 'Bellevue', state: 'WA', country: 'USA', coordinates: [47.6101, -122.2015] },
      { city: 'Everett', state: 'WA', country: 'USA', coordinates: [47.9790, -122.2021] },

      // Major BC cities only
      { city: 'Burnaby', province: 'BC', country: 'Canada', coordinates: [49.2488, -122.9805] },
      { city: 'Surrey', province: 'BC', country: 'Canada', coordinates: [49.1913, -122.8490] },
      { city: 'Richmond', province: 'BC', country: 'Canada', coordinates: [49.1666, -123.1336] },
      { city: 'Victoria', province: 'BC', country: 'Canada', coordinates: [48.4284, -123.3656] },
      { city: 'Kelowna', province: 'BC', country: 'Canada', coordinates: [49.8880, -119.4960] },

      // Major US West Coast cities
      { city: 'San Francisco', state: 'CA', country: 'USA', coordinates: [37.7749, -122.4194] },
      { city: 'Los Angeles', state: 'CA', country: 'USA', coordinates: [34.0522, -118.2437] },
      { city: 'San Diego', state: 'CA', country: 'USA', coordinates: [32.7157, -117.1611] },
      { city: 'Sacramento', state: 'CA', country: 'USA', coordinates: [38.5816, -121.4944] },
      { city: 'Oakland', state: 'CA', country: 'USA', coordinates: [37.8044, -122.2712] },
      { city: 'San Jose', state: 'CA', country: 'USA', coordinates: [37.3382, -121.8863] },

      // Major US cities
      { city: 'New York', state: 'NY', country: 'USA', coordinates: [40.7128, -74.0060] },
      { city: 'Chicago', state: 'IL', country: 'USA', coordinates: [41.8781, -87.6298] },
      { city: 'Houston', state: 'TX', country: 'USA', coordinates: [29.7604, -95.3698] },
      { city: 'Phoenix', state: 'AZ', country: 'USA', coordinates: [33.4484, -112.0740] },
      { city: 'Philadelphia', state: 'PA', country: 'USA', coordinates: [39.9526, -75.1652] },
      { city: 'Denver', state: 'CO', country: 'USA', coordinates: [39.7392, -104.9903] },

      // Major Canadian cities
      { city: 'Toronto', province: 'ON', country: 'Canada', coordinates: [43.6532, -79.3832] },
      { city: 'Montreal', province: 'QC', country: 'Canada', coordinates: [45.5017, -73.5673] },
      { city: 'Calgary', province: 'AB', country: 'Canada', coordinates: [51.0447, -114.0719] },
      { city: 'Ottawa', province: 'ON', country: 'Canada', coordinates: [45.4215, -75.6972] },
      { city: 'Edmonton', province: 'AB', country: 'Canada', coordinates: [53.5461, -113.4938] },
      { city: 'Winnipeg', province: 'MB', country: 'Canada', coordinates: [49.8951, -97.1384] },
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
    const importantCities = ['Seattle', 'Vancouver', 'Portland', 'Spokane', 'Tacoma', 'Bellevue', 'Toronto', 'Montreal', 'Calgary', 'San Francisco', 'Los Angeles', 'San Diego'];

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