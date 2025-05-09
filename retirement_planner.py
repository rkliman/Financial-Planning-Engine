from enum import Enum
import pandas as pd
import warnings
import generate_report as gr
from finlib import required_constant_contribution, calculate_post_tax_income


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
R = 0.07    # rate of return (10%)
I = 0.03    # inflation rate (3%)

NG = 0.02  # desired growth rate for nobility wealth
SP = 0.40  # percentage of income that needs to come from savings

def supplemented_retirement(desired_income: float, retirement_duration: int,
                            rate_of_return: float, rate_of_inflation: float) -> float:
    """
    Calculate principal needed for supplemented retirement.
    This assumes you'll have other income sources (like Social Security)
    covering a portion of your retirement needs.

    Args:
        desired_income: Total annual income needed (in today's dollars)
        retirement_duration: Expected retirement length in years
        rate_of_return: Expected annual return rate (decimal)
        rate_of_inflation: Expected annual inflation rate (decimal)
        supplemental_percentage: Percentage of income that needs to come from savings (decimal)

    Returns:
        Principal amount needed at retirement start
    """
    # Only need to fund the portion not covered by other income sources
    supplemental_income = desired_income * SP

    # Use the same calculation as comfortable retirement but with reduced income need
    return comfy_retirement(supplemental_income, retirement_duration,
                            rate_of_return, rate_of_inflation)


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


def nobility_wealth(desired_income: float, retirement_duration: int,
                    rate_of_return: float, rate_of_inflation: float) -> float:
    """
    Calculate principal needed for nobility wealth.
    This goes beyond generational wealth by ensuring the principal 
    continues to grow in real terms even after withdrawals.

    Args:
        desired_income: Annual withdrawal amount needed (in today's dollars)
        retirement_duration: Not used but included for API consistency
        rate_of_return: Expected annual return rate (decimal)
        rate_of_inflation: Expected annual inflation rate (decimal)
        growth_factor: Annual real growth rate desired beyond inflation (decimal)

    Returns:
        Principal amount needed for perpetual withdrawals with real growth
    """
    # We need to ensure growth even after withdrawals
    print(rate_of_return, rate_of_inflation + NG)
    if rate_of_return <= rate_of_inflation + NG:
        warnings.warn(
            "Rate of return must be greater than inflation plus desired growth rate. Falling back to generational wealth.")
        return generational_wealth(
            desired_income, retirement_duration, rate_of_return, rate_of_inflation)

    # The principal needs to be large enough to:
    # 1. Generate the desired income
    # 2. Keep up with inflation
    # 3. Grow at the specified real rate
    return desired_income / (rate_of_return - rate_of_inflation - NG)

def calculate_principal_by_goal(future_income: float, retirement_time: int,
                                rate_of_return: float, inflation_rate: float,
                                goal: FinGoal) -> float:
    """Calculate required principal based on financial goal."""
    func_map = {
        FinGoal.Supplemented: supplemented_retirement,
        FinGoal.Sustainable: comfy_retirement,
        FinGoal.Generational: generational_wealth,
        FinGoal.Nobility: nobility_wealth
    }
    return func_map[goal](future_income, retirement_time, rate_of_return, inflation_rate)


def analyze_brokerage_account(future_income: float, growth_rate: float, inflation_rate: float,
                              investment_time: int, retirement_time: int, goal: FinGoal) -> dict:
    """Calculate brokerage account retirement needs and contributions based on goal."""
    # For brokerage accounts, consider tax on withdrawals
    brokerage_withdrawal_tax_rate = 0.15  # Simplified capital gains rate
    brokerage_effective_growth = growth_rate - \
        (growth_rate * brokerage_withdrawal_tax_rate)

    principal = calculate_principal_by_goal(
        future_income, retirement_time, brokerage_effective_growth, inflation_rate, goal
    )
    contribution = required_constant_contribution(
        principal, growth_rate, investment_time)

    return {
        "Principal Required": principal,
        "Yearly Contribution": contribution
    }


