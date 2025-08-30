import { VirtualLocation } from './location/virtual_location';
import { URL } from './url';

export class MOPServer extends VirtualLocation {
  public readonly version: string;

  constructor(params: { url: URL; version: string }) {
    super({ url: params.url });
    this.version = params.version;
  }

  static localhost(): MOPServer {
    return new MOPServer({ url: URL.parse('https://localhost'), version: '0.0.0' });
  }
}
