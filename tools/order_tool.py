import json
from pathlib import Path

# Locate  orders.json
BASE_DIR = Path(__file__).resolve().parent
ORDERS_FILE = BASE_DIR / "orders.json"

# load orders 

with open(ORDERS_FILE,"r",encoding="utf-8")as file:
    orders =json.load(file)

# Get the Infromations

def get_order(order_id):
    order_id =order_id.strip().upper()

    order = orders.get(order_id)

    if not order:
        return{
            "found":False,
            "order_id": order_id,
            "message": "order_not found."
        }
    return {
        "found":True,
        "order_id":order_id,
        "customer_name":order["customer_name"],
        "status":order["status"],
        "product":order["product"],
        "order_date":order["order_date"],
        "expected_delivery":order["expected_delivery"]
    }

# test the order tools

if __name__ =="__main__":
     print("=" * 60)
     print("VOICEMIND AI - ORDER TOOL TEST")
     print("=" * 60)

     order_id = "ORD1004"

     result = get_order(order_id)

     print("\nOrder ID:")
     print(order_id)
     print("\nOrder Information:")
     print(result)
     print("=" * 60)