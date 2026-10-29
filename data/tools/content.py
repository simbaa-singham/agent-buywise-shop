"""Written knowledge content (ADR-033), from data/knowledge/_outline/policy_outline.md.

Each document is a list of blocks: ("h1"|"h2"|"p"|"ul"|"ol"|"table", payload).
Renderers in build_documents.py turn the same blocks into DOCX, PDF, HTML, Markdown, etc.
"""

STORE_NAME = "BuyWise"

# ---------------------------------------------------------------- policies
SHIPPING_COMMON = [
    ("h2", "Where we ship"),
    ("p", "We ship to addresses in the United States only. Orders to the 48 contiguous states use the "
          "standard delivery times below. Alaska and Hawaii have longer delivery times and same-day "
          "delivery is not available there. We do not ship internationally."),
    ("h2", "Delivery methods"),
    ("table", [["Method", "Delivery time", "Cost"],
               ["Standard", "3-5 business days", "{standard_cost}"],
               ["Express", "1-2 business days", "$14.99"],
               ["Same-day", "Same day, if ordered by 12 pm local time", "$9.99"]]),
    ("p", "Same-day delivery is available only for addresses within 20 miles of a BuyWise store."),
    ("h2", "Alaska and Hawaii"),
    ("table", [["Method", "Delivery time"], ["Standard", "5-8 business days"], ["Express", "2-4 business days"],
               ["Same-day", "Not available"]]),
    ("h2", "Signatures and PO boxes"),
    ("ul", ["A signature is required for orders over $500.",
            "We cannot deliver orders over $1,000 to a PO box. Please use a street address.",
            "Orders up to $1,000 may be delivered to a PO box using Standard delivery."]),
    ("h2", "Missed deliveries"),
    ("p", "The carrier makes 3 delivery attempts. After the third attempt the package is held at the "
          "carrier's local facility for 5 days. If it is not collected, it is returned to us and the order "
          "is cancelled; the payment authorization or charge is released."),
    ("h2", "Tracking"),
    ("p", "You receive a tracking number by email and in your order details as soon as your order ships. "
          "You can also ask the BuyWise assistant for your order status at any time."),
]


def shipping_policy(version):
    v1 = version == 1
    blocks = [("h1", f"Shipping and Delivery Policy (version {version})"),
              ("p", f"Effective date: {'January 1, 2026' if v1 else 'November 15, 2026'}. "
                    + ("This version replaces all earlier shipping terms." if v1 else
                       "This version replaces version 1 (effective January 1, 2026). The only change is the "
                       "free Standard shipping threshold, which rises from $50 to $75."))]
    cost = "Free on orders over $50; otherwise $5.99" if v1 else "Free on orders over $75; otherwise $5.99"
    for kind, payload in SHIPPING_COMMON:
        if kind == "table":
            payload = [[c.replace("{standard_cost}", cost) for c in row] for row in payload]
        blocks.append((kind, payload))
    return blocks


PICKUP = [
    ("h1", "In-Store Pickup Policy"),
    ("p", "Effective date: January 1, 2026. In-store pickup is free at every BuyWise store."),
    ("h2", "When your order is ready"),
    ("ul", ["If the item is in stock at the store you choose, it is usually ready within 2 hours.",
            "If the item has to be transferred from another store, it is ready in 2-4 days.",
            "We notify you by email and text when your order is ready for pickup."]),
    ("h2", "How long we hold your order"),
    ("p", "We hold pickup orders for 7 days from the day they are ready. After 7 days the order is "
          "cancelled and the payment authorization is released. You will not be charged for an order "
          "that is not picked up."),
    ("h2", "Who can pick up"),
    ("ul", ["The person named on the order, with a valid photo ID.",
            "One alternate pickup person, if you named them at checkout. They must bring a valid photo ID.",
            "To change the alternate pickup person after checkout, contact our staff."]),
    ("h2", "Pickup hours"),
    ("p", "You can pick up during store opening hours, until 30 minutes before the store closes. "
          "Regular hours are Monday to Saturday 10 am to 9 pm and Sunday 11 am to 6 pm; see the holiday "
          "hours notice for exceptions."),
]

