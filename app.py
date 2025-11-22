import streamlit as st
import pandas as pd
import streamlit_authenticator as stauth
import yaml

# ----- USER CONFIGURATION -----
user_config = {
    'credentials': {
        'usernames': {
            'user1': {'email':'user1@email.com','name':'User One','password': stauth.Hasher(['pass123']).generate()[0]},
            'user2': {'email':'user2@email.com','name':'User Two','password': stauth.Hasher(['pass456']).generate()[0]}
        }
    },
    'cookie': {'expiry_days':30},
    'preauthorized': {'emails':['user1@email.com']}
}
# Allow new users to "register" via signup
with open('.streamlit_auth.yaml', 'w') as f:
    yaml.dump(user_config, f)

with open('.streamlit_auth.yaml') as f:
    config = yaml.safe_load(f)

authenticator = stauth.Authenticate(
    config['credentials'],
    'excel-app-auth-cookie',
    'excel-app-key',
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authentication_status, username = authenticator.login('Login', 'main')
if authentication_status is False:
    st.error('Username/password is incorrect')
elif authentication_status is None:
    st.warning('Please enter your username and password')
elif authentication_status:
    authenticator.logout('Logout', 'sidebar')
    st.success(f'Welcome {name}!')

    # ---- UI ----
    st.set_page_config(page_title="Excel Finder App", layout="wide")
    st.markdown("""
    <style>
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
    """, unsafe_allow_html=True)
    mode = st.sidebar.radio("Choose Mode", ("Dark", "Light"))
    container_class = "lightmode" if mode == "Light" else ""
    st.markdown(f'<div class="heading {container_class}">Excel Finder App</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="subheading {container_class}">Upload and Search Data</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload your Excel or CSV file", type=["xlsx", "xls", "csv"])
    search = st.text_input("Find multiple terms (separate by semi-colon ';')...")

    def highlight(cell, terms):
        if terms and pd.notna(cell):
            text = str(cell)
            for term in terms:
                if term and term.lower() in text.lower():
                    # highlight all matching terms
                    text = text.replace(term, f'<span class="neon">{term}</span>')
            return f'<span class="liner {container_class}">{text}</span>'
        return f'<span class="liner {container_class}">{cell}</span>'

    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file, dtype=str)
            else:
                df = pd.read_excel(uploaded_file, dtype=str, engine="openpyxl")
        except Exception:
            st.error("Error reading file. Please check format or try a different file.")
            st.stop()
        
        # Split search string into terms
        terms = [t.strip() for t in search.split(";") if t.strip()] if search else []

        # Filtering: If any search term is present in any value, keep row
        if terms:
            mask = df.apply(lambda row: row.astype(str).apply(lambda x: any(term.lower() in str(x).lower() for term in terms)), axis=1).any(axis=1)
            df_display = df[mask]
        else:
            df_display = df

        # Render table with highlights for ALL matched terms
        table_html = f'<div class="{container_class}"><table>'
        table_html += "<tr>" + "".join([f'<th class="heading">{col}</th>' for col in df_display.columns]) + "</tr>"
        for _, row in df_display.iterrows():
            table_html += "<tr>"
            for cell in row:
                table_html += "<td>" + highlight(cell, terms) + "</td>"
            table_html += "</tr>"
        table_html += "</table></div>"
        st.markdown(table_html, unsafe_allow_html=True)
