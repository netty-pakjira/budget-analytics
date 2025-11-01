from budget_analytics.utils.fileio import read_csv
from budget_analytics.utils.date import clean_date

print("hello world")

df = read_csv("daily_spending_20250920")
df.columns = ["Date", "Name", "Category", "Amount_GBP"]
df = df.dropna(subset="Date")
df["Date"] = df["Date"].map(clean_date)
df

