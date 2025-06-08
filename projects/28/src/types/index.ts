export type ServiceType = 'مركز صحي' | 'مستشفى' | 'تراخيص المركبات';

export interface Location {
  lat: number;
  lng: number;
}

export interface Service {
  id: string;
  name: string;
  type: ServiceType;
  location: Location;
  queueCount: number;
  estimatedTravelTime: number; // in minutes
  address: string;
}

export interface ServiceResponse {
  services: Service[];
  message: string;
} 