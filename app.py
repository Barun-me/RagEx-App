# app.py
import streamlit as st
import requests
import json

st.set_page_config(page_title="RagEx Demo", layout="centered")

st.title("RagEx — Azure Function Demo")
st.markdown(
    "Provide your Azure Function URL (or leave blank and use Demo mode). "
    "If your Function requires a function key, paste it in the Demo Key field."
)

col1, col2 = st.columns([3,1])
with col1:
    function_url = st.text_input(
        "Azure Function URL",
        placeholder="https://<your-function-app>.azurewebsites.net/api/query"
    )
with col2:
    demo_mode = st.checkbox("Demo mode", value=False)

demo_key = st.text_input(
    "Function key (optional)", type="password", placeholder="If your Function needs ?code= or x-functions-key"
)

query = st.text_area("Enter query to send to backend", height=120, placeholder="Summarize this article in two lines...")
top_k = st.number_input("Top K / results to request", min_value=1, max_value=10, value=3, step=1)

if st.button("Run"):
    if not query.strip() and not demo_mode:
        st.error("Please enter a query or enable Demo mode.")
    else:
        with st.spinner("Calling backend..." if not demo_mode else "Showing demo response..."):
            if demo_mode or not function_url.strip():
                # canned demo response so page never looks broken
                demo_response = {
                    "query": query or "Demo: summarize this page",
                    "results": [
                        {"text": "This is a demo summary sentence 1.", "source": "example.com/article"},
                        {"text": "This is a demo summary sentence 2.", "source": "example.com/article"}
                    ],
                    "note": "Demo mode — no live Azure call was made"
                }
                st.success("Demo response")
                st.json(demo_response)
                st.info("Upload a short video or link to your repo in the Cognizant form. This page proves you can produce a working UI.")
            else:
                # prepare payload — adjust keys to match your Function's contract
                payload = {"query": query, "top_k": int(top_k)}
                try:
                    # Many Azure Functions accept a function key as ?code=<key> or x-functions-key header
                    params = {}
                    headers = {"Content-Type": "application/json"}
                    if demo_key:
                        # attach both ways so one of them works for your function
                        params["code"] = demo_key
                        headers["x-functions-key"] = demo_key

                    resp = requests.post(function_url, params=params, headers=headers, json=payload, timeout=20)
                    try:
                        data = resp.json()
                    except ValueError:
                        data = {"status_code": resp.status_code, "text": resp.text}

                    if resp.ok:
                        st.success("Response from Azure Function")
                        st.json(data)
                    else:
                        st.error(f"Function returned HTTP {resp.status_code}")
                        st.write(data)
                except requests.exceptions.RequestException as e:
                    st.error("Request failed")
                    st.exception(e)

st.markdown("---")
st.caption("Notes: Do NOT paste production secrets into public demos. Use a demo key that you can revoke.")
