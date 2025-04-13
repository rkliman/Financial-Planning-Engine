from enum import Enum

class FinGoal(Enum):
    """Enumeration defining different retirement financial goals."""
    Supplemented = 0  # pulls a certain amount from retirement account each year
    Sustainable = 1   # retirement account will be empty at the end of retirement
    Generational = 2  # can perpetually pull from account without loss of value
    Nobility = 3      # pulling from account doesn't diminish growth value

# Global constants
T = 0.20    # Capital Gains tax rate - note: this is simplified and actual rates may vary
T1 = 42     # investment time (years) - accumulation phase
T2 = 35     # retirement time (years) - distribution phase
R = 0.10    # rate of return (10%)
I = 0.03    # inflation rate (3%)

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

def comfy_retirement(desired_income: float, retirement_duration: int, 
                    rate_of_return: float, rate_of_inflation: float) -> float:
    """
    Calculate principal needed for comfortable retirement.
    This uses a modified perpetuity formula that accounts for both 
    investment returns and inflation over a finite time period.
    
    Args:
        desired_income: Annual withdrawal amount needed (in today's dollars)
        retirement_duration: Expected retirement length in years
        rate_of_return: Expected annual return rate (decimal)
        rate_of_inflation: Expected annual inflation rate (decimal)
        
    Returns:
        Principal amount needed at retirement start
    """
    # Using the perpetuity with growth formula adjusted for finite time
    if rate_of_return <= rate_of_inflation:
        raise ValueError("Rate of return must be greater than inflation rate")
    return desired_income * ((1 - ((1 + rate_of_inflation)/(1 + rate_of_return))**retirement_duration) 
                           / (rate_of_return - rate_of_inflation))

def generational_wealth(desired_income: float, retirement_duration: int,
                       rate_of_return: float, rate_of_inflation: float) -> float:
    """
    Calculate principal needed for generational wealth.
    This uses the perpetuity with growth formula to maintain principal indefinitely.
    
    Args:
        desired_income: Annual withdrawal amount needed (in today's dollars)
        retirement_duration: Not used but included for API consistency
        rate_of_return: Expected annual return rate (decimal)
        rate_of_inflation: Expected annual inflation rate (decimal)
        
    Returns:
        Principal amount needed for perpetual withdrawals
    """
    # Using the perpetuity with growth formula
    if rate_of_return <= rate_of_inflation:
        raise ValueError("Rate of return must be greater than inflation rate")
        
    # Add safety check for near-equal values to prevent extremely large results
    if rate_of_return - rate_of_inflation < 0.01:
        print("WARNING: Return rate is very close to inflation rate. Results may be unreliable.")
        
    return desired_income / (rate_of_return - rate_of_inflation)

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
    
    # Calculate tax using progressive brackets
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
        raise ValueError(f"Invalid filing status for capital gains calculation")
    
    # Find applicable tax rate based on income level
    for threshold, rate in cg_brackets[filing_status]:
        if regular_income + gain_amount <= threshold:
            return gain_amount * rate
    
    # If no matching bracket was found, use highest rate
    return gain_amount * cg_brackets[filing_status][-1][1]

def calculate_principal_by_goal(future_income: float, retirement_time: int, 
                                rate_of_return: float, inflation_rate: float, 
                                goal: FinGoal) -> float:
    """Calculate required principal based on financial goal."""
    if goal in [FinGoal.Supplemented, FinGoal.Sustainable]:
        # For supplemented or sustainable retirement, calculate comfortable retirement
        return comfy_retirement(future_income, retirement_time, rate_of_return, inflation_rate)
    elif goal in [FinGoal.Generational, FinGoal.Nobility]:
        # For generational or nobility, calculate generational wealth
        return generational_wealth(future_income, retirement_time, rate_of_return, inflation_rate)
    else:
        raise ValueError(f"Unsupported financial goal: {goal}")

def analyze_brokerage_account(future_income: float, growth_rate: float, inflation_rate: float, 
                             investment_time: int, retirement_time: int, goal: FinGoal) -> dict:
    """Calculate brokerage account retirement needs and contributions based on goal."""
    # For brokerage accounts, consider tax on withdrawals
    brokerage_withdrawal_tax_rate = 0.15  # Simplified capital gains rate
    brokerage_effective_growth = growth_rate - (growth_rate * brokerage_withdrawal_tax_rate)
    
    principal = calculate_principal_by_goal(
        future_income, retirement_time, brokerage_effective_growth, inflation_rate, goal
    )
    contribution = required_constant_contribution(principal, growth_rate, investment_time)
    
    goal_name = goal.name
    return {
        f"Principal ({goal_name})": principal,
        f"Required Contribution ({goal_name})": contribution
    }

