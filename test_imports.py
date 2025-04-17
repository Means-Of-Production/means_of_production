"""
Test script to verify that the circular import issue has been resolved.
"""


def test_import(module_name):
    try:
        if module_name == "Thing":
            from domain.entities.thing import Thing

            print(f"Successfully imported {module_name}")
        elif module_name == "Lender":
            from domain.entities.lenders.lender import Lender

            print(f"Successfully imported {module_name}")
        elif module_name == "Loan":
            from domain.entities.loans.loan import Loan

            print(f"Successfully imported {module_name}")
        elif module_name == "Library":
            from domain.entities.libraries.library import Library

            print(f"Successfully imported {module_name}")
    except ImportError as e:
        print(f"Error importing {module_name}: {e}")


# Test each import individually
test_import("Thing")
test_import("Lender")
test_import("Loan")
test_import("Library")
