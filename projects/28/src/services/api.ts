import { Service, ServiceType, Location } from '../types';
import { mockServices } from './mockData';

export const getServices = async (
  userLocation: Location,
  serviceType: ServiceType
): Promise<Service[]> => {
  // In a real application, this would be an API call
  // For now, we'll filter our mock data and calculate distances
  return mockServices.filter(service => service.type === serviceType);
};

export const calculateBestLocation = (
  services: Service[],
  userLocation: Location
): Service[] => {
  // Calculate a score for each service based on queue count and travel time
  const servicesWithScore = services.map(service => ({
    ...service,
    score: service.queueCount * 2 + service.estimatedTravelTime
  }));

  // Sort by score (lower is better)
  return servicesWithScore.sort((a, b) => a.score - b.score);
}; 