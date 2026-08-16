import os
import json
import time
import random
import requests
import html as _html
from datetime import datetime
from flask import Flask, request
from telebot import TeleBot, types
from telebot.types import MessageEntity, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID", "8471373583"))
ADMIN_IDS = [OWNER_ID]
PORT = int(os.environ.get("PORT", 10000))

if not BOT_TOKEN:
    print("❌ ERROR: BOT_TOKEN not set!")
    exit(1)

print("✅ Bot token loaded!")

bot = TeleBot(BOT_TOKEN, threaded=False)
app = Flask(__name__)

# ============================================================
# FILES & DATA
# ============================================================
USERS_FILE = "users.json"
ORDERS_FILE = "orders.json"
PENDING_FILE = "pending.json"
SETTINGS_FILE = "settings.json"

bot_active = True

# ============================================================
# EMOJI MAPPING
# ============================================================
EMOJI_MAPPING = {
    "✅": ["6246537187614005254", "6246782404476803545", "6010060634803148161", "6010498532488778300"],
    "✔️": ["6246871001062185760", "6010264538375525668", "6010487760710800947"],
    "☑️": ["6246537187614005254", "6010097953773983121"],
    "👁️": ["6035338338406242050", "6035051267087143217", "6034945975963881533", "6034845323405299835"],
    "🔥": ["4956222745814762495", "4956606007221421405", "4956429969396859866", "6086954744268460848"],
    "💥": ["6032673796530377389", "4958479549265347295"],
    "⚡": ["5791970059597386804", "6087079590377820415", "6095843123252957701"],
    "❤️": ["5783157259152397008", "5801084710343938087", "6010280773351904888"],
    "💙": ["5780496071645991525", "6104780447684757396"],
    "💚": ["5888789252493283486"],
    "💛": ["5840261097719148872"],
    "🧡": ["5840263144212529797"],
    "💜": ["5840265018655703965"],
    "🖤": ["5840266939932994956"],
    "⭐": ["6244496562752331516", "5904618938578243567", "6010193314932855525"],
    "🌟": ["6010156854955480259", "6086924086791902713"],
    "✨": ["6010338729640596556", "6010086134023985536", "5801044672658805468"],
    "👑": ["5794422335599546668", "6089003761496232797", "6247039939305808563"],
    "💰": ["6089104607328342288", "6086730718774300509", "6086664791026307819"],
    "💎": ["6086778246882399112", "5791697221799907788"],
    "👍": ["6089313931149448495", "4958626617535497157", "4956582500865410174"],
}

FLAG_MAPPING = {
    "🇮🇳": "5433601609076586221", "🇺🇸": "5433865586356531140", "🇬🇧": "5433827537241258614",
}

# ============================================================
# STYLISH TEXT
# ============================================================
def stylish_text(text: str) -> str:
    stylish_chars = {
        'A': 'ᴀ', 'B': 'ʙ', 'C': 'ᴄ', 'D': 'ᴅ', 'E': 'ᴇ', 'F': 'ꜰ', 'G': 'ɢ',
        'H': 'ʜ', 'I': 'ɪ', 'J': 'ᴊ', 'K': 'ᴋ', 'L': 'ʟ', 'M': 'ᴍ', 'N': 'ɴ',
        'O': 'ᴏ', 'P': 'ᴘ', 'Q': 'ǫ', 'R': 'ʀ', 'S': 'ꜱ', 'T': 'ᴛ', 'U': 'ᴜ',
        'V': 'ᴠ', 'W': 'ᴡ', 'X': 'x', 'Y': 'ʏ', 'Z': 'ᴢ',
        'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ꜰ', 'g': 'ɢ',
        'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ',
        'o': 'ᴏ', 'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ', 's': 'ꜱ', 't': 'ᴛ', 'u': 'ᴜ',
        'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ', 'z': 'ᴢ',
        '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
        '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉'
    }
    result = ""
    for char in text:
        result += stylish_chars.get(char, char)
    return result

# ============================================================
# EMOJI HELPERS
# ============================================================
def _utf16_len(ch: str) -> int:
    return len(ch.encode("utf-16-le")) // 2

def _utf16_len_str(s: str) -> int:
    return len(s.encode("utf-16-le")) // 2

def _build_pe_entities(text: str):
    entities = []
    utf16_offset = 0
    total_utf16 = _utf16_len_str(text)
    
    if total_utf16 > 0:
        entities.append(MessageEntity(type="bold", offset=0, length=total_utf16))
    
    i = 0
    while i < len(text):
        ch = text[i]
        ch_len = _utf16_len(ch)
        
        if ch in EMOJI_MAPPING:
            eid = int(random.choice(EMOJI_MAPPING[ch]))
            entities.append(MessageEntity(
                type="custom_emoji",
                offset=utf16_offset,
                length=ch_len,
                custom_emoji_id=eid
            ))
        elif ch in FLAG_MAPPING:
            eid = int(FLAG_MAPPING[ch])
            entities.append(MessageEntity(
                type="custom_emoji",
                offset=utf16_offset,
                length=ch_len,
                custom_emoji_id=eid
            ))
        utf16_offset += ch_len
        i += 1
    
    return entities

def _send_pe(chat_id, text: str, reply_markup=None):
    try:
        entities = _build_pe_entities(text)
        return bot.send_message(chat_id, text, entities=entities, reply_markup=reply_markup, parse_mode=None)
    except:
        return bot.send_message(chat_id, text, reply_markup=reply_markup)

# ============================================================
# GREEN BUTTONS (Full Green - No Dots)
# ============================================================
def make_green_button(text: str, callback: str = None, url: str = None):
    final_text = stylish_text(text)
    try:
        if callback:
            return InlineKeyboardButton(text=final_text, style="success", callback_data=callback)
        elif url:
            return InlineKeyboardButton(text=final_text, style="success", url=url)
        else:
            return InlineKeyboardButton(text=final_text, style="success")
    except:
        if callback:
            return InlineKeyboardButton(text=final_text, callback_data=callback)
        elif url:
            return InlineKeyboardButton(text=final_text, url=url)
        else:
            return InlineKeyboardButton(text=final_text)

# ============================================================
# DATA FUNCTIONS
# ============================================================
def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    users = {
        "8471373583": {"id": 8471373583, "username": "iflexzyan", "name": "ZYAN", "joined": datetime.now().isoformat(), "uses": 0, "unlimited": True, "banned": False, "ban_paid": True},
    }
    save_users(users)
    return users

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def load_data(file, default=None):
    if default is None:
        default = {}
    if os.path.exists(file):
        try:
            with open(file, "r") as f:
                return json.load(f)
        except:
            return default
    return default

def save_data(file, data):
    try:
        with open(file, "w") as f:
            json.dump(data, f, indent=2)
    except:
        pass

def load_orders():
    return load_data(ORDERS_FILE)

def save_orders(orders):
    save_data(ORDERS_FILE, orders)

def load_pending():
    return load_data(PENDING_FILE)

def save_pending(pending):
    save_data(PENDING_FILE, pending)

def load_settings():
    default = {
        "price": 99,
        "upi": "vanshx111@naviaxis",
        "free_trial": True,
        "bot_name": "FF BAN BOT",
        "developer": "@iflexzyan",
        "support": "@iflexzyan",
        "welcome_image": "https://iili.io/C8DNTyQ.jpg",
        "token_text": "1️⃣ Open Free Fire\n2️⃣ Go to Settings\n3️⃣ Click Account\n4️⃣ Find Data Access\n5️⃣ Copy Token",
        "ban_price": 0,
        "number_info_price": 0
    }
    data = load_data(SETTINGS_FILE)
    for key, val in default.items():
        if key not in data:
            data[key] = val
    return data

def save_settings(settings):
    save_data(SETTINGS_FILE, settings)

def is_admin(user_id):
    return user_id in ADMIN_IDS

def register_user(user_id, username=None, first_name=None):
    users = load_users()
    if str(user_id) not in users:
        users[str(user_id)] = {
            "id": user_id,
            "username": username,
            "name": first_name or "Unknown",
            "joined": datetime.now().isoformat(),
            "uses": 0,
            "unlimited": False,
            "banned": False,
            "ban_paid": False,
            "number_info_paid": False
        }
        save_users(users)
        notify_owner(f"✅ ɴᴇᴡ ᴜsᴇʀ ᴊᴏɪɴᴇᴅ!\n👤 ɪᴅ: {user_id}\n👾 @{username or 'N/A'}")
    return users[str(user_id)]

def get_user(user_id):
    users = load_users()
    return users.get(str(user_id))

def update_user(user_id, key, value):
    users = load_users()
    if str(user_id) in users:
        users[str(user_id)][key] = value
        save_users(users)

def notify_owner(msg):
    try:
        bot.send_message(OWNER_ID, msg)
    except:
        pass

def send_chunked(chat_id, text):
    for i in range(0, len(text), 3800):
        _send_pe(chat_id, text[i:i + 3800])

# ============================================================
# STYLISH PERCENT
# ============================================================
def stylish_percent(percent):
    mapping = {'0': '𝟶', '1': '𝟷', '2': '𝟸', '3': '𝟹', '4': '𝟺',
               '5': '𝟻', '6': '𝟼', '7': '𝟽', '8': '𝟾', '9': '𝟿'}
    return "".join(mapping.get(ch, ch) for ch in str(percent)) + "%"

# ============================================================
# PROCESSING ANIMATIONS
# ============================================================
def show_processing_animation(chat_id):
    steps = [
        ("🟩🟩⬜⬜⬜⬜⬜⬜⬜⬜", "𝟷𝟶%"),
        ("🟩🟩🟩🟩⬜⬜⬜⬜⬜⬜", "𝟸𝟿%"),
        ("🟩🟩🟩🟩🟩🟩⬜⬜⬜⬜", "𝟻𝟶%"),
        ("🟩🟩🟩🟩🟩🟩🟩🟩⬜⬜", "𝟽𝟻%"),
        ("🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩", "𝟷𝟶𝟶%"),
    ]
    msg = bot.send_message(chat_id, f"🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩\n\n🟢 𝟶%")
    for boxes, percent in steps:
        time.sleep(0.45)
        try:
            bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=f"{boxes}\n\n🟢 {percent}")
        except:
            pass
    return msg

