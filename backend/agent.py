import os
import json
import time
from datetime import datetime
from typing import List, Dict

import requests
from dotenv import load_dotenv
from jinja2 import Template
from openai import OpenAI
from rich.console import Console
from tenacity import retry, stop_after_attempt, wait_fixed

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

console = Console()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
SHOPIFY_API_KEY = os.getenv('SHOPIFY_API_KEY')
SHOPIFY_PASSWORD = os.getenv('SHOPIFY_PASSWORD')
SHOPIFY_STORE = os.getenv('SHOPIFY_STORE')
GMAIL_USERNAME = os.getenv('GMAIL_USERNAME')
GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD')
MOCK = os.getenv('MOCK', 'false').lower() == 'true'

STATUS_FILE = os.path.join(os.path.dirname(__file__), 'status.json')

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

EMAIL_TEMPLATE = Template(
    """
Hi {{ customer_name }},

We noticed you left some items in your cart. As a thank you for shopping with us, here is a {{ discount }}% discount!

Cart total: ${{ total }}

Click here to complete your purchase: {{ checkout_url }}
"""
)


def save_status(data):
    with open(STATUS_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def load_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE) as f:
            return json.load(f)
    return {}


def get_abandoned_carts() -> List[Dict]:
    console.log("Fetching abandoned carts")
    if MOCK or not SHOPIFY_API_KEY:
        return [
            {
                'id': 'cart1',
                'customer': {'first_name': 'John', 'email': 'john@example.com'},
                'total_price': '49.99',
                'checkout_url': 'https://example.com/checkout/cart1'
            }
        ]
    url = f"https://{SHOPIFY_API_KEY}:{SHOPIFY_PASSWORD}@{SHOPIFY_STORE}/admin/api/2023-04/checkouts.json?since_id=0"
    response = requests.get(url)
    response.raise_for_status()
    carts = response.json().get('checkouts', [])
    return carts


def create_email(cart, discount: int) -> str:
    customer_name = cart['customer'].get('first_name', 'there')
    rendered = EMAIL_TEMPLATE.render(
        customer_name=customer_name,
        total=cart['total_price'],
        discount=discount,
        checkout_url=cart['checkout_url']
    )
    if client:
        prompt = f"Improve the following marketing email:\n{rendered}"
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content
    return rendered


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def send_email(to_address: str, content: str):
    console.log(f"Sending email to {to_address}")
    if MOCK or not GMAIL_USERNAME:
        console.log("[mock] email sent")
        return True
    import smtplib
    from email.mime.text import MIMEText

    msg = MIMEText(content)
    msg['Subject'] = 'We saved your cart!'
    msg['From'] = GMAIL_USERNAME
    msg['To'] = to_address

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(GMAIL_USERNAME, GMAIL_PASSWORD)
        server.send_message(msg)
    return True


def check_order_recovered(cart_id: str) -> bool:
    console.log(f"Checking if cart {cart_id} recovered")
    if MOCK or not SHOPIFY_API_KEY:
        return False
    url = f"https://{SHOPIFY_API_KEY}:{SHOPIFY_PASSWORD}@{SHOPIFY_STORE}/admin/api/2023-04/orders.json?checkout_id={cart_id}"
    response = requests.get(url)
    response.raise_for_status()
    orders = response.json().get('orders', [])
    return len(orders) > 0


def run_recovery():
    status = load_status()
    status['started_at'] = datetime.utcnow().isoformat()
    carts = get_abandoned_carts()
    status['carts'] = []

    for cart in carts:
        cart_status = {
            'id': cart['id'],
            'email_sent': [],
            'recovered': False
        }
        discount = 10
        for attempt in range(3):
            email_content = create_email(cart, discount)
            send_email(cart['customer']['email'], email_content)
            cart_status['email_sent'].append({'discount': discount, 'time': datetime.utcnow().isoformat()})
            console.log(f"Waiting before checking recovery for cart {cart['id']}")
            time.sleep(1 if MOCK else 3600)
            if check_order_recovered(cart['id']):
                cart_status['recovered'] = True
                break
            discount += 5
        status['carts'].append(cart_status)

    status['finished_at'] = datetime.utcnow().isoformat()
    save_status(status)
    return status
