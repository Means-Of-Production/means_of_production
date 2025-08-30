export class DueDate {
  public readonly date: Date | null;

  constructor(params: { date: Date | null }) {
    this.date = params.date ? new Date(params.date) : null;
    // No timezone mutation; JS Date is UTC-capable. Caller should pass UTC if needed.
  }

  static of(date: Date | null | undefined): DueDate {
    return new DueDate({ date: date ?? null });
  }

  isAfterNow(): boolean {
    if (!this.date) return false;
    const now = new Date();
    return this.stripTime(this.date).getTime() > this.stripTime(now).getTime();
  }

  lessThan(other: DueDate | Date): boolean {
    if (!this.date) return false;
    const otherDate = other instanceof DueDate ? other.date : other;
    if (!otherDate) return true; // other is empty -> we are considered earlier
    return this.stripTime(this.date).getTime() < this.stripTime(otherDate).getTime();
  }

  greaterThan(other: DueDate): boolean {
    if (!this.date) return true;
    if (!other.date) return true;
    return this.stripTime(this.date).getTime() > this.stripTime(other.date).getTime();
  }

  equals(other: unknown): boolean {
    if (!(other instanceof DueDate)) return false;
    if (!this.date && !other.date) return true;
    if (!!this.date !== !!other.date) return false;
    return this.stripTime(this.date!).getTime() === this.stripTime(other.date!).getTime();
  }

  private stripTime(d: Date): Date {
    // Interpret as UTC day by using UTC components
    return new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate()));
  }
}