def show_processing_animation_red(chat_id):
    steps = [
        ("🟥🟥⬜⬜⬜⬜⬜⬜⬜⬜", "𝟷𝟶%"),
        ("🟥🟥🟥🟥⬜⬜⬜⬜⬜⬜", "𝟸𝟿%"),
        ("🟥🟥🟥🟥🟥🟥⬜⬜⬜⬜", "𝟻𝟶%"),
        ("🟥🟥🟥🟥🟥🟥🟥🟥⬜⬜", "𝟽𝟻%"),
        ("🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥", "𝟷𝟶𝟶%"),
    ]
    msg = bot.send_message(chat_id, f"🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥\n\n🔴 𝟶%")
    for boxes, percent in steps:
        time.sleep(0.45)
        try:
            bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=f"{boxes}\n\n🔴 {percent}")
        except:
            pass
    return msg

def show_processing_animation_purple(chat_id):
    width = 10
    msg = None
    for i in range(width):
        row = ["⬜"] * width
        row[i] = "🟪"
        percent = int((i + 1) / width * 100)
        text = "".join(row) + f"\n\n🟣 {stylish_percent(percent)}"
        if msg is None:
            msg = bot.send_message(chat_id, text)
        else:
            try:
                bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=text)
            except:
                pass
        time.sleep(0.4)
    return msg

# ============================================================
# OWNER CREDIT CLEANUP
# ============================================================
def clean_owner_credit(data):
    credit_keys = {"owner", "credit", "credits", "developer", "creator", "made_by", "by", "channel",
                   "dev", "credit_by", "coded_by", "credit_to", "source", "api_owner", "admin"}
    if isinstance(data, dict):
        for key in list(data.keys()):
            if key.lower() in credit_keys:
                data.pop(key, None)
            elif isinstance(data[key], dict):
                clean_owner_credit(data[key])
        data["owner"] = "@iflexcoderr"
    return data

# ============================================================
# JSON RESPONSE
# ============================================================
def send_json_response(chat_id, data, uid_input, prefix="ban_check", clean=False):
    json_filename = f"{prefix}_{uid_input}.json"
    with open(json_filename, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    status = "unknown"
    if isinstance(data, dict):
        ban_info = data.get('ban_info', {})
        if isinstance(ban_info, dict):
            status = ban_info.get('status', 'unknown')
        elif ban_info:
            status = str(ban_info)
        elif 'status' in data:
            status = data.get('status', 'unknown')
    
    if "not banned" in str(status).lower():
        status_emoji = "🟢"
        status_word = "NOT BANNED ✅"
    elif "banned" in str(status).lower():
        status_emoji = "🔴"
        status_word = "BANNED ❌"
    else:
        status_emoji = "🟡"
        status_word = str(status).upper()
    
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    if len(json_str) > 3500:
        json_str = json_str[:3500] + "\n...TRUNCATED..."
    json_str = _html.escape(json_str)
    
    if clean:
        json_block = f"""🟢🔴 ═════════════════════════════ 🟢🔴

<pre>{json_str}</pre>

🟢🔴 ═════════════════════════════ 🟢🔴"""
    else:
        json_block = f"""🟢🔴 ═══《 📄 JSON RESPONSE 》═══ 🟢🔴

<pre>{json_str}</pre>

{status_emoji} Status: {status_word}
🟢🔴 ═══════════════════════"""
    
    try:
        bot.send_message(chat_id, json_block, parse_mode="HTML")
    except:
        _send_pe(chat_id, f"🟢🔴 JSON DATA\n\n<code>{json_str}</code>")
    
    try:
        with open(json_filename, "rb") as f:
            bot.send_document(chat_id, f, caption=f"🟢📄 JSON - {prefix}: {uid_input}")
    except:
        pass
    
    try:
        os.remove(json_filename)
    except:
        pass

# ============================================================
# STYLISH QR TEXT
# ============================================================
def get_stylish_qr_text(upi, price):
    random_emoji = random.choice(["⭐", "✨", "🔥", "💎", "👑", "💰", "💥", "🌟"])
    text = f"""
{random_emoji} ═══《 💰 ᴘᴀʏᴍᴇɴᴛ ɪɴꜰᴏ 》═══ {random_emoji}

{random_emoji} 💳 ᴜᴘɪ: {upi}
{random_emoji} 💰 ᴀᴍᴏᴜɴᴛ: ʀs.{price}

{random_emoji} ═══════════════════════ {random_emoji}

{random_emoji} 📱 ꜱᴄᴀɴ Qʀ ᴛᴏ ᴘᴀʏ

{random_emoji} ═══════════════════════ {random_emoji}

`{upi}`

{random_emoji} 👨‍💻 @ɪꜰʟᴇxᴢʏᴀɴ
{random_emoji} ᴛʜᴀɴᴋ ʏᴏᴜ ꜰᴏʀ ᴄʜᴏᴏꜱɪɴɢ ᴜꜱ! ⭐
"""
    return text

# ============================================================
# USER MENU - FULL GREEN (NO DOTS)
# ============================================================
def get_user_menu(user_id):
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.row(KeyboardButton(stylish_text("BAN ACCOUNT")))
    markup.row(KeyboardButton(stylish_text("FREE TRIAL")), KeyboardButton(stylish_text("UNLIMITED")))
    markup.row(KeyboardButton(stylish_text("BAN CHECK")), KeyboardButton(stylish_text("NUMBER INFO")))
    markup.row(KeyboardButton(stylish_text("PLAYER INFO")), KeyboardButton(stylish_text("HOW TO GET TOKEN")))
    markup.row(KeyboardButton(stylish_text("SUPPORT")), KeyboardButton(stylish_text("HELP")))
    markup.row(KeyboardButton(stylish_text("ABOUT")))
    return markup

# ============================================================
# ADMIN MENU - FULL GREEN (NO DOTS)
# ============================================================
def get_admin_menu(user_id):
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.row(KeyboardButton(stylish_text("BOT OFF")), KeyboardButton(stylish_text("BOT ON")))
    markup.row(KeyboardButton(stylish_text("ADMIN PANEL")), KeyboardButton(stylish_text("STATS")))
    markup.row(KeyboardButton(stylish_text("TOTAL BANS")), KeyboardButton(stylish_text("USERS")))
    markup.row(KeyboardButton(stylish_text("DATA")), KeyboardButton(stylish_text("CHECK ALL")))
    markup.row(KeyboardButton(stylish_text("TOTAL ADMINS")), KeyboardButton(stylish_text("PRICE")))
    markup.row(KeyboardButton(stylish_text("UPI")), KeyboardButton(stylish_text("ADD ADMIN")))
    markup.row(KeyboardButton(stylish_text("ALL COMMANDS")), KeyboardButton(stylish_text("HOW TO GET TOKEN")))
    markup.row(KeyboardButton(stylish_text("BROADCAST")), KeyboardButton(stylish_text("ALL BROADCAST")))
    markup.row(KeyboardButton(stylish_text("SET WELCOME IMAGE")), KeyboardButton(stylish_text("SET TOKEN TEXT")))
    markup.row(KeyboardButton(stylish_text("ADD TOKEN VIDEO")), KeyboardButton(stylish_text("SET BAN PRICE")))
    markup.row(KeyboardButton(stylish_text("SET BAN FREE")), KeyboardButton(stylish_text("SET NUMBER INFO PRICE")))
    markup.row(KeyboardButton(stylish_text("SET NUMBER INFO FREE")))
    return markup

# ============================================================
# START COMMAND
# ============================================================
@bot.message_handler(commands=['start'])
def start_cmd(message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username
        first_name = message.from_user.first_name
        
        settings = load_settings()
        price = settings.get("price", 99)
        developer = settings.get("developer", "@iflexzyan")
        welcome_image = settings.get("welcome_image", "https://iili.io/C8DNTyQ.jpg")
        
        user = register_user(user_id, username, first_name)
        
        if user.get("banned", False):
            _send_pe(message.chat.id, "❌ ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ!")
            return
        
        try:
            bot.send_photo(message.chat.id, photo=welcome_image)
        except:
            pass
        
        welcome_text = f"""
⭐ ═══《 🔥 ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ғғ ʙᴀɴ ʙᴏᴛ 》═══ ⭐

⭐ 👤 ᴜsᴇʀ: {first_name}
⭐ 🆔 ɪᴅ: {user_id}
⭐ 👾 ᴜsᴇʀɴᴀᴍᴇ: @{username or 'N/A'}

⭐ ═══════════════════════ ⭐

⭐ 🎯 𝟷 ғʀᴇᴇ ᴛʀɪᴀʟ - ʙᴀɴ 𝟷 ᴀᴄᴄᴏᴜɴᴛ
⭐ 💰 ᴜɴʟɪᴍɪᴛᴇᴅ ᴀᴄᴄᴇss - ʀs.{price}
⭐ 🔍 BAN CHECK - Check UID status
⭐ 📱 NUMBER INFO - Number details
⭐ 🎮 PLAYER INFO - UID details

⭐ ═══════════════════════ ⭐

⭐ 👨‍💻 ᴅᴇᴠᴇʟᴏᴘᴇʀ: {developer}

⭐ ═══════════════════════ ⭐
"""
        
        if is_admin(user_id):
            markup = get_admin_menu(user_id)
        else:
            markup = get_user_menu(user_id)
        
        _send_pe(message.chat.id, welcome_text, reply_markup=markup)
    except Exception as e:
        print(f"❌ Start error: {e}")

# ============================================================
# BAN ACCOUNT
# ============================================================
user_tokens = {}

@bot.message_handler(func=lambda m: m.text and stylish_text("BAN ACCOUNT") in m.text)
def ban_account_start(message):
    try:
        user_id = message.from_user.id
        user = get_user(user_id)
        
        if not user or user.get("banned", False):
            _send_pe(message.chat.id, "❌ ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ!")
            return
        
        if not user.get("unlimited", False):
            uses = user.get("uses", 0)
            if uses >= 1:
                _send_pe(message.chat.id, f"⚠️ ғʀᴇᴇ ᴛʀɪᴀʟ ᴜsᴇᴅ!\n💰 ᴘᴀʏ ʀs.{load_settings().get('price', 99)}")
                send_payment_qr(message.chat.id)
                return
        
        _send_pe(message.chat.id, "🔑 sᴇɴᴅ ᴛʜᴇ ᴀᴄᴄᴇss ᴛᴏᴋᴇɴ:")
        bot.register_next_step_handler(message, get_ban_token)
    except Exception as e:
        print(f"❌ Ban start error: {e}")

def get_ban_token(message):
    try:
        user_id = message.from_user.id
        token = message.text.strip()
        
        if len(token) < 30:
            _send_pe(message.chat.id, "❌ ɪɴᴠᴀʟɪᴅ ᴛᴏᴋᴇɴ!")
            return
        
        user_tokens[user_id] = token
        
        keyboard = [
            [make_green_button("YES, I AM 100% SURE", callback=f"confirm_ban_{user_id}")],
            [make_green_button("NO, CANCEL", callback="cancel_ban")]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        
        _send_pe(message.chat.id, """
⚠️ ═══《 ⚠️ ᴄᴏɴғɪʀᴍᴀᴛɪᴏɴ 》═══ ⚠️

⚠️ ᴀʀᴇ ʏᴏᴜ 𝟷𝟶𝟶% sᴜʀᴇ?

⚠️ ᴛʜɪs ᴀᴄᴛɪᴏɴ ᴄᴀɴɴᴏᴛ ʙᴇ ᴜɴᴅᴏɴᴇ!

⚠️ ═══════════════════════ ⚠️
""", reply_markup=markup)
    except Exception as e:
        print(f"❌ Get token error: {e}")

@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("confirm_ban_"))
def confirm_ban_callback(call):
    try:
        user_id = int(call.data.split("_")[2])
        if call.from_user.id != user_id:
            _send_pe(call.message.chat.id, "❌ ɴᴏᴛ ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ!")
            bot.answer_callback_query(call.id)
            return
        
        token = user_tokens.pop(user_id, None)
        if not token:
            _send_pe(call.message.chat.id, "❌ sᴇssɪᴏɴ ᴇxᴘɪʀᴇᴅ!")
            bot.answer_callback_query(call.id)
            return
        
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        
        anim_msg = show_processing_animation(call.message.chat.id)
        
        try:
            url = f"https://ffidbanapi.vercel.app/ban-account?access-token={token}&key=ANIXH"
            response = requests.get(url, timeout=30)
            data = response.json()
            
            account_id = data.get('id', 'N/A')
            account_name = data.get('name', 'N/A')
            account_uid = data.get('uid', 'N/A')
            status = data.get('status', 'UNKNOWN')
            
            is_banned = "BANNED" in str(status).upper()
            
            try:
                bot.delete_message(call.message.chat.id, anim_msg.message_id)
            except:
                pass
            
            if is_banned:
                user = get_user(user_id)
                if user:
                    uses = user.get("uses", 0) + 1
                    update_user(user_id, "uses", uses)
                
                orders = load_orders()
                orders[f"{int(time.time())}_{len(orders) + 1}"] = {
                    "user_id": user_id,
                    "uid": account_uid,
                    "name": account_name,
                    "time": datetime.now().isoformat()
                }
                save_orders(orders)
                
                result_text = f"""
⭐ ═══《 ✅ ᴀᴄᴄᴏᴜɴᴛ ʙᴀɴɴᴇᴅ 》═══ ⭐

⭐ 🎯 ʙᴀɴ sᴜᴄᴄᴇssғᴜʟ!

⭐ ═══════════════════════ ⭐

⭐ 🆔 ɪᴅ: {account_id}
⭐ 👤 ɴᴀᴍᴇ: {account_name}
⭐ 🔢 ᴜɪᴅ: {account_uid}

⭐ ═══════════════════════ ⭐

⭐ 👨‍💻 @ɪꜰʟᴇxᴢʏᴀɴ
⭐ ᴛʜᴀɴᴋ ʏᴏᴜ ꜰᴏʀ ᴜꜱɪɴɢ ᴏᴜʀ ʙᴏᴛ! ⭐
"""
                keyboard = [
                    [make_green_button("BAN ANOTHER", callback="ban_another")],
                    [make_green_button("GET UNLIMITED", callback="get_unlimited")]
                ]
                markup = InlineKeyboardMarkup(keyboard)
                _send_pe(call.message.chat.id, result_text, reply_markup=markup)
                notify_owner(f"✅ ʙᴀɴɴᴇᴅ!\n👤 {user_id}\n🔢 {account_uid}")
            else:
                result_text = f"""
⭐ ═══《 ❌ ʙᴀɴ ғᴀɪʟᴇᴅ 》═══ ⭐

⭐ ❌ ɴᴏᴛ ʙᴀɴɴᴇᴅ!

⭐ 🆔 ɪᴅ: {account_id}
⭐ 👤 ɴᴀᴍᴇ: {account_name}
⭐ 🔢 ᴜɪᴅ: {account_uid}
⭐ 📌 sᴛᴀᴛᴜs: {status}

⭐ ═══════════════════════ ⭐

⭐ 👨‍💻 @ɪꜰʟᴇxᴢʏᴀɴ
"""
                _send_pe(call.message.chat.id, result_text)
        except Exception as e:
            try:
                bot.delete_message(call.message.chat.id, anim_msg.message_id)
            except:
                pass
            _send_pe(call.message.chat.id, f"❌ ᴇʀʀᴏʀ: {str(e)}")
        
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"❌ Confirm ban error: {e}")

@bot.callback_query_handler(func=lambda c: c.data == "cancel_ban")
def cancel_ban_callback(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    _send_pe(call.message.chat.id, "✅ ᴄᴀɴᴄᴇʟʟᴇᴅ!")
    user_tokens.pop(call.from_user.id, None)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == "ban_another")
def ban_another_callback(call):
    try:
        user_id = call.from_user.id
        user = get_user(user_id)
        if not user or user.get("banned", False):
            _send_pe(call.message.chat.id, "❌ ʙᴀɴɴᴇᴅ!")
            return
        if not user.get("unlimited", False):
            uses = user.get("uses", 0)
            if uses >= 1:
                _send_pe(call.message.chat.id, f"⚠️ ᴜsᴇᴅ!\n💰 ᴘᴀʏ ʀs.{load_settings().get('price', 99)}")
                send_payment_qr(call.message.chat.id)
                bot.answer_callback_query(call.id)
                return
        _send_pe(call.message.chat.id, "🔑 sᴇɴᴅ ᴛᴏᴋᴇɴ:")
        bot.register_next_step_handler(call.message, get_ban_token)
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"❌ Ban another error: {e}")

