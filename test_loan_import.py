"""
Test script to verify that Loan can be imported.
"""

try:
    from domain.entities.loans.loan import Loan

    print("Successfully imported Loan")
except ImportError as e:
    print(f"Error importing Loan: {e}")
    import traceback

    traceback.print_exc()
