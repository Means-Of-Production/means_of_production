# Basic library flows

## Distributed library
Shelly has an item they want to loan out - a vacuum cleaner.

Bob has use for that item and wants to use it.


### List
Shelly goes to the Distributed Library and adds the Item.

Bob searches for items, and finds the Item.

Bob fires "Start Borrow".  
This
- moves the item out of READY status to BORROWED
- creates the loan with STARTED status
- notifies Shelly there is a borrower
- api - create the loan/start_borrow

Shelly accepts the borrow
- creates a pickup time and location for the item
- puts penalties on people who do not pick up the item

Bob picks up the item
- loan status moves to "BORROWED"
- api - complete_borrow

Bob returns the item
- api call - start_return
- loan status moves to "WAITING_ON_LENDER_ACCEPTANCE"
- check call is made from return location

Shelly accepts the return
- api call - end_return
- loan status moves to "RETURNED"
- item moves to either "RESERVED" if there's a wait, or "READY" if not

```mermaid
flowchart TD
    A[Shelly goes to Distributed Library and adds Item] --> B[Bob searches for items and finds Item]
    B --> C[Bob fires Start Borrow]

    subgraph StartBorrow[Start Borrow]
    C --> D[Item moves from READY to BORROWED]
    C --> E[Loan is created with STARTED status]
    C --> F[Shelly is notified of borrower]
    C --> G[API: create loan/start_borrow]
    end
    
    F --> H[Shelly accepts the borrow]
    H --> I[Creates pickup time and location]
    H --> J[Penalties are put on non-pickups]
    
    I --> K[Bob picks up the item]
    
    subgraph BobPicksUp[Bob picks up]
    K --> L[Loan status moves to BORROWED]
    K --> M[API: complete_borrow]
    end
    
    L --> N[Bob returns the item]
    
    subgraph BobReturns[Bob returns]
    N --> O[API: start_return]
    N --> P[Loan status moves to WAITING_ON_LENDER_ACCEPTANCE]
    N --> Q[Check call is made from return location]
    end
    
    P --> R[Shelly accepts the return]
    
    subgraph ShellyAcceptsReturn[Shelly accepts return]
    R --> S[API: end_return]
    R --> T[Loan status moves to RETURNED]
    R --> U[Item moves to RESERVED or READY]
    end
```