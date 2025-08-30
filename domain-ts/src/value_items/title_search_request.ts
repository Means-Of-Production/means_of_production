export class TitleSearchRequest {
  public readonly search_text?: string | null;

  constructor(params?: { search_text?: string | null }) {
    this.search_text = params?.search_text ?? null;
  }

  equals(other: unknown): boolean {
    if (!(other instanceof TitleSearchRequest)) return false;
    const a = this.search_text ?? null;
    const b = other.search_text ?? null;
    return a === b;
  }

  hash(): number {
    const s = (this.search_text ?? '').toString();
    let hash = 0;
    for (let i = 0; i < s.length; i++) {
      const chr = s.charCodeAt(i);
      hash = (hash << 5) - hash + chr;
      hash |= 0;
    }
    return hash;
  }
}
