import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Excel Finder (Multi-Sheet)", layout="wide")

st.markdown("""
<style>
.heading {font-weight: bold; color: #1089ff; font-size: 2.5rem;}
.subheading {font-weight: bold; color: magenta; font-size: 1.5rem; margin-bottom: 20px;}
.liner {color: white; font-size: 1.15rem;}
.neon {background: #39ff14; color: #000; padding: 2px 8px; border-radius: 5px; box-shadow: 0 0 8px #39ff14;}
.card {background: #222; border-radius:12px; padding:18px; margin-bottom:24px; border: 2px solid #444;}
.table-result th {color:#1089ff; font-weight:bold; background:#222;}
.table-result td {color:#fff;}
.download-btn {margin-top: 24px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="heading">Excel Finder App</div>', unsafe_allow_html=True)
st.markdown('<div class="subheading">Upload a spreadsheet & search data in all tabs</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload Excel/CSV", type=["xlsx", "xls", "csv"])
search = st.text_input("Search (use ';' to separate multiple terms, e.g. alice;bob;charlie):")

def highlight_row(row_str, terms):
    """Highlight all matching search terms in a row"""
    for term in terms:
        if term and term.lower() in row_str.lower():
            row_str = row_str.replace(term, f'<span class="neon">{term}</span>')
    return row_str

if uploaded_file:
    sheets = {}
    file_name = uploaded_file.name.lower()

    if file_name.endswith(".csv"):
        sheets["CSV"] = pd.read_csv(uploaded_file, dtype=str)
    else:
        xls = pd.ExcelFile(uploaded_file)
        for sheet_name in xls.sheet_names:
            sheets[sheet_name] = pd.read_excel(xls, sheet_name, dtype=str)

    terms = [t.strip() for t in search.split(";") if t.strip()]
    results = []

    # For previewing sheet structure
    st.markdown(f"<hr><b>Sheets found: {', '.join(sheets.keys())}</b>", unsafe_allow_html=True)

    # Tab selection for preview
    tab_key = st.selectbox("Preview a sheet", list(sheets.keys()))
    if tab_key:
        st.dataframe(sheets[tab_key].head(20))

    # Performing searches
    for tab, df in sheets.items():
        matches_tab = []
        if terms:
            for row_idx, row in df.iterrows():
                row_str = " | ".join(row.fillna("").astype(str))
                if any(term.lower() in row_str.lower() for term in terms):
                    highlight = highlight_row(row_str, terms)
                    matches_tab.append([tab, row_idx+1, highlight])
        if matches_tab:
            results.extend(matches_tab)

    if terms:
        # Display results and download option
        st.markdown("<hr><div class='subheading'>Search Results</div>", unsafe_allow_html=True)
        if results:
            result_df = pd.DataFrame(results, columns=["Sheet", "Row", "Row Data"])
            # Show nicely formatted results
            st.markdown(
                result_df.to_html(escape=False, index=False, classes=["table-result"]),
                unsafe_allow_html=True,
            )
            # Download as CSV
            csv_buffer = io.StringIO()
            result_df.to_csv(csv_buffer, index=False)
            st.download_button(
                label="Download results as CSV",
                data=csv_buffer.getvalue(),
                file_name="excel_finder_results.csv",
                mime="text/csv",
                help="Download all matching rows from all sheets"
            )
            # Download as XLSX
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                result_df.to_excel(writer, index=False)
            st.download_button(
                label="Download results as Excel",
                data=output.getvalue(),
                file_name="excel_finder_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Download all matching rows from all sheets"
            )
        else:
            st.warning("No matches found in any sheet/tab.")
    else:
        st.info("Enter search terms and click outside the input.")

else:
    st.markdown('<span class="liner card">Please upload a spreadsheet to begin.</span>', unsafe_allow_html=True)
