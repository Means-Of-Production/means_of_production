import { Location } from './location';
import { Distance } from './distance';

export class PhysicalLocation implements Location {
  public readonly latitude?: number | null;
  public readonly longitude?: number | null;
  public readonly street_address: string;
  public readonly city: string;
  public readonly state: string;
  public readonly zip_code: string;
  public readonly country: string;

  constructor(params: {
    latitude?: number | null;
    longitude?: number | null;
    street_address: string;
    city: string;
    state: string;
    zip_code: string;
    country: string;
  }) {
    this.latitude = params.latitude ?? null;
    this.longitude = params.longitude ?? null;
    this.street_address = params.street_address;
    this.city = params.city;
    this.state = params.state;
    this.zip_code = params.zip_code;
    this.country = params.country;
  }

  equals(other: unknown): boolean {
    if (!(other instanceof PhysicalLocation)) return false;
    if (this.latitude && other.latitude && this.latitude !== other.latitude) return false;
    if (this.longitude && other.longitude && this.longitude !== other.longitude) return false;
    return (
      this.street_address === other.street_address &&
      this.city === other.city &&
      this.state === other.state &&
      this.zip_code === other.zip_code
    );
  }

  contains(other: Location): boolean {
    return other instanceof PhysicalLocation && this.equals(other);
  }

  distance(other: PhysicalLocation): Distance {
    if (this.latitude == null || this.longitude == null) {
      throw new Error('This location does not have latitude and longitude set');
    }
    if (other.latitude == null || other.longitude == null) {
      throw new Error('The other location does not have latitude and longitude set');
    }

    // Haversine formula
    const earthRadius = 6371.0; // km
    const toRad = (d: number) => (d * Math.PI) / 180;

    const lat1 = toRad(this.latitude);
    const lon1 = toRad(this.longitude);
    const lat2 = toRad(other.latitude);
    const lon2 = toRad(other.longitude);

    const dlon = lon2 - lon1;
    const dlat = lat2 - lat1;
    const a = Math.sin(dlat / 2) ** 2 + Math.cos(lat1) * Math.cos(lat2) * Math.sin(dlon / 2) ** 2;
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    const distanceKm = earthRadius * c;

    return new Distance(distanceKm);
  }
}
