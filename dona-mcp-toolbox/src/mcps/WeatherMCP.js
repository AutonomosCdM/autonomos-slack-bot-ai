const axios = require('axios');
const logger = require('../utils/logger').createModuleLogger('WeatherMCP');
const mcpConfig = require('../config/mcpConfig');

/**
 * Weather MCP - Real-time weather data and forecasting
 * Provides comprehensive weather information using OpenWeatherMap API
 */
class WeatherMCP {
    constructor() {
        this.config = mcpConfig.getMCPConfig('weather');
        this.cache = new Map();
        this.cacheTTL = 600000; // 10 minutes cache
    }

    /**
     * Get current weather for a location
     * @param {string} location - City name, coordinates, or zip code
     * @param {string} units - Temperature units ('metric', 'imperial', 'standard')
     * @returns {Promise<Object>} Current weather data
     */
    async getCurrentWeather(location, units = 'metric') {
        const startTime = Date.now();
        
        try {
            this._validateApiKey();
            
            const cacheKey = `current_${location}_${units}`;
            const cached = this._getFromCache(cacheKey);
            if (cached) {
                logger.debug(`Returning cached weather for ${location}`);
                return cached;
            }

            logger.info(`Fetching current weather for: ${location}`, { units });

            const params = {
                q: location,
                appid: this.config.apiKey,
                units: units
            };

            const response = await axios.get(`${this.config.baseUrl}/weather`, {
                params,
                timeout: this.config.timeout
            });

            const weather = this._formatCurrentWeather(response.data);
            weather.requestTime = Date.now() - startTime;

            // Cache the result
            this._setCache(cacheKey, weather);

            logger.info(`Retrieved current weather for ${location}`, {
                temperature: weather.temperature,
                condition: weather.condition,
                duration: weather.requestTime
            });

            return weather;

        } catch (error) {
            logger.error(`Error fetching current weather: ${error.message}`, { location });
            throw new Error(`Weather fetch failed: ${error.message}`);
        }
    }

    /**
     * Get weather forecast for a location
     * @param {string} location - City name, coordinates, or zip code
     * @param {number} days - Number of days (1-5 for free tier)
     * @param {string} units - Temperature units
     * @returns {Promise<Object>} Weather forecast data
     */
    async getForecast(location, days = 5, units = 'metric') {
        const startTime = Date.now();
        
        try {
            this._validateApiKey();
            
            const cacheKey = `forecast_${location}_${days}_${units}`;
            const cached = this._getFromCache(cacheKey);
            if (cached) {
                logger.debug(`Returning cached forecast for ${location}`);
                return cached;
            }

            logger.info(`Fetching ${days}-day forecast for: ${location}`, { units });

            const params = {
                q: location,
                appid: this.config.apiKey,
                units: units,
                cnt: days * 8 // 8 forecasts per day (3-hour intervals)
            };

            const response = await axios.get(`${this.config.baseUrl}/forecast`, {
                params,
                timeout: this.config.timeout
            });

            const forecast = this._formatForecast(response.data);
            forecast.requestTime = Date.now() - startTime;

            // Cache the result
            this._setCache(cacheKey, forecast);

            logger.info(`Retrieved ${days}-day forecast for ${location}`, {
                periods: forecast.periods.length,
                duration: forecast.requestTime
            });

            return forecast;

        } catch (error) {
            logger.error(`Error fetching forecast: ${error.message}`, { location, days });
            throw new Error(`Forecast fetch failed: ${error.message}`);
        }
    }

    /**
     * Get weather by geographic coordinates
     * @param {number} lat - Latitude
     * @param {number} lon - Longitude
     * @param {string} units - Temperature units
     * @returns {Promise<Object>} Weather data
     */
    async getWeatherByCoordinates(lat, lon, units = 'metric') {
        const startTime = Date.now();
        
        try {
            this._validateApiKey();
            
            const cacheKey = `coords_${lat}_${lon}_${units}`;
            const cached = this._getFromCache(cacheKey);
            if (cached) {
                logger.debug(`Returning cached weather for coordinates ${lat}, ${lon}`);
                return cached;
            }

            logger.info(`Fetching weather for coordinates: ${lat}, ${lon}`, { units });

            const params = {
                lat: lat,
                lon: lon,
                appid: this.config.apiKey,
                units: units
            };

            const response = await axios.get(`${this.config.baseUrl}/weather`, {
                params,
                timeout: this.config.timeout
            });

            const weather = this._formatCurrentWeather(response.data);
            weather.requestTime = Date.now() - startTime;

            // Cache the result
            this._setCache(cacheKey, weather);

            logger.info(`Retrieved weather for coordinates ${lat}, ${lon}`, {
                location: weather.location,
                temperature: weather.temperature,
                duration: weather.requestTime
            });

            return weather;

        } catch (error) {
            logger.error(`Error fetching weather by coordinates: ${error.message}`, { lat, lon });
            throw new Error(`Weather fetch by coordinates failed: ${error.message}`);
        }
    }

