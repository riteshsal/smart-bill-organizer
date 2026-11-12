import os
import base64
import json
import requests

import streamlit as st
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(
    page_title="Smart Bill Organizer",
    page_icon="🧾"
)

st.title("🧾 Smart Bill Organizer")
st.write("Upload a bill and extract important payment details.")

uploaded_file = st.file_uploader(
    "Upload your bill",
    type=["png", "jpg", "jpeg"]
)


def encode_image(file):
    return base64.b64encode(file.getvalue()).decode("utf-8")


if uploaded_file:

    st.image(
        uploaded_file,
        caption="Uploaded Bill",
        width=500
    )

    # AI extraction
    if st.button("Extract Bill Details"):

        with st.spinner("AI is analyzing the bill..."):

            image_data = encode_image(uploaded_file)

            response = client.chat.completions.create(
                model="qwen/qwen3.8-27b",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """
Analyze this bill and extract the important billing information.

The bill can be any type, such as electricity, mobile, internet,
water, gas, DTH/cable, or another utility/service bill.

Return ONLY valid JSON using exactly these fields:

{
    "provider": "",
    "bill_type": "",
    "customer_name": "",
    "bill_number": "",
    "account_number": "",
    "amount": "",
    "due_date": "",
    "billing_period": ""
}

Extraction rules:

- provider:
  Extract the company or organization that issued the bill.

- bill_type:
  Identify the type of bill such as Electricity, Mobile,
  Internet, Water, Gas, DTH, Cable, etc.

- customer_name:
  Extract the customer or account holder name.

- bill_number:
  Extract ONLY the number explicitly labeled as
  "Bill Number", "Bill No.", "Invoice Number", "Invoice No.",
  or an equivalent bill/invoice label.
  Do NOT use Customer Number, Consumer Number, Account Number,
  Meter Number, Connection Number, Billing Unit, or other numbers.

- account_number:
  Extract the customer/account/consumer number if clearly available.
  Do not use it as the bill_number.

- amount:
  Extract the final amount that the customer needs to pay.
  Prefer the current amount due or total amount payable.

- due_date:
  Extract the payment due date.

- billing_period:
  Extract the billing period or bill month if available.

Important:
- Read the labels carefully before extracting numbers.
- Do not confuse similar-looking numbers from different fields.
- Do not guess or invent information.
- If a field is not available or cannot be read clearly, return null.
- Preserve numbers exactly as they appear on the bill, including leading zeros.
- Return ONLY valid JSON.
"""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{uploaded_file.type};base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                response_format={"type": "json_object"},
            )

            result = json.loads(
                response.choices[0].message.content
            )

            # Save result so it survives Streamlit reruns
            st.session_state["result"] = result

        st.success("Bill details extracted!")


# Human verification
if "result" in st.session_state:

    result = st.session_state["result"]

    st.subheader("Verify Bill Details")

    provider = st.text_input(
        "Provider",
        result.get("provider") or ""
    )

    bill_type = st.text_input(
        "Bill Type",
        result.get("bill_type") or ""
    )

    customer_name = st.text_input(
        "Customer Name",
        result.get("customer_name") or ""
    )

    bill_number = st.text_input(
        "Bill Number",
        result.get("bill_number") or ""
    )

    account_number = st.text_input(
        "Account Number",
        result.get("account_number") or ""
    )

    amount = st.text_input(
        "Amount",
        result.get("amount") or ""
    )

    due_date = st.text_input(
        "Due Date",
        result.get("due_date") or ""
    )

    billing_period = st.text_input(
        "Billing Period",
        result.get("billing_period") or ""
    )

    notification_email = st.text_input(
        "Email for reminder",
        placeholder="your@email.com"
    )

    # Confirm and send to Make
    if st.button("Confirm Bill"):

        if not notification_email:

            st.error("Please enter an email address.")

        else:

            bill_data = {
                "provider": provider,
                "bill_type": bill_type,
                "customer_name": customer_name,
                "bill_number": bill_number,
                "account_number": account_number,
                "amount": amount,
                "due_date": due_date,
                "billing_period": billing_period,
                "notification_email": notification_email
            }

            # Make webhook
            webhook_url = "https://hook.eu1.make.com/hbzuuof8n9jgcd2d5v8a7ejovyb2hjnx"

            response = requests.post(
                webhook_url,
                json=bill_data,
                timeout=10
            )

            st.write("Status:", response.status_code)
            st.write("Response:", response.text)

            if response.status_code == 200:

                st.success(
                    "Bill confirmed and sent to automation!"
                )

                st.json(bill_data)

            else:

                st.error(
                    "Failed to send bill to automation."
                )