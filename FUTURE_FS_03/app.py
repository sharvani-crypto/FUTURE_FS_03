"""
The Rose Atelier — Boutique Website
=====================================
A full-stack Flask e-commerce-style website for a luxury boutique
selling clothing, accessories, and gifts.

Tech: Python Flask + JSON storage + session-based cart
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from datetime import datetime
import json
import os

app = Flask(__name__)
app.secret_key = "rose_atelier_secret_key_2026"

# ─── Data file paths ───────────────────────────────────────────────────────
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
DATA_DIR      = os.path.join(BASE_DIR, "data")
PRODUCTS_FILE = os.path.join(DATA_DIR, "products.json")
BLOG_FILE     = os.path.join(DATA_DIR, "blog.json")
GALLERY_FILE  = os.path.join(DATA_DIR, "gallery.json")
MESSAGES_FILE = os.path.join(DATA_DIR, "messages.json")

# ─── JSON helpers ──────────────────────────────────────────────────────────
def read_json(filepath):
    """Read and return parsed JSON from a file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def write_json(filepath, data):
    """Write data as formatted JSON to a file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ─── Helpers ──────────────────────────────────────────────────────────────
def get_product_by_id(product_id):
    """Find a single product by its ID."""
    products = read_json(PRODUCTS_FILE)
    return next((p for p in products if p["id"] == product_id), None)

def get_cart():
    """Get the current session's cart dict: {product_id: quantity}."""
    return session.get("cart", {})

def save_cart(cart):
    """Persist cart dict back to session."""
    session["cart"] = cart

def cart_details():
    """
    Build a detailed cart list with product info, quantity, and line total.
    Returns (items, total_price, total_items)
    """
    cart = get_cart()
    products = read_json(PRODUCTS_FILE)
    items = []
    total_price = 0
    total_items = 0

    for product_id, qty in cart.items():
        product = next((p for p in products if p["id"] == product_id), None)
        if product:
            line_total = product["price"] * qty
            items.append({
                **product,
                "quantity": qty,
                "line_total": line_total
            })
            total_price += line_total
            total_items += qty

    return items, total_price, total_items

def cart_count():
    """Total number of items (sum of quantities) in cart — for nav badge."""
    cart = get_cart()
    return sum(cart.values())

# Make cart_count available in all templates automatically
@app.context_processor
def inject_cart_count():
    return {"nav_cart_count": cart_count()}

# ══════════════════════════════════════════════════════════════════════════
#  PAGE ROUTES
# ══════════════════════════════════════════════════════════════════════════

@app.route("/")
def home():
    """Homepage — hero, featured products, brand story teaser."""
    products = read_json(PRODUCTS_FILE)
    featured = [p for p in products if p.get("tag") == "Bestseller"][:4]
    return render_template("index.html", featured=featured)

@app.route("/about")
def about():
    """About page — boutique story, mission, founder note."""
    return render_template("about.html")

@app.route("/shop")
def shop():
    """Shop page — full catalog with category filter."""
    products = read_json(PRODUCTS_FILE)
    category = request.args.get("category", "all")

    if category != "all":
        filtered = [p for p in products if p["category"] == category]
    else:
        filtered = products

    return render_template("shop.html", products=filtered, active_category=category)

@app.route("/gallery")
def gallery():
    """Lookbook gallery page — styled photo grid."""
    images = read_json(GALLERY_FILE)
    return render_template("gallery.html", images=images)

@app.route("/blog")
def blog():
    """Blog listing page — style tip articles."""
    posts = read_json(BLOG_FILE)
    posts_sorted = sorted(posts, key=lambda p: p["date"], reverse=True)
    return render_template("blog.html", posts=posts_sorted)

@app.route("/blog/<post_id>")
def blog_post(post_id):
    """Single blog article view."""
    posts = read_json(BLOG_FILE)
    post = next((p for p in posts if p["id"] == post_id), None)
    if not post:
        flash("That article could not be found.", "error")
        return redirect(url_for("blog"))
    other_posts = [p for p in posts if p["id"] != post_id][:2]
    return render_template("blog_post.html", post=post, other_posts=other_posts)

@app.route("/contact", methods=["GET", "POST"])
def contact():
    """Contact page — visit info, contact form, map placeholder."""
    if request.method == "POST":
        name    = request.form.get("name", "").strip()
        email   = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()

        if not name or not email or not message:
            flash("Please fill in your name, email, and message.", "error")
            return redirect(url_for("contact"))

        new_message = {
            "name": name,
            "email": email,
            "message": message,
            "received_at": datetime.now().isoformat(timespec="seconds")
        }
        messages = read_json(MESSAGES_FILE)
        messages.append(new_message)
        write_json(MESSAGES_FILE, messages)

        flash("Thank you — your message has been sent. We'll reply within 24 hours.", "success")
        return redirect(url_for("contact"))

    return render_template("contact.html")

# ══════════════════════════════════════════════════════════════════════════
#  CART ROUTES
# ══════════════════════════════════════════════════════════════════════════

@app.route("/cart")
def view_cart():
    """View cart page — items, quantities, totals."""
    items, total_price, total_items = cart_details()
    return render_template("cart.html", items=items, total_price=total_price, total_items=total_items)

@app.route("/cart/add", methods=["POST"])
def add_to_cart():
    """Add a product to the cart (or increment quantity if already present)."""
    product_id = request.form.get("product_id")
    quantity   = int(request.form.get("quantity", 1))

    product = get_product_by_id(product_id)
    if not product:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"success": False, "error": "Product not found"}), 404
        flash("Product not found.", "error")
        return redirect(url_for("shop"))

    cart = get_cart()
    cart[product_id] = cart.get(product_id, 0) + quantity
    save_cart(cart)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({
            "success": True,
            "cart_count": cart_count(),
            "product_name": product["name"]
        })

    flash(f"Added '{product['name']}' to your cart.", "success")
    return redirect(request.referrer or url_for("shop"))

@app.route("/cart/update", methods=["POST"])
def update_cart():
    """Update the quantity of an item already in the cart."""
    product_id = request.form.get("product_id")
    quantity   = int(request.form.get("quantity", 1))

    cart = get_cart()
    if product_id in cart:
        if quantity <= 0:
            del cart[product_id]
        else:
            cart[product_id] = quantity
        save_cart(cart)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        items, total_price, total_items = cart_details()
        return jsonify({
            "success": True,
            "total_price": total_price,
            "total_items": total_items,
            "cart_count": cart_count()
        })

    return redirect(url_for("view_cart"))

@app.route("/cart/remove", methods=["POST"])
def remove_from_cart():
    """Remove an item entirely from the cart."""
    product_id = request.form.get("product_id")
    cart = get_cart()
    if product_id in cart:
        del cart[product_id]
        save_cart(cart)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        items, total_price, total_items = cart_details()
        return jsonify({
            "success": True,
            "total_price": total_price,
            "total_items": total_items,
            "cart_count": cart_count()
        })

    flash("Item removed from cart.", "info")
    return redirect(url_for("view_cart"))

@app.route("/cart/clear", methods=["POST"])
def clear_cart():
    """Empty the entire cart."""
    session["cart"] = {}
    flash("Your cart has been cleared.", "info")
    return redirect(url_for("view_cart"))

# ══════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    # Ensure messages.json exists
    if not os.path.exists(MESSAGES_FILE):
        write_json(MESSAGES_FILE, [])

    print("\n✅  The Rose Atelier — Boutique Website")
    print("   Running at: http://127.0.0.1:5000\n")
    app.run(debug=True)