@bot.callback_query_handler(func=lambda c: c.data == "get_unlimited")
def get_unlimited_callback(call):
    try:
        send_payment_qr(call.message.chat.id)
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"❌ Get unlimited error: {e}")

# ============================================================
# BAN CHECK
# ============================================================
@bot.message_handler(func=lambda m: m.text and stylish_text("BAN CHECK") in m.text)
def ban_check_start(message):
    user_id = message.from_user.id
    user = get_user(user_id)

    if not user or user.get("banned", False):
        _send_pe(message.chat.id, "❌ ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ!")
        return

    settings = load_settings()
    ban_price = settings.get("ban_price", 0)

    if ban_price > 0:
        user_paid = user.get("ban_paid", False)
        if not user_paid:
            text = f"""
⭐ ═══《 🔍 BAN CHECK 》═══ ⭐

⭐ 💰 Price: Rs.{ban_price}
⭐ ⚠️ You need to pay to use this!

⭐ 💳 Pay & send screenshot to admin.
⭐ 👨‍💻 @iflexzyan
"""
            keyboard = [
                [make_green_button("PAY NOW", callback=f"ban_pay_{user_id}")],
                [make_green_button("CONTACT", url="https://t.me/iflexzyan")]
            ]
            markup = InlineKeyboardMarkup(keyboard)
            _send_pe(message.chat.id, text, reply_markup=markup)
            return

    _send_pe(message.chat.id, "🔍 sᴇɴᴅ ᴛʜᴇ ᴜɪᴅ:")
    bot.register_next_step_handler(message, process_ban_check)

def process_ban_check(message):
    uid_input = message.text.strip()
    user_id = message.from_user.id

    if not uid_input.isdigit():
        _send_pe(message.chat.id, "❌ Invalid UID! Send only numbers.")
        return

    anim_msg = show_processing_animation(message.chat.id)

    try:
        url = f"https://crownx-premium-bancheck.lovable.app/baninfo?uid={uid_input}"
        response = requests.get(url, timeout=15)

        if response.status_code == 200:
            data = response.json()

            if isinstance(data, list):
                if len(data) > 0:
                    data = data[0]
                else:
                    _send_pe(message.chat.id, "❌ No data found!")
                    return

            try:
                bot.delete_message(message.chat.id, anim_msg.message_id)
            except:
                pass

            send_json_response(message.chat.id, data, uid_input)

        else:
            try:
                bot.delete_message(message.chat.id, anim_msg.message_id)
            except:
                pass
            _send_pe(message.chat.id, f"❌ API Error {response.status_code}")
    except Exception as e:
        try:
            bot.delete_message(message.chat.id, anim_msg.message_id)
        except:
            pass
        _send_pe(message.chat.id, f"❌ Error: {str(e)}")

# ============================================================
# NUMBER INFO - WITH PAID/FREE
# ============================================================
@bot.message_handler(func=lambda m: m.text and stylish_text("NUMBER INFO") in m.text)
def number_info_start(message):
    try:
        user_id = message.from_user.id
        user = get_user(user_id)

        if not user or user.get("banned", False):
            _send_pe(message.chat.id, "❌ ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ!")
            return

        settings = load_settings()
        number_price = settings.get("number_info_price", 0)

        if number_price > 0:
            user_paid = user.get("number_info_paid", False)
            if not user_paid:
                text = f"""
⭐ ═══《 📱 NUMBER INFO 》═══ ⭐

⭐ 💰 Price: Rs.{number_price}
⭐ ⚠️ You need to pay to use this!

⭐ 💳 Pay & send screenshot to admin.
⭐ 👨‍💻 @iflexzyan
"""
                keyboard = [
                    [make_green_button("PAY FOR NUMBER INFO", callback=f"number_pay_{user_id}")],
                    [make_green_button("CONTACT", url="https://t.me/iflexzyan")]
                ]
                markup = InlineKeyboardMarkup(keyboard)
                _send_pe(message.chat.id, text, reply_markup=markup)
                return

        _send_pe(message.chat.id, "📱 sᴇɴᴅ ᴛʜᴇ ɴᴜᴍʙᴇʀ:")
        bot.register_next_step_handler(message, process_number_info)
    except Exception as e:
        print(f"❌ Number info error: {e}")

