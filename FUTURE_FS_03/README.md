# The Rose Atelier — Boutique Website

A full-stack, elegant boutique website built with **Python Flask** and **JSON-based storage**, designed as a "Local Business Website" mini-project deliverable. Built for a fictional boutique selling clothing, accessories, and gifts, with a complete shopping cart system.

---

## 1. Project Title
**The Rose Atelier — Luxury Boutique E-Commerce Website**

---

## 2. Aim
To design and build a professional, visually polished website for a local boutique business, demonstrating real-world web development skills including front-end design, back-end logic, and session-based shopping cart functionality — suitable as a live pitch project to a real business owner.

---

## 3. Abstract
This project simulates a complete boutique storefront for "The Rose Atelier," a fictional shop selling clothing, accessories, and gifts. It includes a home page, brand story, full shop catalog with category filtering, a styled lookbook gallery, a journal/blog section, a fully functional shopping cart (add/update/remove, session-persisted), and a contact page with a working enquiry form. All data — products, blog posts, gallery captions, and contact messages — is stored in JSON files, requiring no database setup.

---

## 4. Introduction
Many local boutique owners rely on word-of-mouth and in-person visits alone, missing the credibility and reach a professional website provides. This project demonstrates how a small retail business — clothing, accessories, or gift shop — can present itself online with a premium look and a functioning product browsing/cart experience, without needing complex infrastructure.

---

## 5. Problem Statement
Local boutiques often can't justify the cost of a custom-built e-commerce platform, yet a generic template fails to capture their brand's personality. This project shows that a lightweight Flask + JSON stack can deliver a distinctive, on-brand storefront experience at low cost and complexity.

---

## 6. Objectives
- Build a polished, brand-specific visual identity (not a generic template look)
- Provide full product browsing with category filtering
- Implement a working shopping cart (add, update quantity, remove, clear)
- Provide brand storytelling pages (About, Lookbook, Journal)
- Provide a working contact form that stores enquiries
- Ensure full responsiveness across desktop, tablet, and mobile
- Deliver clean, well-commented, beginner-friendly code

---

## 7. Technologies Used

| Layer        | Technology                          |
|--------------|--------------------------------------|
| Backend      | Python 3.9+, Flask 3.x               |
| Frontend     | HTML5, CSS3 (custom, no framework), JavaScript (ES6) |
| Storage      | JSON files (no database)             |
| Session      | Flask server-side sessions (cart)    |
| Fonts        | Google Fonts — Cormorant & Jost      |
| Icons        | Hand-drawn inline SVG (no external icon library) |

---

## 8. Features

### Pages
- **Home** — animated hero, bestseller products, brand story teaser, value strip
- **About** — full boutique story, mission, founder's note
- **Shop** — full catalog with category filter (clothing / accessories / gifts)
- **Lookbook (Gallery)** — styled photo grid showcase
- **Journal (Blog)** — style tip articles with individual post pages
- **Contact** — visit info, working contact form, map placeholder, social links
- **Cart** — live item list, quantity adjustment, remove/clear, running total

### Functionality
- Add to cart via AJAX (no page reload) with toast confirmation
- Live quantity +/- controls on the cart page (AJAX-updated totals)
- Remove individual items or clear the whole cart
- Cart count badge in navigation updates live
- Category filter pills on the shop page
- Contact form validates and stores messages to JSON
- Scroll-triggered fade-in animations and a signature "ribbon" underline on headings
- Fully responsive: collapses to a mobile drawer navigation under 768px

---

## 9. Folder Structure

```
rose-atelier/
├── app.py                    # Flask application & all routes
├── requirements.txt          # Python dependencies
├── README.md                 # This file
│
├── data/
│   ├── products.json         # Full product catalog
│   ├── blog.json             # Journal/style-tip articles
│   ├── gallery.json          # Lookbook image captions
│   └── messages.json         # Contact form submissions
│
├── templates/
│   ├── base.html              # Shared layout: nav, footer, mobile drawer
│   ├── icons.html              # Reusable inline-SVG icon macros
│   ├── index.html              # Homepage
│   ├── about.html              # About / brand story page
│   ├── shop.html                # Product catalog + filter
│   ├── gallery.html            # Lookbook page
│   ├── blog.html                # Journal listing page
│   ├── blog_post.html           # Single article view
│   ├── contact.html             # Contact page + form
│   └── cart.html                 # Shopping cart page
│
└── static/
    ├── css/
    │   └── style.css          # Full design system & styles
    └── js/
        └── script.js           # Cart AJAX, nav, scroll animations
```

---

## 10. Data Structures Used

### `products.json` — Array of product objects
```json
{
  "id": "p001",
  "name": "Blush Silk Wrap Dress",
  "category": "clothing",
  "price": 4899,
  "image": "dress1.jpg",
  "description": "...",
  "tag": "Bestseller"
}
```

### `messages.json` — Array of contact form submissions
```json
{
  "name": "Anaya Rao",
  "email": "anaya@example.com",
  "message": "...",
  "received_at": "2026-06-19T00:25:39"
}
```

### Cart (Flask session, not a file)
```python
session["cart"] = { "p001": 2, "p104": 1 }   # {product_id: quantity}
```

**Data structures used internally:**
- Python `dict` — cart storage (`{product_id: quantity}`)
- Python `list` — products, blog posts, gallery items, messages
- List comprehensions — category filtering, featured-product selection
- `next()` with generator expression — single-item lookups by ID

