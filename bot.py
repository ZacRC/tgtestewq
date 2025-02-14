import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import json
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Get logger
logger = logging.getLogger(__name__)

# Product configuration with enhanced descriptions
GRASS_PRODUCTS = {
    "0.5": {
        "weight": 0.5,
        "price": 5.00,
        "unit": "gram",
        "description": "Perfect sample size for first-time buyers"
    },
    "1": {
        "weight": 1,
        "price": 9.00,
        "unit": "gram",
        "description": "Our most popular personal size"
    },
    "3.5": {
        "weight": 3.5,
        "price": 30.00,
        "unit": "grams",
        "description": "Classic eighth, ideal for regular users"
    },
    "7": {
        "weight": 7,
        "price": 55.00,
        "unit": "grams",
        "description": "Quarter size, great value for money"
    },
    "14": {
        "weight": 14,
        "price": 100.00,
        "unit": "grams",
        "description": "Half-size portion with premium savings"
    },
    "28": {
        "weight": 28,
        "price": 180.00,
        "unit": "grams",
        "description": "Full size with maximum value"
    },
    "56": {
        "weight": 56,
        "price": 340.00,
        "unit": "grams",
        "description": "Bulk purchase with extra savings"
    },
    "112": {
        "weight": 112,
        "price": 650.00,
        "unit": "grams",
        "description": "Wholesale quantity for serious buyers"
    },
    "224": {
        "weight": 224,
        "price": 1200.00,
        "unit": "grams",
        "description": "Premium bulk package with major savings"
    },
    "448": {
        "weight": 448,
        "price": 2200.00,
        "unit": "grams",
        "description": "Maximum quantity with best value"
    }
}

# Add this after GRASS_PRODUCTS declaration
DEFAULT_PRODUCT_CATALOG = {
    "Blue Dream": {
        "name": "Blue Dream",
        "description": "Sweet berry aroma with balanced full body relaxation",
        "type": "Hybrid",
        "thc": "18-24%",
        "prices": GRASS_PRODUCTS
    },
    "OG Kush": {
        "name": "OG Kush",
        "description": "Classic strain with earthy pine and sour lemon notes",
        "type": "Hybrid",
        "thc": "20-25%",
        "prices": GRASS_PRODUCTS
    },
    "Purple Haze": {
        "name": "Purple Haze",
        "description": "Sweet and earthy with berry and grape notes",
        "type": "Sativa",
        "thc": "16-20%",
        "prices": GRASS_PRODUCTS
    },
    "Northern Lights": {
        "name": "Northern Lights",
        "description": "Sweet and spicy with crystal trichomes",
        "type": "Indica",
        "thc": "16-21%",
        "prices": GRASS_PRODUCTS
    }
}

# Initialize with default values
PRODUCT_CATALOG = {}

# Add this after DEFAULT_PRODUCT_CATALOG
DEFAULT_PRODUCT_IMAGES = {
    "Blue Dream": "https://i.imgur.com/CsY7GcA.png",
    "OG Kush": "https://i.imgur.com/47uY36h.png",
    "Purple Haze": "https://i.imgur.com/N9QS7tq.png",
    "Northern Lights": "https://i.imgur.com/pZEcGUf.png"
}

# Initialize with default values
PRODUCT_IMAGES = {}

# Shopping cart storage (in-memory for demonstration)
SHOPPING_CARTS = {}

# Add this after SHOPPING_CARTS declaration
CHECKOUT_STEPS = {}  # Store checkout progress for users
SHIPPING_INFO = {}   # Store shipping information

# Add these after the existing storage declarations
USER_ORDERS = {}  # Store order history for users

# Add after other global variables
ADMIN_USERNAME = "CrackerJackson"

# Add after global variables
DATA_DIR = "data"
ORDERS_FILE = os.path.join(DATA_DIR, "orders.json")
CARTS_FILE = os.path.join(DATA_DIR, "carts.json")
CATALOG_FILE = os.path.join(DATA_DIR, "catalog.json")

def format_price(price):
    """Format price with 2 decimal places and $ symbol"""
    return f"${price:.2f}"

def get_product_button_text(weight, details, cart_quantity=0):
    """Format product button text with quantity if in cart"""
    base_text = f"{weight}g - {format_price(details['price'])}"
    if cart_quantity > 0:
        base_text += f" (×{cart_quantity})"
    return base_text

def get_cart_summary(cart):
    """Get a formatted cart summary"""
    if not cart:
        return ""
    
    total = 0
    summary = "\n💎 *Your Selection:*\n"
    for cart_key, quantity in cart.items():
        product_name, weight = cart_key.split('_')
        price = PRODUCT_CATALOG[product_name]['prices'][weight]['price'] * quantity
        total += price
        summary += f"• {product_name} {weight}g × {quantity}\n"
    summary += f"\n*Total: {format_price(total)}*\n"
    return summary + "\n─────────────────\n"