def process_number_info(message):
    try:
        number = message.text.strip().replace("+", "").replace(" ", "").replace("-", "")
        user_id = message.from_user.id

        if not number.isdigit() or len(number) < 10:
            _send_pe(message.chat.id, "❌ Invalid number! Send only digits (10+).")
            return

        anim_msg = show_processing_animation_red(message.chat.id)

        try:
            url = f"https://168.144.112.157:5000/api/info?number={number}"
            response = requests.get(url, timeout=20, verify=False)

            if response.status_code == 200:
                data = response.json()
                data = clean_owner_credit(data)

                try:
                    bot.delete_message(message.chat.id, anim_msg.message_id)
                except:
                    pass

                send_json_response(message.chat.id, data, number, prefix="number_info", clean=True)
            else:
                try:
                    bot.delete_message(message.chat.id, anim_msg.message_id)
                except:
                    pass
                _send_pe(message.chat.id, f"❌ API Error {response.status_code}")
        except Exception as e:
            try:
                bot.delete_message(message.chat.id, anim_msg.message_id)
            except:
                pass
            _send_pe(message.chat.id, f"❌ Error: {str(e)}")
    except Exception as e:
        print(f"❌ Process number error: {e}")

# ============================================================
# PLAYER INFO
# ============================================================
@bot.message_handler(func=lambda m: m.text and stylish_text("PLAYER INFO") in m.text)
def player_info_start(message):
    try:
        user_id = message.from_user.id
        user = get_user(user_id)

        if not user or user.get("banned", False):
            _send_pe(message.chat.id, "❌ ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ!")
            return

        _send_pe(message.chat.id, "🎮 sᴇɴᴅ ᴛʜᴇ ᴘʟᴀʏᴇʀ ᴜɪᴅ:")
        bot.register_next_step_handler(message, process_player_info)
    except Exception as e:
        print(f"❌ Player info error: {e}")

def process_player_info(message):
    try:
        uid = message.text.strip()
        user_id = message.from_user.id

        if not uid.isdigit():
            _send_pe(message.chat.id, "❌ Invalid UID! Send only numbers.")
            return

        anim_msg = show_processing_animation_purple(message.chat.id)

        try:
            url = f"https://info.killersharmabot.online/player-info?uid={uid}"
            response = requests.get(url, timeout=20)

            if response.status_code == 200:
                data = response.json()

                try:
                    bot.delete_message(message.chat.id, anim_msg.message_id)
                except:
                    pass

                send_json_response(message.chat.id, data, uid, prefix="player_info", clean=True)
            else:
                try:
                    bot.delete_message(message.chat.id, anim_msg.message_id)
                except:
                    pass
                _send_pe(message.chat.id, f"❌ API Error {response.status_code}")
        except Exception as e:
            try:
                bot.delete_message(message.chat.id, anim_msg.message_id)
            except:
                pass
            _send_pe(message.chat.id, f"❌ Error: {str(e)}")
    except Exception as e:
        print(f"❌ Process player error: {e}")

# ============================================================
# NUMBER INFO PAYMENT
# ============================================================
@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("number_pay_"))
def handle_number_pay(call):
    user_id = int(call.data.split("_")[2])
    if call.from_user.id != user_id:
        _send_pe(call.message.chat.id, "❌ Not your request!")
        bot.answer_callback_query(call.id)
        return

    settings = load_settings()
    number_price = settings.get("number_info_price", 0)
    upi = settings.get("upi", "vanshx111@naviaxis")

    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=upi://pay?pa={upi}&am={number_price}&cu=INR"

    text = get_stylish_qr_text(upi, number_price)

    keyboard = [
        [make_green_button("I HAVE PAID", callback=f"number_paid_{user_id}")],
        [make_green_button("SUPPORT", url="https://t.me/iflexzyan")]
    ]
    markup = InlineKeyboardMarkup(keyboard)

    try:
        bot.send_photo(call.message.chat.id, photo=qr_url, caption=text, reply_markup=markup)
    except:
        _send_pe(call.message.chat.id, text, reply_markup=markup)

    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("number_paid_"))
def handle_number_paid(call):
    user_id = int(call.data.split("_")[2])
    if call.from_user.id != user_id:
        _send_pe(call.message.chat.id, "❌ Not your request!")
        bot.answer_callback_query(call.id)
        return

    _send_pe(call.message.chat.id, "📸 Send payment screenshot to admin!")
    bot.answer_callback_query(call.id)

    admin_text = f"""
⭐ ═══《 🔔 NUMBER INFO PAYMENT 》═══ ⭐

⭐ 👤 User: {call.from_user.first_name}
⭐ 🆔 ID: {user_id}
⭐ 💰 Amount: Rs.{load_settings().get('number_info_price', 0)}
⭐ 📱 Username: @{call.from_user.username or 'N/A'}

⭐ ═══════════════════════ ⭐
"""
    for admin in ADMIN_IDS:
        _send_pe(admin, admin_text)

# ============================================================
# SET NUMBER INFO PRICE & FREE - ADMIN
# ============================================================
@bot.message_handler(func=lambda m: m.text and stylish_text("SET NUMBER INFO PRICE") in m.text)
def set_number_price_start(message):
    if not is_admin(message.from_user.id):
        return
    _send_pe(message.chat.id, "💰 Send new Number Info price (0 = FREE):")
    bot.register_next_step_handler(message, process_set_number_price)

def process_set_number_price(message):
    if not is_admin(message.from_user.id):
        return
    try:
        price = int(message.text.strip())
        if price < 0:
            _send_pe(message.chat.id, "❌ Price cannot be negative!")
            return
        settings = load_settings()
        settings["number_info_price"] = price
        save_settings(settings)
        _send_pe(message.chat.id, f"✅ Number Info price set to Rs.{price}")
    except:
        _send_pe(message.chat.id, "❌ Invalid number!")

@bot.message_handler(func=lambda m: m.text and stylish_text("SET NUMBER INFO FREE") in m.text)
def set_number_free(message):
    if not is_admin(message.from_user.id):
        return
    settings = load_settings()
    settings["number_info_price"] = 0
    save_settings(settings)
    _send_pe(message.chat.id, "✅ Number Info is now FREE for everyone! 🎉")

# ============================================================
# OTHER USER COMMANDS
# ============================================================
@bot.message_handler(func=lambda m: m.text and stylish_text("FREE TRIAL") in m.text)
def free_trial_cmd(message):
    try:
        user_id = message.from_user.id
        user = get_user(user_id)
        
        if not user:
            _send_pe(message.chat.id, "❌ /start ғɪʀsᴛ!")
            return
        
        if user.get("unlimited", False):
            _send_pe(message.chat.id, "✅ ᴀʟʀᴇᴀᴅʏ ᴜɴʟɪᴍɪᴛᴇᴅ!")
            return
        
        uses = user.get("uses", 0)
        if uses >= 1:
            _send_pe(message.chat.id, f"⚠️ ᴜsᴇᴅ!\n💰 ᴘᴀʏ ʀs.{load_settings().get('price', 99)}")
            send_payment_qr(message.chat.id)
            return
        
        _send_pe(message.chat.id, """
🆓 ғʀᴇᴇ ᴛʀɪᴀʟ ᴀᴄᴛɪᴠᴀᴛᴇᴅ! 🎯

🔑 sᴇɴᴅ ᴛᴏᴋᴇɴ ᴛᴏ ʙᴀɴ:
1️⃣ ᴄʟɪᴄᴋ "BAN ACCOUNT"
2️⃣ sᴇɴᴅ ᴛᴏᴋᴇɴ
3️⃣ ᴄᴏɴғɪʀᴍ

⭐ @ɪꜰʟᴇxᴢʏᴀɴ ⭐
""")
    except Exception as e:
        print(f"❌ Free trial error: {e}")

@bot.message_handler(func=lambda m: m.text and stylish_text("UNLIMITED") in m.text)
def unlimited_cmd(message):
    try:
        user_id = message.from_user.id
        user = get_user(user_id)
        
        if user and user.get("unlimited", False):
            _send_pe(message.chat.id, "✅ ᴀʟʀᴇᴀᴅʏ ᴜɴʟɪᴍɪᴛᴇᴅ!")
            return
        
        send_payment_qr(message.chat.id)
    except Exception as e:
        print(f"❌ Unlimited error: {e}")

@bot.message_handler(func=lambda m: m.text and stylish_text("HOW TO GET TOKEN") in m.text)
def how_to_get_token(message):
    try:
        settings = load_settings()
        token_text = settings.get("token_text", "1️⃣ Open Free Fire\n2️⃣ Go to Settings\n3️⃣ Click Account\n4️⃣ Find Data Access\n5️⃣ Copy Token")
        
        _send_pe(message.chat.id, f"""
⭐ ═══《 🔑 ʜᴏᴡ ᴛᴏ ɢᴇᴛ ᴛᴏᴋᴇɴ 》═══ ⭐

⭐ {token_text}

⭐ ═══════════════════════ ⭐
""")
        
        if os.path.exists("token_video.mp4"):
            with open("token_video.mp4", "rb") as f:
                bot.send_video(message.chat.id, f, caption="⭐ ᴠɪᴅᴇᴏ ɢᴜɪᴅᴇ")
    except Exception as e:
        print(f"❌ How to get token error: {e}")

@bot.message_handler(func=lambda m: m.text and stylish_text("SUPPORT") in m.text)
def support_cmd(message):
    try:
        settings = load_settings()
        support = settings.get("support", "@iflexzyan")
        
        text = f"""
⭐ ═══《 📞 sᴜᴘᴘᴏʀᴛ 》═══ ⭐

⭐ 👨‍💻 {support}

⭐ ғᴏʀ ᴀɴʏ ɪssᴜᴇ:
⭐ 📱 {support}

⭐ ═══════════════════════ ⭐
"""
        markup = InlineKeyboardMarkup([
            [make_green_button("CONTACT", url=f"https://t.me/{support.replace('@', '')}")]
        ])
        _send_pe(message.chat.id, text, reply_markup=markup)
    except Exception as e:
        print(f"❌ Support error: {e}")

