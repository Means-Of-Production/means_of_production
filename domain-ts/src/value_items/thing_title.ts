export class ThingTitle {
  public readonly name: string;
  public readonly upc?: string;
  public readonly isbn?: string;
  public readonly description?: string;

  constructor(params: {
    name: string;
    upc?: string | null;
    isbn?: string | null;
    description?: string | null;
  }) {
    this.name = params.name;
    this.upc = params.upc ?? undefined;
    this.isbn = params.isbn ?? undefined;
    this.description = params.description ?? undefined;
  }

  equals(other: unknown): boolean {
    if (!(other instanceof ThingTitle)) return false;
    if (this.name !== other.name) return false;
    if (this.upc && other.upc && this.upc !== other.upc) return false;
    if (this.isbn && other.isbn && this.isbn !== other.isbn) return false;
    return true;
  }

  hash(): number {
    const s = this.name.replace(/_/g, '-').toLowerCase();
    let hash = 0;
    for (let i = 0; i < s.length; i++) {
      const chr = s.charCodeAt(i);
      hash = (hash << 5) - hash + chr;
      hash |= 0;
    }
    return hash;
  }
}