def analyze_traditional_ira(future_income: float, growth_rate: float, inflation_rate: float,
                            investment_time: int, retirement_time: int, goal: FinGoal,
                            filing_status: str, annual_contribution_limit: float) -> dict:
    """Calculate traditional IRA retirement needs and contributions based on goal."""
    # Withdrawals taxed as income
    _, withdrawal_tax_rate = calculate_post_tax_income(
        future_income, filing_status)

    # Use full growth rate during accumulation, but account for taxes on withdrawals
    principal = calculate_principal_by_goal(
        future_income /
        (1 - withdrawal_tax_rate), retirement_time, growth_rate, inflation_rate, goal
    )
    required_contribution = required_constant_contribution(
        principal, growth_rate, investment_time)

    return {
        "Principal Required": principal,
        "Yearly Contribution": required_contribution,
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
    required_contribution = required_constant_contribution(
        principal, growth_rate, investment_time)

    return {
        "Principal Required": principal,
        "Yearly Contribution": required_contribution,
        "Contribution Limit Met?": "Yes" if required_contribution > annual_contribution_limit else "No"
    }


def analyze_traditional_401k(future_income: float, growth_rate: float, inflation_rate: float,
                             investment_time: int, retirement_time: int, goal: FinGoal,
                             filing_status: str, annual_contribution_limit: float,
                             employer_match: float) -> dict:
    """Calculate traditional 401k retirement needs and contributions based on goal."""
    # Withdrawals taxed as income
    _, withdrawal_tax_rate = calculate_post_tax_income(
        future_income, filing_status)

    principal = calculate_principal_by_goal(
        future_income /
        (1 - withdrawal_tax_rate), retirement_time, growth_rate, inflation_rate, goal
    )
    base_contribution = required_constant_contribution(
        principal, growth_rate, investment_time)

    # Apply employer match up to contribution limits
    employee_contribution = base_contribution * (1 - employer_match)
    employer_contribution = employee_contribution * employer_match
    total_contribution = employee_contribution + employer_contribution

    return {
        "Principal Required": principal,
        "Yearly Contribution": employee_contribution,
        "Employee Contribution": employee_contribution,
        "Employer Contribution": employer_contribution,
        "Total Contribution": total_contribution,
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
    base_contribution = required_constant_contribution(
        principal, growth_rate, investment_time)

    # Apply employer match up to contribution limits
    employee_contribution = base_contribution * (1 - employer_match)
    employer_contribution = employee_contribution * employer_match
    total_contribution = employee_contribution + employer_contribution

    # Calculate the effective contribution cost accounting for taxes
    # For Roth, contributions are made after-tax, so the cost is higher
    _, effective_tax_rate = calculate_post_tax_income(
        current_income, filing_status)
    effective_contribution = employee_contribution / (1 - effective_tax_rate)

    return {
        "Principal Required": principal,
        "Yearly Contribution": employee_contribution,
        "Employee Contribution After-Tax": employee_contribution,
        "Employer Contribution Traditional": employer_contribution,
        "Total Contribution": total_contribution,
        "Effective Pre-Tax Cost": effective_contribution,
        "Contribution Limit Met?": "Yes" if base_contribution > annual_contribution_limit else "No",
        # "Note": "Employer match contributions go into a Traditional 401(k), not the Roth 401(k)"
    }


def analyze_retirement_options(quality_of_life: float, growth_rate: float,
                               investment_time: int, retirement_time: int,
                               goal: FinGoal = FinGoal.Sustainable,
                               filing_status: str = 'single',
                               employer_match: float = 0.05,
                               annual_contribution_limit_401k: float = 23500,
                               annual_contribution_limit_ira: float = 7000):
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
    # for account_type, calculations in results.items():
    #     print(f"\n{account_type} Analysis:")
    #     print("-" * 40)
    #     for metric, value in calculations.items():
    #         if isinstance(value, str):
    #             print(f"{metric}: {value}")
    #         else:
    #             print(f"{metric}: ${value:,.2f}")

    # Comparison section - highlights key differences
    # print("\nAccount Type Comparison:")
    # print("=" * 50)
    # print("Tax Treatment Summary:")
    # print("- Brokerage: Contributions are after-tax, growth is taxed annually, withdrawals may be taxed at capital gains rates")
    # print("- Traditional IRA/401(k): Contributions are pre-tax, growth is tax-deferred, withdrawals are taxed as ordinary income")
    # print("- Roth IRA/401(k): Contributions are after-tax, growth and qualified withdrawals are tax-free")
    # print("\nKey Considerations:")
    # print("- Traditional accounts work best if you expect to be in a lower tax bracket in retirement")
    # print("- Roth accounts work best if you expect to be in a higher tax bracket in retirement")
    # print("- 401(k) accounts have higher contribution limits than IRAs")
    # print("- Employer match is effectively 'free money' and improves return regardless of account type")
    # print("- Roth 401(k) employer match contributions go into a Traditional 401(k)")
    return results


# Example usage
if __name__ == "__main__":
    W = 126000  # current yearly income
    Wt, _ = calculate_post_tax_income(W)
    # Rw = 700000 # desired retirment income
    Rw = Wt

    print(f"\nRetirement Analysis")
    print("=" * 50)
    print(f"Parameters:")
    print(f"Quality of Life Income: ${Wt:,.2f}/year (2024 dollars)")
    print(f"Investment Period: {T1} years")
    print(f"Retirement Period: {T2} years")
    print(f"Expected Return: {R*100:.1f}%")
    print(f"Inflation Rate: {I*100:.1f}%")
    print("=" * 50)

    supplemented = analyze_retirement_options(
        Rw, R, T1, T2, FinGoal.Supplemented, filing_status='single')
    sustainable = analyze_retirement_options(
        Rw, R, T1, T2, FinGoal.Sustainable, filing_status='single')
    generational = analyze_retirement_options(
        Rw, R, T1, T2, FinGoal.Generational, filing_status='single')
    nobility = analyze_retirement_options(
        Rw, R, T1, T2, FinGoal.Nobility, filing_status='single')

    account_types = ["Brokerage Account", "Traditional IRA",
                     "Roth IRA", "Traditional 401k", "Roth 401k"]
    financial_goals = [f"Supplemented ({(1-SP)*100:.1f}%)", "Sustainable Retirement",
                       "Generational Wealth", f"Nobility (+{NG*100:.1f}%/yr)"]

    df_principal = pd.DataFrame()
    for account_type in account_types:
        df_principal[account_type] = [
            supplemented[account_type]["Principal Required"],
            sustainable[account_type]["Principal Required"],
            generational[account_type]["Principal Required"],
            nobility[account_type]["Principal Required"]
        ]
    df_principal.index = financial_goals

    df_contribution = pd.DataFrame()
    for account_type in account_types:
        df_contribution[account_type] = [
            supplemented[account_type]["Yearly Contribution"],
            sustainable[account_type]["Yearly Contribution"],
            generational[account_type]["Yearly Contribution"],
            nobility[account_type]["Yearly Contribution"]
        ]
    df_contribution.index = financial_goals

    # Transpose the DataFrames
    df_principal_t = df_principal.T
    df_contribution_t = df_contribution.T
    
    gr.plot_finances(df_principal_t, df_contribution_t, (W, Wt, T1, T2, R, I, SP, NG))
    