@bot.message_handler(func=lambda m: m.text and stylish_text("HELP") in m.text)
def help_cmd(message):
    try:
        user_id = message.from_user.id
        if is_admin(user_id):
            markup = get_admin_menu(user_id)
        else:
            markup = get_user_menu(user_id)
        
        help_text = """
⭐ ═══《 ❓ ʜᴇʟᴘ 》═══ ⭐

⭐ ʜᴏᴡ ᴛᴏ ᴜsᴇ:

⭐ 𝟷️⃣ ᴄʟɪᴄᴋ BAN ACCOUNT
⭐ 𝟸️⃣ sᴇɴᴅ ᴀᴄᴄᴇss ᴛᴏᴋᴇɴ
⭐ 𝟹️⃣ ᴄᴏɴғɪʀᴍ ʏᴇs
⭐ 𝟺️⃣ ᴀᴄᴄᴏᴜɴᴛ ɢᴇᴛs ʙᴀɴɴᴇᴅ!

⭐ ═══════════════════ ⭐

⭐ 🆓 ғʀᴇᴇ ᴛʀɪᴀʟ: 𝟷 ʙᴀɴ
⭐ 💰 ᴜɴʟɪᴍɪᴛᴇᴅ: ᴘᴀʏ & ɢᴇᴛ
⭐ 🔍 BAN CHECK: Check UID status
⭐ 📱 NUMBER INFO: Number details
⭐ 🎮 PLAYER INFO: UID details

⭐ ═══════════════════ ⭐

⭐ 👨‍💻 @ɪꜰʟᴇxᴢʏᴀɴ
⭐ ᴛʜᴀɴᴋ ʏᴏᴜ ꜰᴏʀ ᴜꜱɪɴɢ ᴏᴜʀ ʙᴏᴛ! ⭐
"""
        _send_pe(message.chat.id, help_text, reply_markup=markup)
    except Exception as e:
        print(f"❌ Help error: {e}")

@bot.message_handler(func=lambda m: m.text and stylish_text("ABOUT") in m.text)
def about_cmd(message):
    try:
        settings = load_settings()
        developer = settings.get("developer", "@iflexzyan")
        
        text = f"""
⭐ ═══《 ℹ️ ᴀʙᴏᴜᴛ 》═══ ⭐

⭐ 🤖 ғғ ʙᴀɴ ʙᴏᴛ

⭐ 🔫 ʙᴀɴ ғʀᴇᴇ ғɪʀᴇ ᴀᴄᴄᴏᴜɴᴛs
⭐ 🔍 BAN CHECK - UID status check
⭐ 📱 NUMBER INFO - Number details
⭐ 🎮 PLAYER INFO - UID details
⭐ 💰 ᴘᴀʏ & ɢᴇᴛ ᴜɴʟɪᴍɪᴛᴇᴅ
⭐ 🆓 𝟷 ғʀᴇᴇ ᴛʀɪᴀʟ

⭐ 👨‍💻 {developer}
⭐ ᴛʜᴀɴᴋ ʏᴏᴜ ꜰᴏʀ ᴜꜱɪɴɢ ᴏᴜʀ ʙᴏᴛ! ⭐
"""
        _send_pe(message.chat.id, text)
    except Exception as e:
        print(f"❌ About error: {e}")

# ============================================================
# ADMIN COMMANDS
# ============================================================
@bot.message_handler(func=lambda m: m.text and stylish_text("ADMIN PANEL") in m.text)
def admin_panel_cmd(message):
    if not is_admin(message.from_user.id):
        return
    text = """
⭐ ═══《 👑 ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ 》═══ ⭐

⭐ /approve ID - APPROVE
⭐ /disapprove ID - REJECT
⭐ /ban ID - BAN
⭐ /unban ID - UNBAN
⭐ /users - ALL USERS
⭐ /data - FULL DATA REPORT
⭐ /checkall - CHECK ALL
⭐ /totalbans - TOTAL ID BANS
⭐ /totaladmins - ADMINS
⭐ /price <AMT> - CHANGE
⭐ /upi <UPI> - CHANGE
⭐ /developer <@> - CHANGE
⭐ /addadmin ID - ADD
⭐ /broadcastuser ID MSG - SEND
⭐ /allbroadcast MSG - ALL

⭐ ═══════════════════════ ⭐
"""
    _send_pe(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text and stylish_text("STATS") in m.text)
def stats_cmd(message):
    if not is_admin(message.from_user.id):
        return
    users = load_users()
    orders = load_orders()
    pending = load_pending()
    settings = load_settings()
    text = f"""
⭐ ═══《 📊 sᴛᴀᴛs 》═══ ⭐

⭐ 👥 ᴜsᴇʀs: {len(users)}
⭐ 🔫 ɪᴅ ʙᴀɴs: {len(orders)}
⭐ 💰 ᴘᴇɴᴅɪɴɢ: {len(pending)}
⭐ 💎 ᴜɴʟɪᴍɪᴛᴇᴅ: {sum(1 for u in users.values() if u.get('unlimited', False))}
⭐ 👑 ᴀᴅᴍɪɴs: {len(ADMIN_IDS)}
⭐ 💳 ᴘʀɪᴄᴇ: ʀs.{settings.get('price', 99)}
⭐ 🏦 ᴜᴘɪ: {settings.get('upi', 'vanshx111@naviaxis')}
⭐ 👨‍💻 {settings.get('developer', '@iflexzyan')}

⭐ ═══════════════════════ ⭐
"""
    _send_pe(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text and stylish_text("TOTAL BANS") in m.text)
def total_bans_btn(message):
    if not is_admin(message.from_user.id):
        return
    orders = load_orders()
    total = len(orders)
    text = f"""
⭐ ═══《 🔫 ᴛᴏᴛᴀʟ ɪᴅ ʙᴀɴs 》═══ ⭐

⭐ 🔫 ᴛᴏᴛᴀʟ ʙᴀɴs: {total}

⭐ ═══════════════════════ ⭐
"""
    if orders:
        text += "\n⭐ 📋 ʟᴀᴛᴇsᴛ ʙᴀɴs:\n"
        items = list(orders.items())[-15:]
        for key, ban in reversed(items):
            uid = ban.get('uid', 'N/A')
            name = ban.get('name', 'N/A')
            btime = str(ban.get('time', ''))[:16].replace('T', ' ')
            text += f"\n⭐ 🔢 UID: {uid}\n⭐ 👤 {name}\n⭐ 🕒 {btime}\n⭐ ─────────────"
    else:
        text += "\n\n⭐ ɴᴏ ʙᴀɴs ʏᴇᴛ!"
    send_chunked(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text and stylish_text("USERS") in m.text)
def users_cmd(message):
    if not is_admin(message.from_user.id):
        return
    users = load_users()
    text = "⭐ ═══《 👥 ᴜsᴇʀs 》═══ ⭐\n\n"
    for uid, data in users.items():
        status = "💎" if data.get("unlimited", False) else "🆓"
        banned = "🚫" if data.get("banned", False) else "✅"
        text += f"⭐ • {data.get('name', 'Unknown')} (@{data.get('username', 'N/A')}) - {status} {banned}\n"
    text += f"\n⭐ ᴛᴏᴛᴀʟ: {len(users)}"
    send_chunked(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text and stylish_text("DATA") in m.text)
def data_cmd(message):
    if not is_admin(message.from_user.id):
        return
    users = load_users()
    orders = load_orders()
    pending = load_pending()
    settings = load_settings()
    ban_counts = {}
    for o in orders.values():
        k = str(o.get("user_id", ""))
        ban_counts[k] = ban_counts.get(k, 0) + 1
    lines = [
        "⭐ ═══《 📦 FULL BOT DATA 》═══ ⭐",
        f"⭐ 👥 USERS: {len(users)}",
        f"⭐ 🔫 ID BANS: {len(orders)}",
        f"⭐ 💰 PENDING PAYMENTS: {len(pending)}",
        f"⭐ 💎 UNLIMITED: {sum(1 for u in users.values() if u.get('unlimited'))}",
        f"⭐ 🚫 BANNED USERS: {sum(1 for u in users.values() if u.get('banned'))}",
        f"⭐ 💳 PRICE: Rs.{settings.get('price', 99)} | BAN CHECK: Rs.{settings.get('ban_price', 0)}",
        "",
        "⭐ 👥 USER WISE DETAILS:"
    ]
    for uid, u in users.items():
        st = "💎" if u.get("unlimited") else "🆓"
        bn = "🚫BANNED" if u.get("banned") else "✅"
        ad = "👑" if int(uid) in ADMIN_IDS else ""
        lines.append(f"⭐ • {u.get('name', '?')} (@{u.get('username', 'N/A')}) {ad} | ID:{uid} | {st} {bn} | 🔫BANS:{ban_counts.get(str(uid), 0)}")
    if pending:
        lines.append("")
        lines.append("⭐ 💳 PAYMENT REQUESTS:")
        for pid, p in pending.items():
            lines.append(f"⭐ • {p.get('name', '?')} (@{p.get('username', 'N/A')}) | ID:{pid} | {str(p.get('requested', ''))[:16]}")
    lines.append("")
    lines.append("⭐ ═══════════════════════ ⭐")
    send_chunked(message.chat.id, "\n".join(lines))
    data = {
        "users": users,
        "orders": orders,
        "pending": pending,
        "settings": settings,
        "admins": ADMIN_IDS,
        "generated": datetime.now().isoformat()
    }
    try:
        with open("bot_data.json", "w") as f:
            json.dump(data, f, indent=2)
        with open("bot_data.json", "rb") as f:
            bot.send_document(message.chat.id, f, caption="⭐ 📥 DATA EXPORT")
    except:
        pass

@bot.message_handler(func=lambda m: m.text and stylish_text("CHECK ALL") in m.text)
def check_all_cmd(message):
    if not is_admin(message.from_user.id):
        return
    users = load_users()
    if not users:
        _send_pe(message.chat.id, "⭐ ɴᴏ ᴜsᴇʀs ғᴏᴜɴᴅ!")
        return
    text = "⭐ ═══《 👥 ᴀʟʟ ᴜsᴇʀs 》═══ ⭐\n\n"
    for uid, data in users.items():
        status = "💎" if data.get("unlimited", False) else "🆓"
        banned = "🚫" if data.get("banned", False) else "✅"
        admin = "👑" if int(uid) in ADMIN_IDS else ""
        text += f"⭐ • {data.get('name', 'Unknown')} (@{data.get('username', 'N/A')}) - {status} {banned} {admin}\n"
    text += f"\n⭐ ᴛᴏᴛᴀʟ: {len(users)}"
    send_chunked(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text and stylish_text("TOTAL ADMINS") in m.text)
