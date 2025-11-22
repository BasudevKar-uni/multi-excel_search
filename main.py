import streamlit as st
import pandas as pd

# ----- THEME -----
st.set_page_config(page_title="Excel Finder App", layout="wide", initial_sidebar_state="auto")

# Custom CSS for dark/light mode and highlights
st.markdown("""
    <style>
    body {font-family: Arial;}
    .heading {font-weight: bold; color: #1089ff; font-size: 32px;}
    .subheading {font-weight: bold; color: magenta; font-size: 24px;}
    .liner {color: white; font-size: 18px;}
    .highlight {background: #39ff14; color: black; padding:2px 8px; border-radius:4px;}
    .light .heading, .light .subheading, .light .liner {color: #222 !important;}
    .light .heading {color: #1089ff !important;}
    .light .subheading {color: magenta !important;}
    </style>
""", unsafe_allow_html=True)

# ---- MODE SWITCH ----

mode = st.sidebar.radio("Choose Mode", ("Dark", "Light"))
if mode=="Light":
    st.markdown('<div class="light"></div>', unsafe_allow_html=True)

# ---- HEADINGS ----
st.markdown('<div class="heading">Excel Finder App</div>', unsafe_allow_html=True)
st.markdown('<div class="subheading">Upload your Excel/CSV, Search any Data</div>', unsafe_allow_html=True)

# ---- UPLOAD FILE ----
uploaded_file = st.file_uploader("Upload your Excel/CSV file", type=["xlsx", "xls", "csv"])
search = st.text_input("Search for data in sheet...")

if uploaded_file:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file, dtype=str)
    else:
        df = pd.read_excel(uploaded_file, dtype=str, engine="openpyxl")

    # Show table with highlights
    def highlight_terms(cell, search):
        if search and pd.notna(cell) and search.lower() in str(cell).lower():
            return f'<span class="highlight">{cell}</span>'
        else:
            return str(cell)

    if search:
        # Show only rows where any cell matches
        mask = df.apply(lambda row: row.astype(str).str.contains(search, case=False, na=False)).any(axis=1)
        df_show = df[mask]
    else:
        df_show = df

    # Display table with custom formatting
    table_html = "<table>"
    for i, row in df_show.iterrows():
        table_html += "<tr>"
        for cell in row:
            table_html += f'<td class="liner">{highlight_terms(cell, search)}</td>'
        table_html += "</tr>"
    table_html += "</table>"

    st.markdown(table_html, unsafe_allow_html=True)
