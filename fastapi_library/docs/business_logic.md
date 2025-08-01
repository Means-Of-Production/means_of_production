# 📜 Business Logic – Distributed Library System (Phase One)

This document defines the **behaviors (use cases)** and **business rules** for the library system.  
It is intended to guide **FastAPI route design**, **testing**, and **domain enforcement**.

---

## 1. Add Behaviors (Actions / Use Cases)

Each **core entity** has specific actions it can perform.  
Behaviors include **inputs**, **expected outcomes**, and **constraints**.

---

### 👤 Borrower Actions

| Action              | Description                                             | Inputs                | Constraints / Rules                                             |
|---------------------|---------------------------------------------------------|-----------------------|-----------------------------------------------------------------|
| **Register Account**| Create a new borrower profile                           | Name, Email, Phone    | Must be unique and verified; assigned to a specific library     |
| **Search for Things**| Search library inventory by title, category, or type   | Search query          | Must be an approved member                                     |
| **Request a Loan**  | Submit a loan request for an available item             | Thing ID, Borrower ID | Borrower must be in good standing; max 3 active loans           |
| **Return an Item**  | Start the return process for a borrowed item            | Loan ID               | Loan must exist and belong to borrower; status transitions apply |
| **View My Loans**   | Check active, overdue, or returned loans                | Borrower ID           | Shows loan history and any pending fees                        |

---

### 🏠 Lender Actions

| Action               | Description                                           | Inputs                        | Constraints / Rules                          |
|----------------------|-------------------------------------------------------|-------------------------------|----------------------------------------------|
| **Register Account** | Create a lender profile                               | Name, Email, Location         | Must provide valid contact and return location |
| **Add a Thing**      | Add a new item to the library for lending             | Title, Description, Condition | Item is assigned `READY` status; stored in DB |
| **View Item Status** | View if an item is borrowed, available, or overdue    | Thing ID                      | Must be the owner of the item                 |
| **Remove Thing**     | Remove an item from the library                       | Thing ID                      | Only allowed if item is not currently on loan |

---

### 📚 Library Actions

| Action                      | Description                                             | Inputs                          | Constraints / Rules                           |
|-----------------------------|---------------------------------------------------------|---------------------------------|-----------------------------------------------|
| **Set Loan Policies**       | Configure rules such as max loans and default duration  | Loan time, max loans            | Changes affect all new loans                  |
| **Approve/Deny Loan Request**| Review and accept or reject loan requests             | Borrower ID, Thing ID           | Must check borrower standing and item status  |
| **Track Overdue Loans**     | Monitor and flag overdue loans                         | Auto-checked or via cron        | Changes `Loan.status` to `OVERDUE`           |
| **Accept Donations (Optional)**| Add community-contributed items                    | Thing Info, Donor Info          | Must be approved by a librarian               |
| **Generate Fees**           | Charge borrowers for overdue or damaged items          | Loan ID                         | Creates a `LibraryFee` linked to the borrower |

---

## 2. Notes for FastAPI Route Planning

Each action can map to a **RESTful endpoint** or RPC-style route:

| HTTP Verb | Endpoint                         | Description                        |
|---------- |----------------------------------|------------------------------------|
| POST      | `/borrowers/register`            | Register new borrower              |
| GET       | `/borrowers/{id}/loans`          | View borrower's loans              |
| GET       | `/things/search`                 | Search available items             |
| POST      | `/loans/request`                 | Submit a loan request              |
| POST      | `/returns/start`                 | Begin return process               |
| POST      | `/lenders/register`              | Register new lender                |
| POST      | `/things/add`                    | Add a new item                     |
| GET       | `/things/status/{thing_id}`      | Check item status                  |
| DELETE    | `/things/{thing_id}`             | Remove an item (if not on loan)    |
| POST      | `/library/policies`              | Set or update loan policies        |
| GET       | `/loans/overdue`                 | View overdue loans                 |
| POST      | `/fees/generate`                 | Generate fee for overdue/damaged item |

> ✅ **Tip:** Use `PATCH` for status changes like returning an item or paying a fee.

---

## 3. Document Business Rules

A **good system** enforces clear, non-ambiguous rules:

| Rule ID  | Rule Description                                                            |
|--------- |---------------------------------------------------------------------------- |
| **BR-001** | A borrower can have **at most 3 active loans** at any time.                |
| **BR-002** | An item’s `status` must be `READY` before it can be borrowed.              |
| **BR-003** | A lender **cannot remove** an item that is currently on loan.              |
| **BR-004** | Loans **expire after the default period** (e.g., 14 days) unless permanent.|
| **BR-005** | Returning a loan **after the due date** flags the borrower and may generate a fee or demerit. |
| **BR-006** | Libraries can **restrict or approve** external borrowers.                  |
| **BR-007** | Loan status transitions must follow the lifecycle: `READY → BORROWED → RETURN_STARTED → RETURNED/OVERDUE/DAMAGED`. |
| **BR-008** | Donated items must be **approved before appearing in the catalog**.        |
| **BR-009** | Only the **owner or library admin** can see the full borrowing history of an item. |
| **BR-010** | Borrowers with **outstanding fees or demerits** cannot make new requests.  |
| **BR-011** | A `LibraryFee` must always reference a **Loan or Thing** for traceability. |

---

This document will guide:

- ✅ **FastAPI endpoint design**
- ✅ **Domain enforcement in models/services**
- ✅ **Future database schema and constraints**
- ✅ **Test planning for borrowing, returning, and fee handling**

---
