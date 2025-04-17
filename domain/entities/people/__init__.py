from __future__ import annotations
from typing import TYPE_CHECKING

# Use TYPE_CHECKING for potentially circular imports
if TYPE_CHECKING:
    from domain.entities.people.borrower import Borrower
    from domain.entities.people.person import Person
    from domain.entities.people.user import User
    from domain.entities.people.person_borrower import PersonBorrower


# Lazy imports to avoid circular dependencies
def __getattr__(name):
    if name == "Borrower":
        from domain.entities.people.borrower import Borrower

        return Borrower
    elif name == "Person":
        from domain.entities.people.person import Person

        return Person
    elif name == "User":
        from domain.entities.people.user import User

        return User
    elif name == "PersonBorrower":
        from domain.entities.people.person_borrower import PersonBorrower

        return PersonBorrower
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["Borrower", "Person", "User", "PersonBorrower"]