ORDERS = [
    ("h1", "Order Changes, Cancellations and Limits"),
    ("p", "Effective date: January 1, 2026."),
    ("h2", "Changing or cancelling an order"),
    ("p", "You can change or cancel an order yourself while its status is Placed, which is usually about "
          "the first 30 minutes after you order. Once an order is Processing, it can no longer be changed "
          "online; our staff can help, but changes are not guaranteed. Shipped orders cannot be cancelled."),
    ("h2", "Quantity limits"),
    ("table", [["Category", "Maximum per order"], ["Phones (same model)", "2"], ["Tablets", "5"],
               ["Laptops", "5"], ["Watches", "5"], ["Audio", "5"], ["Accessories", "5"]]),
    ("p", "The phone limit applies per model: for example, you can order two iPhone 18 Pro and two "
          "iPhone 17 in the same order, but not three iPhone 18 Pro."),
    ("h2", "Order statuses"),
    ("table", [["Status", "What it means"],
               ["Placed", "We received your order; it can still be changed or cancelled."],
               ["Processing", "We are preparing your order; changes need staff help."],
               ["Shipped", "Your order left our warehouse; a tracking number is available."],
               ["Out for delivery", "The carrier is delivering your order today."],
               ["Delivered", "The carrier confirmed delivery."],
               ["Ready for pickup", "Your order is waiting at the store for 7 days."],
               ["Picked up", "You collected your order."],
               ["Delayed", "Your order is late; we are working with the carrier and will update you."],
               ["Cancelled", "The order was cancelled and any payment authorization released."]]),
]

PAYMENT = [
    ("h1", "Payment Policy"),
    ("p", "Effective date: January 1, 2026."),
    ("h2", "Accepted payment methods"),
    ("p", "We accept credit cards, debit cards and digital wallets. You pay through a secure payment link; "
          "BuyWise and the shopping assistant never see or store your full card details."),
    ("h2", "Payment links"),
    ("ul", ["A payment link expires 30 minutes after it is created.",
            "If your link expires, ask the assistant or our staff for a new link. Your cart is kept.",
            "Never share a payment link with anyone else."]),
    ("h2", "When you are charged"),
    ("p", "Your payment is authorized when you place the order and charged when the order ships or when "
          "you pick it up. If an order is cancelled before it ships or is picked up, the authorization is "
          "released."),
    ("h2", "Sales tax"),
    ("p", "Sales tax is calculated from the delivery address. For in-store pickup, the sales tax of the "
          "store's state and city applies instead."),
    ("h2", "Not offered"),
    ("ul", ["Financing or installment plans", "Gift cards", "Splitting one order across several payment methods"]),
]

PRICING = [
    ("h1", "Pricing Policy"),
    ("p", "Effective date: January 1, 2026."),
    ("p", "Prices may change at any time. The price shown when you place your order is the price you pay; "
          "later price changes, up or down, do not affect orders already placed."),
    ("p", "We do not offer price matching with other retailers."),
    ("p", "Current prices are always shown on the product page and by the assistant, which reads them "
          "live from our catalog. Prices printed in old emails, notices or help articles may be out of date."),
]

WARRANTY = [
    ("h1", "Warranty Policy"),
    ("p", "Effective date: January 1, 2026. Every product sold by BuyWise comes with the manufacturer's "
          "1-year limited warranty, starting on the date of delivery or pickup."),
    ("h2", "What is covered"),
    ("table", [["Covered", "Not covered"],
               ["Defects in materials and workmanship", "Accidental damage, such as drops and cracked screens"],
               ["Battery that fails under normal use", "Liquid damage"],
               ["Faulty buttons, ports and speakers", "Cosmetic wear, scratches and dents"],
               ["Included accessories with defects", "Damage from unauthorized repairs or modifications"]]),
    ("h2", "How to make a warranty claim"),
    ("ol", ["Contact BuyWise staff through the assistant (ask for a person) or in a store.",
            "Have your order number and the product's serial number ready.",
            "Staff check the warranty dates and help you start the claim with the manufacturer."]),
    ("p", "The shopping assistant can explain what the warranty covers, but it cannot start or process a "
          "warranty claim. It will connect you with our staff instead."),
    ("h2", "Your consumer rights"),
    ("p", "This warranty is in addition to any rights you have under the consumer protection laws of your state."),
]

