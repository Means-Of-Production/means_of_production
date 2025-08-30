import { Location } from './location';
import { URL } from '../url';

export class VirtualLocation implements Location {
  public readonly url: URL;

  constructor(params: { url: URL }) {
    this.url = params.url;
  }

  contains(other: Location): boolean {
    return other instanceof VirtualLocation && this.url.equals(other.url);
  }
}