    /**
     * Get air quality data for a location
     * @param {number} lat - Latitude
     * @param {number} lon - Longitude
     * @returns {Promise<Object>} Air quality data
     */
    async getAirQuality(lat, lon) {
        const startTime = Date.now();
        
        try {
            this._validateApiKey();
            
            const cacheKey = `air_quality_${lat}_${lon}`;
            const cached = this._getFromCache(cacheKey);
            if (cached) {
                logger.debug(`Returning cached air quality for ${lat}, ${lon}`);
                return cached;
            }

            logger.info(`Fetching air quality for coordinates: ${lat}, ${lon}`);

            const params = {
                lat: lat,
                lon: lon,
                appid: this.config.apiKey
            };

            const response = await axios.get(`${this.config.baseUrl.replace('/data/2.5', '')}/data/2.5/air_pollution`, {
                params,
                timeout: this.config.timeout
            });

            const airQuality = this._formatAirQuality(response.data);
            airQuality.requestTime = Date.now() - startTime;

            // Cache the result
            this._setCache(cacheKey, airQuality);

            logger.info(`Retrieved air quality for ${lat}, ${lon}`, {
                aqi: airQuality.aqi,
                duration: airQuality.requestTime
            });

            return airQuality;

        } catch (error) {
            logger.error(`Error fetching air quality: ${error.message}`, { lat, lon });
            throw new Error(`Air quality fetch failed: ${error.message}`);
        }
    }

    /**
     * Search for locations by name
     * @param {string} query - Location search query
     * @param {number} limit - Maximum number of results
     * @returns {Promise<Array>} Array of location objects
     */
    async searchLocations(query, limit = 5) {
        try {
            this._validateApiKey();
            
            logger.info(`Searching locations: ${query}`, { limit });

            const params = {
                q: query,
                limit: Math.min(limit, 5),
                appid: this.config.apiKey
            };

            const response = await axios.get(`${this.config.baseUrl.replace('/data/2.5', '')}/geo/1.0/direct`, {
                params,
                timeout: this.config.timeout
            });

            const locations = response.data.map(location => ({
                name: location.name,
                country: location.country,
                state: location.state,
                lat: location.lat,
                lon: location.lon
            }));

            logger.info(`Found ${locations.length} locations for query: ${query}`);
            return locations;

        } catch (error) {
            logger.error(`Error searching locations: ${error.message}`, { query });
            throw new Error(`Location search failed: ${error.message}`);
        }
    }

    /**
     * Get weather alerts for a location
     * @param {number} lat - Latitude
     * @param {number} lon - Longitude
     * @returns {Promise<Object>} Weather alerts data
     */
    async getWeatherAlerts(lat, lon) {
        try {
            this._validateApiKey();
            
            logger.info(`Fetching weather alerts for: ${lat}, ${lon}`);

            const params = {
                lat: lat,
                lon: lon,
                appid: this.config.apiKey
            };

            const response = await axios.get(`${this.config.baseUrl}/onecall`, {
                params,
                timeout: this.config.timeout
            });

            const alerts = response.data.alerts || [];
            const formattedAlerts = alerts.map(alert => ({
                event: alert.event,
                start: new Date(alert.start * 1000).toISOString(),
                end: new Date(alert.end * 1000).toISOString(),
                description: alert.description,
                tags: alert.tags
            }));

            logger.info(`Retrieved ${formattedAlerts.length} weather alerts`);
            return {
                location: { lat, lon },
                alerts: formattedAlerts,
                alertCount: formattedAlerts.length
            };

        } catch (error) {
            logger.error(`Error fetching weather alerts: ${error.message}`, { lat, lon });
            throw new Error(`Weather alerts fetch failed: ${error.message}`);
        }
    }

