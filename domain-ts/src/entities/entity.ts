import { ID } from '../value_items';

export abstract class Entity {
  // In TS we expose an abstract getter similar to Python's abstract property
  abstract get entity_id(): ID;

  equals(other: unknown): boolean {
    return other instanceof Entity && this.entity_id.equals(other.entity_id);
  }
}
