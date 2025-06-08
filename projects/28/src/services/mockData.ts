import { Service } from '@/types';

export const mockServices: Service[] = [
  {
    id: '1',
    name: 'مستشفى الجامعة الأردنية',
    type: 'مستشفى',
    location: { lat: 31.9539, lng: 35.9106 },
    queueCount: 15,
    estimatedTravelTime: 20,
    address: 'شارع الملكة رانيا العبدالله، عمان',
  },
  {
    id: '2',
    name: 'مركز صحي الهاشمي الشمالي',
    type: 'مركز صحي',
    location: { lat: 31.9771, lng: 35.9428 },
    queueCount: 8,
    estimatedTravelTime: 15,
    address: 'الهاشمي الشمالي، عمان',
  },
  {
    id: '3',
    name: 'ترخيص المركبات - الوحدات',
    type: 'تراخيص المركبات',
    location: { lat: 31.9289, lng: 35.9317 },
    queueCount: 25,
    estimatedTravelTime: 30,
    address: 'الوحدات، عمان',
  },
  {
    id: '4',
    name: 'مستشفى البشير',
    type: 'مستشفى',
    location: { lat: 31.9419, lng: 35.9428 },
    queueCount: 20,
    estimatedTravelTime: 25,
    address: 'شارع الملك عبدالله الأول، عمان',
  },
  {
    id: '5',
    name: 'مركز صحي الجبيهة',
    type: 'مركز صحي',
    location: { lat: 32.0266, lng: 35.8711 },
    queueCount: 5,
    estimatedTravelTime: 10,
    address: 'الجبيهة، عمان',
  },
]; 