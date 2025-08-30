export class EmailAddress {
  public readonly value: string;

  constructor(value: string) {
    this.value = value;
  }

  equals(other: unknown): boolean {
    return other instanceof EmailAddress && other.value === this.value;
  }

  hash(): number {
    // simple string hash
    let hash = 0;
    for (let i = 0; i < this.value.length; i++) {
      const chr = this.value.charCodeAt(i);
      hash = (hash << 5) - hash + chr;
      hash |= 0; // Convert to 32bit integer
    }
    return hash;
  }
}