PRIVACY = [
    ("h1", "Privacy Policy"),
    ("p", "Effective date: January 1, 2026."),
    ("h2", "What we collect"),
    ("ul", ["Your name, email address, phone number and delivery address",
            "Your orders and support tickets",
            "Your conversations with the BuyWise shopping assistant"]),
    ("p", "We never collect or store full card numbers; payments go through a secure payment provider."),
    ("h2", "How long we keep your data"),
    ("table", [["Data", "Kept for"], ["Chat transcripts", "90 days, then deleted or anonymized"],
               ["Orders", "7 years, for accounting; your identity can be removed on request"],
               ["Account profile", "Until you delete your account"]]),
    ("h2", "Your rights"),
    ("p", "You can ask for a copy of your data or for your account to be deleted. Contact our staff "
          "through the assistant or in a store. Deletion removes your profile, conversations and tickets; "
          "orders are kept for accounting without your identity. Copies in our backups are removed within 30 days."),
    ("h2", "How we protect your data"),
    ("p", "Contact details are encrypted, staff see them masked by default, and every time staff reveal "
          "full details it is recorded. The assistant removes personal details before processing your messages."),
]

ACCOUNTS = [
    ("h1", "Accounts and Guest Checkout"),
    ("p", "Effective date: January 1, 2026."),
    ("h2", "Guest checkout"),
    ("p", "You can buy without creating an account. To check the status of a guest order, the assistant "
          "sends a one-time code to the email address or phone number on the order."),
    ("h2", "One-time codes"),
    ("ul", ["A code is valid for 10 minutes.", "You have 3 attempts to enter it.",
            "After 3 wrong attempts, you must wait 15 minutes before requesting a new code.",
            "BuyWise staff will never ask you to read a code out to them."]),
    ("h2", "Accounts"),
    ("p", "With an account you can see all your orders, save addresses and chat with the assistant without "
          "verifying each time. If you start chatting as a guest and then sign in, your conversation continues."),
]

RETURNS = [
    ("h1", "Returns, Exchanges, Refunds and Trade-ins"),
    ("p", "Effective date: January 1, 2026."),
    ("p", "The BuyWise shopping assistant does not handle returns, exchanges, refunds or trade-ins. "
          "If you want to return or exchange a product, ask the assistant to connect you with our staff, "
          "or visit any BuyWise store. Staff will explain the options for your order."),
    ("p", "BuyWise does not currently offer a trade-in program."),
]

SUPPORT = [
    ("h1", "Support and Talking to a Person"),
    ("p", "Effective date: January 1, 2026."),
    ("p", "BuyWise staff are available in chat from 8 am to 10 pm Eastern Time, every day. Ask the "
          "assistant for a person at any time. Outside those hours, the assistant creates a support ticket "
          "and our staff reply the next day."),
    ("p", "The assistant also offers to connect you with staff when it cannot answer a question, when a "
          "request is outside what it can do (for example returns or warranty claims), or when you seem frustrated."),
]

POLICY_UPDATE_EMAIL = (
    "Hello BuyWise team,\n\n"
    "From November 15, 2026, the free Standard shipping threshold changes from $50 to $75. "
    "All other shipping terms stay the same. The updated policy (version 2) is attached.\n\n"
    "Until November 15, version 1 applies: Standard shipping is free on orders over $50.\n\n"
    "Please make sure customers are told the threshold that applies on the day they order.\n\n"
    "BuyWise Policy Team"
)

