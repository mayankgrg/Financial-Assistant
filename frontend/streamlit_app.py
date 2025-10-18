import streamlit as st
import requests
import io
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt

BACKEND_URL = st.secrets.get("BACKEND_URL") if "BACKEND_URL" in st.secrets else st.sidebar.text_input("Backend URL", value="http://localhost:8000")
st.set_page_config(page_title="Fin Assistant", layout="wide")

st.title("Fin Assistant — Upload bank statements and get advice")

tab1, tab2 = st.tabs(["Expense analysis", "Credit card helper"])

with tab1:
    st.header("Upload statement (CSV / PDF / Image)")
    uploaded = st.file_uploader("Choose a file", type=['csv','pdf','png','jpg','jpeg'])
    if uploaded:
        st.info("Uploading to backend for parsing... (data is processed in-memory & not saved)")
        files = {"file": (uploaded.name, uploaded.getvalue(), uploaded.type)}
        resp = requests.post(f"{BACKEND_URL}/upload/file", files=files, timeout=60)
        if resp.status_code != 200:
            st.error("Failed to parse file: " + resp.text)
        else:
            data = resp.json()
            transactions = data.get("transactions", [])
            if not transactions:
                st.warning("No transactions found or parser could not detect format.")
            else:
                df = pd.DataFrame(transactions)
                st.subheader("Parsed transactions (sample)")
                st.dataframe(df.head(50))

                st.subheader("Original expense pie chart")
                payload = {"transactions": df.to_dict(orient='records')}
                pie_resp = requests.post(f"{BACKEND_URL}/analysis/pie_image", json=payload, timeout=60)
                if pie_resp.status_code == 200:
                    st.image(pie_resp.content, use_column_width=True)
                else:
                    st.error("Failed to generate pie chart")

                st.subheader("Get suggestions")
                strategy = st.selectbox("Strategy", ["conservative", "moderate", "aggressive"])
                sug_resp = requests.post(f"{BACKEND_URL}/analysis/suggestions", json=payload, params={"strategy": strategy}, timeout=60)
                if sug_resp.status_code == 200:
                    j = sug_resp.json()
                    st.write("Total: ", j['original']['total'])
                    st.write("Suggestions:")
                    for s in j['suggestions']:
                        st.markdown(f"- **{s['category'].title()}**: {s['suggestion']} — expected savings **${s['expected_savings']:.2f}**")
                    st.subheader("Adjusted pie chart")
                    # Show adjusted pie (we can build locally)
                    adjusted = j['adjusted']['aggregates']
                    labels = list(adjusted.keys())
                    sizes = [v for v in adjusted.values()]
                    fig, ax = plt.subplots()
                    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
                    ax.axis('equal')
                    st.pyplot(fig)
                else:
                    st.error("Suggestion generation failed.")

with tab2:
    st.header("Credit card comparison helper")
    st.write("Enter preferences: assign relative importance (sum doesn't have to be 1).")
    pref_cols = st.columns(3)
    travel_w = pref_cols[0].number_input("Travel weight", value=1.0, min_value=0.0)
    cashback_w = pref_cols[1].number_input("Cashback weight", value=1.0, min_value=0.0)
    dining_w = pref_cols[2].number_input("Dining weight", value=0.5, min_value=0.0)
    st.write("Add card offers (name, apr, annual fee, rewards as JSON like {'travel':3,'cashback':1})")
    cards = []
    n = st.number_input("How many cards to compare?", min_value=1, max_value=8, value=2)
    for i in range(int(n)):
        st.markdown(f"**Card {i+1}**")
        name = st.text_input(f"Card {i+1} name", key=f"name{i}")
        apr = st.number_input(f"Card {i+1} APR (percent)", key=f"apr{i}", value=20.0)
        fee = st.number_input(f"Card {i+1} annual fee", key=f"fee{i}", value=0.0)
        reward_raw = st.text_input(f"Card {i+1} rewards (e.g. travel:3,cashback:1)", key=f"rew{i}", value="travel:3,cashback:1")
        reward = {}
        for pair in reward_raw.split(","):
            if ":" in pair:
                k, v = pair.split(":")
                try:
                    reward[k.strip()] = float(v)
                except:
                    continue
        if name:
            cards.append({
                "name": name,
                "apr": apr,
                "annual_fee": fee,
                "reward_rate": reward,
                "notes": ""
            })
    if st.button("Compare cards"):
        if not cards:
            st.warning("Add at least one card with a name.")
        else:
            payload = {
                "user_preferences": {"travel": travel_w, "cashback": cashback_w, "dining": dining_w},
                "card_options": cards
            }
            resp = requests.post(f"{BACKEND_URL}/analysis/credit/compare", json=payload, timeout=30)
            if resp.status_code == 200:
                res = resp.json()
                st.write("Comparison results (higher score is better):")
                st.table(res['results'])
            else:
                st.error("Card comparison failed.")
