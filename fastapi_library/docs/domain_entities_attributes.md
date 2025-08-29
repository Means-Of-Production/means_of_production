## DOMAIN ENTITIES & ATTRIBUTES

This section defines the **core domain entities**, their **key attributes**, and **relationships** for Phase One of the Distributed Library System.

---

# Core Entities

Based on the project, here are the **main entities**:

| Entity         | Description                                                   |
|----------------|---------------------------------------------------------------|
| **Library**    | Central organizer that manages borrowing, items, and members. |
| **Lender**     | A person/entity that owns an item and lists it for borrowing. |
| **Borrower**   | A person/entity that wants to borrow items.                   |
| **Thing**      | The actual item to be borrowed.                               |
| **Loan**       | The temporary transfer of a Thing to a Borrower.              |
| **LibraryFee** | Fee imposed for overdue or damaged items.                     |

---

## 1. Library (Base Class)

Represents a collection of items available for lending.

| Attribute                  | Type                 | Description                                         |
|----------------------------|---------------------|-----------------------------------------------------|
| `library_id`               | `ID`                 | Unique identifier for the library                   |
| `name`                     | `LibraryName`        | Name of the library                                 |
| `description`              | `LibraryDescription` | Description of the library                          |
| `location`                 | `Location`           | Physical or virtual location                        |
| `default_loan_time`        | `timedelta`          | Duration a borrower can hold an item by default     |
| `loans`                    | `List[Loan]`         | Collection of all loans associated with the library |
| `fee_schedule`             | `FeeSchedule`        | Rules for calculating fees                          |
| `max_fines_before_suspension` | `Money`          | Limit of outstanding fines before suspension        |

---

## 2. SimpleLibrary (Library subclass)

An **in-house library** that owns all its items.

| Attribute  | Type           | Description                       |
|------------|----------------|-----------------------------------|
| `_items`   | `List[Thing]`  | All items managed by this library |

---

## 3. DistributedLibrary (Library subclass)

A **distributed library** composed of multiple lenders and items.

| Attribute   | Type           | Description                                                     |
|-------------|----------------|-----------------------------------------------------------------|
| `area`      | `PhysicalArea` | Geographical area the distributed library covers                |
| `_lenders`  | `List[Lender]` | People or entities who own items loaned out through the library |

---

## 4. Borrower

Someone who borrows things from the library.

| Attribute               | Type                            | Description                               |
|-------------------------|---------------------------------|-------------------------------------------|
| `borrower_id`           | `ID`                            | Unique ID of the borrower                  |
| `library_id`            | `ID`                            | Library this borrower belongs to           |
| `verification_flags`    | `List[BorrowerVerificationFlags]` | Indicates verification/compliance actions |
| `fees`                  | `List[LibraryFee]` (abstract)    | Outstanding or paid fees                   |

Methods:
- `apply_fee(fee: LibraryFee)` – Assigns a fee to the borrower.

---

## 5. Lender

A person or entity that owns items in a distributed library.

| Attribute                   | Type                    | Description                       |
|-----------------------------|-------------------------|-----------------------------------|
| `lender_id`                 | `ID`                    | Unique ID of the lender           |
| `items`                     | `List[Thing]`           | Items they’re lending out         |
| `preferred_return_location` | `str` or `PhysicalArea` | Where items should be returned to |

---

## 6. Thing

Represents a **physical item** (book, tool, device, etc.) in the library.

| Attribute           | Type           | Description                           |
|---------------------|----------------|---------------------------------------|
| `thing_id`          | `ID`           | Unique ID for the item                |
| `title`             | `ThingTitle`   | Name/title of the item                |
| `description`       | `str`          | Optional description                  |
| `owner_id`          | `ID`           | Lender or Library that owns the item  |
| `storage_location`  | `Location`     | Physical storage location             |
| `purchase_cost`     | `Money`        | Purchase cost (optional)              |
| `image_urls`        | `List[str]`    | Optional media for the item           |
| `status`            | `ThingStatus`  | `READY`, `BORROWED`, `DAMAGED`, etc.  |

> **Note:** `Thing.status` follows strict transitions (READY → BORROWED → RETURNED/RESERVED → DAMAGED).

---

## 7. Loan

Represents an **ongoing or completed borrowing event**.

