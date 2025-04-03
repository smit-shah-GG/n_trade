#!/usr/bin/env python3

# work/other/n_trade/run_regression.py

import pandas as pd
import numpy as np
import statsmodels.api as sm
import os

# ----------------------
# 1. Define File Paths
# ----------------------
# Assuming the script is run from the root of the project directory
base_path = "~/work/other/n_trade"
exports_file = os.path.join(base_path, "IMP5330.csv")
reer_file = os.path.join(
    base_path, "REER INDIA Q.xlsx"
)  # Assuming this is the source for quarterly REER
iip_file = os.path.join(base_path, "iip_data.csv")

# ----------------------
# 2. Data Import and Initial Preparation
# ----------------------

# --- Exports Data (Monthly) ---
try:
    # IMP5330 uses 'observation_date' and 'IMP5330'
    df_exp = pd.read_csv(
        exports_file,
        parse_dates=["observation_date"],
        index_col="observation_date",
    )
    df_exp.rename(columns={"IMP5330": "Exports"}, inplace=True)
    # Ensure index is DatetimeIndex
    df_exp.index = pd.to_datetime(df_exp.index)
    print(f"Successfully loaded Exports data from {exports_file}")
    print(f"Exports data shape: {df_exp.shape}")
    print("Exports data head:\n", df_exp.head())
except FileNotFoundError:
    print(f"Error: Exports file not found at {exports_file}")
    exit()
except KeyError as e:
    print(f"Error: Column {e} not found in {exports_file}. Check column names.")
    exit()
except Exception as e:
    print(f"An error occurred loading {exports_file}: {e}")
    exit()

# --- REER Data (Assuming Quarterly) ---
try:
    # Assuming columns 'Date' and 'REER' in the Excel file, sheet 'Sheet1'
    # Adjust sheet_name and column names if different
    df_reer = pd.read_excel(
        reer_file,
        sheet_name="Quarterly",
        parse_dates=["observation_date"],
        index_col="observation_date",
    )
    # Select only the REER column if others exist
    if "REER" not in df_reer.columns:
        # Check common alternative names if 'REER' isn't present
        possible_reer_cols = [
            col
            for col in df_reer.columns
            if "reer" in col.lower() or "effective exchange" in col.lower()
        ]
        if not possible_reer_cols:
            raise KeyError(
                "Could not find a REER column. Please check column names in REER INDIA Q.xlsx."
            )
        reer_col_name = possible_reer_cols[0]
        print(f"Warning: Using '{reer_col_name}' as the REER column.")
        df_reer = df_reer[[reer_col_name]]
        df_reer.rename(columns={reer_col_name: "REER"}, inplace=True)
    else:
        df_reer = df_reer[["REER"]]

    # Ensure index is DatetimeIndex
    df_reer.index = pd.to_datetime(df_reer.index)
    # Convert REER index to Quarter End for consistent merging
    # (e.g., if dates are like 2012-01-01, they represent Q1, ending 2012-03-31)
    df_reer.index = df_reer.index.to_period("Q").to_timestamp("Q")
    print(f"Successfully loaded REER data from {reer_file}")
    print(f"REER data shape: {df_reer.shape}")
    print("REER data head:\n", df_reer.head())
except FileNotFoundError:
    print(f"Error: REER file not found at {reer_file}")
    exit()
except KeyError as e:
    print(
        f"Error loading REER: Column {e} not found or REER column couldn't be identified."
    )
    print(f"Please ensure '{reer_file}' has 'Date' and 'REER' columns (or similar).")
    exit()
except Exception as e:
    print(f"An error occurred loading {reer_file}: {e}")
    exit()


# --- IIP Data (Monthly) ---
try:
    # iip_data.csv uses 'Date' (YYYY-MM format) and 'IIP'
    df_iip = pd.read_csv(iip_file, parse_dates=["Date"], index_col="Date")
    # Ensure index is DatetimeIndex
    df_iip.index = pd.to_datetime(df_iip.index)
    # Ensure only IIP column exists
    if "IIP" not in df_iip.columns:
        raise KeyError("Column 'IIP' not found in iip_data.csv.")
    df_iip = df_iip[["IIP"]]
    print(f"Successfully loaded IIP data from {iip_file}")
    print(f"IIP data shape: {df_iip.shape}")
    print("IIP data head:\n", df_iip.head())
except FileNotFoundError:
    print(f"Error: IIP file not found at {iip_file}")
    exit()
except KeyError as e:
    print(f"Error: Column {e} not found in {iip_file}. Check column names.")
    exit()
except Exception as e:
    print(f"An error occurred loading {iip_file}: {e}")
    exit()


