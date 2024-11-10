from enum import Enum

class FinGoal(Enum):
    Supplemented = 0  # pulls a certain amount from retirement account each year
    Sustainable = 1   # retirement account will be empty at the end of retirement
    Generational = 2  # can perpetually pull from account without loss of value
    Nobility = 3      # pulling from account doesn't diminish growth value

# Global constants
T = 0.20    # Capital Gains tax
T1 = 35     # investment time (years)
T2 = 30     # retirement time (years)
R = 0.10     # rate of return (10%)
I = 0.04    # inflation rate (3%)

def constant_contribution(R: float, T: int, C: float) -> float:
    """Calculate final amount with constant contribution."""
    return C * ((1 + R)**T - 1) / R

def comfy_retirement(desired_income: float, retirement_duration: int, 
                    rate_of_return: float, rate_of_inflation: float) -> float:
    """Calculate principal needed for comfortable retirement."""
    # Using the perpetuity with growth formula adjusted for finite time
    if rate_of_return <= rate_of_inflation:
        raise ValueError("Rate of return must be greater than inflation rate")
    return desired_income * ((1 - ((1 + rate_of_inflation)/(1 + rate_of_return))**retirement_duration) 
                           / (rate_of_return - rate_of_inflation))

def generational_wealth(desired_income: float, retirement_duration: int,
                       rate_of_return: float, rate_of_inflation: float) -> float:
    """Calculate principal needed for generational wealth."""
    # Using the perpetuity with growth formula
    if rate_of_return <= rate_of_inflation:
        raise ValueError("Rate of return must be greater than inflation rate")
    return desired_income / (rate_of_return - rate_of_inflation)

def required_constant_contribution(target_amount: float, rate_of_return: float, 
                                 investment_duration: int) -> float:
    """Calculate required yearly contribution to reach target amount."""
    if rate_of_return <= 0:
        raise ValueError("Rate of return must be positive")
    return (target_amount * rate_of_return) / ((1 + rate_of_return)**investment_duration - 1)

def calculate_post_tax_income(income: float, filing_status: str = 'single') -> tuple:
    """Calculate post-tax income using progressive tax brackets."""
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
        raise ValueError(f"Invalid filing status. Must be one of: {', '.join(brackets.keys())}")
    
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
    
    for bracket_max, rate in brackets[filing_status]:
        if taxable_income > previous_bracket:
            taxable_in_bracket = min(taxable_income - previous_bracket, bracket_max - previous_bracket)
            tax_in_bracket = taxable_in_bracket * rate
            total_tax += tax_in_bracket
            
            if taxable_income <= bracket_max:
                break
                
        previous_bracket = bracket_max
    
    post_tax_income = income - total_tax
    effective_tax_rate = (total_tax / income) if income > 0 else 0
    
    return post_tax_income, effective_tax_rate

def analyze_retirement_options(quality_of_life: float, growth_rate: float,
                             investment_time: int, retirement_time: int,
                             goal: FinGoal = FinGoal.Sustainable,
                             filing_status: str = 'single'):
    """Analyze different retirement investment options."""
    
    print(f"\nRetirement Analysis")
    print("=" * 50)
    print(f"Parameters:")
    print(f"Quality of Life Income: ${quality_of_life:,.2f}/year")
    print(f"Investment Period: {investment_time} years")
    print(f"Retirement Period: {retirement_time} years")
    print(f"Expected Return: {growth_rate*100:.1f}%")
    print(f"Inflation Rate: {I*100:.1f}%")
    print(f"Goal: {goal.name}")
    print("=" * 50)
    
    # Brokerage Account Analysis
    future_income = quality_of_life * (1 + I)**investment_time
    effective_growth = (1 - T) * growth_rate
    
    results = {
        "Brokerage Account": {},
        "Traditional IRA": {},
        "Roth IRA": {}
    }
    
    # Brokerage calculations
    results["Brokerage Account"].update({
        "Principal (Comfortable)": comfy_retirement(future_income, retirement_time, effective_growth, I),
        "Required Contribution (Comfortable)": required_constant_contribution(
            comfy_retirement(future_income, retirement_time, effective_growth, I),
            growth_rate, investment_time
        ),
        "Principal (Generational)": generational_wealth(future_income, retirement_time, effective_growth, I),
        "Required Contribution (Generational)": required_constant_contribution(
            generational_wealth(future_income, retirement_time, effective_growth, I),
            growth_rate, investment_time
        )
    })
    
    # Traditional IRA calculations
    _, withdrawal_tax_rate = calculate_post_tax_income(quality_of_life, filing_status)
    trad_principal_comfy = comfy_retirement(quality_of_life, retirement_time, growth_rate, I)
    trad_principal_gen = generational_wealth(quality_of_life, retirement_time, growth_rate, I)
    
    results["Traditional IRA"].update({
        "Principal (Comfortable)": trad_principal_comfy,
        "Withdrawal Tax (Comfortable)": withdrawal_tax_rate * trad_principal_comfy,
        "Required Contribution (Comfortable)": required_constant_contribution(
            trad_principal_comfy, growth_rate, investment_time
        ),
        "Principal (Generational)": trad_principal_gen,
        "Withdrawal Tax (Generational)": withdrawal_tax_rate * trad_principal_gen,
        "Required Contribution (Generational)": required_constant_contribution(
            trad_principal_gen, growth_rate, investment_time
        )
    })
    
    # Roth IRA calculations
    results["Roth IRA"].update({
        "Principal (Comfortable)": comfy_retirement(quality_of_life, retirement_time, growth_rate, I),
        "Required Contribution (Comfortable)": required_constant_contribution(
            comfy_retirement(quality_of_life, retirement_time, growth_rate, I),
            growth_rate, investment_time
        ),
        "Principal (Generational)": generational_wealth(quality_of_life, retirement_time, growth_rate, I),
        "Required Contribution (Generational)": required_constant_contribution(
            generational_wealth(quality_of_life, retirement_time, growth_rate, I),
            growth_rate, investment_time
        )
    })
    
    # Print results
    for account_type, calculations in results.items():
        print(f"\n{account_type} Analysis:")
        print("-" * 40)
        for metric, value in calculations.items():
            print(f"{metric}: ${value:,.2f}")

# Example usage
if __name__ == "__main__":
    W = 120_000  # current yearly income
    Wt, _ = calculate_post_tax_income(W)
    analyze_retirement_options(Wt, R, T1, T2, FinGoal.Sustainable)