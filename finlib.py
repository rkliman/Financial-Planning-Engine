def constant_contribution(R: float, T: int, C: float) -> float:
    """
    Calculate final amount with constant contribution.

    Args:
        R: Annual rate of return (decimal)
        T: Time period in years
        C: Annual contribution amount

    Returns:
        Final account value after T years
    """
    return C * ((1 + R)**T - 1) / R

def required_constant_contribution(target_amount: float, rate_of_return: float,
                                   investment_duration: int) -> float:
    """
    Calculate required yearly contribution to reach target amount.

    Args:
        target_amount: Desired final account value
        rate_of_return: Expected annual return rate (decimal)
        investment_duration: Years of investment

    Returns:
        Required annual contribution amount
    """
    if rate_of_return <= 0:
        raise ValueError("Rate of return must be positive")
    return (target_amount * rate_of_return) / ((1 + rate_of_return)**investment_duration - 1)

def calculate_fica(income: float, filing_status: str = 'single') -> float:
    social_security_cap = 168600
    ss_tax = min(income, social_security_cap) * 0.062
    medicare_tax = income * 0.0145

    # Additional Medicare Tax for high earners
    addl_medicare_threshold = {
        'single': 200000,
        'married_joint': 250000,
        'married_separate': 125000,
        'head_household': 200000
    }

    addl_medicare = 0
    if income > addl_medicare_threshold[filing_status]:
        addl_medicare = (
            income - addl_medicare_threshold[filing_status]) * 0.009

    return ss_tax + medicare_tax + addl_medicare


def calculate_post_tax_income(income: float, filing_status: str = 'single') -> tuple:
    """
    Calculate post-tax income using progressive tax brackets (2024 rates).

    Args:
        income: Gross annual income
        filing_status: Tax filing status ('single', 'married_joint', etc.)

    Returns:
        Tuple of (post-tax income, effective tax rate)
    """
    brackets = {
        'single': [
            (11600, 0.10),
            (47150, 0.12),
            (100525, 0.22),
            (191950, 0.24),
            (243725, 0.32),
            (609350, 0.35),
            (float('inf'), 0.37)
        ],
        'married_joint': [
            (23200, 0.10),
            (94300, 0.12),
            (201050, 0.22),
            (383900, 0.24),
            (487450, 0.32),
            (731200, 0.35),
            (float('inf'), 0.37)
        ],
        'married_separate': [
            (11600, 0.10),
            (47150, 0.12),
            (100525, 0.22),
            (191950, 0.24),
            (243725, 0.32),
            (365600, 0.35),
            (float('inf'), 0.37)
        ],
        'head_household': [
            (16550, 0.10),
            (63100, 0.12),
            (100500, 0.22),
            (191950, 0.24),
            (243700, 0.32),
            (609350, 0.35),
            (float('inf'), 0.37)
        ]
    }

    if filing_status not in brackets:
        raise ValueError(
            f"Invalid filing status. Must be one of: {', '.join(brackets.keys())}")

    # Standard deduction 2024
    std_deduction = {
        'single': 14600,
        'married_joint': 29200,
        'married_separate': 14600,
        'head_household': 21900
    }

    # Apply standard deduction
    taxable_income = max(0, income - std_deduction[filing_status])

    total_tax = 0
    previous_bracket = 0

    # Calculate tax using progressive brackets
    for bracket_max, rate in brackets[filing_status]:
        if taxable_income > previous_bracket:
            taxable_in_bracket = min(
                taxable_income - previous_bracket, bracket_max - previous_bracket)
            tax_in_bracket = taxable_in_bracket * rate
            total_tax += tax_in_bracket

            if taxable_income <= bracket_max:
                break

        previous_bracket = bracket_max

    fica_tax = calculate_fica(income, filing_status)
    post_tax_income = income - total_tax - fica_tax
    effective_tax_rate = ((total_tax + fica_tax) / income) if income > 0 else 0

    return post_tax_income, effective_tax_rate


def calculate_capital_gains_tax(gain_amount: float, regular_income: float, filing_status: str = 'single') -> float:
    """
    Calculate capital gains tax based on 2024 rates.

    Args:
        gain_amount: Amount of capital gain
        regular_income: Other taxable income
        filing_status: Tax filing status

    Returns:
        Estimated capital gains tax
    """
    # 2024 capital gains tax brackets
    cg_brackets = {
        'single': [
            (44625, 0.0),
            (492300, 0.15),
            (float('inf'), 0.20)
        ],
        'married_joint': [
            (89250, 0.0),
            (553850, 0.15),
            (float('inf'), 0.20)
        ],
        'married_separate': [
            (44625, 0.0),
            (276900, 0.15),
            (float('inf'), 0.20)
        ],
        'head_household': [
            (59750, 0.0),
            (523050, 0.15),
            (float('inf'), 0.20)
        ]
    }

    if filing_status not in cg_brackets:
        raise ValueError(
            f"Invalid filing status for capital gains calculation")

    # Find applicable tax rate based on income level
    for threshold, rate in cg_brackets[filing_status]:
        if regular_income + gain_amount <= threshold:
            return gain_amount * rate

    # If no matching bracket was found, use highest rate
    return gain_amount * cg_brackets[filing_status][-1][1]