def total_admins_cmd(message):
    if not is_admin(message.from_user.id):
        return
    text = "⭐ ═══《 👑 ᴛᴏᴛᴀʟ ᴀᴅᴍɪɴs 》═══ ⭐\n\n"
    for admin_id in ADMIN_IDS:
        user = get_user(admin_id)
        if user:
            text += f"⭐ • {user.get('name', 'Unknown')} (@{user.get('username', 'N/A')}) - 🆔 {admin_id}\n"
        else:
            text += f"⭐ • 🆔 {admin_id}\n"
    text += f"\n⭐ ᴛᴏᴛᴀʟ: {len(ADMIN_IDS)}"
    _send_pe(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text and stylish_text("BOT ON") in m.text)
def bot_on_btn(message):
    if not is_admin(message.from_user.id):
        return
    global bot_active
    bot_active = True
    _send_pe(message.chat.id, "✅ 🟢 ʙᴏᴛ ɪs ɴᴏᴡ ᴏɴʟɪɴᴇ!")

@bot.message_handler(func=lambda m: m.text and stylish_text("BOT OFF") in m.text)
def bot_off_btn(message):
    if not is_admin(message.from_user.id):
        return
    global bot_active
    bot_active = False
    _send_pe(message.chat.id, "✅ 🔴 ʙᴏᴛ ɪs ɴᴏᴡ ᴏғғʟɪɴᴇ!")

@bot.message_handler(func=lambda m: m.text and stylish_text("PRICE") in m.text)
def price_btn(message):
    if not is_admin(message.from_user.id):
        return
    _send_pe(message.chat.id, f"⭐ 💰 ᴄᴜʀʀᴇɴᴛ: ʀs.{load_settings().get('price', 99)}\n⭐ /price <ᴀᴍᴛ>")

@bot.message_handler(func=lambda m: m.text and stylish_text("UPI") in m.text)
def upi_btn(message):
    if not is_admin(message.from_user.id):
        return
    _send_pe(message.chat.id, f"⭐ 🏦 ᴄᴜʀʀᴇɴᴛ: {load_settings().get('upi', 'vanshx111@naviaxis')}\n⭐ /upi <ɴᴇᴡ>")

@bot.message_handler(func=lambda m: m.text and stylish_text("ADD ADMIN") in m.text)
def add_admin_btn(message):
    if not is_admin(message.from_user.id):
        return
    _send_pe(message.chat.id, "⭐ /addadmin ɪᴅ")

@bot.message_handler(func=lambda m: m.text and stylish_text("ALL COMMANDS") in m.text)
def all_commands_cmd(message):
    if not is_admin(message.from_user.id):
        return
    text = """
⭐ ═══《 📋 ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs 》═══ ⭐

⭐ /start - sᴛᴀʀᴛ ʙᴏᴛ
⭐ /help - ʜᴇʟᴘ ɢᴜɪᴅᴇ
⭐ /approve ID - ᴀᴘᴘʀᴏᴠᴇ
⭐ /disapprove ID - ʀᴇᴊᴇᴄᴛ
⭐ /ban ID - ʙᴀɴ
⭐ /unban ID - ᴜɴʙᴀɴ
⭐ /users - ᴀʟʟ ᴜsᴇʀs
⭐ /data - ғᴜʟʟ ᴅᴀᴛᴀ ʀᴇᴘᴏʀᴛ
⭐ /checkall - ᴄʜᴇᴄᴋ ᴀʟʟ
⭐ /totalbans - ᴛᴏᴛᴀʟ ɪᴅ ʙᴀɴs
⭐ /totaladmins - ᴀᴅᴍɪɴs
⭐ /price <AMT> - ᴄʜᴀɴɢᴇ
⭐ /upi <UPI> - ᴄʜᴀɴɢᴇ
⭐ /developer <@> - ᴄʜᴀɴɢᴇ
⭐ /addadmin ID - ᴀᴅᴅ
⭐ /broadcastuser ID MSG - SEND
⭐ /allbroadcast MSG - ALL

⭐ ═══════════════════════ ⭐
"""
    _send_pe(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text and stylish_text("BROADCAST") in m.text and stylish_text("ALL") not in m.text)
def broadcast_btn_msg(message):
    if not is_admin(message.from_user.id):
        return
    _send_pe(message.chat.id, "⭐ /broadcastuser ɪᴅ ᴍsɢ")

@bot.message_handler(func=lambda m: m.text and stylish_text("ALL BROADCAST") in m.text)
def all_broadcast_btn_msg(message):
    if not is_admin(message.from_user.id):
        return
    _send_pe(message.chat.id, "⭐ /allbroadcast ᴍsɢ")

@bot.message_handler(func=lambda m: m.text and stylish_text("SET WELCOME IMAGE") in m.text)
def set_welcome_image_btn(message):
    if not is_admin(message.from_user.id):
        return
    _send_pe(message.chat.id, "⭐ sᴇɴᴅ ᴀ ᴘʜᴏᴛᴏ ᴏʀ ɪᴍᴀɢᴇ ᴜʀʟ")
    bot.register_next_step_handler(message, save_welcome_image)

def save_welcome_image(message):
    if not is_admin(message.from_user.id):
        return
    settings = load_settings()
    if message.photo:
        settings["welcome_image"] = message.photo[-1].file_id
        save_settings(settings)
        _send_pe(message.chat.id, "✅ ᴡᴇʟᴄᴏᴍᴇ ɪᴍᴀɢᴇ ᴜᴘᴅᴀᴛᴇᴅ!")
    elif message.text and message.text.startswith("http"):
        settings["welcome_image"] = message.text.strip()
        save_settings(settings)
        _send_pe(message.chat.id, "✅ ᴡᴇʟᴄᴏᴍᴇ ɪᴍᴀɢᴇ ᴜʀʟ ᴜᴘᴅᴀᴛᴇᴅ!")
    else:
        _send_pe(message.chat.id, "❌ sᴇɴᴅ ᴀ ᴘʜᴏᴛᴏ ᴏʀ ᴠᴀʟɪᴅ ᴜʀʟ!")

@bot.message_handler(func=lambda m: m.text and stylish_text("SET TOKEN TEXT") in m.text)
def set_token_text_btn(message):
    if not is_admin(message.from_user.id):
        return
    _send_pe(message.chat.id, "⭐ sᴇɴᴅ ɴᴇᴡ ᴛᴏᴋᴇɴ ᴛᴇxᴛ")
    bot.register_next_step_handler(message, save_token_text)

def save_token_text(message):
    if not is_admin(message.from_user.id):
        return
    settings = load_settings()
    settings["token_text"] = message.text.strip()
    save_settings(settings)
    _send_pe(message.chat.id, "✅ ᴛᴏᴋᴇɴ ᴛᴇxᴛ ᴜᴘᴅᴀᴛᴇᴅ!")

@bot.message_handler(func=lambda m: m.text and stylish_text("ADD TOKEN VIDEO") in m.text)
def add_token_video_btn(message):
    if not is_admin(message.from_user.id):
        return
    _send_pe(message.chat.id, "📤 sᴇɴᴅ ᴠɪᴅᴇᴏ")
    bot.register_next_step_handler(message, save_token_video)

def save_token_video(message):
    if message.video:
        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open("token_video.mp4", "wb") as f:
            f.write(downloaded_file)
        _send_pe(message.chat.id, "✅ ᴠɪᴅᴇᴏ sᴀᴠᴇᴅ!")
    else:
        _send_pe(message.chat.id, "❌ sᴇɴᴅ ᴀ ᴠɪᴅᴇᴏ!")

@bot.message_handler(func=lambda m: m.text and stylish_text("SET BAN PRICE") in m.text)
def set_ban_price_start(message):
    if not is_admin(message.from_user.id):
        return
    _send_pe(message.chat.id, "💰 Send new ban price (0 = FREE):")
    bot.register_next_step_handler(message, process_set_ban_price)

def process_set_ban_price(message):
    if not is_admin(message.from_user.id):
        return
    try:
        price = int(message.text.strip())
        if price < 0:
            _send_pe(message.chat.id, "❌ Price cannot be negative!")
            return
        settings = load_settings()
        settings["ban_price"] = price
        save_settings(settings)
        _send_pe(message.chat.id, f"✅ Ban price set to Rs.{price}")
    except:
        _send_pe(message.chat.id, "❌ Invalid number!")

@bot.message_handler(func=lambda m: m.text and stylish_text("SET BAN FREE") in m.text)
def set_ban_free(message):
    if not is_admin(message.from_user.id):
        return
    settings = load_settings()
    settings["ban_price"] = 0
    save_settings(settings)
    _send_pe(message.chat.id, "✅ Ban check is now FREE for everyone! 🎉")

# ============================================================
# BAN CHECK PAYMENT
# ============================================================
@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("ban_pay_"))
def handle_ban_pay(call):
    user_id = int(call.data.split("_")[2])
    if call.from_user.id != user_id:
        _send_pe(call.message.chat.id, "❌ Not your request!")
        bot.answer_callback_query(call.id)
        return

    settings = load_settings()
    ban_price = settings.get("ban_price", 0)
    upi = settings.get("upi", "vanshx111@naviaxis")

    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=upi://pay?pa={upi}&am={ban_price}&cu=INR"

    text = get_stylish_qr_text(upi, ban_price)

    keyboard = [
        [make_green_button("I HAVE PAID", callback=f"ban_paid_{user_id}")],
        [make_green_button("SUPPORT", url="https://t.me/iflexzyan")]
    ]
    markup = InlineKeyboardMarkup(keyboard)

    try:
        bot.send_photo(call.message.chat.id, photo=qr_url, caption=text, reply_markup=markup)
    except:
        _send_pe(call.message.chat.id, text, reply_markup=markup)

    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("ban_paid_"))
def handle_ban_paid(call):
    user_id = int(call.data.split("_")[2])
    if call.from_user.id != user_id:
        _send_pe(call.message.chat.id, "❌ Not your request!")
        bot.answer_callback_query(call.id)
        return

    _send_pe(call.message.chat.id, "📸 Send payment screenshot to admin!")
    bot.answer_callback_query(call.id)

    admin_text = f"""
⭐ ═══《 🔔 BAN CHECK PAYMENT 》═══ ⭐

⭐ 👤 User: {call.from_user.first_name}
⭐ 🆔 ID: {user_id}
⭐ 💰 Amount: Rs.{load_settings().get('ban_price', 0)}
⭐ 📱 Username: @{call.from_user.username or 'N/A'}

⭐ ═══════════════════════ ⭐
"""
    for admin in ADMIN_IDS:
        _send_pe(admin, admin_text)

