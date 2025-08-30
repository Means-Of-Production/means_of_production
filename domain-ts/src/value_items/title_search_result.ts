import { ID } from './id';
import { ThingTitle } from './thing_title';
import { EntityNotAssignedIdError } from './exceptions';

export class LibrarySearchResult<TLibrary, TThing> {
  public readonly library: TLibrary;
  private _things: TThing[] = [];

  constructor(params: { library: TLibrary }) {
    this.library = params.library;
  }

  addThing(item: TThing): this {
    this._things.push(item);
    return this;
  }

  get things(): ReadonlyArray<TThing> {
    return this._things;
  }

  get num_copies(): number {
    return this._things.length;
  }
}

export class TitleSearchResult<TLibrary extends { entity_id?: ID; name?: string }, TThing> {
  public readonly title: ThingTitle;
  private _libraryResults: Map<string, LibrarySearchResult<TLibrary, TThing>> = new Map();

  constructor(params: { title: ThingTitle }) {
    this.title = params.title;
  }

  get num_copies(): number {
    let sum = 0;
    for (const lr of this._libraryResults.values()) sum += lr.num_copies;
    return sum;
  }

  get library_results(): Iterable<LibrarySearchResult<TLibrary, TThing>> {
    return this._libraryResults.values();
  }

  getForLibrary(library: TLibrary): LibrarySearchResult<TLibrary, TThing> {
    const id = library.entity_id;
    if (!id) {
      throw new EntityNotAssignedIdError(`Library ${library.name ?? ''} has not yet been saved!`);
    }
    const key = id.toString();
    let result = this._libraryResults.get(key);
    if (!result) {
      result = new LibrarySearchResult<TLibrary, TThing>({ library });
      this._libraryResults.set(key, result);
    }
    return result;
  }
}
