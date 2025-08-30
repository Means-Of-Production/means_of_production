export class PersonName {
  public readonly salutation?: string;
  public readonly first_name: string;
  public readonly middle_name?: string;
  public readonly last_name: string;
  public readonly suffix?: string;

  constructor(params: {
    salutation?: string | null;
    first_name: string;
    middle_name?: string | null;
    last_name: string;
    suffix?: string | null;
  }) {
    this.salutation = params.salutation ?? undefined;
    this.first_name = params.first_name;
    this.middle_name = params.middle_name ?? undefined;
    this.last_name = params.last_name;
    this.suffix = params.suffix ?? undefined;
  }
}
