import { v4 as uuidv4, validate as uuidValidate } from 'uuid';

export class ID {
  public readonly id: string;

  constructor(id: string) {
    this.id = id;
  }

  static parse(value: string): ID {
    if (!uuidValidate(value)) {
      throw new Error('Invalid UUID');
    }
    return new ID(value);
  }

  static generate(): ID {
    return new ID(uuidv4());
  }

  equals(other: unknown): boolean {
    return other instanceof ID && other.id === this.id;
  }

  toString(): string {
    return this.id;
  }
}