# ============================================================
# PAYMENT SYSTEM
# ============================================================
def send_payment_qr(chat_id):
    try:
        settings = load_settings()
        upi = settings.get("upi", "vanshx111@naviaxis")
        price = settings.get("price", 99)

        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=upi://pay?pa={upi}&am={price}&cu=INR"

        text = get_stylish_qr_text(upi, price)

        keyboard = [
            [make_green_button("I HAVE PAID", callback=f"paid_{chat_id}")],
            [make_green_button("CANCEL", callback="cancel_payment")]
        ]
        markup = InlineKeyboardMarkup(keyboard)

        try:
            bot.send_photo(chat_id, photo=qr_url, caption=text, reply_markup=markup)
        except:
            _send_pe(chat_id, text, reply_markup=markup)
    except Exception as e:
        print(f"❌ Payment QR error: {e}")

@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("paid_"))
def handle_paid(call):
    try:
        user_id = call.from_user.id
        chat_id = call.message.chat.id

        try:
            bot.delete_message(chat_id, call.message.message_id)
        except:
            pass

        pending = load_pending()
        pending[str(user_id)] = {
            "user_id": user_id,
            "username": call.from_user.username,
            "name": call.from_user.first_name,
            "status": "pending",
            "requested": datetime.now().isoformat()
        }
        save_pending(pending)

        _send_pe(chat_id, "📸 sᴇɴᴅ sᴄʀᴇᴇɴsʜᴏᴛ!")
        bot.register_next_step_handler(call.message, receive_payment_screenshot)
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"❌ Paid callback error: {e}")

def receive_payment_screenshot(message):
    try:
        user_id = message.from_user.id

        if message.photo:
            file_id = message.photo[-1].file_id
            pending = load_pending()
            if str(user_id) in pending:
                pending[str(user_id)]["screenshot"] = file_id
                pending[str(user_id)]["status"] = "pending"
                save_pending(pending)

            _send_pe(message.chat.id, "✅ ʀᴇᴄᴇɪᴠᴇᴅ!\n⏳ ᴡᴀɪᴛ ғᴏʀ ᴀᴅᴍɪɴ")

            admin_text = f"""
⭐ ═══《 💰 ɴᴇᴡ ᴘᴀʏᴍᴇɴᴛ 》═══ ⭐

⭐ 👤 {message.from_user.first_name}
⭐ 🆔 {user_id}
⭐ 👾 @{message.from_user.username or 'N/A'}

⭐ ═══════════════════════ ⭐
"""
            keyboard = [
                [make_green_button("APPROVE", callback=f"admin_approve_{user_id}")],
                [make_green_button("REJECT", callback=f"admin_disapprove_{user_id}")]
            ]
            markup = InlineKeyboardMarkup(keyboard)

            for admin in ADMIN_IDS:
                try:
                    bot.send_photo(admin, photo=file_id, caption=admin_text, reply_markup=markup)
                except:
                    bot.send_message(admin, admin_text, reply_markup=markup)
        else:
            _send_pe(message.chat.id, "❌ sᴇɴᴅ ᴀ ᴘʜᴏᴛᴏ!")
    except Exception as e:
        print(f"❌ Screenshot receive error: {e}")

@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("admin_approve_"))
def admin_approve_callback(call):
    try:
        if not is_admin(call.from_user.id):
            _send_pe(call.message.chat.id, "❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ!")
            bot.answer_callback_query(call.id)
            return

        user_id = int(call.data.split("_")[2])

        update_user(user_id, "unlimited", True)
        update_user(user_id, "uses", 0)
        update_user(user_id, "ban_paid", True)

        pending = load_pending()
        if str(user_id) in pending:
            del pending[str(user_id)]
            save_pending(pending)

        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass

        _send_pe(call.message.chat.id, f"✅ ᴜsᴇʀ {user_id} ᴀᴘᴘʀᴏᴠᴇᴅ!")

        try:
            bot.send_message(user_id, """
🎉 ᴄᴏɴɢʀᴀᴛs! ᴜɴʟɪᴍɪᴛᴇᴅ ᴀᴄᴄᴇss! 🎉

⭐ ɴᴏᴡ ʏᴏᴜ ᴄᴀɴ ʙᴀɴ ᴀɴʏ ᴀᴄᴄᴏᴜɴᴛ!
⭐ ᴛʜᴀɴᴋ ʏᴏᴜ ꜰᴏʀ ᴄʜᴏᴏꜱɪɴɢ ᴜꜱ!

⭐ @ɪꜰʟᴇxᴢʏᴀɴ ⭐
""")
        except:
            pass

        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"❌ Admin approve error: {e}")

@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("admin_disapprove_"))
def admin_disapprove_callback(call):
    try:
        if not is_admin(call.from_user.id):
            _send_pe(call.message.chat.id, "❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ!")
            bot.answer_callback_query(call.id)
            return

        user_id = int(call.data.split("_")[2])

        pending = load_pending()
        if str(user_id) in pending:
            del pending[str(user_id)]
            save_pending(pending)

        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass

        _send_pe(call.message.chat.id, f"❌ ᴜsᴇʀ {user_id} ʀᴇᴊᴇᴄᴛᴇᴅ!")

        try:
            bot.send_message(user_id, "❌ ᴘᴀʏᴍᴇɴᴛ ɴᴏᴛ ᴀᴘᴘʀᴏᴠᴇᴅ.")
        except:
            pass

        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"❌ Admin disapprove error: {e}")

