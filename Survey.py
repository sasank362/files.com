import PySimpleGUI as sg
import random
import secrets
import string
import feedparser
import smtplib
import pyotp
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import stripe

#Configure your Stripe API key
stripe.api.key = "pk_test_51NpXtzSEAdhnFc1sOEEltY47SmpyJw0T34C1XsuM3v6dU7xGxZdSFSNIcfUWUCGyVzycJXfvXM7RITlQy5PkjJmM00zG7hRdQZ"

# Dictionary to store user information
users = {}


def fetch_rss_feeds():
    # RSS feed URLs
    feed_urls = [
        'https://feeds.bbci.co.uk/news/rss.xml',
        'https://www.nytimes.com/svc/collections/v1/publish/https://www.nytimes.com/section/world/rss.xml',
        'https://www.theguardian.com/world/rss',
        'https://rss.cnn.com/rss/cnn_topstories.rss',
        'https://www.aljazeera.com/xml/rss/all.xml'
    ]

    # Create an empty list to store the parsed feed items
    feed_items = []

    # Fetch and parse each RSS feed
    for url in feed_urls:
        feed = feedparser.parse(url)

        # Extract relevant information from each feed item
        for entry in feed.entries:
            # Get the title value from the feed entry
            title = entry.title

            # Generate a random price between 50 and 100 RS
            price = str(random.randint(50, 100)) + " RS"

            # Add the title and price to the feed_items list
            feed_items.append({"title": title, "price": price})

    return feed_items


def display_rss_feeds(feed_items):
    # Create the UI layout
    layout = [
        [sg.Text('Select items to purchase:', font=('Helvetica', 20))],
        [sg.Listbox(values=[item["title"] for item in feed_items], size=(50, 10), key="-ITEMS-", enable_events=True, select_mode='extended')],
        [sg.Button('Continue'), sg.Button('Cancel')]
    ]

    window = sg.Window('Select Items', layout, element_justification='center')

    selected_items = []

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == 'Cancel':
            break

        if event == 'Continue':
            selected_titles = values["-ITEMS-"]
            selected_items = [item for item in feed_items if item["title"] in selected_titles]
            break

    window.close()

    return selected_items

def generate_access_token():
    alphabet = string.ascii_letters + string.digits
    token = ''.join(secrets.choice(alphabet) for _ in range(20))
    access_link = "http://example.com/access/" + token
    return access_link


def display_payment_portal(selected_items):
    total_price = sum([int(item['price'].split()[0]) for item in selected_items])

    layout = [
        [sg.Text('Payment Portal', font=('Helvetica', 20))],
        [sg.Text('Selected Items:', font=('Helvetica', 14))],
        [sg.Listbox(values=[f"{item['title']} ({item['price']})" for item in selected_items], size=(60, 5), disabled=True)],
        [sg.Text(f'Total Price: {total_price} RS', font=('Helvetica', 14))],
        [sg.Text('Email:', size=(20, 1)), sg.Input(key='-EMAIL-', size=(30, 1))],
        [sg.Button('Make Payment (Paytm)')]
    ]

    window = sg.Window('Payment Portal', layout, element_justification='center')

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED:
            break

        if event == 'Make Payment (Paytm)':
            user_email = values['-EMAIL-']
            access_link = generate_access_token()
            send_access_link_email(user_email, access_link)
            sg.popup('Payment successful! An email with the access link has been sent to your email address.')
            break

    window.close()

def create_stripe_payment(access_link, total_price):
    try:
        # Create a Stripe Checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'RSS Feeds Access',
                    },
                    'unit_amount': total_price * 100,  # Convert to cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=access_link,
            cancel_url='http://example.com/cancel',  # Update with your cancel URL
        )

        # Redirect to the Stripe Checkout page
        stripe.open(session.url)
        return True
    except Exception as e:
        return False


def send_otp_email(email, otp):
    sender_email = 'chenchusasanksasi99@gmail.com'  # Replace with your own Gmail address
    sender_password = 'gnsjdzptydnxxkjj'  # Replace with your own Gmail password
    receiver_email = email

    message = MIMEMultipart("alternative")
    message["Subject"] = "OTP Verification"
    message["From"] = sender_email
    message["To"] = receiver_email

    text = f"Your OTP: {otp}"
    html = f"<html><body><p>Your OTP: {otp}</p></body></html>"

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())