def analyze_traditional_ira(future_income: float, growth_rate: float, inflation_rate: float, 
                           investment_time: int, retirement_time: int, goal: FinGoal,
                           filing_status: str, annual_contribution_limit: float) -> dict:
    """Calculate traditional IRA retirement needs and contributions based on goal."""
    # Withdrawals taxed as income
    _, withdrawal_tax_rate = calculate_post_tax_income(future_income, filing_status)
    
    # Use full growth rate during accumulation, but account for taxes on withdrawals
    principal = calculate_principal_by_goal(
        future_income / (1 - withdrawal_tax_rate), retirement_time, growth_rate, inflation_rate, goal
    )
    required_contribution = required_constant_contribution(principal, growth_rate, investment_time)
    
    goal_name = goal.name
    return {
        f"Principal ({goal_name})": principal,
        f"Required Contribution ({goal_name})": min(required_contribution, annual_contribution_limit),
        "Contribution Limit Met?": "Yes" if required_contribution > annual_contribution_limit else "No"
    }

def analyze_roth_ira(future_income: float, growth_rate: float, inflation_rate: float, 
                    investment_time: int, retirement_time: int, goal: FinGoal,
                    annual_contribution_limit: float) -> dict:
    """Calculate Roth IRA retirement needs and contributions based on goal."""
    # No taxes on qualified withdrawals
    principal = calculate_principal_by_goal(
        future_income, retirement_time, growth_rate, inflation_rate, goal
    )
    required_contribution = required_constant_contribution(principal, growth_rate, investment_time)
    
    goal_name = goal.name
    return {
        f"Principal ({goal_name})": principal,
        f"Required Contribution ({goal_name})": min(required_contribution, annual_contribution_limit),
        "Contribution Limit Met?": "Yes" if required_contribution > annual_contribution_limit else "No"
    }

def analyze_traditional_401k(future_income: float, growth_rate: float, inflation_rate: float, 
                           investment_time: int, retirement_time: int, goal: FinGoal,
                           filing_status: str, annual_contribution_limit: float, 
                           employer_match: float) -> dict:
    """Calculate traditional 401k retirement needs and contributions based on goal."""
    # Withdrawals taxed as income
    _, withdrawal_tax_rate = calculate_post_tax_income(future_income, filing_status)
    
    principal = calculate_principal_by_goal(
        future_income / (1 - withdrawal_tax_rate), retirement_time, growth_rate, inflation_rate, goal
    )
    base_contribution = required_constant_contribution(principal, growth_rate, investment_time)
    
    # Apply employer match up to contribution limits
    employee_contribution = min(base_contribution, annual_contribution_limit)
    employer_contribution = min(employee_contribution * employer_match, 
                               annual_contribution_limit * employer_match)
    total_contribution = employee_contribution + employer_contribution
    
    goal_name = goal.name
    return {
        f"Principal ({goal_name})": principal,
        f"Employee Contribution ({goal_name})": employee_contribution,
        f"Employer Contribution ({goal_name})": employer_contribution,
        f"Total Contribution ({goal_name})": total_contribution,
        "Contribution Limit Met?": "Yes" if base_contribution > annual_contribution_limit else "No"
    }

def analyze_roth_401k(future_income: float, growth_rate: float, inflation_rate: float, 
                    investment_time: int, retirement_time: int, goal: FinGoal,
                    filing_status: str, annual_contribution_limit: float, 
                    employer_match: float, current_income: float) -> dict:
    """Calculate Roth 401k retirement needs and contributions based on goal."""
    # No taxes on qualified withdrawals
    principal = calculate_principal_by_goal(
        future_income, retirement_time, growth_rate, inflation_rate, goal
    )
    base_contribution = required_constant_contribution(principal, growth_rate, investment_time)
    
    # Apply employer match up to contribution limits
    employee_contribution = min(base_contribution, annual_contribution_limit)
    employer_contribution = min(employee_contribution * employer_match, 
                               annual_contribution_limit * employer_match)
    total_contribution = employee_contribution + employer_contribution
    
    # Calculate the effective contribution cost accounting for taxes
    # For Roth, contributions are made after-tax, so the cost is higher
    _, effective_tax_rate = calculate_post_tax_income(current_income, filing_status)
    effective_contribution = employee_contribution / (1 - effective_tax_rate)
    
    goal_name = goal.name
    return {
        f"Principal ({goal_name})": principal,
        f"Employee Contribution After-Tax ({goal_name})": employee_contribution,
        f"Employer Contribution Traditional ({goal_name})": employer_contribution,
        f"Total Contribution ({goal_name})": total_contribution,
        f"Effective Pre-Tax Cost ({goal_name})": effective_contribution,
        "Contribution Limit Met?": "Yes" if base_contribution > annual_contribution_limit else "No",
        "Note": "Employer match contributions go into a Traditional 401(k), not the Roth 401(k)"
    }

