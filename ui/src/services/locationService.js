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

  // Cities database prioritizing USA and Canada for your user base
  getAllCities() {
    return [
      // Canada - Priority for your user base
      { city: 'Toronto', province: 'ON', country: 'Canada', coordinates: [43.6532, -79.3832] },
      { city: 'Vancouver', province: 'BC', country: 'Canada', coordinates: [49.2827, -123.1207] },
      { city: 'Montreal', province: 'QC', country: 'Canada', coordinates: [45.5017, -73.5673] },
      { city: 'Calgary', province: 'AB', country: 'Canada', coordinates: [51.0447, -114.0719] },
      { city: 'Edmonton', province: 'AB', country: 'Canada', coordinates: [53.5461, -113.4938] },
      { city: 'Ottawa', province: 'ON', country: 'Canada', coordinates: [45.4215, -75.6972] },
      { city: 'Winnipeg', province: 'MB', country: 'Canada', coordinates: [49.8951, -97.1384] },
      { city: 'Quebec City', province: 'QC', country: 'Canada', coordinates: [46.8139, -71.2080] },
      { city: 'Hamilton', province: 'ON', country: 'Canada', coordinates: [43.2557, -79.8711] },
      { city: 'Kitchener', province: 'ON', country: 'Canada', coordinates: [43.4516, -80.4925] },
      { city: 'London', province: 'ON', country: 'Canada', coordinates: [42.9849, -81.2453] },
      { city: 'Halifax', province: 'NS', country: 'Canada', coordinates: [44.6488, -63.5752] },
      { city: 'Victoria', province: 'BC', country: 'Canada', coordinates: [48.4284, -123.3656] },
      { city: 'Windsor', province: 'ON', country: 'Canada', coordinates: [42.3149, -83.0364] },
      { city: 'Saskatoon', province: 'SK', country: 'Canada', coordinates: [52.1332, -106.6700] },
      { city: 'Regina', province: 'SK', country: 'Canada', coordinates: [50.4452, -104.6189] },
      { city: 'Langley', province: 'BC', country: 'Canada', coordinates: [49.1042, -122.6604] },

      // United States - Priority for your user base
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
      { city: 'Miami', state: 'FL', country: 'USA', coordinates: [25.7617, -80.1918] },
      { city: 'Atlanta', state: 'GA', country: 'USA', coordinates: [33.7490, -84.3880] },
      { city: 'Tampa', state: 'FL', country: 'USA', coordinates: [27.9506, -82.4572] },
      { city: 'Orlando', state: 'FL', country: 'USA', coordinates: [28.5383, -81.3792] },
      { city: 'Detroit', state: 'MI', country: 'USA', coordinates: [42.3314, -83.0458] },
      { city: 'Las Vegas', state: 'NV', country: 'USA', coordinates: [36.1699, -115.1398] },
      { city: 'Minneapolis', state: 'MN', country: 'USA', coordinates: [44.9778, -93.2650] },
      { city: 'Cleveland', state: 'OH', country: 'USA', coordinates: [41.4993, -81.6944] },
      { city: 'Pittsburgh', state: 'PA', country: 'USA', coordinates: [40.4406, -79.9959] },
      { city: 'Sacramento', state: 'CA', country: 'USA', coordinates: [38.5816, -121.4944] },

      // International cities (for global users)
      { city: 'London', country: 'United Kingdom', coordinates: [51.5074, -0.1278] },
      { city: 'Paris', country: 'France', coordinates: [48.8566, 2.3522] },
      { city: 'Berlin', country: 'Germany', coordinates: [52.5200, 13.4050] },
      { city: 'Sydney', state: 'NSW', country: 'Australia', coordinates: [-33.8688, 151.2093] },
      { city: 'Melbourne', state: 'VIC', country: 'Australia', coordinates: [-37.8136, 144.9631] },
      { city: 'Tokyo', country: 'Japan', coordinates: [35.6762, 139.6503] },
      { city: 'Mexico City', country: 'Mexico', coordinates: [19.4326, -99.1332] },

      // Additional international cities
      { city: 'Amsterdam', country: 'Netherlands', coordinates: [52.3676, 4.9041] },
      { city: 'Barcelona', country: 'Spain', coordinates: [41.3851, 2.1734] },
      { city: 'Rome', country: 'Italy', coordinates: [41.9028, 12.4964] },
      { city: 'Stockholm', country: 'Sweden', coordinates: [59.3293, 18.0686] },
      { city: 'Zurich', country: 'Switzerland', coordinates: [47.3769, 8.5417] },
      { city: 'Dublin', country: 'Ireland', coordinates: [53.3498, -6.2603] },

      // Eastern Europe & Balkans
      { city: 'Sarajevo', country: 'Bosnia and Herzegovina', coordinates: [43.8563, 18.4131] },
      { city: 'Belgrade', country: 'Serbia', coordinates: [44.7866, 20.4489] },
      { city: 'Zagreb', country: 'Croatia', coordinates: [45.8150, 15.9819] },
      { city: 'Vienna', country: 'Austria', coordinates: [48.2082, 16.3738] },
      { city: 'Prague', country: 'Czech Republic', coordinates: [50.0755, 14.4378] },
      { city: 'Budapest', country: 'Hungary', coordinates: [47.4979, 19.0402] }
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

  // Get popular locations for the area based on user's actual location
  getPopularLocationsForArea(lat, lon) {
    // Get cities within 500 miles to be more inclusive for North American users
    const nearby = this.getCitiesWithinRadius(lat, lon, 500);

    // Prioritize nearby cities from USA and Canada
    const priorityCountries = ['USA', 'Canada'];

    // Separate priority countries from international
    const priorityCities = nearby.filter(city =>
      priorityCountries.includes(city.country)
    );

    const internationalCities = nearby.filter(city =>
      !priorityCountries.includes(city.country)
    );

    // Combine: priority cities first, then international, all sorted by distance
    const sortedCities = [
      ...priorityCities.slice(0, 6),  // Top 6 from USA/Canada
      ...internationalCities.slice(0, 2)  // Top 2 international
    ].sort((a, b) => a.distance - b.distance);

    // If we don't have enough cities in range, add top cities from priority countries
    if (sortedCities.length < 8) {
      const allCities = this.getAllCities();
      const topPriorityCities = allCities
        .filter(city => priorityCountries.includes(city.country))
        .filter(city => !sortedCities.find(s => s.city === city.city))
        .slice(0, 8 - sortedCities.length);

      sortedCities.push(...topPriorityCities);
    }

    return sortedCities.slice(0, 8);
  }
}

export default new LocationService();