async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, is_callback=False):
    """Send the main menu - can be used for both new messages and callbacks"""
    
    # Calculate date 3 days ago for lab results
    test_date = datetime.now() - timedelta(days=3)
    formatted_date = test_date.strftime("%B %d, %Y")
    
    # First, send the welcome GIF
    if not is_callback:
        # Premium animated logo GIF
        gif_url = "https://s13.gifyu.com/images/b2nKf.gif"
        await update.message.reply_animation(
            animation=gif_url,
            parse_mode='Markdown',
            width=800,  # Specify optimal width
            height=600,  # Specify optimal height
            disable_notification=True  # Reduce compression
        )
        
        # Second GIF
        second_gif_url = "https://s13.gifyu.com/images/b2nzZ.gif"
        await update.message.reply_animation(
            animation=second_gif_url,
            parse_mode='Markdown',
            width=800,  # Specify optimal width
            height=600,  # Specify optimal height
            disable_notification=True  # Reduce compression
        )
    
    welcome_message = (
        "✨ TOP Gear\n"
        "🔬 Lab Tested WITH results\n"
        "🚚 Unmatched Delivery Stealth \n\n"
        "Our team ALWAYS assures quality and ZERO additives. As it is extreamly important to stay safe and healthy; if you are not working with us we can recommend WinstonE2, PlanetHollywood and RushRush products.\n\n"
        f"🧪 Latest Lab Test: _{formatted_date}_"
    )
    
    # Main menu buttons
    keyboard = [
        [InlineKeyboardButton("Shop Now", callback_data='view_products')],
        [
            InlineKeyboardButton("Your Shopping Cart", callback_data='view_cart'),
            InlineKeyboardButton("Your Orders", callback_data='view_orders')
        ],
        [InlineKeyboardButton("Support & FAQ", callback_data='help')],
        [InlineKeyboardButton("Lab Results", callback_data='lab_results')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if is_callback:
        if update.callback_query.message.photo:
            # If there's a photo, delete it and send a new text message
            await update.callback_query.message.delete()
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=welcome_message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await update.callback_query.edit_message_text(
                welcome_message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    else:
        await update.message.reply_text(
            welcome_message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the start command"""
    user_id = update.effective_user.id
    SHOPPING_CARTS[user_id] = {}
    
    if update.effective_user.username == ADMIN_USERNAME:
        await admin_panel(update, context)
    else:
        await send_main_menu(update, context)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Provide help information and FAQ"""
    help_text = (
        "❓ *Support & Frequently Asked Questions* ❓\n\n"
        "*Quick Commands:*\n"
        "• /start - Return to main menu\n"
        "• /help - View this help guide\n\n"
        "*FAQ:*\n"
        "Q: How long does delivery take?\n"
        "A: Typically 3-5 business days\n\n"
        "Q: What payment methods are accepted?\n"
        "A: Bitcoin & Monero\n\n"
        "Q: Are lab results available?\n"
        "A: Yes, check the Lab Results button\n\n"
        "Q: Is this product clean?\n"
        "A: Yes, we assure you that this product is clean and free of any additives. Quality is our top priority.\n\n"
        "Q: Where do you ship?\n"
        "A: Only within USA.\n\n"
        "Q: My order never arrived, what do I do?\n"
        "A: Contact support directly you will recive tracking number if package is lost or underweight 100% product reship.\n\n"
        "Q: Do I recive a tracking number?\n"
        "A: You will not unless requested directly. This is for your and our privacy and security.\n\n"
        "*Need More Help?*\n"
        "Contact our support here.\n"
        "Message us your questions or problems with your order"
    )
    
    keyboard = [[InlineKeyboardButton("🔙 Return to Main Menu", callback_data='start')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if isinstance(update, Update) and update.callback_query:
        await update.callback_query.edit_message_text(
            help_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            help_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def vip_benefits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display VIP benefits"""
    query = update.callback_query
    await query.answer()
    
    vip_text = (
        "💎 *Exclusive VIP Benefits* 💎\n\n"
        "*Premium Member Advantages:*\n"
        "🌟 Early Access to New Products\n"
        "💰 Exclusive Discounts\n"
        "🎁 Special Bonus Rewards\n"
        "🚚 Priority Shipping\n"
        "📱 24/7 VIP Support\n\n"
        "*How to Qualify:*\n"
        "Complete 3 orders to automatically unlock VIP status!"
    )
    
    keyboard = [[InlineKeyboardButton("🔙 Return to Main Menu", callback_data='start')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        vip_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def view_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display product catalog with navigation"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # Get current product index from context or set to 0
    if 'product_index' not in context.user_data:
        context.user_data['product_index'] = 0
    
    products = list(PRODUCT_CATALOG.values())
    current_index = context.user_data['product_index']
    current_product = products[current_index]
    
    # Get cart summary
    cart = SHOPPING_CARTS.get(user_id, {})
    cart_summary = get_cart_summary(cart) if cart else ""
    
    message = (
        f"🌿 *{current_product['name']}* 🌿\n"
        "─────────────────\n"
        f"*Description:*\n{current_product['description']}\n"
        "─────────────────\n"
    )
    
    if cart_summary:
        message += cart_summary
    
    # Product view buttons
    keyboard = [
        [InlineKeyboardButton("Personal (0.5g - 7g)", callback_data=f'view_personal_{current_product["name"]}')],
        [InlineKeyboardButton("Bulk (14g - 56g)", callback_data=f'view_bulk_{current_product["name"]}')],
        [InlineKeyboardButton("Wholesale (112g - 448g)", callback_data=f'view_wholesale_{current_product["name"]}')]
    ]
    
    # Add navigation row
    nav_buttons = []
    if current_index > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data='prev_product'))
    if current_index < len(products) - 1:
        nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data='next_product'))
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    # Add cart and back buttons
    keyboard.append([
        InlineKeyboardButton("Cart", callback_data='view_cart'),
        InlineKeyboardButton("↩️ Back", callback_data='start')
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # First, send the product image
    if query.message.photo:
        # If there's already a photo, edit the message
        await query.message.edit_media(
            media=InputMediaPhoto(
                media=PRODUCT_IMAGES[current_product['name']],
                caption=message,
                parse_mode='Markdown'
            ),
            reply_markup=reply_markup
        )
    else:
        # If there's no photo yet, delete the text message and send a new photo message
        await query.message.delete()
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=PRODUCT_IMAGES[current_product['name']],
            caption=message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def handle_product_navigation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle next/previous product navigation"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'next_product':
        context.user_data['product_index'] = min(
            context.user_data.get('product_index', 0) + 1,
            len(PRODUCT_CATALOG) - 1
        )
    else:  # prev_product
        context.user_data['product_index'] = max(
            context.user_data.get('product_index', 0) - 1,
            0
        )
    
    await view_products(update, context)

async def view_product_weights(update: Update, context: ContextTypes.DEFAULT_TYPE, category):
    """Display weight options for a specific product and category"""
    query = update.callback_query
    await query.answer()
    
    # Extract product name from callback data
    product_name = query.data.split('_')[-1]
    product = PRODUCT_CATALOG[product_name]
    
    user_id = query.from_user.id
    cart = SHOPPING_CARTS.get(user_id, {})
    cart_summary = get_cart_summary(cart)
    
    message = (
        f"🌿 *{product['name']}* 🌿\n"
        f"*{category.title()} Amounts*\n"
        "─────────────────\n"
    )
    
    if cart_summary:
        message += cart_summary
    
    if category == 'personal':
        standard_list = ["0.5", "1", "3.5", "7"]
    elif category == 'bulk':
        standard_list = ["14", "28", "56"]
    elif category == 'wholesale':
        standard_list = ["112", "224", "448"]
    else:
        standard_list = []

    available_options = [w for w in standard_list if w in product['prices']]
    if not available_options:
        # Fallback: use all available pricing keys sorted by numeric value
        available_options = sorted(product['prices'], key=lambda x: float(x))
    
    keyboard = []
    for weight in available_options:
        details = product['prices'][weight]
        cart_quantity = cart.get(f"{product_name}_{weight}", 0)
        quantity_text = f" ({cart_quantity}x)" if cart_quantity > 0 else ""
        keyboard.append([
            InlineKeyboardButton(
                f"{weight}g - {format_price(details['price'])}{quantity_text}",
                callback_data=f'add_to_cart_{product_name}_{weight}'
            )
        ])
    
    # Add navigation buttons
    keyboard.extend([
        [
            InlineKeyboardButton("⬅️ Back", callback_data='view_products'),
            InlineKeyboardButton("Cart", callback_data='view_cart')
        ],
        [InlineKeyboardButton("↩️ Menu", callback_data='start')]
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Check if the message has a photo
    if query.message.photo:
        # If there's a photo, edit the caption
        await query.message.edit_caption(
            caption=message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        # If no photo, edit the text
        await query.message.edit_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

# Add this helper function
def add_to_cart_with_product(user_id, product_name, weight, quantity=1):
    """Add product to cart with its name"""
    if user_id not in SHOPPING_CARTS:
        SHOPPING_CARTS[user_id] = {}
    
    cart_key = f"{product_name}_{weight}"
    if cart_key in SHOPPING_CARTS[user_id]:
        SHOPPING_CARTS[user_id][cart_key] += quantity
    else:
        SHOPPING_CARTS[user_id][cart_key] = quantity

async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a product to cart with product name"""
    query = update.callback_query
    await query.answer()
    
    # Extract product name and weight from callback data
    parts = query.data.split('_')
    # Format is 'add_to_cart_Product Name_weight'
    # Reconstruct product name from middle parts
    product_name = ' '.join(parts[3:-1])  # Join all parts between 'add_to_cart' and weight
    weight = parts[-1]  # Last part is weight
    
    user_id = query.from_user.id
    add_to_cart_with_product(user_id, product_name, weight)
    
    # Show quick confirmation
    await query.answer(f"Added {weight}g of {product_name} to cart!")
    
    # Return to product view
    await view_products(update, context)

async def view_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display shopping cart"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    cart = SHOPPING_CARTS.get(user_id, {})
    
    if not cart:
        empty_cart_message = (
            "🛒 *Your Shopping Cart is Empty*\n\n"
            "Explore our premium collection to find your perfect match!\n\n"
            "Need recommendations? Use the help button for assistance."
        )
        keyboard = [
            [InlineKeyboardButton(" Browse Collection", callback_data='view_products')],
            [InlineKeyboardButton("🔙 Return to Main Menu", callback_data='start')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
    else:
        cart_message = "🛒 *Your Premium Selection*\n\n"
        total = 0
        
        # Group items by product
        products_in_cart = {}
        for cart_key, quantity in cart.items():
            product_name, weight = cart_key.split('_')
            if product_name not in products_in_cart:
                products_in_cart[product_name] = []
            products_in_cart[product_name].append((weight, quantity))
        
        # Display items grouped by product
        for product_name, items in products_in_cart.items():
            cart_message += f"*{product_name}:*\n"
            for weight, quantity in items:
                price = PRODUCT_CATALOG[product_name]['prices'][weight]['price']
                item_total = price * quantity
                total += item_total
                cart_message += f"   • {weight}g × {quantity} = {format_price(item_total)}\n"
            cart_message += "\n"
        
        cart_message += (
            "─────────────────\n"
            f"*Subtotal: {format_price(total)}*\n"
            f"*Shipping: FREE*\n"
            f"*Total: {format_price(total)}*"
        )
        
        # Cart buttons
        keyboard = [
            [InlineKeyboardButton("Proceed to Checkout", callback_data='checkout')],
            [InlineKeyboardButton("Continue Shopping", callback_data='view_products')],
            [InlineKeyboardButton("Clear Cart", callback_data='clear_cart')],
            [InlineKeyboardButton("↩️ Back to Menu", callback_data='start')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        empty_cart_message = cart_message

    # Check if the message has a photo
    if query.message.photo:
        # If there's a photo, delete it and send a new text message
        await query.message.delete()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=empty_cart_message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        # If no photo, edit the text
        await query.edit_message_text(
            text=empty_cart_message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def clear_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear the shopping cart"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    SHOPPING_CARTS[user_id] = {}
    
    clear_message = (
        "🗑 *Cart Successfully Cleared*\n\n"
        "Your shopping cart has been emptied.\n"
        "Ready to start fresh with your premium selection!"
    )
    
    keyboard = [
        [InlineKeyboardButton(" Browse Collection", callback_data='view_products')],
        [InlineKeyboardButton("🔙 Return to Main Menu", callback_data='start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        clear_message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def start_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the checkout process"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    cart = SHOPPING_CARTS.get(user_id, {})
    
    if not cart:
        await query.edit_message_text(
            "❌ *Cart is Empty*\n\nPlease add products before checkout.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Browse Products", callback_data='view_products')
            ]]),
            parse_mode='Markdown'
        )
        return

    # Initialize checkout process
    CHECKOUT_STEPS[user_id] = {
        'step': 'shipping',  # Start with shipping
        'order_id': f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}-{user_id}"
    }
    
    shipping_message = (
        "📦 *Enter Shipping Information* 📦\n"
        "─────────────────\n\n"
        "Please provide your shipping details in the following format:\n\n"
        "*Name*\n"
        "Street Address\n"
        "City, State ZIP\n\n"
        "Example:\n"
        "_John Smith_\n"
        "_123 Main St_\n"
        "_New York, NY 10001_"
    )
    
    keyboard = [
        [InlineKeyboardButton("↩️ Back to Cart", callback_data='view_cart')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = await query.edit_message_text(shipping_message, reply_markup=reply_markup, parse_mode='Markdown')
    
    # Store the message ID for later deletion
    context.user_data['shipping_menu_message_id'] = message.message_id

async def handle_shipping_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process shipping information and move to payment selection"""
    user_id = update.effective_user.id
    
    if user_id not in CHECKOUT_STEPS or CHECKOUT_STEPS[user_id]['step'] != 'shipping':
        return
    
    shipping_info = update.message.text
    cart = SHOPPING_CARTS.get(user_id, {})
    
    # Delete the user's shipping info message
    await update.message.delete()
    
    # Find and delete the shipping menu message
    if 'shipping_menu_message_id' in context.user_data:
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=context.user_data['shipping_menu_message_id']
            )
        except Exception:
            pass  # Message might already be deleted
    
    # Calculate total
    total = 0
    review_message = (
        "🛒 *Order Review*\n"
        "─────────────────\n\n"
        "*Selected Products:*\n"
    )
    
    # Group items by product
    products_in_cart = {}
    for cart_key, quantity in cart.items():
        product_name, weight = cart_key.split('_')
        if product_name not in products_in_cart:
            products_in_cart[product_name] = []
        products_in_cart[product_name].append((weight, quantity))
    
    # Display items grouped by product
    for product_name, items in products_in_cart.items():
        review_message += f"*{product_name}:*\n"
        for weight, quantity in items:
            price = PRODUCT_CATALOG[product_name]['prices'][weight]['price']
            item_total = price * quantity
            total += item_total
            review_message += f"   • {weight}g × {quantity} = {format_price(item_total)}\n"
        review_message += "\n"
    
    review_message += (
        "─────────────────\n"
        f"*Subtotal:* {format_price(total)}\n"
        "*Shipping:* FREE\n"
        f"*Total:* {format_price(total)}\n\n"
        "*Shipping Details:*\n"
        f"{shipping_info}\n\n"
        "Please select your payment method:"
    )
    
    # Update checkout step and store shipping info
    CHECKOUT_STEPS[user_id]['step'] = 'payment'
    CHECKOUT_STEPS[user_id]['shipping_info'] = shipping_info
    
    # Payment selection buttons
    keyboard = [
        [InlineKeyboardButton("Bitcoin", callback_data='payment_btc')],
        [InlineKeyboardButton("Monero", callback_data='payment_xmr')],
        [InlineKeyboardButton("↩️ Back", callback_data='checkout')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(review_message, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_payment_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle payment method selection and show payment details"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    payment_method = 'bitcoin' if query.data == 'payment_btc' else 'monero'
    cart = SHOPPING_CARTS.get(user_id, {})
    
    # Calculate total
    total = 0
    for cart_key, quantity in cart.items():
        product_name, weight = cart_key.split('_')
        price = PRODUCT_CATALOG[product_name]['prices'][weight]['price']
        total += price * quantity
    
    # Store order details in context for later use
    context.user_data['pending_order'] = {
        'order_id': CHECKOUT_STEPS[user_id]['order_id'],
        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'status': 'pending',
        'total': total,
        'items': dict(cart),
        'payment_method': payment_method,
        'shipping_info': CHECKOUT_STEPS[user_id]['shipping_info']
    }
    
    # Update checkout step
    CHECKOUT_STEPS[user_id]['step'] = 'confirm_payment'
    
    # Simulate crypto addresses
    btc_address = "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"
    xmr_address = "44AFFq5kSiGBoZ4NMDwYtN18obc8AemS33DBLWs3H7otXft3XjrpDtQGv7SqSsaBYBb98uNbr2VBBEt7f2wfn3RVGQBEP3A"
    
    payment_message = (
        "💳 *Payment Details*\n"
        "─────────────────\n\n"
        f"*Order ID:* `{context.user_data['pending_order']['order_id']}`\n\n"
        "*Selected Products:*\n"
    )
    
    # Add itemized list to payment message
    for cart_key, quantity in cart.items():
        product_name, weight = cart_key.split('_')
        price = PRODUCT_CATALOG[product_name]['prices'][weight]['price']
        item_total = price * quantity
        payment_message += f"• {product_name} {weight}g × {quantity} = {format_price(item_total)}\n"
    
    payment_message += (
        f"\n*Total Amount:* {format_price(total)}\n"
        f"*Payment Method:* {payment_method.title()}\n\n"
        "*Send payment to:*\n"
        f"`{btc_address if payment_method == 'bitcoin' else xmr_address}`\n\n"
        "*After sending payment, click the button below to confirm:*"
    )
    
    # Payment confirmation buttons
    keyboard = [
        [InlineKeyboardButton("Confirm Payment Sent", callback_data='confirm_payment')],
        [InlineKeyboardButton("↩️ Change Payment", callback_data='checkout')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(payment_message, reply_markup=reply_markup, parse_mode='Markdown')

async def confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle payment confirmation and complete order"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if user_id not in CHECKOUT_STEPS or CHECKOUT_STEPS[user_id]['step'] != 'confirm_payment':
        return
    
    if 'pending_order' not in context.user_data:
        await query.edit_message_text(
            "❌ Error: Order details not found. Please try again.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("↩️ Back to Menu", callback_data='start')]]),
            parse_mode='Markdown'
        )
        return
    
    # Get the pending order from context
    order = context.user_data['pending_order']
    
    # Initialize user's orders list if it doesn't exist
    if user_id not in USER_ORDERS:
        USER_ORDERS[user_id] = []
    
    # Add the order to user's orders
    USER_ORDERS[user_id].append(order)
    
    # Save data immediately
    save_data()
    
    confirmation_message = (
        "🎉 *Order Successfully Placed!* 🎉\n"
        "─────────────────\n\n"
        f"*Order ID:* `{order['order_id']}`\n\n"
        "*Selected Products:*\n"
    )
    
    # Add itemized list to confirmation
    for cart_key, quantity in order['items'].items():
        product_name, weight = cart_key.split('_')
        price = PRODUCT_CATALOG[product_name]['prices'][weight]['price']
        item_total = price * quantity
        confirmation_message += f"• {product_name} {weight}g × {quantity} = {format_price(item_total)}\n"
    
    confirmation_message += (
        f"\n*Total Amount:* {format_price(order['total'])}\n"
        f"*Payment Method:* {order['payment_method'].title()}\n\n"
        "*Shipping Details:*\n"
        f"{order['shipping_info']}\n\n"
        "Your order has been confirmed and will be processed shortly.\n"
        "You can check your order status or update shipping details\n"
        "in the Order History section.\n\n"
        "*Thank you for your purchase!* 🙏"
    )
    
    # Order confirmation buttons
    keyboard = [
        [InlineKeyboardButton("View Order Status", callback_data='view_orders')],
        [InlineKeyboardButton("↩️ Back to Menu", callback_data='start')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(confirmation_message, reply_markup=reply_markup, parse_mode='Markdown')
    
    # Clear cart, checkout data, and pending order
    SHOPPING_CARTS[user_id] = {}
    if user_id in CHECKOUT_STEPS:
        del CHECKOUT_STEPS[user_id]
    if 'pending_order' in context.user_data:
        del context.user_data['pending_order']
    save_data()

async def view_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display user's order history with pagination"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    orders = USER_ORDERS.get(user_id, [])
    
    # Get page number from context or start at 0
    page = context.user_data.get('user_order_page', 0)
    orders_per_page = 5
    
    if not orders:
        orders_message = (
            "📦 *Your Order History* 📦\n\n"
            "*Recent Orders:*\n"
            "No orders found in your history yet.\n\n"
            "Start shopping to create your first order!"
        )
        
        keyboard = [
            [InlineKeyboardButton("Start Shopping", callback_data='view_products')],
            [InlineKeyboardButton("↩️ Return to Main Menu", callback_data='start')]
        ]
    else:
        # Sort orders by date (newest first)
        orders.sort(key=lambda x: datetime.strptime(x['date'], "%Y-%m-%d %H:%M:%S"), reverse=True)
        
        total_pages = (len(orders) + orders_per_page - 1) // orders_per_page
        
        # Ensure page is within valid range
        page = min(max(0, page), total_pages - 1)
        context.user_data['user_order_page'] = page
        
        start_idx = page * orders_per_page
        end_idx = min(start_idx + orders_per_page, len(orders))
        current_orders = orders[start_idx:end_idx]
        
        orders_message = f"📦 *Your Order History* 📦\nPage {page + 1} of {total_pages}\n\n"
        
        for order in current_orders:
            status_emoji = {
                'pending': '⏳',
                'processing': '🔄',
                'shipped': '🚚',
                'delivered': '✅',
                'cancelled': '❌'
            }.get(order.get('status', 'pending'), '⏳')
            
            orders_message += (
                f"*Order ID:* `{order['order_id']}`\n"
                f"*Date:* {order['date']}\n"
                f"*Status:* {status_emoji} {order['status'].title()}\n"
                f"*Total:* {format_price(order['total'])}\n"
                f"*Payment:* {order['payment_method'].title()}\n\n"
                "*Items:*\n"
            )
            
            # Display items in order
            if isinstance(order.get('items', {}), dict):
                for cart_key, quantity in order['items'].items():
                    if '_' in cart_key:
                        product_name, weight = cart_key.split('_')
                        orders_message += f"• {product_name} {weight}g × {quantity}\n"
                    else:
                        # Handle legacy orders
                        orders_message += f"• Product: N/A {cart_key}g × {quantity}\n"
            orders_message += "─────────────────\n"
        
        # Create navigation buttons
        keyboard = []
        nav_buttons = []
        
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data='user_prev_page'))
        if page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data='user_next_page'))
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        # Add action buttons
        keyboard.extend([
            [InlineKeyboardButton("Update Shipping", callback_data='update_shipping')],
            [InlineKeyboardButton("New Order", callback_data='view_products')],
            [InlineKeyboardButton("↩️ Menu", callback_data='start')]
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(orders_message, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_user_order_navigation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user order history navigation"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'user_next_page':
        context.user_data['user_order_page'] = context.user_data.get('user_order_page', 0) + 1
    elif query.data == 'user_prev_page':
        context.user_data['user_order_page'] = max(0, context.user_data.get('user_order_page', 0) - 1)
    
    await view_orders(update, context)

async def update_shipping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Allow users to update shipping address for pending orders"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    orders = USER_ORDERS.get(user_id, [])
    pending_orders = [order for order in orders if order['status'] in ['pending', 'processing']]
    
    if not pending_orders:
        message = (
            "📦 *Update Shipping Address* 📦\n\n"
            "You have no pending orders that can be updated.\n"
            "Only pending or processing orders can have shipping details modified."
        )
        keyboard = [[InlineKeyboardButton("🔙 Back to Orders", callback_data='view_orders')]]
    else:
        message = (
            "📦 *Update Shipping Address* 📦\n\n"
            "*Select order to update:*\n\n"
        )
        
        keyboard = []
        for order in pending_orders:
            message += (
                f"*Order ID:* `{order['order_id']}`\n"
                f"*Current Address:*\n{order['shipping_info']}\n"
                "─────────────────\n"
            )
            keyboard.append([
                InlineKeyboardButton(
                    f"Update {order['order_id']}", 
                    callback_data=f'update_shipping_{order["order_id"]}'
                )
            ])
        
        keyboard.append([InlineKeyboardButton("🔙 Back to Orders", callback_data='view_orders')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def start_shipping_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the shipping update process for a specific order"""
    query = update.callback_query
    await query.answer()
    
    order_id = query.data.split('_')[-1]
    user_id = query.from_user.id
    
    # Store the order being updated
    context.user_data['updating_order'] = order_id
    
    message = (
        "📦 *Update Shipping Address* 📦\n"
        "─────────────────\n\n"
        f"*Order ID:* `{order_id}`\n\n"
        "Please provide your new shipping details in the following format:\n\n"
        "*Name*\n"
        "Street Address\n"
        "City, State ZIP\n\n"
        "Example:\n"
        "_John Smith_\n"
        "_123 Main St_\n"
        "_New York, NY 10001_\n\n"
        "Enter your new shipping information exactly as shown above."
    )
    
    keyboard = [[InlineKeyboardButton("🔙 Cancel Update", callback_data='view_orders')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_shipping_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process the shipping address update"""
    user_id = update.effective_user.id
    new_address = update.message.text
    
    if 'updating_order' not in context.user_data:
        return
    
    order_id = context.user_data['updating_order']
    orders = USER_ORDERS.get(user_id, [])
    
    # Find and update the order
    for order in orders:
        if order['order_id'] == order_id:
            order['shipping_info'] = new_address
            break
    
    confirmation = (
        "✅ *Shipping Address Updated* ✅\n"
        "─────────────────\n\n"
        f"*Order ID:* `{order_id}`\n\n"
        "*New Shipping Address:*\n"
        f"{new_address}\n\n"
        "Your shipping details have been successfully updated."
    )
    
    keyboard = [
        [InlineKeyboardButton("📋 View Orders", callback_data='view_orders')],
        [InlineKeyboardButton("🏠 Main Menu", callback_data='start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(confirmation, reply_markup=reply_markup, parse_mode='Markdown')
    del context.user_data['updating_order']

async def view_lab_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display lab results with dynamic date"""
    query = update.callback_query
    await query.answer()
    
    # Calculate date 3 days ago
    test_date = datetime.now() - timedelta(days=3)
    formatted_date = test_date.strftime("%B %d, %Y")
    
    lab_results = (
        "🧪 *Laboratory Analysis Results* 🧪\n\n"
        f"*Test Date:* {formatted_date}\n"
        "*Lab Facility:* CannaLytics Research Center\n\n"
        "*Product Analysis:*\n"
        "✅ Purity: 99.99%\n"
        "✅ Pesticides: None Detected\n"
        "✅ Heavy Metals: None Detected\n"
        "✅ Microbials: Pass\n"
        "✅ Residual Solvents: Pass\n\n"
        "*Quality Metrics:*\n"
        "• Moisture Content: 12%\n"
        "• Terpene Profile: Premium Grade\n"
        "• Visual Inspection: Exceptional\n\n"
        "*Certification:*\n"
        "This product meets or exceeds all quality and safety standards.\n"
        "Certificate ID: LAB-" + test_date.strftime("%Y%m%d") + "-MA\n\n"
        "_Results verified by independent third-party laboratory._"
    )
    
    # Lab results buttons
    keyboard = [
        [InlineKeyboardButton("Shop Products", callback_data='view_products')],
        [InlineKeyboardButton("↩️ Back to Menu", callback_data='start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        lab_results,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display admin panel with order management options"""
    if update.effective_user.username != ADMIN_USERNAME:
        return
    
    query = update.callback_query
    if query:
        await query.answer()
    
    admin_message = (
        "👑 *Admin Control Panel* 👑\n\n"
        "Select an option to manage:"
    )
    
    keyboard = [
        [InlineKeyboardButton("📋 View All Orders", callback_data='admin_view_orders')],
        [InlineKeyboardButton("🔍 Search Orders", callback_data='admin_search_orders')],
        [InlineKeyboardButton("📊 Order Statistics", callback_data='admin_stats')],
        [InlineKeyboardButton("🌿 Manage Products", callback_data='admin_manage_products')],
        [InlineKeyboardButton("🗑 Delete All Orders", callback_data='admin_delete_all_confirm')],
        [InlineKeyboardButton("↩️ Back to Main Menu", callback_data='start')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if query:
        await query.edit_message_text(admin_message, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(admin_message, reply_markup=reply_markup, parse_mode='Markdown')

async def admin_view_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display all orders with pagination"""
    if update.effective_user.username != ADMIN_USERNAME:
        return
    
    query = update.callback_query
    await query.answer()
    
    # Get page number from context or start at 0
    page = context.user_data.get('admin_order_page', 0)
    orders_per_page = 5
    
    # Collect all orders from all users
    all_orders = []
    for user_id, orders in USER_ORDERS.items():
        for order in orders:
            order['user_id'] = user_id
            all_orders.append(order)
    
    # Sort orders by date (newest first)
    all_orders.sort(key=lambda x: datetime.strptime(x['date'], "%Y-%m-%d %H:%M:%S"), reverse=True)
    
    total_orders = len(all_orders)
    total_pages = (total_orders + orders_per_page - 1) // orders_per_page
    
    if total_orders == 0:
        message = "📋 *No orders found*"
        keyboard = [[InlineKeyboardButton("↩️ Back to Admin Panel", callback_data='admin_panel')]]
    else:
        start_idx = page * orders_per_page
        end_idx = min(start_idx + orders_per_page, total_orders)
        current_orders = all_orders[start_idx:end_idx]
        
        message = "📋 *All Orders*\n\n"
        
        for order in current_orders:
            status_emoji = {
                'pending': '⏳',
                'processing': '🔄',
                'shipped': '🚚',
                'delivered': '✅',
                'cancelled': '❌'
            }.get(order['status'], '⏳')
            
            message += (
                f"*Order ID:* `{order['order_id']}`\n"
                f"*Date:* {order['date']}\n"
                f"*Status:* {status_emoji} {order['status'].title()}\n"
                f"*Total:* ${order['total']:.2f}\n"
                f"*Payment:* {order['payment_method'].title()}\n\n"
                "*Items:*\n"
            )
            
            for cart_key, quantity in order['items'].items():
                product_name, weight = cart_key.split('_')
                message += f"• {product_name} {weight}g × {quantity}\n"
            
            message += f"\n*Shipping Info:*\n{order['shipping_info']}\n"
            message += "\n─────────────────\n\n"
        
        message += f"Page {page + 1} of {total_pages}"
        
        # Navigation buttons
        keyboard = []
        nav_buttons = []
        
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data='admin_prev_page'))
        if page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data='admin_next_page'))
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        # Action buttons for each order
        for order in current_orders:
            keyboard.extend([
                [InlineKeyboardButton(
                    f"Update Status - {order['order_id']}",
                    callback_data=f"admin_update_status_{order['order_id']}"
                )],
                [InlineKeyboardButton(
                    f"🗑 Delete Order - {order['order_id']}",
                    callback_data=f"admin_delete_confirm_{order['order_id']}"
                )]
            ])
        
        keyboard.append([InlineKeyboardButton("↩️ Back to Admin Panel", callback_data='admin_panel')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def admin_delete_order_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show confirmation dialog for deleting a single order"""
    if update.effective_user.username != ADMIN_USERNAME:
        return
    
    query = update.callback_query
    await query.answer()
    
    order_id = query.data.split('_')[-1]
    
    message = (
        "⚠️ *Delete Order Confirmation* ⚠️\n\n"
        f"Are you sure you want to delete order *{order_id}*?\n"
        "This action cannot be undone."
    )
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Yes, Delete", callback_data=f'admin_delete_order_{order_id}'),
            InlineKeyboardButton("❌ No, Cancel", callback_data='admin_view_orders')
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def admin_delete_all_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show confirmation dialog for deleting all orders"""
    if update.effective_user.username != ADMIN_USERNAME:
        return
    
    query = update.callback_query
    await query.answer()
    
    total_orders = sum(len(orders) for orders in USER_ORDERS.values())
    
    message = (
        "⚠️ *Delete All Orders Confirmation* ⚠️\n\n"
        f"Are you sure you want to delete *ALL {total_orders} orders*?\n"
        "This action cannot be undone and will affect all users."
    )
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Yes, Delete All", callback_data='admin_delete_all_orders'),
            InlineKeyboardButton("❌ No, Cancel", callback_data='admin_panel')
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def admin_delete_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete a single order"""
    if update.effective_user.username != ADMIN_USERNAME:
        return
    
    query = update.callback_query
    await query.answer()
    
    order_id = query.data.split('_')[-1]
    order_found = False
    
    # Find and delete the order
    for user_id, orders in USER_ORDERS.items():
        for order in orders[:]:  # Create a copy to iterate while removing
            if order['order_id'] == order_id:
                orders.remove(order)
                order_found = True
                # If user has no orders left, clean up
                if not orders:
                    del USER_ORDERS[user_id]
                break
        if order_found:
            break
    
    if order_found:
        save_data()  # Save changes to disk
        await query.answer("Order deleted successfully!")
    else:
        await query.answer("Order not found!", show_alert=True)
    
    # Return to order view
    await admin_view_orders(update, context)

async def admin_delete_all_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete all orders from all users"""
    if update.effective_user.username != ADMIN_USERNAME:
        return
    
    query = update.callback_query
    await query.answer()
    
    # Clear all orders
    USER_ORDERS.clear()
    save_data()  # Save changes to disk
    
    message = (
        "✅ *All Orders Deleted* ✅\n\n"
        "All orders have been successfully deleted from the system."
    )
    
    keyboard = [[InlineKeyboardButton("↩️ Back to Admin Panel", callback_data='admin_panel')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def admin_update_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Update order status"""
    if update.effective_user.username != ADMIN_USERNAME:
        return
    
    query = update.callback_query
    await query.answer()
    
    order_id = query.data.split('_')[-1]
    
    message = f"Select new status for Order ID: `{order_id}`"
    
    keyboard = [
        [InlineKeyboardButton("⏳ Pending", callback_data=f'admin_set_status_{order_id}_pending')],
        [InlineKeyboardButton("🔄 Processing", callback_data=f'admin_set_status_{order_id}_processing')],
        [InlineKeyboardButton("🚚 Shipped", callback_data=f'admin_set_status_{order_id}_shipped')],
        [InlineKeyboardButton("✅ Delivered", callback_data=f'admin_set_status_{order_id}_delivered')],
        [InlineKeyboardButton("❌ Cancelled", callback_data=f'admin_set_status_{order_id}_cancelled')],
        [InlineKeyboardButton("↩️ Back to Orders", callback_data='admin_view_orders')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def admin_set_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set the new status for an order"""
    if update.effective_user.username != ADMIN_USERNAME:
        return
    
    query = update.callback_query
    await query.answer()
    
    # Extract order_id and new_status from callback data
    parts = query.data.split('_')
    order_id = parts[-2]  # Second to last part is order_id
    new_status = parts[-1]  # Last part is the status
    
    # Status notification messages
    status_messages = {
        'processing': (
            "🔄 *Order Status Update* 🔄\n\n"
            f"Your order (*{order_id}*) is now being processed!\n\n"
            "We are preparing your items for shipment.\n"
            "You will receive another notification when your order ships."
        ),
        'shipped': (
            "🚚 *Order Status Update* 🚚\n\n"
            f"Your order (*{order_id}*) has been shipped!\n\n"
            "Your package is on its way to you.\n"
            "Thank you for your business!"
        ),
        'delivered': (
            "✅ *Order Status Update* ✅\n\n"
            f"Your order (*{order_id}*) has been marked as delivered!\n\n"
            "We hope you enjoy your products.\n"
            "Thank you for choosing our service!"
        ),
        'cancelled': (
            "❌ *Order Status Update* ❌\n\n"
            f"Your order (*{order_id}*) has been cancelled.\n\n"
            "If you have any questions about this cancellation,\n"
            "please contact our support."
        ),
        'pending': (
            "⏳ *Order Status Update* ⏳\n\n"
            f"Your order (*{order_id}*) status has been updated to pending.\n\n"
            "We will process your order soon.\n"
            "Thank you for your patience."
        )
    }
    
    # Update order status
    status_updated = False
    for user_id, user_orders in USER_ORDERS.items():
        for order in user_orders:
            if order['order_id'] == order_id:
                order['status'] = new_status
                status_updated = True
                save_data()  # Save after updating order status
                
                # Send notification for any status change
                if new_status in status_messages:
                    try:
                        await context.bot.send_message(
                            chat_id=user_id,
                            text=status_messages[new_status],
                            parse_mode='Markdown'
                        )
                    except Exception as e:
                        print(f"Failed to notify user {user_id}: {e}")
                break
        if status_updated:
            break
    
    # Show confirmation message to admin
    await query.answer(f"Order status updated to: {new_status}")
    
    # Return to order view
    await admin_view_orders(update, context)

async def admin_handle_navigation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin panel navigation"""
    if update.effective_user.username != ADMIN_USERNAME:
        return
    
    query = update.callback_query
    await query.answer()
    
    if query.data == 'admin_next_page':
        context.user_data['admin_order_page'] = context.user_data.get('admin_order_page', 0) + 1
    elif query.data == 'admin_prev_page':
        context.user_data['admin_order_page'] = max(0, context.user_data.get('admin_order_page', 0) - 1)
    
    await admin_view_orders(update, context)

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display order statistics"""
    if update.effective_user.username != ADMIN_USERNAME:
        return
    
    query = update.callback_query
    await query.answer()
    
    # Collect all orders
    all_orders = []
    for user_orders in USER_ORDERS.values():
        all_orders.extend(user_orders)
    
    # Calculate statistics
    total_orders = len(all_orders)
    if total_orders == 0:
        stats_message = "📊 *No orders to analyze*"
    else:
        total_revenue = sum(order['total'] for order in all_orders)
        status_counts = {}
        payment_methods = {}
        product_quantities = {}
        
        for order in all_orders:
            # Count statuses
            status_counts[order['status']] = status_counts.get(order['status'], 0) + 1
            
            # Count payment methods
            payment_methods[order['payment_method']] = payment_methods.get(order['payment_method'], 0) + 1
            
            # Count product quantities
            for cart_key, quantity in order['items'].items():
                product_name = cart_key.split('_')[0]
                product_quantities[product_name] = product_quantities.get(product_name, 0) + quantity
        
        stats_message = (
            "📊 *Order Statistics* 📊\n\n"
            f"*Total Orders:* {total_orders}\n"
            f"*Total Revenue:* ${total_revenue:.2f}\n\n"
            "*Order Status Breakdown:*\n"
        )
        
        for status, count in status_counts.items():
            percentage = (count / total_orders) * 100
            stats_message += f"• {status.title()}: {count} ({percentage:.1f}%)\n"
        
        stats_message += "\n*Payment Methods:*\n"
        for method, count in payment_methods.items():
            percentage = (count / total_orders) * 100
            stats_message += f"• {method.title()}: {count} ({percentage:.1f}%)\n"
        
        stats_message += "\n*Popular Products:*\n"
        sorted_products = sorted(product_quantities.items(), key=lambda x: x[1], reverse=True)
        for product, quantity in sorted_products:
            stats_message += f"• {product}: {quantity}g sold\n"
    
    keyboard = [[InlineKeyboardButton("↩️ Back to Admin Panel", callback_data='admin_panel')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(stats_message, reply_markup=reply_markup, parse_mode='Markdown')

async def admin_manage_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display product management interface"""
    if update.effective_user.username != ADMIN_USERNAME:
        return
    
    query = update.callback_query
    await query.answer()
    
    message = (
        "🌿 *Product Management* 🌿\n\n"
        "Current Products:\n\n"
    )
    
    keyboard = [
        [InlineKeyboardButton("➕ Create New Product", callback_data='admin_create_product')]
    ]
    
    # List all products with edit buttons
    for product_name in PRODUCT_CATALOG.keys():
        message += (
            f"• {product_name}\n"
            f"  Description: {PRODUCT_CATALOG[product_name]['description']}\n\n"
        )
        keyboard.extend([
            [InlineKeyboardButton(
                f"✏️ Edit Name - {product_name}",
                callback_data=f'admin_edit_product_{product_name}'
            )],
            [InlineKeyboardButton(
                f"📝 Edit Description - {product_name}",
                callback_data=f'admin_edit_desc_{product_name}'
            )],
            [InlineKeyboardButton(
                f"🖼 Edit Image - {product_name}",
                callback_data=f'admin_edit_image_{product_name}'
            )]
        ])
    
    keyboard.append([InlineKeyboardButton("↩️ Back to Admin Panel", callback_data='admin_panel')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def admin_edit_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the product editing process"""
    if update.effective_user.username != ADMIN_USERNAME:
        return
    
    query = update.callback_query
    await query.answer()
    
    # Extract product name from callback data
    product_name = '_'.join(query.data.split('_')[3:])  # Get everything after 'admin_edit_product_'
    
    message = (
        f"✏️ *Edit Product: {product_name}* ✏️\n\n"
        "Please enter the new name for this product.\n\n"
        "*Current Details:*\n"
        f"Name: {product_name}\n"
        f"Type: {PRODUCT_CATALOG[product_name]['type']}\n"
        f"THC: {PRODUCT_CATALOG[product_name]['thc']}\n\n"
        "To change the name, simply send the new name as a message.\n"
        "The name should be clear and concise."
    )
    
    # Store the product being edited in context
    context.user_data['editing_product'] = product_name
    
    keyboard = [[InlineKeyboardButton("🔙 Cancel", callback_data='admin_manage_products')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_product_name_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process the product name update"""
    if update.effective_user.username != ADMIN_USERNAME:
        return
    
    new_name = update.message.text.strip()
    old_name = context.user_data.get('editing_product')
    
    if not old_name or old_name not in PRODUCT_CATALOG:
        await update.message.reply_text(
            "❌ Error: Product not found or edit session expired.\nPlease try again from the product management menu."
        )
        return
    
    if new_name in PRODUCT_CATALOG:
        await update.message.reply_text(
            "❌ Error: A product with this name already exists.\nPlease choose a different name."
        )
        return
    
    # Update the product catalog
    PRODUCT_CATALOG[new_name] = PRODUCT_CATALOG.pop(old_name)
    PRODUCT_CATALOG[new_name]['name'] = new_name
    
    # Update product images mapping
    if old_name in PRODUCT_IMAGES:
        PRODUCT_IMAGES[new_name] = PRODUCT_IMAGES.pop(old_name)
    
    # Save the updated catalog to file
    save_data()
    
    # Clear the editing state
    del context.user_data['editing_product']
    
    confirmation = (
        "✅ *Product Name Updated Successfully* ✅\n\n"
        f"Old name: {old_name}\n"
        f"New name: {new_name}\n\n"
        "Note: This change will apply to all new orders.\n"
        "Existing orders will maintain their original product names."
    )
    
    keyboard = [
        [InlineKeyboardButton("📋 Back to Products", callback_data='admin_manage_products')],
        [InlineKeyboardButton("🏠 Admin Panel", callback_data='admin_panel')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(confirmation, reply_markup=reply_markup, parse_mode='Markdown')

async def admin_edit_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the product description editing process"""
    if update.effective_user.username != ADMIN_USERNAME:
        return
    
    query = update.callback_query
    await query.answer()
    
    # Extract product name from callback data
    product_name = '_'.join(query.data.split('_')[3:])  # Get everything after 'admin_edit_desc_'
    
    message = (
        f"📝 *Edit Description: {product_name}* 📝\n\n"
        "*Current Description:*\n"
        f"{PRODUCT_CATALOG[product_name]['description']}\n\n"
        "Please enter the new description for this product.\n"
        "Send the description as a message."
    )
    
    # Store the product being edited in context
    context.user_data['editing_product_desc'] = product_name
    
    keyboard = [[InlineKeyboardButton("🔙 Cancel", callback_data='admin_manage_products')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_description_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process the product description update"""
    if update.effective_user.username != ADMIN_USERNAME:
        return
    
    new_description = update.message.text.strip()
    product_name = context.user_data.get('editing_product_desc')
    
    if not product_name or product_name not in PRODUCT_CATALOG:
        await update.message.reply_text(
            "❌ Error: Product not found or edit session expired.\nPlease try again from the product management menu."
        )
        return
    
    # Update the product description
    PRODUCT_CATALOG[product_name]['description'] = new_description
    
    # Save the updated catalog to file
    save_data()
    
    # Clear the editing state
    del context.user_data['editing_product_desc']
    
    confirmation = (
        "✅ *Product Description Updated Successfully* ✅\n\n"
        f"Product: {product_name}\n"
        f"New Description: {new_description}\n\n"
        "The description has been updated successfully."
    )
    
    keyboard = [
        [InlineKeyboardButton("📋 Back to Products", callback_data='admin_manage_products')],
        [InlineKeyboardButton("🏠 Admin Panel", callback_data='admin_panel')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(confirmation, reply_markup=reply_markup, parse_mode='Markdown')

# Update handle_callback to include product management
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all callback queries"""
    query = update.callback_query
    
    # Admin panel callbacks
    if query.data.startswith('admin_'):
        if update.effective_user.username != ADMIN_USERNAME:
            await query.answer("⚠️ Access denied: Admin only", show_alert=True)
            return
        if query.data == 'admin_panel':
            await admin_panel(update, context)
        elif query.data == 'admin_create_product':
            await admin_create_product(update, context)
        elif query.data == 'admin_view_orders':
            context.user_data['admin_order_page'] = 0
            await admin_view_orders(update, context)
        elif query.data == 'admin_manage_products':
            await admin_manage_products(update, context)
        elif query.data.startswith('admin_edit_product_'):
            await admin_edit_product(update, context)
        elif query.data.startswith('admin_edit_desc_'):
            await admin_edit_description(update, context)
        elif query.data.startswith('admin_edit_image_'):
            await admin_edit_image(update, context)
        elif query.data in ['admin_next_page', 'admin_prev_page']:
            await admin_handle_navigation(update, context)
        elif query.data.startswith('admin_update_status_'):
            await admin_update_status(update, context)
        elif query.data.startswith('admin_set_status_'):
            await admin_set_status(update, context)
        elif query.data == 'admin_stats':
            await admin_stats(update, context)
        elif query.data.startswith('admin_delete_confirm_'):
            await admin_delete_order_confirm(update, context)
        elif query.data.startswith('admin_delete_order_'):
            await admin_delete_order(update, context)
        elif query.data == 'admin_delete_all_confirm':
            await admin_delete_all_confirm(update, context)
        elif query.data == 'admin_delete_all_orders':
            await admin_delete_all_orders(update, context)
        return
    
    # User order navigation
    if query.data in ['user_next_page', 'user_prev_page']:
        await handle_user_order_navigation(update, context)
        return
    
    # Existing callback handlers
    if query.data == 'start':
        await send_main_menu(update, context, is_callback=True)
    elif query.data == 'help':
        await help_command(update, context)
    elif query.data == 'view_products':
        await view_products(update, context)
    elif query.data in ['next_product', 'prev_product']:
        await handle_product_navigation(update, context)
    elif query.data.startswith('view_personal_'):
        await view_product_weights(update, context, 'personal')
    elif query.data.startswith('view_bulk_'):
        await view_product_weights(update, context, 'bulk')
    elif query.data.startswith('view_wholesale_'):
        await view_product_weights(update, context, 'wholesale')
    elif query.data == 'view_cart':
        await view_cart(update, context)
    elif query.data == 'clear_cart':
        await clear_cart(update, context)
    elif query.data == 'checkout':
        await start_checkout(update, context)
    elif query.data in ['payment_btc', 'payment_xmr']:
        await handle_payment_selection(update, context)
    elif query.data == 'confirm_payment':
        await confirm_payment(update, context)
    elif query.data == 'view_orders':
        context.user_data['user_order_page'] = 0  # Reset page when viewing orders
        await view_orders(update, context)
    elif query.data == 'update_shipping':
        await update_shipping(update, context)
    elif query.data.startswith('update_shipping_'):
        await start_shipping_update(update, context)
    elif query.data == 'lab_results':
        await view_lab_results(update, context)
    elif query.data.startswith('add_to_cart_'):
        await add_to_cart(update, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Route text messages to appropriate handlers"""
    user_id = update.effective_user.id
    
    # Handle product description update
    if update.effective_user.username == ADMIN_USERNAME and 'editing_product_desc' in context.user_data:
        await handle_description_update(update, context)
        return
    
    # Handle product name update
    if update.effective_user.username == ADMIN_USERNAME and 'editing_product' in context.user_data:
        await handle_product_name_update(update, context)
        return
    
    # Handle product image update
    if update.effective_user.username == ADMIN_USERNAME and 'editing_product_image' in context.user_data:
        await handle_product_image_update(update, context)
        return
    
    # Handle shipping update
    if 'updating_order' in context.user_data:
        await handle_shipping_update(update, context)
    # Handle initial shipping info during checkout
    elif user_id in CHECKOUT_STEPS and CHECKOUT_STEPS[user_id]['step'] == 'shipping':
        await handle_shipping_info(update, context)

    # Insert the following code after 'user_id = update.effective_user.id' in the handle_message function
    if update.effective_user.username == ADMIN_USERNAME and 'creating_new_product' in context.user_data:
        creation_data = context.user_data['creating_new_product']
        current_step = creation_data.get('step')
        text = update.message.text.strip()
        if current_step == 'name':
            creation_data['name'] = text
            creation_data['step'] = 'description'
            await update.message.reply_text("Please enter the product *DESCRIPTION*:", parse_mode='Markdown')
            return
        elif current_step == 'description':
            creation_data['description'] = text
            creation_data['step'] = 'image'
            await update.message.reply_text("Please enter the product *IMAGE URL* (must start with http:// or https://):", parse_mode='Markdown')
            return
        elif current_step == 'image':
            creation_data['image'] = text
            creation_data['step'] = 'pricing'
            await update.message.reply_text("Please enter the *PRICING INFORMATION* in the following format:\n\nweight,price,unit,description; weight,price,unit,description; ...", parse_mode='Markdown')
            return
        elif current_step == 'pricing':
            pricing_text = text
            pricing_dict = {}
            entries = pricing_text.split(';')
            for entry in entries:
                entry = entry.strip()
                if not entry:
                    continue
                parts = entry.split(',')
                if len(parts) != 4:
                    await update.message.reply_text("Invalid pricing format. Each entry must have 4 comma-separated values: weight,price,unit,description.")
                    return
                weight = parts[0].strip()
                try:
                    price = float(parts[1].strip())
                except Exception:
                    await update.message.reply_text("Invalid price value. Please enter a number for the price.")
                    return
                unit = parts[2].strip()
                desc = parts[3].strip()
                pricing_dict[weight] = {"weight": float(weight), "price": price, "unit": unit, "description": desc}
            creation_data['pricing'] = pricing_dict
            product_name = creation_data['name']
            if product_name in PRODUCT_CATALOG:
                await update.message.reply_text(f"A product with the name '{product_name}' already exists. Please try again with a different name.")
                return
            PRODUCT_CATALOG[product_name] = {
                "name": product_name,
                "description": creation_data['description'],
                "type": "Custom",
                "thc": "N/A",
                "prices": pricing_dict
            }
            PRODUCT_IMAGES[product_name] = creation_data['image']
            save_data()
            del context.user_data['creating_new_product']
            await update.message.reply_text(f"✅ Product '{product_name}' created successfully!")
            return

def save_data():
    """Save orders, carts, and product catalog to files"""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    try:
        # Save orders with proper formatting
        with open(ORDERS_FILE, 'w') as f:
            # Convert user IDs to strings for JSON serialization
            orders_data = {str(k): v for k, v in USER_ORDERS.items()}
            json.dump(orders_data, f, indent=2)
        
        # Save carts with proper formatting
        with open(CARTS_FILE, 'w') as f:
            # Convert user IDs to strings for JSON serialization
            carts_data = {str(k): v for k, v in SHOPPING_CARTS.items()}
            json.dump(carts_data, f, indent=2)
            
        # Save product catalog
        with open(CATALOG_FILE, 'w') as f:
            json.dump({
                'catalog': PRODUCT_CATALOG,
                'images': PRODUCT_IMAGES
            }, f, indent=2)
            
    except Exception as e:
        logger.error(f"Error saving data: {e}")

def load_data():
    """Load orders, carts, and product catalog from files"""
    global USER_ORDERS, SHOPPING_CARTS, PRODUCT_CATALOG, PRODUCT_IMAGES
    
    try:
        # Load orders
        if os.path.exists(ORDERS_FILE):
            with open(ORDERS_FILE, 'r') as f:
                orders_data = json.load(f)
                # Convert user IDs back to integers
                USER_ORDERS = {int(k): v for k, v in orders_data.items()}
        else:
            USER_ORDERS = {}
        
        # Load carts
        if os.path.exists(CARTS_FILE):
            with open(CARTS_FILE, 'r') as f:
                carts_data = json.load(f)
                # Convert user IDs back to integers
                SHOPPING_CARTS = {int(k): v for k, v in carts_data.items()}
        else:
            SHOPPING_CARTS = {}
            
        # Initialize PRODUCT_CATALOG and PRODUCT_IMAGES
        PRODUCT_CATALOG.clear()
        PRODUCT_IMAGES.clear()
        
        if os.path.exists(CATALOG_FILE):
            with open(CATALOG_FILE, 'r') as f:
                catalog_data = json.load(f)
            # Use the saved catalog if available
            if 'catalog' in catalog_data and isinstance(catalog_data['catalog'], dict):
                PRODUCT_CATALOG.update(catalog_data['catalog'])
            else:
                # Log warning but do not overwrite saved changes
                logger.warning("Catalog file exists but no valid 'catalog' key found.")
            
            if 'images' in catalog_data and isinstance(catalog_data['images'], dict):
                PRODUCT_IMAGES.update(catalog_data['images'])
            else:
                logger.warning("Catalog file exists but no valid 'images' key found.")
            
            logger.info(f"Loaded product catalog from file: {PRODUCT_CATALOG}")
        else:
            # No catalog file exists, use defaults
            PRODUCT_CATALOG.update(DEFAULT_PRODUCT_CATALOG)
            PRODUCT_IMAGES.update(DEFAULT_PRODUCT_IMAGES)
            logger.info("No catalog file found; using default product catalog.")
                
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        PRODUCT_CATALOG.update(DEFAULT_PRODUCT_CATALOG)
        PRODUCT_IMAGES.update(DEFAULT_PRODUCT_IMAGES)

# New function to start editing the product image
async def admin_edit_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.username != ADMIN_USERNAME:
        return
    query = update.callback_query
    await query.answer()
    # Extract product name from callback data
    product_name = '_'.join(query.data.split('_')[3:])  # Get everything after 'admin_edit_image_'
    current_image = PRODUCT_IMAGES.get(product_name, 'No image set.')
    message = (
        f"🖼 *Edit Image for: {product_name}* 🖼\n\n"
        f"*Current Image URL:*\n{current_image}\n\n"
        "Please send the new image URL for this product.\n"
        "Ensure the URL starts with http:// or https://"
    )
    context.user_data['editing_product_image'] = product_name
    keyboard = [[InlineKeyboardButton("🔙 Cancel", callback_data='admin_manage_products')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')


# New function to handle the product image update
async def handle_product_image_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.username != ADMIN_USERNAME:
        return
    new_image_url = update.message.text.strip()
    product_name = context.user_data.get('editing_product_image')
    if not product_name or product_name not in PRODUCT_CATALOG:
        await update.message.reply_text(
            "❌ Error: Product not found or edit session expired.\nPlease try again from the product management menu."
        )
        return
    # Update the product image URL
    PRODUCT_IMAGES[product_name] = new_image_url
    save_data()
    del context.user_data['editing_product_image']
    confirmation = (
        "✅ *Product Image Updated Successfully* ✅\n\n"
        f"Product: {product_name}\n"
        f"New Image URL: {new_image_url}\n\n"
        "The image has been updated successfully."
    )
    keyboard = [
        [InlineKeyboardButton("📋 Back to Products", callback_data='admin_manage_products')],
        [InlineKeyboardButton("🏠 Admin Panel", callback_data='admin_panel')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(confirmation, reply_markup=reply_markup, parse_mode='Markdown')

# New function to initiate product creation
async def admin_create_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Initiate new product creation process for admin."""
    if update.effective_user.username != ADMIN_USERNAME:
        return
    # Set up creation state
    context.user_data['creating_new_product'] = { 'step': 'name' }
    # Respond to admin asking for the product name
    # Use callback if available, else send a message
    if update.callback_query:
        await update.callback_query.edit_message_text(
            """➕ *Create New Product*

Please enter the product *NAME*:"""
        )
    else:
        await update.message.reply_text(
            """➕ *Create New Product*

Please enter the product *NAME*:""",
            parse_mode='Markdown'
        )

def main():
    """Start the bot."""
    token = os.getenv('TELEGRAM_TOKEN')
    if not token:
        logger.error("No token found! Make sure to set TELEGRAM_TOKEN environment variable.")
        return

    # Load saved data
    load_data()

    application = Application.builder().token(token).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    # Update message handler to use the new routing function
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message
    ))

    # Start the Bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main() 