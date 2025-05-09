from retirement_planner import analyze_retirement_options, FinGoal
from house_planner import calculate_annual_saving
from finlib import calculate_post_tax_income

if __name__ == "__main__":
    goal = FinGoal.Sustainable
    income = 126000
    rate_of_return = 0.09  # Expected return
    current_age = 26
    expected_retirement_age = 56
    expected_lifespan = 85
    
    working_years = expected_retirement_age - current_age
    retirement_years = expected_lifespan - expected_retirement_age
    real_income = calculate_post_tax_income(income)[0]  # Post-tax income
    sustainable = analyze_retirement_options(
        real_income, rate_of_return, working_years, retirement_years, goal, filing_status='single')
    
    percents = {}
    for account_name, account_data in sustainable.items():
        print(f"{account_name}: {account_data['Yearly Contribution']} ({account_data['Yearly Contribution']/real_income:.1%})")
        percents[account_name] = account_data['Yearly Contribution']/real_income
        
    house_price = 800000
    hysa_rate = 0.04
    time_to_purchase = 5
    annual_house_save, monthly_house_save = calculate_annual_saving(house_price, hysa_rate, time_to_purchase)
    save_percent = annual_house_save / real_income
    
    
    monthly_expenses = {
        "Rent": 1600,
        "Groceries": 500,
        "Utilities": 200,
        "Gas": 150,
    }
    annual_costs = sum(monthly_expenses.values()) * 12
    
    money_left = real_income - (annual_house_save + annual_costs + sustainable['Roth 401k']['Yearly Contribution'])
    money_left_per_month = money_left / 12
    print(money_left_per_month)
        
    
        
    
        