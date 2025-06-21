import streamlit as st
import pandas as pd
import os
from io import BytesIO

# --- Streamlit App Config ---
st.set_page_config(page_title="Excel Sweeper App by Tariq Rahim", layout="wide")

# --- Custom CSS Styling ---
def inject_custom_css():
    st.markdown("""
        <style>
            .main { background-color: #f5f5f5; }
            .block-container {
                padding: 3rem 2rem;
                border-radius: 12px;
                background-color: #ffffff;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            }
            h1, h2, h3, h4, h5, h6 { color: #003366; }
            .stButton>button {
                border: none;
                border-radius: 8px;
                background-color: #0078D7;
                color: white;
                padding: 0.75rem 1.5rem;
                font-size: 1rem;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            }
            .stButton>button:hover { background-color: #005a9e; cursor: pointer; }
            .stDataFrame, .stTable { border-radius: 10px; overflow: hidden; }
            .css-1aumxhk, .css-18e3th9 { text-align: left; color: #000000; }
            .stRadio>label, .stCheckbox>label { font-weight: bold; color: #000000; }
            .stDownloadButton>button {
                background-color: #28a745;
                color: white;
            }
            .stDownloadButton>button:hover { background-color: #218838; }
        </style>
    """, unsafe_allow_html=True)

# --- File Reader ---
def read_file(file):
    ext = os.path.splitext(file.name)[-1].lower()
    if ext == ".csv":
        return pd.read_csv(file), ext
    elif ext == ".xlsx":
        return pd.read_excel(file), ext
    else:
        st.error(f"Unsupported file type: {ext}")
        return None, None

# --- Cleaning Options ---
def data_cleaning_ui(df, file):
    st.subheader("🛠️ Data Cleaning Options")
    if st.checkbox(f"Clean Data for {file.name}"):
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"Remove Duplicates from {file.name}"):
                df.drop_duplicates(inplace=True)
                st.success("Duplicates Removed!")
        with col2:
            if st.button(f"Fill Missing Values for {file.name}"):
                numeric_cols = df.select_dtypes(include=['number']).columns
                df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                st.success("Missing Values Filled with Column Means!")
    return df

# --- Column Selection ---
def column_selector_ui(df, file):
    st.subheader("🎯 Select Columns to Convert")
    cols = st.multiselect(f"Choose Columns for {file.name}", df.columns, default=df.columns)
    return df[cols]

# --- Visualization ---
def show_visualization_ui(df, file):
    st.subheader("📊 Data Visualization")
    if st.checkbox(f"Show Visualization for {file.name}"):
        st.bar_chart(df.select_dtypes(include='number').iloc[:, :2])

# --- File Converter ---
def convert_file_ui(df, file, ext):
    st.subheader("🔄 Conversion Options")
    conv_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=file.name)
    if st.button(f"Convert {file.name}"):
        buffer = BytesIO()
        new_ext = ".csv" if conv_type == "CSV" else ".xlsx"
        if conv_type == "CSV":
            df.to_csv(buffer, index=False)
            mime = "text/csv"
        else:
            df.to_excel(buffer, index=False, engine='openpyxl')
            mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        buffer.seek(0)
        st.download_button(
            label=f"⬇️ Download {file.name} as {conv_type}",
            data=buffer,
            file_name=file.name.replace(ext, new_ext),
            mime=mime
        )

# --- Main App ---
def main():
    inject_custom_css()
    st.title("Excel Sweeper App by Tariq Rahim")
    st.write("Transform your files between CSV and Excel formats with built-in data cleaning and visualization.")

    uploaded_files = st.file_uploader(
        "Upload your files (CSV or Excel):",
        type=["csv", "xlsx"],
        accept_multiple_files=True
    )

    if uploaded_files:
        for file in uploaded_files:
            df, ext = read_file(file)
            if df is None:
                continue

            st.write(f"**📄 File Name:** {file.name}")
            st.write(f"**📏 File Size:** {file.size / 1024:.2f} KB")
            st.write("🔍 Preview of the Uploaded File:")
            st.dataframe(df.head())

            df = data_cleaning_ui(df, file)
            df = column_selector_ui(df, file)
            show_visualization_ui(df, file)
            convert_file_ui(df, file, ext)

        st.success("🎉 All files processed successfully!")

if __name__ == "__main__":
    main()