| Attribute         | Type                    | Description                                                  |
|-------------------|------------------------|--------------------------------------------------------------|
| `loan_id`         | `ID`                    | Unique loan ID                                               |
| `item`            | `Thing`                 | The item being borrowed                                      |
| `borrower_id`     | `ID`                    | Borrower taking the item                                     |
| `due_date`        | `DueDate`               | When the item should be returned                             |
| `return_location` | `str` or `PhysicalArea` | Location where the item must be returned                     |
| `time_returned`   | `datetime \| None`      | When the item was actually returned                          |
| `status`          | `LoanStatus`            | Lifecycle: `BORROWED`, `RETURN_STARTED`, `RETURNED`, etc.    |

Computed:
- `active`: Boolean → True if status is `BORROWED`
- `lender_id`: Derived from `item.owner_id`

---

## 8. LibraryFee

Fee imposed on a borrower for overdue, lost, or damaged items.

| Attribute        | Type        | Description                                              |
|------------------|------------|----------------------------------------------------------|
| `library_fee_id` | `ID`        | Unique fee ID                                            |
| `library_id`     | `ID`        | Library charging the fee                                 |
| `amount`         | `Money`     | Fee amount                                               |
| `status`         | `FeeStatus` | Enum: `OUTSTANDING`, `PAID`, etc.                        |
| `charged_for_id` | `ID`        | References a `Loan` or `Thing` that triggered the fee    |

---

## 9. Value Objects / Enums

These wrap primitive types and ensure type safety and state validation:

| Value Object                                      | Description                                          |
|---------------------------------------------------|------------------------------------------------------|
| `ID`                                              | Unique identifier, often UUID                        |
| `ThingStatus`                                     | Enum: `READY`, `BORROWED`, `RESERVED`, `DAMAGED`     |
| `LoanStatus`                                      | Enum: `BORROWED`, `RETURN_STARTED`, `RETURNED`, etc. |
| `FeeStatus`                                       | Enum: `OUTSTANDING`, `PAID`                          |
| `DueDate`                                         | Date wrapper with comparison helpers                 |
| `Money`                                           | Represents an amount with currency                   |
| `PhysicalArea`                                    | Represents physical or geospatial location           |
| `ThingTitle`, `LibraryName`, `BorrowerName`, etc. | Strongly-typed strings with validations              |

---

## Relationship Summary

| From               | To                    | Type                              | Cardinality           | Notes                                       |
| ------------------ | --------------------- | --------------------------------- | --------------------- | ------------------------------------------- |
| Library            | Borrower              | Aggregation                       | 1 ⇒ \*                | Library has many borrowers                  |
| Library            | Loan                  | Aggregation                       | 1 ⇒ \*                | Library tracks many loans                   |
| Library            | Thing                 | (via SimpleLibrary or via Lender) | 1 ⇒ \*                | Items managed/owned in context              |
| SimpleLibrary      | Thing                 | Ownership                         | 1 ⇒ \*                | Directly owns items                         |
| DistributedLibrary | Lender                | Composition                       | 1 ⇒ \*                | Has many lenders                            |
| Lender             | Thing                 | Ownership                         | 1 ⇒ \*                | Lender owns items                           |
| Borrower           | Loan                  | Association                       | 1 ⇒ \*                | Borrower can have many loans                |
| Thing              | Loan                  | Association                       | 1 ⇒ 1 per active loan | A loan is for a specific thing              |
| Loan               | Thing                 | Dependency                        | \*                    | Loan references the thing                   |
| Loan               | Borrower              | Dependency                        | \*                    | Loan references borrower                    |
| Loan               | LibraryFee (indirect) | Reference                         | 0..1                  | Fees may be charged for a loan              |
| Borrower           | LibraryFee            | Aggregation                       | 1 ⇒ \*                | Borrower can have multiple outstanding fees |

---

## ERD Sketch 

[Person]
   ▲
   │ (administrator)
[Library]◄──────────────┐
  │                     │
  │ has                 │ contains
  ▼                     ▼
[Borrower]───┐       [Loan]───► [Thing] ◄───[Lender]
    │        │         ▲           ▲          │
    │        │         │           │          │
    │        └──────►  |           |          │
    │  has fees (LibraryFee)       |          │
    ▼                            owner        │
[LibraryFee]                               [DistributedLibrary]
                                             ▲
                                             │ has
                                          [Lender] (multiple)



## Domain Entity-Relationship Diagram

![Domain Entities Diagram](/root/projects/means_of_production/fastapi_library/docs/images/domain_entities.drawio.png)