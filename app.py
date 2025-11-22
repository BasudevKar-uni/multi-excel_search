import streamlit as st
import pandas as pd

# ---- PAGE CONFIG ----
st.set_page_config(page_title="Excel Finder App", layout="wide")

# ---- CUSTOM STYLES ----
custom_css = """
<style>
body {font-family: Arial;}
.heading {font-weight: bold; color: #1089ff; font-size: 2.5rem;}
.subheading {font-weight: bold; color: magenta; font-size: 1.5rem;}
.liner {color: white; font-size: 1.15rem;}
.neon {background: #39ff14; color: #000; padding: 2px 8px; border-radius: 5px;
  box-shadow: 0 0 8px #39ff14, 0 0 12px #fff;}
.lightmode .heading, .lightmode .subheading, .lightmode .liner {color: #222 !important;}
.lightmode .heading {color: #1089ff !important;}
.lightmode .subheading {color: magenta !important;}
.lightmode .liner {color: #222 !important;}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ---- MODE SWITCH ----
mode = st.sidebar.radio("Choose Mode", ("Dark", "Light"))
container_class = "lightmode" if mode == "Light" else ""

# ---- HEADINGS ----
st.markdown(f'<div class="heading {container_class}">Excel Finder App</div>', unsafe_allow_html=True)
st.markdown(f'<div class="subheading {container_class}">Upload and Search Data</div>', unsafe_allow_html=True)

# ---- FILE UPLOAD ----
uploaded_file = st.file_uploader("Upload your Excel or CSV file", type=["xlsx", "xls", "csv"])
search = st.text_input("Find...")

def highlight(cell, search):
    if search and pd.notna(cell) and search.lower() in str(cell).lower():
        return f'<span class="neon">{cell}</span>'
    return f'<span class="liner {container_class}">{cell}</span>'

if uploaded_file:
    # Read file into a dataframe
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file, dtype=str)
        else:
            df = pd.read_excel(uploaded_file, dtype=str, engine="openpyxl")
    except Exception:
        st.error("Error reading file. Please check format or try a different file.")
        st.stop()

    # Filtering/search
    if search:
        mask = df.apply(lambda row: row.astype(str).str.contains(search, case=False, na=False)).any(axis=1)
        df_display = df[mask]
    else:
        df_display = df

    # Render table with highlighted search terms
    table_html = f'<div class="{container_class}"><table>'
    # Table header
    table_html += "<tr>" + "".join([f'<th class="heading">{col}</th>' for col in df_display.columns]) + "</tr>"
    # Rows
    for _, row in df_display.iterrows():
        table_html += "<tr>"
        for cell in row:
            table_html += "<td>" + highlight(cell, search) + "</td>"
        table_html += "</tr>"
    table_html += "</table></div>"

    st.markdown(table_html, unsafe_allow_html=True)
else:
    st.markdown(f'<span class="liner {container_class}">Please upload an Excel or CSV file to begin.</span>', unsafe_allow_html=True)