HOLIDAY_NOTICE = [
    "BUYWISE - HOLIDAY HOURS 2026",
    "All stores",
    "Thanksgiving Day, Thu Nov 26: CLOSED",
    "Black Friday, Fri Nov 27: 8 am - 10 pm",
    "Sat Nov 28 - Sun Nov 29: regular hours",
    "Christmas Eve, Thu Dec 24: 10 am - 4 pm",
    "Christmas Day, Fri Dec 25: CLOSED",
    "New Year's Eve, Thu Dec 31: 10 am - 6 pm",
    "New Year's Day, Fri Jan 1, 2027: CLOSED",
    "Pickup orders: last pickup 30 min before closing.",
    "Online orders and chat stay open on all days.",
]

RATE_CARD = [
    "BUYWISE SHIPPING RATE CARD",
    "Effective Jan 1, 2026 (policy v1)",
    "STANDARD  3-5 days   FREE over $50, else $5.99",
    "EXPRESS   1-2 days   $14.99",
    "SAME-DAY  order by 12 pm   $9.99 (within 20 mi of a store)",
    "ALASKA / HAWAII: Standard 5-8 days, Express 2-4 days",
    "No same-day in AK / HI",
    "Signature required over $500",
    "No PO boxes over $1,000",
]

QUICK_TIPS = """BuyWise internal quick tips for store staff (plain text)
Last updated: 2026-10-01

- Pickup: check photo ID against the order name or the named alternate person.
- Pickup orders are held 7 days after they are ready, then cancelled automatically.
- Payment links expire after 30 minutes - send a new one, the cart is kept.
- Phones are limited to 2 per model per order. Other categories: 5.
- Returns and exchanges: the assistant hands these to staff. Use the store's returns process.
- Warranty: 1-year manufacturer warranty from delivery or pickup date. Accidental and liquid damage are not covered.
- Never ask a customer to read out their one-time code.
- Holiday hours are in the holiday notice; Thanksgiving and Christmas Day are closed.
"""

TRAINING_SLIDES = [
    ("Store pickup process", ["Staff training", "Applies to all BuyWise stores", "Version 2026-10"],
     "Welcome. This session covers the pickup process end to end. It takes about 15 minutes."),
    ("1. Order arrives", ["Order appears in the pickup queue with status Ready for pickup",
                          "In-stock items: prepare within 2 hours",
                          "Transferred items: 2-4 days, prepare on arrival"],
     "Prioritize orders by the ready time shown in the queue."),
    ("2. Customer arrives", ["Ask for the order number", "Check photo ID", "Name must match the order or the named alternate"],
     "If the name does not match and no alternate was named, do not release the order. Offer to contact staff support."),
    ("3. Hand over", ["Scan items to confirm the order", "Payment is captured at handover", "Status changes to Picked up"],
     "Payment was only authorized at order time; it is charged when the customer picks up."),
    ("Hold period and timing", ["Held 7 days after ready", "Then cancelled automatically, authorization released",
                                "Last pickup 30 minutes before closing"],
     "Remind customers who are near the end of the hold period."),
    ("Quick reference", None,
     "The table on this slide is the summary customers ask about most often."),
]
TRAINING_TABLE = [["Topic", "Rule"], ["Hold period", "7 days"], ["ID required", "Photo ID"],
                  ["Alternate person", "One, named at checkout"], ["Last pickup", "30 min before closing"]]

