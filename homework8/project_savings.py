import sys

import matplotlib.pyplot as plt


def project_savings(
    start_amount,
    monthly_deposit,
    years,
    treasury_rate,
    treasury_date,
    certificate_rate,
    stock_return,
):
    """Print and plot fixed-rate savings projections."""
    options = [
        ("Savings at the Treasury Bills rate", treasury_rate),
        ("Certificate", certificate_rate),
        ("Stock index fund, assumed", stock_return),
    ]

    print(f"start_amount: ${start_amount:.2f}")
    print(f"monthly_deposit: ${monthly_deposit:.2f}")
    print(f"years: {years}")
    print(f"treasury_rate: {treasury_rate:.2f}% (Treasury Bills average, {treasury_date})")
    print(f"certificate_rate: {certificate_rate:.2f}% (club rate sheet)")
    print(f"stock_return: {stock_return:.2f}% (club board assumption)")

    total_deposited = start_amount + monthly_deposit * 12 * years
    balances_by_option = []
    year_numbers = list(range(years + 1))

    for name, annual_rate in options:
        balance = start_amount
        yearly_balances = [balance]
        monthly_rate = annual_rate / 12 / 100

        for month in range(1, years * 12 + 1):
            balance += balance * monthly_rate
            balance += monthly_deposit
            if month % 12 == 0:
                yearly_balances.append(balance)

        balances_by_option.append(yearly_balances)
        print(f"{name}")
        print(f"  rate: {annual_rate:.2f}%")
        print(f"  final balance: ${balance:.2f}")
        print(f"  growth over total deposited: ${balance - total_deposited:.2f}")

    print(f"total deposited: ${total_deposited:.2f}")
    print("Education, not advice. These projections use fixed rates. Real savings rates change, and stock returns vary from year to year and can be negative.")

    plt.figure(figsize=(10, 6))
    for (name, annual_rate), yearly_balances in zip(options, balances_by_option):
        plt.plot(
            year_numbers,
            yearly_balances,
            marker="o",
            label=f"{name} ({annual_rate:.2f}%)",
        )

    deposited_by_year = [start_amount + monthly_deposit * 12 * year for year in year_numbers]
    plt.plot(
        year_numbers,
        deposited_by_year,
        linestyle="--",
        color="black",
        label="Total deposited",
    )
    plt.xticks(year_numbers)
    plt.xlabel("years")
    plt.ylabel("balance in dollars")
    plt.title("Larkspur Investment Club savings projection")
    plt.legend()
    plt.tight_layout()
    plt.savefig("projection.png")
    plt.close()
    print("plot saved as projection.png")


if __name__ == "__main__":
    if sys.argv[1:] == ["--example"]:
        project_savings(
            start_amount=500,
            monthly_deposit=100,
            years=4,
            treasury_rate=4.10,
            treasury_date="2026-09-30",
            certificate_rate=3.75,
            stock_return=7.0,
        )
