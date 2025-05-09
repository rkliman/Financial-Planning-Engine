from finlib import required_constant_contribution, calculate_post_tax_income

DOWNPAYMENT = 0.2
INTEREST_RATE = 0.07

def calculate_monthly_payment(principal, annual_interest_rate, years):
    monthly_interest_rate = annual_interest_rate / 12
    number_of_payments = years * 12
    monthly_payment = (principal * monthly_interest_rate) / \
        (1 - (1 + monthly_interest_rate) ** -number_of_payments)
    return monthly_payment

def calculate_annual_saving(house_price, annual_interest_rate, time_until_purchase):
    annual_payment = required_constant_contribution(
        target_amount=DOWNPAYMENT * house_price, rate_of_return=annual_interest_rate, investment_duration=time_until_purchase)
    return annual_payment, annual_payment / 12


if __name__ == __name__ == "__main__":
    LOAN_TERM = 30
    TIME_TO_PURCHASE = 5
    SALARY = 126000
    HOUSE_PRICE = 800000

    # Calculate the required constant contribution to reach downpayment in 5 years

    annual_save, monthly_save = calculate_annual_saving(HOUSE_PRICE, 0.04, TIME_TO_PURCHASE)
    income, rate = calculate_post_tax_income(SALARY)
    print(
        f"Monthly savings needed to reach downpayment in {TIME_TO_PURCHASE} years: ${annual_save/12:,.2f} ({annual_save/income:.1%} of salary)")

    payment = calculate_monthly_payment(
        HOUSE_PRICE * (1 - DOWNPAYMENT), INTEREST_RATE, LOAN_TERM)
    print(f"House price: ${HOUSE_PRICE:,.2f}")
    print(f"Downpayment: ${DOWNPAYMENT * HOUSE_PRICE:,.2f} ({DOWNPAYMENT:.1%})")
    print(f"Monthly payment: ${payment:,.2f}")
