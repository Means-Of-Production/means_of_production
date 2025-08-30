export class Distance {
  public readonly kilometers: number;

  constructor(kilometers: number) {
    if (kilometers < 0) throw new Error('kilometers must be >= 0');
    this.kilometers = kilometers;
  }

  static fromMiles(miles: number): Distance {
    return new Distance(miles / 1.60934);
  }

  get miles(): number {
    return this.kilometers / 1.60934;
  }

  equals(other: unknown): boolean {
    return other instanceof Distance && this.kilometers === other.kilometers;
  }

  lt(other: Distance): boolean {
    return this.kilometers < other.kilometers;
  }

  gt(other: Distance): boolean {
    return this.kilometers > other.kilometers;
  }

  le(other: Distance): boolean {
    return this.kilometers <= other.kilometers;
  }

  ge(other: Distance): boolean {
    return this.kilometers >= other.kilometers;
  }

  add(other: Distance): Distance {
    return new Distance(this.kilometers + other.kilometers);
  }
}
