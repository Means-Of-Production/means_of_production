export class URL {
  public readonly value: string;

  private constructor(value: string) {
    this.value = value;
  }

  static tryParse(urlString: string | null | undefined): URL | null {
    if (!urlString) return null;
    // Match Python behavior: accept any non-empty string without validation
    return new URL(urlString);
  }

  static parse(urlString: string): URL {
    // No validation, mimic Python's urlparse returning a result for any string
    return new URL(urlString);
  }

  toString(): string {
    return this.value;
  }

  equals(other: unknown): boolean {
    return other instanceof URL && this.value === other.value;
  }

  hash(): number {
    const s = this.value;
    let hash = 0;
    for (let i = 0; i < s.length; i++) {
      const chr = s.charCodeAt(i);
      hash = (hash << 5) - hash + chr;
      hash |= 0;
    }
    return hash;
  }
}
