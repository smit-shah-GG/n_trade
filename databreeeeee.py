import pandas as pd
import matplotlib.pyplot as plt

# Read the Excel files from the /mnt/data/ directory.
# (Ensure that the files contain a date column and a REER column.)

# For China – assumed columns: 'Date', 'REER'
df_china = pd.read_excel("REER CHINA Q.xlsx")
df_china.rename(columns={"REER": "REER_China"}, inplace=True)
df_china["Date"] = pd.to_datetime(df_china["Date"])

# For USA – assumed columns: 'Date', 'REER'
df_usa = pd.read_excel("REER USA Q.xlsx")
df_usa.rename(columns={"REER": "REER_USA"}, inplace=True)
df_usa["Date"] = pd.to_datetime(df_usa["Date"])

# For India – assumed columns: 'Date', 'REER'
df_india = pd.read_excel("REER INDIA Q.xlsx")
df_india.rename(columns={"REER": "REER_India"}, inplace=True)
df_india["Date"] = pd.to_datetime(df_india["Date"])

# Merge the dataframes on the 'Date' column.
# We use an outer join to keep all available dates.
df_merged = pd.merge(
    df_china[["Date", "REER_China"]],
    df_usa[["Date", "REER_USA"]],
    on="Date",
    how="outer",
)
df_merged = pd.merge(
    df_merged, df_india[["Date", "REER_India"]], on="Date", how="outer"
)

# Sort the merged dataframe by Date
df_merged.sort_values("Date", inplace=True)

# Optionally, save the merged dataset to a new Excel file.
df_merged.to_excel("Merged_REER.xlsx", index=False)
print("Merged data saved to '/mnt/data/Merged_REER.xlsx'.")

# Plot the REER time series for each country.
plt.figure(figsize=(12, 6))
plt.plot(df_merged["Date"], df_merged["REER_China"], label="China REER", marker="o")
plt.plot(df_merged["Date"], df_merged["REER_USA"], label="USA REER", marker="s")
plt.plot(df_merged["Date"], df_merged["REER_India"], label="India REER", marker="^")
plt.xlabel("Date")
plt.ylabel("REER")
plt.title("Quarterly Real Effective Exchange Rate (REER)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
