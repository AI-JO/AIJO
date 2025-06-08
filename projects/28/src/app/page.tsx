'use client';

import { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { Service, ServiceType, Location } from '../types';
import { getServices, calculateBestLocation } from '../services/api';
import 'leaflet/dist/leaflet.css';

export default function Home() {
  const [userLocation, setUserLocation] = useState<Location | null>(null);
  const [selectedType, setSelectedType] = useState<ServiceType | null>(null);
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Get user's location
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setUserLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          });
        },
        (error) => {
          console.error('Error getting location:', error);
          // Default to Amman coordinates
          setUserLocation({ lat: 31.9539, lng: 35.9106 });
        }
      );
    }
  }, []);

  const handleServiceTypeSelect = async (type: ServiceType) => {
    if (!userLocation) return;
    
    setLoading(true);
    setSelectedType(type);
    try {
      const services = await getServices(userLocation, type);
      const sortedServices = calculateBestLocation(services, userLocation);
      setServices(sortedServices);
    } catch (error) {
      console.error('Error fetching services:', error);
    }
    setLoading(false);
  };

  const serviceTypes: ServiceType[] = ['مركز صحي', 'مستشفى', 'تراخيص المركبات'];

  return (
    <main className="min-h-screen p-4 bg-gray-100">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-6 text-center">خدمات المواقع في الأردن</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          {serviceTypes.map((type) => (
            <button
              key={type}
              onClick={() => handleServiceTypeSelect(type)}
              className={`p-4 rounded-lg text-lg font-semibold ${
                selectedType === type
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-800 hover:bg-blue-50'
              }`}
            >
              {type}
            </button>
          ))}
        </div>

        {userLocation && (
          <div className="h-[500px] rounded-lg overflow-hidden shadow-lg mb-6">
            <MapContainer
              center={[userLocation.lat, userLocation.lng]}
              zoom={13}
              style={{ height: '100%', width: '100%' }}
            >
              <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              />
              {services.map((service) => (
                <Marker
                  key={service.id}
                  position={[service.location.lat, service.location.lng]}
                >
                  <Popup>
                    <div className="text-right">
                      <h3 className="font-bold">{service.name}</h3>
                      <p>العنوان: {service.address}</p>
                      <p>عدد المنتظرين: {service.queueCount}</p>
                      <p>وقت الوصول المتوقع: {service.estimatedTravelTime} دقيقة</p>
                    </div>
                  </Popup>
                </Marker>
              ))}
            </MapContainer>
          </div>
        )}

        {loading ? (
          <div className="text-center">جاري التحميل...</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {services.map((service) => (
              <div
                key={service.id}
                className="bg-white rounded-lg p-4 shadow-md"
              >
                <h3 className="text-xl font-bold mb-2">{service.name}</h3>
                <p>العنوان: {service.address}</p>
                <p>عدد المنتظرين: {service.queueCount}</p>
                <p>وقت الوصول المتوقع: {service.estimatedTravelTime} دقيقة</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </main>
  );
} 