# ----------------------
# 3. Convert Monthly Data to Quarterly
# ----------------------
# Resample monthly data (Exports, IIP) to quarterly frequency using the mean
# 'QE' means Quarter End frequency. Adjust if your quarter definition differs.
try:
    df_exp_q = df_exp.resample("QE").mean()
    df_iip_q = df_iip.resample("QE").mean()
    print("Resampled Exports and IIP data to quarterly frequency.")
    print("Quarterly Exports head:\n", df_exp_q.head())
    print("Quarterly IIP head:\n", df_iip_q.head())
except Exception as e:
    print(f"Error during resampling to quarterly data: {e}")
    exit()

# ----------------------
# 4. Align/merge data by Date (quarterly frequency)
# ----------------------
# Merge all into one DataFrame on the date index (now quarterly for all)
df_merged = pd.concat([df_exp_q, df_reer, df_iip_q], axis=1)

# Drop rows with any missing values that might result from non-overlapping dates or resampling
print(f"\nShape before dropping NA: {df_merged.shape}")
df_merged.dropna(inplace=True)
print(f"Shape after dropping NA: {df_merged.shape}")

if df_merged.empty:
    print("\nError: Merged DataFrame is empty after dropping missing values.")
    print("This might be due to non-overlapping date ranges between the datasets.")
    print("Check the date ranges of your input files:")
    print(f"  Exports dates: {df_exp.index.min()} to {df_exp.index.max()}")
    print(f"  REER dates: {df_reer.index.min()} to {df_reer.index.max()}")
    print(f"  IIP dates: {df_iip.index.min()} to {df_iip.index.max()}")
    exit()
else:
    print("Merged data head:\n", df_merged.head())
    print(f"Final dataset range: {df_merged.index.min()} to {df_merged.index.max()}")


# ----------------------
# 5. Take natural logs of the variables
# ----------------------
try:
    df_merged["ln_exp"] = np.log(df_merged["Exports"])
    df_merged["ln_reer"] = np.log(df_merged["REER"])
    df_merged["ln_iip"] = np.log(df_merged["IIP"])
    print("\nCalculated natural logarithms of variables.")
    print("Data head with logs:\n", df_merged.head())
except Exception as e:
    print(f"Error calculating logarithms: {e}")
    # Check for non-positive values which cause log errors
    print("\nChecking for non-positive values:")
    print("Exports <= 0:", (df_merged["Exports"] <= 0).any())
    print("REER <= 0:", (df_merged["REER"] <= 0).any())
    print("IIP <= 0:", (df_merged["IIP"] <= 0).any())
    exit()

# ----------------------
# 6. Set up the regression model
# ----------------------
# Regression: ln_exp = a1 + a2*ln_reer + a3*ln_iip + error
y = df_merged["ln_exp"]
X = df_merged[["ln_reer", "ln_iip"]]
X = sm.add_constant(X)  # add intercept term (a1)

print("\nRegression Setup:")
print("Dependent variable (y) head:\n", y.head())
print("Independent variables (X) head:\n", X.head())

# ----------------------
# 7. Run the regression
# ----------------------
try:
    model = sm.OLS(y, X)  # Ordinary Least Squares
    results = model.fit()
    print("\nRegression analysis complete.")
except Exception as e:
    print(f"Error running OLS regression: {e}")
    exit()

# ----------------------
# 8. Print the summary
# ----------------------
print("\n" + "=" * 80)
print("                     REGRESSION RESULTS")
print("=" * 80)
print(
    f"Dependent Variable: ln_exp (Log of Exports from {os.path.basename(exports_file)})"
)
print(
    f"Independent Variables: ln_reer (Log of REER from {os.path.basename(reer_file)}),"
)
print(f"                       ln_iip (Log of IIP from {os.path.basename(iip_file)})")
print(
    f"Data Range: {df_merged.index.min().strftime('%Y-%m-%d')} to {df_merged.index.max().strftime('%Y-%m-%d')}"
)
print(f"Number of Observations: {results.nobs}")
print("-" * 80)
print(results.summary())
print("=" * 80)

# ----------------------
# 9. (Optional) Store fitted values and residuals
# ----------------------
df_merged["fitted_ln_exp"] = results.fittedvalues
df_merged["residuals"] = results.resid

# Display the first few rows with fitted values/residuals
# print("\nFinal DataFrame with logs, fitted values, and residuals (head):")
# print(df_merged.head())

# Optionally save the merged data with results
# output_file = os.path.join(base_path, "regression_output_data.csv")
# df_merged.to_csv(output_file)
# print(f"\nFull dataset with results saved to {output_file}")
