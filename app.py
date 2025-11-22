import streamlit as st
import pandas as pd

st.set_page_config(page_title="Excel Finder (Multi-Sheet)", layout="wide")

st.markdown("""
<style>
.heading {font-weight: bold; color: #1089ff; font-size: 2.5rem;}
.subheading {font-weight: bold; color: magenta; font-size: 1.5rem;}
.liner {color: white; font-size: 1.15rem;}
.neon {background: #39ff14; color: #000; padding: 2px 8px; border-radius: 5px; box-shadow: 0 0 8px #39ff14;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="heading">Excel Finder App</div>', unsafe_allow_html=True)
st.markdown('<div class="subheading">Upload spreadsheet & search all sheets</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload Excel/CSV", type=["xlsx", "xls", "csv"])
search = st.text_input("Enter search terms separated by ';' (e.g. alice;bob;charlie)")

if uploaded_file:
    # Read all sheets if Excel, or single CSV
    sheets = {}
    file_name = uploaded_file.name.lower()
    if file_name.endswith(".csv"):
        sheets["CSV"] = pd.read_csv(uploaded_file, dtype=str)
    else:
        # Read all sheets
        xls = pd.ExcelFile(uploaded_file)
        for sheet_name in xls.sheet_names:
            sheets[sheet_name] = pd.read_excel(xls, sheet_name, dtype=str)
    
    terms = [t.strip() for t in search.split(";") if t.strip()]
    results = []  # Store search results

    # For each sheet/tab...
    for tab, df in sheets.items():
        matches_tab = []
        if terms:
            for row_idx, row in df.iterrows():
                row_str = " | ".join(row.fillna("").astype(str))
                for term in terms:
                    if term.lower() in row_str.lower():
                        # Highlight
                        highlight_row = row_str.replace(term, f'<span class="neon">{term}</span>')
                        matches_tab.append((term, row_idx+1, highlight_row))
        if matches_tab:
            results.append({
                "tab": tab,
                "matches": matches_tab
            })

    if terms:
        if results:
            st.markdown("<b>Search Results:</b>", unsafe_allow_html=True)
            for res in results:
                st.markdown(f"<hr><span class='subheading'>Tab/Sheet: {res['tab']}</span>", unsafe_allow_html=True)
                st.markdown("<b>Matching rows:</b>", unsafe_allow_html=True)
                for row in res["matches"]:
                    term, idx, row_html = row
                    st.markdown(f"<div class='liner'>Row {idx}: {row_html}</div>", unsafe_allow_html=True)
        else:
            st.warning("No matches found in any sheet/tab.")
    else:
        st.info("Enter search terms and click outside the input.")

else:
    st.markdown('<span class="liner">Please upload a spreadsheet to begin.</span>', unsafe_allow_html=True)