    /**
     * Format current weather data
     * @private
     */
    _formatCurrentWeather(data) {
        return {
            location: {
                name: data.name,
                country: data.sys.country,
                coordinates: {
                    lat: data.coord.lat,
                    lon: data.coord.lon
                }
            },
            temperature: {
                current: Math.round(data.main.temp),
                feelsLike: Math.round(data.main.feels_like),
                min: Math.round(data.main.temp_min),
                max: Math.round(data.main.temp_max)
            },
            condition: {
                main: data.weather[0].main,
                description: data.weather[0].description,
                icon: data.weather[0].icon
            },
            humidity: data.main.humidity,
            pressure: data.main.pressure,
            visibility: data.visibility / 1000, // Convert to km
            wind: {
                speed: data.wind.speed,
                direction: data.wind.deg,
                gust: data.wind.gust
            },
            clouds: data.clouds.all,
            sunrise: new Date(data.sys.sunrise * 1000).toISOString(),
            sunset: new Date(data.sys.sunset * 1000).toISOString(),
            timestamp: new Date(data.dt * 1000).toISOString()
        };
    }

    /**
     * Format forecast data
     * @private
     */
    _formatForecast(data) {
        return {
            location: {
                name: data.city.name,
                country: data.city.country,
                coordinates: {
                    lat: data.city.coord.lat,
                    lon: data.city.coord.lon
                }
            },
            periods: data.list.map(period => ({
                datetime: new Date(period.dt * 1000).toISOString(),
                temperature: {
                    current: Math.round(period.main.temp),
                    feelsLike: Math.round(period.main.feels_like),
                    min: Math.round(period.main.temp_min),
                    max: Math.round(period.main.temp_max)
                },
                condition: {
                    main: period.weather[0].main,
                    description: period.weather[0].description,
                    icon: period.weather[0].icon
                },
                humidity: period.main.humidity,
                pressure: period.main.pressure,
                wind: {
                    speed: period.wind.speed,
                    direction: period.wind.deg
                },
                clouds: period.clouds.all,
                precipitation: period.rain ? period.rain['3h'] : 0
            }))
        };
    }

    /**
     * Format air quality data
     * @private
     */
    _formatAirQuality(data) {
        const aqiLevels = ['Good', 'Fair', 'Moderate', 'Poor', 'Very Poor'];
        const components = data.list[0].components;
        
        return {
            coordinates: {
                lat: data.coord.lat,
                lon: data.coord.lon
            },
            aqi: data.list[0].main.aqi,
            aqiLevel: aqiLevels[data.list[0].main.aqi - 1] || 'Unknown',
            components: {
                co: components.co,        // Carbon monoxide
                no: components.no,        // Nitric oxide
                no2: components.no2,      // Nitrogen dioxide
                o3: components.o3,        // Ozone
                so2: components.so2,      // Sulphur dioxide
                pm2_5: components.pm2_5,  // Fine particles matter
                pm10: components.pm10,    // Coarse particulate matter
                nh3: components.nh3       // Ammonia
            },
            timestamp: new Date(data.list[0].dt * 1000).toISOString()
        };
    }

    /**
     * Validate API key
     * @private
     */
    _validateApiKey() {
        if (!this.config.apiKey) {
            throw new Error('Weather API key not configured. Set WEATHER_API_KEY environment variable.');
        }
    }

    /**
     * Get item from cache if valid
     * @private
     */
    _getFromCache(key) {
        const item = this.cache.get(key);
        if (item && Date.now() - item.timestamp < this.cacheTTL) {
            return item.data;
        }
        if (item) {
            this.cache.delete(key);
        }
        return null;
    }

    /**
     * Set item in cache
     * @private
     */
    _setCache(key, data) {
        this.cache.set(key, {
            data,
            timestamp: Date.now()
        });
    }

    /**
     * Clear cache
     */
    clearCache() {
        this.cache.clear();
        logger.info('Weather cache cleared');
    }

    /**
     * Get cache statistics
     * @returns {Object} Cache stats
     */
    getCacheStats() {
        return {
            size: this.cache.size,
            keys: Array.from(this.cache.keys()),
            ttl: this.cacheTTL
        };
    }

    /**
     * Get supported units
     * @returns {Object} Units information
     */
    getSupportedUnits() {
        return {
            metric: {
                temperature: 'Celsius',
                windSpeed: 'm/s',
                pressure: 'hPa'
            },
            imperial: {
                temperature: 'Fahrenheit', 
                windSpeed: 'mph',
                pressure: 'hPa'
            },
            standard: {
                temperature: 'Kelvin',
                windSpeed: 'm/s',
                pressure: 'hPa'
            }
        };
    }
}

module.exports = WeatherMCP;