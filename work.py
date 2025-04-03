import pandas as pd
import numpy as np
import statsmodels.api as sm

# ----------------------
# 1. Data import
# ----------------------
# Below are EXAMPLES of reading data from CSV/Excel. You should adjust the file paths,
# sheet names, and column names to match your actual data.
#
# Let's assume we have three datasets:
# 1) Exports (imp5330.csv) with columns: "Date", "Exports"
# 2) REER (REER INDIA Q.xlsx) with columns: "Date", "REER"
# 3) IIP (IndicesIIP2011-12Monthly_annual_Jan25.xlsx) with columns: "Date", "IIP"
#
# Also, assume all have a quarterly "Date" in a consistent format, which we can parse as dates.

# Example for CSV with Exports
df_exp = pd.read_csv("/mnt/data/IMP5330.csv", parse_dates=["Date"])
df_exp.set_index("Date", inplace=True)

# Example for Excel with REER
df_reer = pd.read_excel(
    "/mnt/data/REER INDIA Q.xlsx", sheet_name="Sheet1", parse_dates=["Date"]
)
df_reer.set_index("Date", inplace=True)

# Example for Excel with IIP
df_iip = pd.read_excel(
    "/mnt/data/IndicesIIP2011-12Monthly_annual_Jan25.xlsx",
    sheet_name="Quarterly",
    parse_dates=["Date"],
)
df_iip.set_index("Date", inplace=True)

# ----------------------
# 2. Align/merge data by Date (quarterly frequency)
# ----------------------
# We assume each dataset is already at a quarterly frequency. If not,
# you would resample or otherwise convert them to a common frequency.
# Merge all into one DataFrame on the date index:
df_merged = pd.concat([df_exp["Exports"], df_reer["REER"], df_iip["IIP"]], axis=1)
df_merged.dropna(inplace=True)  # drop rows with missing values

# ----------------------
# 3. Take natural logs of the variables
# ----------------------
df_merged["ln_exp"] = np.log(df_merged["Exports"])
df_merged["ln_reer"] = np.log(df_merged["REER"])
df_merged["ln_iip"] = np.log(df_merged["IIP"])

# ----------------------
# 4. Set up the regression model
# ----------------------
# Our regression equation is:
#     ln_exp = a1 + a2*ln_reer + a3*ln_iip + error
#
# We can use statsmodels. We first define the exogenous variables (X)
# with a constant and the endogenous variable (y).
y = df_merged["ln_exp"]
X = df_merged[["ln_reer", "ln_iip"]]
X = sm.add_constant(X)  # add intercept

# ----------------------
# 5. Run the regression
# ----------------------
model = sm.OLS(y, X)  # Ordinary Least Squares
results = model.fit()

# ----------------------
# 6. Print the summary
# ----------------------
print(results.summary())

# ----------------------
# 7. (Optional) Inspect residuals, etc.
# ----------------------
# You could, for example, store the fitted values or residuals:
df_merged["fitted"] = results.fittedvalues
df_merged["residuals"] = results.resid

# Display the first few rows to confirm
print(df_merged.head())