def send_access_link_email(email, access_link):
    sender_email = 'chenchusasanksasi99@gmail.com'
    sender_password = 'gnsjdzptydnxxkjj'
    receiver_email = email

    message = MIMEMultipart("alternative")
    message["Subject"] = "Access Link"
    message["From"] = sender_email
    message["To"] = receiver_email

    text = f"Click the following link to access your purchased RSS feeds: {access_link}"
    html = f"<html><body><p>Click the following link to access your purchased RSS feeds:</p><p><a href='{access_link}'>{access_link}</a></p></body></html>"

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())


def register():
    layout = [
        [sg.Text('Register', font=('Helvetica', 20))],
        [sg.Text('Email:', size=(20, 1)), sg.Input(key='-EMAIL-', size=(30, 1))],
        [sg.Text('Password:', size=(20, 1)), sg.Input(key='-PASSWORD-', size=(30, 1), password_char='*')],
        [sg.Text('Phone number:', size=(20, 1)), sg.Input(key='-PHONE-', size=(30, 1))],
        [sg.Text('Driving license or passport number:', size=(20, 1)), sg.Input(key='-DOCUMENT-', size=(30, 1))],
        [sg.Text('DOB:', size=(20, 1)), sg.Input(key='-DOB-', size=(30, 1))],
        [sg.Button('Register'), sg.Button('Cancel')]
    ]

    window = sg.Window('Register', layout, element_justification='center')

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == 'Cancel':
            break

        email = values['-EMAIL-']
        password = values['-PASSWORD-']
        phone = values['-PHONE-']
        document = values['-DOCUMENT-']
        dob = values['-DOB-']

        otp_secret = pyotp.random_base32()

        # Generate OTP and send it to user's email
        otp = pyotp.TOTP(otp_secret, interval=300)
        send_otp_email(email, otp.now())

        # Store user information
        users[email] = {'password': password, 'phone': phone, 'document': document, 'dob': dob, 'otp_secret': otp_secret}

        # Verify OTP
        layout = [
            [sg.Text('OTP Verification', font=('Helvetica', 20))],
            [sg.Text('Enter the OTP sent to your email:', size=(40, 1))],
            [sg.Input(key='-OTP-', size=(30, 1))],
            [sg.Button('Verify')]
        ]

        window2 = sg.Window('OTP Verification', layout, element_justification='center')

        while True:
            event2, values2 = window2.read()

            if event2 == sg.WINDOW_CLOSED:
                break

            if event2 == 'Verify':
                entered_otp = values2['-OTP-']

                if otp.verify(entered_otp):
                    window2.close()
                    window.close()
                    return True
                else:
                    sg.popup('Invalid OTP. Please try again.')

        window2.close()

    window.close()
    return False


def login():
    layout = [
        [sg.Text('Login', font=('Helvetica', 20))],
        [sg.Text('Email:', size=(20, 1)), sg.Input(key='-EMAIL-', size=(30, 1))],
        [sg.Text('Password:', size=(20, 1)), sg.Input(key='-PASSWORD-', size=(30, 1), password_char='*')],
        [sg.Button('Login'), sg.Button('Cancel')]
    ]

    window = sg.Window('Login', layout, element_justification='center')

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == 'Cancel':
            break

        email = values['-EMAIL-']
        password = values['-PASSWORD-']

        if email in users and users[email]['password'] == password:
            window.close()
            return True
        else:
            sg.popup('Invalid email or password. Please try again.')

    window.close()
    return False


def main_menu():
    layout = [
        [sg.Text('Main Menu', font=('Helvetica', 20))],
        [sg.Button('View RSS Feeds'), sg.Button('Logout')]
    ]

    window = sg.Window('Main Menu', layout, element_justification='center')

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == 'Logout':
            break

        if event == 'View RSS Feeds':
            feed_items = fetch_rss_feeds()
            selected_items = display_rss_feeds(feed_items)
            display_payment_portal(selected_items)

    window.close()


def start_program():
    layout = [
        [sg.Text('Welcome to RSS Reader', font=('Helvetica', 20))],
        [sg.Button('Login'), sg.Button('Register')]
    ]

    window = sg.Window('RSS Reader', layout, element_justification='center')

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED:
            break

        if event == 'Login':
            if login():
                main_menu()

        if event == 'Register':
            if register():
                main_menu()

    window.close()


if __name__ == "__main__":
    start_program()