# ---------------------------------------------------------------- how-to guides
GUIDES = {
    "setup-new-phone": ("Set up your new phone and move your data", [
        "Charge your new phone and keep your old phone nearby with Bluetooth and Wi-Fi turned on.",
        "Turn on the new phone and follow the on-screen setup until you see the option to transfer data.",
        "Hold the old phone near the new one and follow the prompts to start a direct transfer.",
        "Keep both phones close together and connected to power until the transfer finishes.",
        "Sign in to your accounts and check that your apps, photos and messages arrived."]),
    "esim-setup": ("Set up an eSIM", [
        "Some models, such as iPhone Air, support eSIM only and have no physical SIM tray.",
        "During setup, choose to transfer your number from your old phone or scan your carrier's QR code.",
        "If your carrier is not listed, contact the carrier for an eSIM activation code.",
        "Restart the phone after activation and make a test call."]),
    "pair-earbuds": ("Pair your AirPods with a phone", [
        "Open the charging case next to your unlocked phone.",
        "Tap Connect on the setup card that appears on the phone.",
        "For AirPods Pro 3 and AirPods 4 with Active Noise Cancellation, choose a listening mode after pairing.",
        "If no card appears, press and hold the button on the case until the light flashes white, then try again."]),
    "pair-watch": ("Pair your watch with a phone", [
        "Turn on the watch by holding the side button until the logo appears.",
        "Hold the watch near your phone and wait for the pairing screen.",
        "Point the phone camera at the watch face to pair, then follow the prompts.",
        "Choose your band size settings and wrist preference, then let the watch sync."]),
    "magsafe-charging": ("Charge with MagSafe", [
        "Connect the MagSafe Charger to a USB-C power adapter of 30 W or more for the fastest wireless charging.",
        "Place the phone on the charger; the magnets align it automatically.",
        "MagSafe cases can stay on. Remove other thick cases, wallets or metal objects.",
        "Qi2 devices also charge on a MagSafe Charger, usually at lower power."]),
    "fast-wired-charging": ("Get the fastest wired charging", [
        "Use a USB-C cable and a USB-C power adapter.",
        "iPhone 18 Pro and iPhone 18 Pro Max support up to 60 W wired charging with a suitable adapter.",
        "Other phones charge fast with a 30-40 W adapter; a 20 W adapter still works, just slower.",
        "Charging slows down above 80% to protect the battery."]),
    "pencil-setup": ("Pair Pencil Pro or Pencil (USB-C) with a tablet", [
        "Pencil Pro pairs by attaching it magnetically to the side of a compatible tablet.",
        "Pencil Pro works with iPad Pro (M5), iPad Air (M4) and iPad mini (A17 Pro), but not with iPad (A16).",
        "Pencil (USB-C) pairs by connecting it to the tablet with a USB-C cable and works with every tablet we sell."]),
    "setup-tablet": ("Set up a new tablet", [
        "Turn on the tablet and choose your language and region.",
        "Join Wi-Fi and sign in with your account, or set up as new.",
        "Restore from a backup or transfer from another device if you have one.",
        "Turn on automatic updates in settings."]),
    "setup-laptop": ("Set up a new laptop", [
        "Connect the laptop to power and open the lid; it turns on automatically.",
        "Follow the setup assistant to join Wi-Fi and sign in.",
        "Use the migration assistant to move files from an older computer if needed.",
        "MacBook Pro 14-inch (M6) pre-orders ship from November 6, 2026."]),
    "track-order": ("Track your order", [
        "Ask the BuyWise assistant 'Where is my order?' and give your order number, for example BW-100002.",
        "Signed-in customers see all their orders; guests verify with a one-time code.",
        "When your order ships you receive a tracking number by email.",
        "If your order shows Delayed, staff are already working with the carrier."]),
    "change-pickup-person": ("Change who picks up your order", [
        "You can name one alternate pickup person at checkout.",
        "To change it later, ask the assistant to connect you with staff.",
        "The alternate person must bring a valid photo ID."]),
    "new-payment-link": ("Get a new payment link", [
        "Payment links expire after 30 minutes.",
        "Ask the assistant for a new payment link; your cart and prices at order time are kept.",
        "Open the link on your own device and complete payment there."]),
    "check-warranty": ("Check if your warranty covers a problem", [
        "Every product has a 1-year manufacturer warranty from the delivery or pickup date.",
        "Defects are covered; drops, cracked screens, liquid damage and cosmetic wear are not.",
        "To start a claim, ask the assistant to connect you with staff and have your order number ready."]),
}
GUIDES_AS_MARKDOWN = {"fast-wired-charging", "pencil-setup", "track-order", "new-payment-link", "check-warranty"}

