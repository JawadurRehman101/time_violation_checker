import streamlit as st
import pandas as pd
from datetime import datetime

st.title("⏱️ Time Violation Checker")
st.write("Upload an Excel file. The file must have time columns at column A and column I. The time format should be `YYYY.MM.DD HH:MM:SS`.")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:
    try:
        # Read Excel by skipping first 7 rows, use header on 8th row (index 7)
        df = pd.read_excel(uploaded_file, sheet_name="Sheet1", header=7, engine="openpyxl")

        # Rename time columns for clarity
        start_time_col = df.columns[0]
        end_time_col = df.columns[8]
        df = df.rename(columns={start_time_col: "Start Time", end_time_col: "End Time"})

        # Parse datetime columns
        df["Start Time"] = pd.to_datetime(df["Start Time"], format="%Y.%m.%d %H:%M:%S", errors='coerce')
        df["End Time"] = pd.to_datetime(df["End Time"], format="%Y.%m.%d %H:%M:%S", errors='coerce')

        # Drop rows where time couldn't be parsed
        df_cleaned = df.dropna(subset=["Start Time", "End Time"]).copy()

        # Calculate time difference in seconds
        df_cleaned["Time Difference (s)"] = (df_cleaned["End Time"] - df_cleaned["Start Time"]).dt.total_seconds()

        # Find violations (time difference less than 60 seconds)
        violations = df_cleaned[df_cleaned["Time Difference (s)"] < 60]

        if not violations.empty:
            st.error(f"⛔ Violation(s) found! The following rows have a time difference of less than 60 seconds:")
            # Row numbers relative to Excel (considering header is at row 8)
            violation_rows = violations.index + 8 + 1  # +1 because Excel is 1-based
            st.write(f"Violated Row Numbers: {violation_rows.tolist()}")
            st.dataframe(violations[["Start Time", "End Time", "Time Difference (s)"]])
        else:
            st.success("✅ No violations found! All time differences are >= 60 seconds.")

    except Exception as e:
        st.error(f"⚠️ Error reading the file: {e}")
