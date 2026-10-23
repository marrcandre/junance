from decimal import Decimal


def calculate_return(position, current_value):
    current_value = (
        current_value if isinstance(current_value, Decimal) else Decimal(str(current_value))
    )
    return current_value - position.cost_basis