# ---------------------------------------------------------------- written compatibility notes
COMPAT_NOTES = [
    ("Cases are model-specific", "A case fits exactly one phone model. A case for iPhone 18 Pro does not fit "
     "iPhone 18 Pro Max or iPhone 17, even though they look similar."),
    ("MagSafe and Qi2", "Phones with MagSafe or Qi2 charge on the MagSafe Charger. iPhone Duo is not listed "
     "as MagSafe compatible in our catalog; use USB-C."),
    ("Watch bands", "Bands come in two size groups. The smaller band fits 40 mm and 42 mm cases. The larger "
     "band fits 44 mm, 46 mm and 49 mm cases."),
    ("Pencils", "Pencil Pro does not work with iPad (A16). Pencil (USB-C) works with every tablet we sell."),
    ("Power adapters", "Any USB-C power adapter charges any USB-C device. Laptops and 60 W phones charge "
     "slowly on a 20 W adapter."),
    ("Laptops and MagSafe", "MagSafe 3 on laptops is a different connector from MagSafe phone charging; the "
     "phone MagSafe Charger does not charge laptops."),
]

# ---------------------------------------------------------------- policy FAQs (written)
FAQ_POLICY = {
    "shipping": [
        ("Do you ship outside the United States?", "No. We ship to US addresses only."),
        ("How long does Standard delivery take?", "3-5 business days in the 48 contiguous states."),
        ("Is shipping free?", "Standard shipping is free on orders over $50 (policy version 1, in force until November 14, 2026). From November 15, 2026 the threshold is $75. Otherwise Standard costs $5.99."),
        ("How much is Express delivery?", "$14.99, delivered in 1-2 business days."),
        ("Can I get same-day delivery?", "Yes, for $9.99, if you order by 12 pm local time and your address is within 20 miles of a BuyWise store."),
        ("Do you deliver to Alaska and Hawaii?", "Yes. Standard takes 5-8 business days and Express 2-4 business days. Same-day is not available."),
        ("Can I ship to a PO box?", "Yes for orders up to $1,000 using Standard delivery. Orders over $1,000 need a street address."),
        ("Will I need to sign for my delivery?", "Yes, if your order is over $500."),
        ("What happens if I miss my delivery?", "The carrier tries 3 times, then holds the package for 5 days. If it is not collected, it is returned and the order is cancelled."),
        ("When do I get a tracking number?", "As soon as your order ships, by email and in your order details."),
        ("Is the free shipping threshold changing?", "Yes. From November 15, 2026, Standard shipping is free on orders over $75 instead of $50."),
    ],
    "pickup": [
        ("Is in-store pickup free?", "Yes, pickup is always free."),
        ("How soon can I pick up my order?", "Usually within 2 hours if the item is in stock at your store, or in 2-4 days if it is transferred from another store."),
        ("How long will the store hold my order?", "7 days from the day it is ready. After that it is cancelled and you are not charged."),
        ("Can someone else pick up my order?", "Yes, one alternate person named at checkout, with a valid photo ID."),
        ("Can I change the pickup person after ordering?", "Yes, ask the assistant to connect you with staff."),
        ("What do I need to bring?", "Your order number and a valid photo ID."),
        ("Until what time can I pick up?", "Until 30 minutes before the store closes."),
        ("What are the store hours?", "Monday to Saturday 10 am to 9 pm, Sunday 11 am to 6 pm. Holiday hours differ; see the holiday notice."),
        ("Are stores open on Thanksgiving?", "No. All stores are closed on Thanksgiving Day, November 26, 2026."),
        ("What are the Black Friday hours?", "8 am to 10 pm on Friday, November 27, 2026."),
    ],
    "orders": [
        ("Can I cancel my order?", "Yes, while it is Placed, usually the first 30 minutes. After that, staff can help but changes are not guaranteed. Shipped orders cannot be cancelled."),
        ("Can I change my delivery address after ordering?", "Only while the order is Placed. After that, contact staff."),
        ("How many phones can I buy in one order?", "Up to 2 of the same phone model per order."),
        ("How many tablets or accessories can I order?", "Up to 5 per category per order."),
        ("What does Processing mean?", "We are preparing your order; it can no longer be changed online."),
        ("What does Delayed mean?", "Your order is late and we are working with the carrier. We will update you."),
        ("What does Ready for pickup mean?", "Your order is waiting at the store for 7 days."),
        ("How do I check my order status?", "Ask the assistant with your order number. Guests verify with a one-time code."),
        ("Can I order a product that is out of stock?", "Out-of-stock items cannot be ordered. Ask the assistant to check another store for pickup."),
        ("Can I pre-order the MacBook Pro 14-inch (M6)?", "Yes. Pre-orders opened on October 28, 2026 and orders ship from November 6, 2026."),
    ],
    "payment": [
        ("What payment methods do you accept?", "Credit cards, debit cards and digital wallets, through a secure payment link."),
        ("My payment link expired. What do I do?", "Ask for a new link. Links expire after 30 minutes and your cart is kept."),
        ("When will I be charged?", "Your payment is authorized at order time and charged when the order ships or is picked up."),
        ("How is sales tax calculated?", "From your delivery address, or from the store's location for pickup."),
        ("Do you offer financing?", "No, financing and installment plans are not offered."),
        ("Can I use a gift card?", "No, gift cards are not accepted."),
        ("Can I split payment between two cards?", "No, each order uses one payment method."),
        ("Does the assistant see my card number?", "No. Payment happens on a secure payment page; BuyWise never stores full card numbers."),
        ("Do you price match?", "No, we do not offer price matching."),
        ("If the price drops after I order, do I get the lower price?", "No. You pay the price shown when you placed the order."),
    ],
    "warranty": [
        ("What warranty do products have?", "The manufacturer's 1-year limited warranty from the delivery or pickup date."),
        ("Is a cracked screen covered?", "No. Accidental damage such as drops and cracked screens is not covered."),
        ("Is water damage covered?", "No, liquid damage is not covered."),
        ("Is a faulty battery covered?", "Yes, if it fails under normal use within the warranty period."),
        ("How do I make a warranty claim?", "Ask the assistant to connect you with staff, or visit a store, with your order number and serial number."),
        ("Can the assistant process my warranty claim?", "No. It explains coverage and connects you with staff to start the claim."),
        ("Are scratches covered?", "No, cosmetic wear such as scratches and dents is not covered."),
    ],
    "account": [
        ("Do I need an account to buy?", "No, guest checkout is available."),
        ("How do guests check order status?", "With a one-time code sent to the email or phone on the order."),
        ("How long is a one-time code valid?", "10 minutes, with 3 attempts."),
        ("I entered the wrong code three times. What now?", "Wait 15 minutes, then request a new code."),
        ("Will staff ask me for my code?", "No. BuyWise staff never ask you to read out a one-time code."),
        ("How long do you keep chat transcripts?", "90 days, then they are deleted or anonymized."),
        ("Can I delete my account?", "Yes. Ask staff; your profile, conversations and tickets are deleted and orders are kept without your identity."),
        ("Can I get a copy of my data?", "Yes, ask our staff for a data export."),
        ("Can I return a product?", "The assistant does not handle returns. Ask to be connected with staff or visit a store."),
        ("Do you offer trade-ins?", "No, there is no trade-in program."),
        ("When can I talk to a person?", "Staff are available in chat 8 am to 10 pm Eastern Time daily; outside those hours a ticket is created and staff reply the next day."),
    ],
}

# Deliberate price-cleaning tests (ADR-034): product prices inside help pages must be stripped at ingestion.
PRICE_LEAK_BANNER = "New: iPhone 18 Pro - from $1,199. iPhone Duo - from $1,999. Limited stock available now!"
PRICE_LEAK_ANSWER = ("What is the cheapest phone?", "The iPhone 17e is our entry phone and starts at $699 for 256GB.")