---

## 11. System Architecture

```
Browser
  │
  ▼
Flask Routes (app.py)
  │
  ├── GET  /, /about, /shop, /gallery, /blog, /blog/<id>, /contact
  │        → render_template() with data read from JSON
  │
  ├── POST /contact
  │        → validates input → appends to messages.json
  │
  └── Cart Routes (session-based, AJAX-friendly)
       ├── POST /cart/add      → adds/increments item in session["cart"]
       ├── POST /cart/update   → sets item quantity (or removes if 0)
       ├── POST /cart/remove   → deletes item from session["cart"]
       ├── POST /cart/clear    → empties session["cart"]
       └── GET  /cart          → renders cart with live totals
```

---

## 12. Working Flow

1. Visitor lands on the Home page and sees bestseller products
2. Visitor browses the Shop page, optionally filtering by category
3. Visitor clicks "Add to Cart" — handled via AJAX, cart badge updates instantly
4. Visitor opens the Cart page, adjusts quantities or removes items
5. Cart totals recalculate live via AJAX without a page reload
6. Visitor reads the About page or Journal articles for brand context
7. Visitor sends an enquiry via the Contact form to complete their order
   (no real payment gateway — by design, per project scope)
8. Message is saved to `messages.json` for the boutique owner to review

---

## 13. Algorithm Explanation

### Cart Total Calculation
```python
def cart_details():
    cart = get_cart()                      # {product_id: quantity}
    products = read_json(PRODUCTS_FILE)
    items, total_price, total_items = [], 0, 0

    for product_id, qty in cart.items():
        product = next((p for p in products if p["id"] == product_id), None)
        if product:
            line_total = product["price"] * qty
            items.append({**product, "quantity": qty, "line_total": line_total})
            total_price += line_total
            total_items += qty

    return items, total_price, total_items
```
This iterates the cart dictionary, looks up full product details for each ID,
computes a line total, and accumulates the cart-wide total and item count.

### Category Filtering (Shop page)
```python
if category != "all":
    filtered = [p for p in products if p["category"] == category]
else:
    filtered = products
```
A simple list comprehension filters the full catalog by the `category`
query parameter from the URL.

### Scroll-Reveal Animation
JavaScript's `IntersectionObserver` watches elements with the
`.fade-in-scroll` or `.ribbon-heading` class, adding an `.in-view` class
the moment they enter the viewport — triggering a CSS transition.

---

## 14. UI/UX Design Explanation

The design system uses a **blush pink, rose gold, and ivory** palette to express
"elegant and luxurious" without leaning on dark, heavy materials. Two typefaces
are paired deliberately: **Cormorant** (a high-contrast display serif) for
headings, and **Jost** (a clean geometric sans) for body text and UI labels —
giving the page an editorial, boutique-catalog feel rather than a generic
template look.

The signature visual device is the **"ribbon" underline**: section headings
draw an animated gold-to-rose line beneath themselves on scroll, echoing the
ribbon used in the boutique's own gift-wrapping — a detail tied directly to
the brand's identity rather than a decorative default.

Product cards use thin rose-gold corner brackets on hover, referencing a
jewelry display case rather than a generic shadow-elevated card.

---

## 15. Security Features

- Server-side input validation on the contact form before writing to JSON
- Jinja2 auto-escaping prevents XSS in all rendered templates
- Cart state stored server-side in Flask's signed session cookie (not exposed as raw client data)
- POST-only mutation routes (add/update/remove/clear) — never GET

---

## 16. Gamification Explanation
*(Not applicable to this project — The Rose Atelier is a boutique storefront, not a wellness/engagement platform. No gamification elements were required per the task brief.)*

---

## 17. Emotional Analysis System
*(Not applicable to this project — see note above. This boutique site focuses on brand storytelling and shopping experience rather than emotional/wellness tracking.)*

---

## 18. Advantages
- Zero database dependency — runs anywhere Python runs
- Clean, distinctive visual identity instead of a generic e-commerce template
- Fully functional cart experience without payment gateway complexity
- Fast to deploy and demo for a live pitch to a real business owner
- Codebase is small enough to walk through fully in a presentation

---

## 19. Limitations
- No real payment gateway (by design — for a college mini-project)
- No user accounts or order history persistence beyond the session
- No image upload system — placeholder SVG illustrations used in place of real photography
- JSON storage is not suitable for high-traffic production use

---

## 20. Future Scope
- Replace JSON storage with SQLite/PostgreSQL for persistence across sessions
- Integrate a real payment gateway (Razorpay/Stripe) for genuine checkout
- Add user accounts with order history
- Add real product photography
- Add an admin panel for the boutique owner to manage products directly
- Add email notifications for new contact form submissions

---

## 21. Conclusion
This project demonstrates a complete, deployable boutique website — covering brand storytelling, product browsing, cart management, and customer contact — all built without a database, using a clean Flask + JSON architecture. It's designed to be both a strong academic submission and a credible live pitch to a real local boutique owner, showing concretely how a professional website can expand their reach and credibility.

---

## 22. How to Run the Project

### Prerequisites
- Python 3.9 or higher
- pip

### Steps

```bash
# 1. Navigate into the project folder
cd rose-atelier

# 2. (Optional) Create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python app.py

# 5. Open in browser
#    http://127.0.0.1:5000
```

No login or setup is required — the site is public-facing by design.