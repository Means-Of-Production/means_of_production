import { Location } from './location';
import { PhysicalLocation } from './physical_location';
import { Distance } from './distance';

export class PhysicalArea implements Location {
  public readonly center_point: PhysicalLocation;
  public readonly radius: Distance;

  constructor(params: { center_point: PhysicalLocation; radius: Distance }) {
    this.center_point = params.center_point;
    this.radius = params.radius;
  }

  contains(other: Location): boolean {
    if (other instanceof PhysicalLocation) {
      const distance = this.center_point.distance(other);
      return distance.lt(this.radius);
    } else if (other instanceof PhysicalArea) {
      const offset = this.center_point.distance(other.center_point);
      return offset.add(other.radius).lt(this.radius);
    }
    throw new Error(`Cannot compute contain for location type ${typeof other}`);
  }
}
