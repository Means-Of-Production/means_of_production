import { ID } from './id';
import { Money } from './money';

export class AuctionBid {
  public readonly amount_bid: Money;
  public readonly amount_paid: Money;
  public readonly made_by_id: ID;
  public readonly made_for_id: ID;

  constructor(params: { amount_bid: Money; amount_paid: Money; made_by_id: ID; made_for_id: ID }) {
    this.amount_bid = params.amount_bid;
    this.amount_paid = params.amount_paid;
    this.made_by_id = params.made_by_id;
    this.made_for_id = params.made_for_id;
  }

  equals(other: unknown): boolean {
    if (!(other instanceof AuctionBid)) return false;
    return (
      this.amount_bid.equals(other.amount_bid) &&
      this.amount_paid.equals(other.amount_paid) &&
      this.made_by_id.equals(other.made_by_id) &&
      this.made_for_id.equals(other.made_for_id)
    );
  }

  hash(): number {
    const s = [
      this.amount_bid.toJSON().amount,
      this.amount_paid.toJSON().amount,
      this.made_by_id.toString(),
      this.made_for_id.toString(),
    ].join('|');
    let hash = 0;
    for (let i = 0; i < s.length; i++) {
      const chr = s.charCodeAt(i);
      hash = (hash << 5) - hash + chr;
      hash |= 0;
    }
    return hash;
  }
}