@bot.callback_query_handler(func=lambda c: c.data == "cancel_payment")
def cancel_payment_callback(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    _send_pe(call.message.chat.id, "✅ ᴄᴀɴᴄᴇʟʟᴇᴅ!")
    bot.answer_callback_query(call.id)

# ============================================================
# COMMAND HANDLERS
# ============================================================
@bot.message_handler(commands=['approve'])
def approve_user(message):
    if not is_admin(message.from_user.id):
        _send_pe(message.chat.id, "❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ!")
        return
    parts = message.text.split()
    if len(parts) < 2:
        _send_pe(message.chat.id, "❌ /approve ID")
        return
    try:
        user_id = int(parts[1])
    except:
        _send_pe(message.chat.id, "❌ ɪɴᴠᴀʟɪᴅ ɪᴅ!")
        return
    update_user(user_id, "unlimited", True)
    update_user(user_id, "uses", 0)
    update_user(user_id, "ban_paid", True)
    pending = load_pending()
    if str(user_id) in pending:
        del pending[str(user_id)]
        save_pending(pending)
    _send_pe(message.chat.id, f"✅ ᴜsᴇʀ {user_id} ᴀᴘᴘʀᴏᴠᴇᴅ!")
    try:
        bot.send_message(user_id, "🎉 ᴄᴏɴɢʀᴀᴛs! ᴜɴʟɪᴍɪᴛᴇᴅ ᴀᴄᴄᴇss!")
    except:
        pass

@bot.message_handler(commands=['disapprove'])
def disapprove_user(message):
    if not is_admin(message.from_user.id):
        _send_pe(message.chat.id, "❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ!")
        return
    parts = message.text.split()
    if len(parts) < 2:
        _send_pe(message.chat.id, "❌ /disapprove ID")
        return
    try:
        user_id = int(parts[1])
    except:
        _send_pe(message.chat.id, "❌ ɪɴᴠᴀʟɪᴅ ɪᴅ!")
        return
    pending = load_pending()
    if str(user_id) in pending:
        del pending[str(user_id)]
        save_pending(pending)
    _send_pe(message.chat.id, f"❌ ᴜsᴇʀ {user_id} ʀᴇᴊᴇᴄᴛᴇᴅ!")

@bot.message_handler(commands=['ban'])
def ban_user_cmd(message):
    if not is_admin(message.from_user.id):
        _send_pe(message.chat.id, "❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ!")
        return
    parts = message.text.split()
    if len(parts) < 2:
        _send_pe(message.chat.id, "❌ /ban ID")
        return
    try:
        user_id = int(parts[1])
    except:
        _send_pe(message.chat.id, "❌ ɪɴᴠᴀʟɪᴅ ɪᴅ!")
        return
    update_user(user_id, "banned", True)
    _send_pe(message.chat.id, f"✅ ᴜsᴇʀ {user_id} ʙᴀɴɴᴇᴅ!")

@bot.message_handler(commands=['unban'])
def unban_user_cmd(message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        _send_pe(message.chat.id, "❌ /unban ID")
        return
    try:
        user_id = int(parts[1])
    except:
        _send_pe(message.chat.id, "❌ ɪɴᴠᴀʟɪᴅ ɪᴅ!")
        return
    update_user(user_id, "banned", False)
    _send_pe(message.chat.id, f"✅ ᴜsᴇʀ {user_id} ᴜɴʙᴀɴɴᴇᴅ!")

@bot.message_handler(commands=['users'])
def users_cmd_cmd(message):
    if not is_admin(message.from_user.id):
        return
    users = load_users()
    text = "⭐ ═══《 👥 ᴀʟʟ ᴜsᴇʀs 》═══ ⭐\n\n"
    for uid, data in users.items():
        status = "💎" if data.get("unlimited", False) else "🆓"
        banned = "🚫" if data.get("banned", False) else "✅"
        admin = "👑" if int(uid) in ADMIN_IDS else ""
        text += f"⭐ • {data.get('name', 'Unknown')} (@{data.get('username', 'N/A')}) - {status} {banned} {admin}\n"
    text += f"\n⭐ ᴛᴏᴛᴀʟ: {len(users)}"
    send_chunked(message.chat.id, text)

@bot.message_handler(commands=['data'])
def data_cmd_cmd(message):
    if not is_admin(message.from_user.id):
        return
    users = load_users()
    orders = load_orders()
    pending = load_pending()
    settings = load_settings()
    ban_counts = {}
    for o in orders.values():
        k = str(o.get("user_id", ""))
        ban_counts[k] = ban_counts.get(k, 0) + 1
    lines = [
        "⭐ ═══《 📦 FULL BOT DATA 》═══ ⭐",
        f"⭐ 👥 USERS: {len(users)}",
        f"⭐ 🔫 ID BANS: {len(orders)}",
        f"⭐ 💰 PENDING PAYMENTS: {len(pending)}",
        f"⭐ 💎 UNLIMITED: {sum(1 for u in users.values() if u.get('unlimited'))}",
        f"⭐ 🚫 BANNED USERS: {sum(1 for u in users.values() if u.get('banned'))}",
        f"⭐ 💳 PRICE: Rs.{settings.get('price', 99)} | BAN CHECK: Rs.{settings.get('ban_price', 0)}",
        "",
        "⭐ 👥 USER WISE DETAILS:"
    ]
    for uid, u in users.items():
        st = "💎" if u.get("unlimited") else "🆓"
        bn = "🚫BANNED" if u.get("banned") else "✅"
        ad = "👑" if int(uid) in ADMIN_IDS else ""
        lines.append(f"⭐ • {u.get('name', '?')} (@{u.get('username', 'N/A')}) {ad} | ID:{uid} | {st} {bn} | 🔫BANS:{ban_counts.get(str(uid), 0)}")
    if pending:
        lines.append("")
        lines.append("⭐ 💳 PAYMENT REQUESTS:")
        for pid, p in pending.items():
            lines.append(f"⭐ • {p.get('name', '?')} (@{p.get('username', 'N/A')}) | ID:{pid} | {str(p.get('requested', ''))[:16]}")
    lines.append("")
    lines.append("⭐ ═══════════════════════ ⭐")
    send_chunked(message.chat.id, "\n".join(lines))
    data = {
        "users": users,
        "orders": orders,
        "pending": pending,
        "settings": settings,
        "admins": ADMIN_IDS,
        "generated": datetime.now().isoformat()
    }
    try:
        with open("bot_data.json", "w") as f:
            json.dump(data, f, indent=2)
        with open("bot_data.json", "rb") as f:
            bot.send_document(message.chat.id, f, caption="⭐ 📥 DATA EXPORT")
    except:
        pass

@bot.message_handler(commands=['checkall'])
def checkall_cmd(message):
    if not is_admin(message.from_user.id):
        return
    users = load_users()
    if not users:
        _send_pe(message.chat.id, "⭐ ɴᴏ ᴜsᴇʀs ғᴏᴜɴᴅ!")
        return
    text = "⭐ ═══《 👥 ᴀʟʟ ᴜsᴇʀs 》═══ ⭐\n\n"
    for uid, data in users.items():
        status = "💎" if data.get("unlimited", False) else "🆓"
        banned = "🚫" if data.get("banned", False) else "✅"
        admin = "👑" if int(uid) in ADMIN_IDS else ""
        text += f"⭐ • {data.get('name', 'Unknown')} (@{data.get('username', 'N/A')}) - {status} {banned} {admin}\n"
    text += f"\n⭐ ᴛᴏᴛᴀʟ: {len(users)}"
    send_chunked(message.chat.id, text)

@bot.message_handler(commands=['totalbans'])
def totalbans_cmd(message):
    if not is_admin(message.from_user.id):
        return
    orders = load_orders()
    total = len(orders)
    text = f"""
⭐ ═══《 🔫 ᴛᴏᴛᴀʟ ɪᴅ ʙᴀɴs 》═══ ⭐

⭐ 🔫 ᴛᴏᴛᴀʟ ʙᴀɴs: {total}

⭐ ═══════════════════════ ⭐
"""
    if orders:
        text += "\n⭐ 📋 ʟᴀᴛᴇsᴛ ʙᴀɴs:\n"
        items = list(orders.items())[-15:]
        for key, ban in reversed(items):
            uid = ban.get('uid', 'N/A')
            name = ban.get('name', 'N/A')
            btime = str(ban.get('time', ''))[:16].replace('T', ' ')
            text += f"\n⭐ 🔢 UID: {uid}\n⭐ 👤 {name}\n⭐ 🕒 {btime}\n⭐ ─────────────"
    else:
        text += "\n\n⭐ ɴᴏ ʙᴀɴs ʏᴇᴛ!"
    send_chunked(message.chat.id, text)

@bot.message_handler(commands=['totaladmins'])
def totaladmins_cmd(message):
    if not is_admin(message.from_user.id):
        return
    text = "⭐ ═══《 👑 ᴛᴏᴛᴀʟ ᴀᴅᴍɪɴs 》═══ ⭐\n\n"
    for admin_id in ADMIN_IDS:
        user = get_user(admin_id)
        if user:
            text += f"⭐ • {user.get('name', 'Unknown')} (@{user.get('username', 'N/A')}) - 🆔 {admin_id}\n"
        else:
            text += f"⭐ • 🆔 {admin_id}\n"
    text += f"\n⭐ ᴛᴏᴛᴀʟ: {len(ADMIN_IDS)}"
    _send_pe(message.chat.id, text)

@bot.message_handler(commands=['price'])
def price_cmd(message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        _send_pe(message.chat.id, f"⭐ 💰 ᴄᴜʀʀᴇɴᴛ: ʀs.{load_settings().get('price', 99)}\n⭐ /price <AMT>")
        return
    try:
        price = int(parts[1])
        settings = load_settings()
        settings["price"] = price
        save_settings(settings)
        _send_pe(message.chat.id, f"✅ ᴘʀɪᴄᴇ sᴇᴛ ᴛᴏ ʀs.{price}")
    except:
        _send_pe(message.chat.id, "❌ ɪɴᴠᴀʟɪᴅ ᴀᴍᴏᴜɴᴛ!")

@bot.message_handler(commands=['upi'])
def upi_cmd(message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        _send_pe(message.chat.id, f"⭐ 🏦 ᴄᴜʀʀᴇɴᴛ: {load_settings().get('upi', 'vanshx111@naviaxis')}\n⭐ /upi <NEW>")
        return
    upi = parts[1]
    settings = load_settings()
    settings["upi"] = upi
    save_settings(settings)
    _send_pe(message.chat.id, f"✅ ᴜᴘɪ sᴇᴛ ᴛᴏ {upi}")

@bot.message_handler(commands=['developer'])
def developer_cmd(message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        _send_pe(message.chat.id, f"⭐ 👨‍💻 ᴄᴜʀʀᴇɴᴛ: {load_settings().get('developer', '@iflexzyan')}\n⭐ /developer <@>")
        return
    developer = parts[1]
    settings = load_settings()
    settings["developer"] = developer
    settings["support"] = developer
    save_settings(settings)
    _send_pe(message.chat.id, f"✅ ᴅᴇᴠᴇʟᴏᴘᴇʀ sᴇᴛ ᴛᴏ {developer}")

@bot.message_handler(commands=['addadmin'])
def add_admin_cmd(message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        _send_pe(message.chat.id, "❌ /addadmin ID")
        return
    try:
        user_id = int(parts[1])
        if user_id not in ADMIN_IDS:
            ADMIN_IDS.append(user_id)
            _send_pe(message.chat.id, "✅ ᴀᴅᴍɪɴ ᴀᴅᴅᴇᴅ!")
        else:
            _send_pe(message.chat.id, "⚠️ ᴀʟʀᴇᴀᴅʏ ᴀᴅᴍɪɴ!")
    except:
        _send_pe(message.chat.id, "❌ ɪɴᴠᴀʟɪᴅ ɪᴅ!")

@bot.message_handler(commands=['broadcastuser'])
def broadcast_user(message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        _send_pe(message.chat.id, "❌ /broadcastuser ID MSG")
        return
    try:
        user_id = int(parts[1])
        msg = parts[2]
        bot.send_message(user_id, f"📢 {msg}")
        _send_pe(message.chat.id, f"✅ sᴇɴᴛ ᴛᴏ {user_id}!")
    except:
        _send_pe(message.chat.id, "❌ ғᴀɪʟᴇᴅ!")

@bot.message_handler(commands=['allbroadcast'])
def all_broadcast(message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        _send_pe(message.chat.id, "❌ /allbroadcast MSG")
        return
    msg = parts[1]
    users = load_users()
    sent = 0
    failed = 0
    _send_pe(message.chat.id, f"⏳ sᴇɴᴅɪɴɢ ᴛᴏ {len(users)} ᴜsᴇʀs...")
    for user_id in users.keys():
        try:
            bot.send_message(int(user_id), f"📢 {msg}")
            sent += 1
            time.sleep(0.05)
        except:
            failed += 1
    _send_pe(message.chat.id, f"⭐ ᴄᴏᴍᴘʟᴇᴛᴇ!\n⭐ ᴛᴏᴛᴀʟ: {len(users)}\n⭐ sᴇɴᴛ: {sent}\n⭐ ғᴀɪʟᴇᴅ: {failed}")

# ============================================================
# FLASK WEBHOOK
# ============================================================
@app.route('/', methods=['GET'])
def index():
    return "✅ FF BAN BOT is running!"

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    try:
        if request.headers.get('content-type') == 'application/json':
            json_string = request.get_data().decode('utf-8')
            update = types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return '', 200
    except Exception as e:
        print(f"❌ Webhook error: {e}")
    return '', 403

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("✅ ʙᴏᴛ sᴛᴀʀᴛᴇᴅ!")
    print(f"✅ ᴏᴡɴᴇʀ: {OWNER_ID}")
    print(f"✅ ᴜsᴇʀs: {len(load_users())}")
    print(f"✅ ᴀᴅᴍɪɴs: {len(ADMIN_IDS)}")

    try:
        bot.remove_webhook()
        print("✅ ᴡᴇʙʜᴏᴏᴋ ʀᴇᴍᴏᴠᴇᴅ!")
    except Exception as e:
        print(f"⚠️ {e}")

    try:
        hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
        if hostname:
            webhook_url = f"https://{hostname}/{BOT_TOKEN}"
            bot.set_webhook(url=webhook_url)
            print(f"✅ ᴡᴇʙʜᴏᴏᴋ sᴇᴛ: {webhook_url}")
        else:
            print("⚠️ ɴᴏ ʜᴏsᴛɴᴀᴍᴇ, ᴜsɪɴɢ ᴘᴏʟʟɪɴɢ")
            bot.infinity_polling()
            exit()
    except Exception as e:
        print(f"⚠️ {e}, ғᴀʟʟɪɴɢ ʙᴀᴄᴋ ᴛᴏ ᴘᴏʟʟɪɴɢ")
        bot.infinity_polling()
        exit()

    app.run(host='0.0.0.0', port=PORT)