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
PRODUCT_CATALOG = {
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

# Add this after PRODUCT_CATALOG declaration
PRODUCT_IMAGES = {
    "Blue Dream": "https://i.imgur.com/CsY7GcA.png",
    "OG Kush": "https://i.imgur.com/47uY36h.png",
    "Purple Haze": "https://i.imgur.com/N9QS7tq.png",
    "Northern Lights": "https://i.imgur.com/pZEcGUf.png"
}

# Shopping cart storage (in-memory for demonstration)
SHOPPING_CARTS = {}

# Add this after SHOPPING_CARTS declaration
CHECKOUT_STEPS = {}  # Store checkout progress for users
SHIPPING_INFO = {}   # Store shipping information

# Add these after the existing storage declarations
USER_ORDERS = {}  # Store order history for users

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
        f"*Type:* {current_product['type']}\n"
        f"*THC:* {current_product['thc']}\n\n"
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
    
    weights = {
        'personal': ["0.5", "1", "3.5", "7"],
        'bulk': ["14", "28", "56"],
        'wholesale': ["112", "224", "448"]
    }[category]
    
    keyboard = []
    for weight in weights:
        details = product['prices'][weight]
        cart_quantity = cart.get(f"{product_name}_{weight}", 0)
        quantity_text = f" ({cart_quantity}x)" if cart_quantity > 0 else ""
        keyboard.append([InlineKeyboardButton(
            f"{weight}g - {format_price(details['price'])}{quantity_text}",
            callback_data=f'add_to_cart_{product_name}_{weight}'
        )])
    
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
    
    # Create order
    order = {
        'order_id': CHECKOUT_STEPS[user_id]['order_id'],
        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'status': 'pending',
        'total': total,
        'items': dict(cart),
        'payment_method': payment_method,
        'shipping_info': CHECKOUT_STEPS[user_id]['shipping_info']
    }
    
    # Save order to user's history
    if user_id not in USER_ORDERS:
        USER_ORDERS[user_id] = []
    USER_ORDERS[user_id].append(order)
    
    # Update checkout step
    CHECKOUT_STEPS[user_id]['step'] = 'confirm_payment'
    
    # Simulate crypto addresses
    btc_address = "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"
    xmr_address = "44AFFq5kSiGBoZ4NMDwYtN18obc8AemS33DBLWs3H7otXft3XjrpDtQGv7SqSsaBYBb98uNbr2VBBEt7f2wfn3RVGQBEP3A"
    
    payment_message = (
        "💳 *Payment Details*\n"
        "─────────────────\n\n"
        f"*Order ID:* `{order['order_id']}`\n\n"
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
    
    order_id = CHECKOUT_STEPS[user_id]['order_id']
    
    # Find the order and update its status
    for order in USER_ORDERS[user_id]:
        if order['order_id'] == order_id:
            order['status'] = 'processing'
            
            confirmation_message = (
                "🎉 *Order Successfully Placed!* 🎉\n"
                "─────────────────\n\n"
                f"*Order ID:* `{order_id}`\n\n"
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
            
            # Clear cart and checkout data
            SHOPPING_CARTS[user_id] = {}
            del CHECKOUT_STEPS[user_id]
            break

async def view_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display user's order history"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    orders = USER_ORDERS.get(user_id, [])
    
    if not orders:
        orders_message = (
            "📦 *Your Order History* 📦\n\n"
            "*Recent Orders:*\n"
            "No orders found in your history yet.\n\n"
            "Start shopping to create your first order!"
        )
        
        keyboard = [
            [InlineKeyboardButton(" Start Shopping", callback_data='view_products')],
            [InlineKeyboardButton("🔙 Return to Main Menu", callback_data='start')]
        ]
    else:
        orders_message = "📦 *Your Order History* 📦\n\n"
        
        # Show last 5 orders
        for order in orders[-5:]:
            status_emoji = {
                'pending': '⏳',
                'processing': '🔄',
                'shipped': '🚚',
                'delivered': '✅',
                'cancelled': '❌'
            }.get(order['status'], '⏳')
            
            orders_message += (
                f"*Order ID:* `{order['order_id']}`\n"
                f"*Date:* {order['date']}\n"
                f"*Status:* {status_emoji} {order['status'].title()}\n"
                f"*Total:* {format_price(order['total'])}\n\n"
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
        
        # Order history buttons
        keyboard = [
            [InlineKeyboardButton("Update Shipping", callback_data='update_shipping')],
            [InlineKeyboardButton("New Order", callback_data='view_products')],
            [InlineKeyboardButton("↩️ Menu", callback_data='start')]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(orders_message, reply_markup=reply_markup, parse_mode='Markdown')

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

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all callback queries"""
    query = update.callback_query
    
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
    
    # Handle shipping update
    if 'updating_order' in context.user_data:
        await handle_shipping_update(update, context)
    # Handle initial shipping info during checkout
    elif user_id in CHECKOUT_STEPS and CHECKOUT_STEPS[user_id]['step'] == 'shipping':
        await handle_shipping_info(update, context)

def main():
    """Start the bot."""
    token = os.getenv('TELEGRAM_TOKEN')
    if not token:
        logger.error("No token found! Make sure to set TELEGRAM_TOKEN environment variable.")
        return

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