def analyze_retirement_options(quality_of_life: float, growth_rate: float,
                               investment_time: int, retirement_time: int,
                               goal: FinGoal = FinGoal.Sustainable,
                               filing_status: str = 'single',
                               employer_match: float = 0.05,
                               annual_contribution_limit_401k: float = 22500,
                               annual_contribution_limit_ira: float = 6500):
    """
    Analyze different retirement investment options.
    
    Args:
        quality_of_life: Annual income needed in retirement (current dollars)
        growth_rate: Expected investment return rate
        investment_time: Years until retirement
        retirement_time: Expected years in retirement
        goal: Financial goal for retirement (from FinGoal enum)
        filing_status: Tax filing status
        employer_match: Percentage of employer 401k match
        annual_contribution_limit_401k: Annual contribution limit for 401k
        annual_contribution_limit_ira: Annual contribution limit for IRA
    """
    
    print(f"\nRetirement Analysis")
    print("=" * 50)
    print(f"Parameters:")
    print(f"Quality of Life Income: ${quality_of_life:,.2f}/year")
    print(f"Investment Period: {investment_time} years")
    print(f"Retirement Period: {retirement_time} years")
    print(f"Expected Return: {growth_rate*100:.1f}%")
    print(f"Inflation Rate: {I*100:.1f}%")
    print(f"Goal: {goal.name}")
    print(f"Employer Match (for 401k): {employer_match*100:.1f}%")
    print("=" * 50)
    
    # Calculate future income needs adjusted for inflation
    future_income = quality_of_life * (1 + I)**investment_time
    
    # Calculate results for each account type based on specified goal
    results = {
        "Brokerage Account": analyze_brokerage_account(
            future_income, growth_rate, I, investment_time, retirement_time, goal
        ),
        "Traditional IRA": analyze_traditional_ira(
            future_income, growth_rate, I, investment_time, retirement_time, goal,
            filing_status, annual_contribution_limit_ira
        ),
        "Roth IRA": analyze_roth_ira(
            future_income, growth_rate, I, investment_time, retirement_time, goal,
            annual_contribution_limit_ira
        ),
        "Traditional 401k": analyze_traditional_401k(
            future_income, growth_rate, I, investment_time, retirement_time, goal,
            filing_status, annual_contribution_limit_401k, employer_match
        ),
        "Roth 401k": analyze_roth_401k(
            future_income, growth_rate, I, investment_time, retirement_time, goal,
            filing_status, annual_contribution_limit_401k, employer_match, quality_of_life
        )
    }

    # Print results
    for account_type, calculations in results.items():
        print(f"\n{account_type} Analysis:")
        print("-" * 40)
        for metric, value in calculations.items():
            if isinstance(value, str):
                print(f"{metric}: {value}")
            else:
                print(f"{metric}: ${value:,.2f}")

    # Comparison section - highlights key differences
    print("\nAccount Type Comparison:")
    print("=" * 50)
    print("Tax Treatment Summary:")
    print("- Brokerage: Contributions are after-tax, growth is taxed annually, withdrawals may be taxed at capital gains rates")
    print("- Traditional IRA/401(k): Contributions are pre-tax, growth is tax-deferred, withdrawals are taxed as ordinary income")
    print("- Roth IRA/401(k): Contributions are after-tax, growth and qualified withdrawals are tax-free")
    print("\nKey Considerations:")
    print("- Traditional accounts work best if you expect to be in a lower tax bracket in retirement")
    print("- Roth accounts work best if you expect to be in a higher tax bracket in retirement")
    print("- 401(k) accounts have higher contribution limits than IRAs")
    print("- Employer match is effectively 'free money' and improves return regardless of account type")
    print("- Roth 401(k) employer match contributions go into a Traditional 401(k)")

    print(f"\nRecommended Strategy Based on Required Contributions for {goal.name} Goal:")
    # Find lowest required contribution approach
    min_contribution = float('inf')
    min_account_type = ""
    
    for account_type, calculations in results.items():
        if account_type == "Traditional 401k":
            contribution_key = f"Employee Contribution ({goal.name})"
        elif account_type == "Roth 401k":
            contribution_key = f"Employee Contribution After-Tax ({goal.name})"
        else:
            contribution_key = f"Required Contribution ({goal.name})"
        
        contribution = calculations.get(contribution_key, float('inf'))
        
        if contribution < min_contribution:
            min_contribution = contribution
            min_account_type = account_type
    
    print(f"Lowest contribution requirement: {min_account_type} (${min_contribution:,.2f}/year)")

# Example usage
if __name__ == "__main__":
    W = 100000  # current yearly income
    Wt, _ = calculate_post_tax_income(W)
    analyze_retirement_options(Wt, R, T1, T2, FinGoal.Sustainable, filing_status='single')