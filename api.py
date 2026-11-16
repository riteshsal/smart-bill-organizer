from fastapi import FastAPI
from database import get_bills_due_tomorrow

app = FastAPI()


@app.get("/bills/due-tomorrow")
def bills_due_tomorrow():
    bills = get_bills_due_tomorrow()

    return {
        "bills": [
            {
                "id": bill[0],
                "provider": bill[1],
                "bill_type": bill[2],
                "amount": float(bill[3]),
                "due_date": str(bill[4]),
                "user_email": bill[5]
            }
            for bill in bills
        ]
    }