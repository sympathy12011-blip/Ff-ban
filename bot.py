import os, json, io, time, random, requests
import html as _html
from datetime import datetime
from flask import Flask, request
from telebot import TeleBot, types
from telebot.types import MessageEntity, InlineKeyboardMarkup, InlineKeyboardButton

# ============================================================
# CONFIG
# ============================================================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID  = int(os.environ.get("OWNER_ID", "8471373583"))
ADMIN_IDS = [OWNER_ID, 8586849798]
PORT      = int(os.environ.get("PORT", 10000))

if not BOT_TOKEN:
    print("ERROR: BOT_TOKEN not set!")
    raise SystemExit(1)

bot = TeleBot(BOT_TOKEN, threaded=False)
app = Flask(__name__)

# ============================================================
# FILES & APIS
# ============================================================
USERS_FILE   = "users.json"
ORDERS_FILE  = "orders.json"
PENDING_FILE = "pending.json"
SETTINGS_FILE= "settings.json"
BANS_FILE    = "bans.json"

BAN_API       = "https://ffidbanapi.vercel.app/ban-account?access-token={token}&key=ANIXH"
BANCHECK_API  = "https://crownx-premium-bancheck.lovable.app/baninfo?uid={uid}"
PLAYER_API    = "https://info.killersharmabot.online/player-info?uid={uid}"
NUMBER_API    = "https://stars-water-forward-agenda.trycloudflare.com/api/info?number={number}"
DEV           = "@iflexcoderr"

# ============================================================
# JSON HELPERS
# ============================================================
def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_users():   return load_json(USERS_FILE, {})
def save_users(d):  save_json(USERS_FILE, d)
def load_pending(): return load_json(PENDING_FILE, {})
def save_pending(d):save_json(PENDING_FILE, d)
def load_bans():    return load_json(BANS_FILE, [])
def save_bans(d):   save_json(BANS_FILE, d)
def load_orders():  return load_json(ORDERS_FILE, [])
def save_orders(d): save_json(ORDERS_FILE, d)

DEFAULT_SETTINGS = {
    "price": 19,
    "upi": "vansh111@naviaxis",
    "free_trial": True,
    "bot_name": "FF BAN BOT",
    "developer": "@iflexcoderr",
    "support": "@iflexcoderr",
    "welcome_image": "https://iili.io/C8DNTyQ.jpg",
    "token_text": "https://www.fftools.site/free-fire-token-generator",
    "ban_price": 0,
    "outfit_api": "https://info.killersharmabot.online/player-info?uid={uid}",
}

def load_settings():
    d = load_json(SETTINGS_FILE, {})
    for k, v in DEFAULT_SETTINGS.items():
        d.setdefault(k, v)
    return d

def save_settings(d):
    save_json(SETTINGS_FILE, d)

def seed():
    if not os.path.exists(USERS_FILE):
        save_users({
            "8471373583": {"id": 8471373583, "username": "iflexzyan", "name": "ZYAN", "uses": 0, "unlimited": True, "ban_paid": True, "banned": False},
            "8586849798": {"id": 8586849798, "username": "iflexcoderr", "name": "IFLEXCODER", "uses": 0, "unlimited": True, "ban_paid": True, "banned": False},
            "8612102965": {"id": 8612102965, "username": "", "name": "BOY X", "uses": 0, "unlimited": True, "ban_paid": True, "banned": False},
            "6358005865": {"id": 6358005865, "username": "", "name": "Batman", "uses": 0, "unlimited": False, "ban_paid": True, "banned": False},
            "8989141742": {"id": 8989141742, "username": "VexoraAdsBot", "name": "SHIVAM", "uses": 0, "unlimited": False, "ban_paid": True, "banned": False},
            "8777322894": {"id": 8777322894, "username": "", "name": "Deleted", "uses": 0, "unlimited": False, "ban_paid": False, "banned": False},
            "7931733354": {"id": 7931733354, "username": "", "name": "RYNOX_FF", "uses": 0, "unlimited": True, "ban_paid": True, "banned": False},
        })
    if not os.path.exists(PENDING_FILE):
        save_pending({"8348145490": {"name": "Money", "username": "", "status": "pending", "requested": datetime.now().isoformat()}})
    if not os.path.exists(SETTINGS_FILE):
        save_settings(DEFAULT_SETTINGS)
    if not os.path.exists(BANS_FILE):
        save_bans([])
    if not os.path.exists(ORDERS_FILE):
        save_orders([])

seed()

def get_user(uid):
    return load_users().get(str(uid), {})

def update_user(uid, key, value):
    users = load_users()
    u = str(uid)
    if u not in users:
        users[u] = {"id": uid, "username": "", "name": "User", "uses": 0, "unlimited": False, "ban_paid": False, "banned": False}
    users[u][key] = value
    save_users(users)

def register_user(uid, username="", name="User"):
    users = load_users()
    u = str(uid)
    if u not in users:
        users[u] = {"id": uid, "username": username or "", "name": name or "User",
                    "uses": 0, "unlimited": False, "ban_paid": False, "banned": False}
        save_users(users)
        try:
            bot.send_message(OWNER_ID, "✅ ɴᴇᴡ ᴜsᴇʀ\n👤 " + str(uid) + "\n👾 @" + str(username))
        except Exception:
            pass
    return users[u]

def is_admin(uid):
    return uid == OWNER_ID or uid in ADMIN_IDS

BOT_STATE = {"active": True}
state = {}

# ============================================================
# STYLISH TEXT & DIGITS
# ============================================================
def stylish_text(text):
    m = {'A':'ᴀ','B':'ʙ','C':'ᴄ','D':'ᴅ','E':'ᴇ','F':'ꜰ','G':'ɢ','H':'ʜ','I':'ɪ','J':'ᴊ','K':'ᴋ','L':'ʟ','M':'ᴍ','N':'ɴ','O':'ᴏ','P':'ᴘ','Q':'ǫ','R':'ʀ','S':'ꜱ','T':'ᴛ','U':'ᴜ','V':'ᴠ','W':'ᴡ','X':'x','Y':'ʏ','Z':'ᴢ',
         'a':'ᴀ','b':'ʙ','c':'ᴄ','d':'ᴅ','e':'ᴇ','f':'ꜰ','g':'ɢ','h':'ʜ','i':'ɪ','j':'ᴊ','k':'ᴋ','l':'ʟ','m':'ᴍ','n':'ɴ','o':'ᴏ','p':'ᴘ','q':'ǫ','r':'ʀ','s':'ꜱ','t':'ᴛ','u':'ᴜ','v':'ᴠ','w':'ᴡ','x':'x','y':'ʏ','z':'ᴢ'}
    return "".join(m.get(ch, ch) for ch in str(text))

DIGIT_MAP = str.maketrans("0123456789", "𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿")
def sd(n):
    return str(n).translate(DIGIT_MAP)

def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

# ============================================================
# CUSTOM EMOJI ENTITIES
# ============================================================
EMOJI_MAPPING = {
    "✅": ["6246537187614005254","6246782404476803545","6010060634803148161","6010498532488778300"],
    "✔️": ["6246871001062185760","6010264538375525668","6010487760710800947"],
    "🔥": ["4956222745814762495","4956606007221421405","4956429969396859866","6086954744268460848"],
    "💥": ["6032673796530377389","4958479549265347295"],
    "⚡": ["5791970059597386804","6087079590377820415","6095843123252957701"],
    "❤️": ["5783157259152397008","5801084710343938087","6010280773351904888"],
    "💙": ["5780496071645991525","6104780447684757396"],
    "💚": ["5888789252493283486"],
    "💛": ["5840261097719148872"],
    "🧡": ["5840263144212529797"],
    "💜": ["5840265018655703965"],
    "🖤": ["5840266939932994956"],
    "⭐": ["6244496562752331516","5904618938578243567","6010193314932855525"],
    "🌟": ["6010156854955480259","6086924086791902713"],
    "✨": ["6010338729640596556","6010086134023985536","5801044672658805468"],
    "👑": ["5794422335599546668","6089003761496232797","6247039939305808563"],
    "💰": ["6089104607328342288","6086730718774300509","6086664791026307819"],
    "💵": ["6089140105233044310"],
    "💎": ["6086778246882399112","5791697221799907788"],
    "👍": ["6089313931149448495","4958626617535497157","4956582500865410174"],
    "👎": ["6088789257285988672"],
    "👏": ["6093744967304352336","4956582500865410174"],
    "😀": ["6093864814071780526","6093922327978840798"],
    "😂": ["5782741660936966676","5782746664573867142"],
    "😉": ["6089024570612781324"],
    "😊": ["5780690182692935276"],
    "😍": ["6010179687001625256"],
    "😘": ["6044373012566774137"],
    "😎": ["6032853480782172520","6044373012566774137"],
    "😢": ["5780793884678296697"],
    "😭": ["5783024321324651865"],
    "😠": ["6035355642829475999","6034843326245508065"],
    "😡": ["6035355642829475999"],
    "🤔": ["5782756916660802905","5783034045130610245","6093666528316625608"],
}
FLAGS = {
    "🇮🇳": "5433601609076586221","🇺🇸": "5433865586356531140","🇬🇧": "5433827537241258614",
    "🇫🇷": "5433636707549331311","🇩🇪": "5433845881046578644","🇯🇵": "5434147542369579483",
    "🇷🇺": "5433674924168328689","🇧🇷": "5433825269498525925","🇵🇰": "5434064563601421981",
}

def utf16(s):
    return len(s.encode("utf-16-le")) // 2

def build_entities(text):
    ents = []
    total = utf16(text)
    if total > 0:
        ents.append(MessageEntity(type="bold", offset=0, length=total))
    off, i = 0, 0
    while i < len(text):
        ch = text[i]
        l = utf16(ch)
        eid = None
        if ch in EMOJI_MAPPING:
            eid = random.choice(EMOJI_MAPPING[ch])
        elif ch in FLAGS:
            eid = FLAGS[ch]
        if eid:
            ents.append(MessageEntity(type="custom_emoji", offset=off, length=l, custom_emoji_id=int(eid)))
        off += l
        i += 1
    return ents

def _send_pe(chat_id, text, markup=None):
    try:
        return bot.send_message(chat_id, text, entities=build_entities(text), reply_markup=markup)
    except Exception:
        return bot.send_message(chat_id, text, reply_markup=markup)

def sendm(chat_id, text, markup=None):
    try:
        return bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)
    except Exception:
        return bot.send_message(chat_id, text, reply_markup=markup)

# ============================================================
# FULLY GREEN / RED BUTTONS
# ============================================================
def B(text, cb=None, url=None, style="success"):
    kw = {"text": stylish_text(text)}
    if cb:  kw["callback_data"] = cb
    if url: kw["url"] = url
    kw["style"] = style
    try:
        return InlineKeyboardButton(**kw)
    except Exception:
        kw.pop("style", None)
        return InlineKeyboardButton(**kw)

def kb(rows):
    return InlineKeyboardMarkup([r if isinstance(r, list) else [r] for r in rows])

# ============================================================
# MENUS (TERE CODE KE SARE BUTTONS + NAYE)
# ============================================================
def user_menu(uid):
    rows = [
        [B("🔫 BAN ACCOUNT", cb="ban_account"), B("🔍 BAN CHECK", cb="ban_check")],
        [B("🎮 PLAYER INFO", cb="player_info"), B("📱 NUMBER INFO", cb="number_info")],
        [B("🎁 FREE TRIAL", cb="free_trial"), B("💎 UNLIMITED", cb="unlimited")],
        [B("🔑 HOW TO GET TOKEN", cb="token_guide"), B("📞 SUPPORT", cb="support")],
        [B("ℹ️ HELP", cb="help"), B("ℹ️ ABOUT", cb="about")],
    ]
    if is_admin(uid):
        rows.append([B("👑 ADMIN PANEL", cb="admin_panel")])
    return kb(rows)

def admin_menu():
    return kb([
        [B("🔫 TOTAL BANS", cb="total_bans"), B("🔁 CHECK ALL BANNED", cb="check_all_banned")],
        [B("👥 PENDING USERS", cb="pending_users"), B("👥 ALL USERS", cb="all_users")],
        [B("📊 STATS", cb="stats"), B("📦 DATA EXPORT", cb="data_export")],
        [B("💰 PRICE", cb="set_price"), B("🏦 UPI", cb="set_upi")],
        [B("🔑 TOKEN TEXT", cb="set_token_text"), B("🎬 TOKEN VIDEO", cb="token_video")],
        [B("🖼 WELCOME IMAGE", cb="set_welimg"), B("🌐 OUTFIT API", cb="set_outfit_api")],
        [B("💵 SET BAN PRICE", cb="set_ban_price"), B("🆓 SET BAN FREE", cb="set_ban_free")],
        [B("👑 TOTAL ADMINS", cb="admins"), B("📋 ALL COMMANDS", cb="all_commands")],
        [B("📢 BROADCAST", cb="broadcast"), B("🟢 BOT ON", cb="bot_on")],
        [B("🔴 BOT OFF", cb="bot_off"), B("◀️ BACK", cb="back_main")],
    ])

# ============================================================
# PROCESSING ANIMATION (purple sab jagah, number info = red)
# ============================================================
ANIM = {
    "purple": ("🟪", "🟣"),
    "red":    ("🟥", "🔴"),
}

def show_processing(chat_id, color="purple"):
    box, dot = ANIM.get(color, ANIM["purple"])
    msg = bot.send_message(chat_id, f"{box * 10}\n\n{dot} 𝟶%")
    for fill, pct in ((2, "𝟷𝟶"), (4, "𝟹𝟶"), (6, "𝟻𝟶"), (8, "𝟽𝟻"), (10, "𝟷𝟶𝟶")):
        time.sleep(0.4)
        try:
            bot.edit_message_text(f"{box * fill}{'⬜' * (10 - fill)}\n\n{dot} {pct}%", chat_id, msg.message_id)
        except Exception:
            pass
    return msg

def update_progress(msg, done, total, color="purple"):
    box, dot = ANIM.get(color, ANIM["purple"])
    if total <= 0: total = 1
    fill = min(10, max(1, round(10 * done / total)))
    pct = sd(round(100 * done / total))
    try:
        bot.edit_message_text(f"{box * fill}{'⬜' * (10 - fill)}\n\n{dot} {pct}%", msg.chat.id, msg.message_id)
    except Exception:
        pass

# ============================================================
# SIRF JSON RESPONSE (block + .json file, koi extra text nahi)
# ============================================================
def send_json_only(chat_id, data, label="DATA"):
    text = json.dumps(data, indent=2, ensure_ascii=False)
    try:
        bio = io.BytesIO(text.encode("utf-8"))
        bio.name = f"{label}.json"
        bot.send_document(chat_id, bio, visible_file_name=f"{label}.json")
    except Exception as e:
        print("json file error:", e)
    chunk = text if len(text) <= 3800 else text[:3800] + "\n...TRUNCATED..."
    try:
        bot.send_message(chat_id, f"<pre>{esc(chunk)}</pre>", parse_mode="HTML")
    except Exception:
        bot.send_message(chat_id, chunk)

# ============================================================
# PHOTOS (banner/outfit - API me URL mile toh)
# ============================================================
IMG_KEYS = ("img", "pic", "photo", "banner", "avatar", "icon", "url", "image", "head", "outfit", "skin", "pet")

def walk_urls(data, out):
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, str) and v.startswith("http") and any(t in k.lower() for t in IMG_KEYS):
                out.append(v)
            else:
                walk_urls(v, out)
    elif isinstance(data, list):
        for it in data:
            walk_urls(it, out)

def send_photos(chat_id, data, limit=2):
    urls = []
    walk_urls(data, urls)
    sent = 0
    for u in urls:
        if sent >= limit:
            break
        try:
            r = requests.get(u, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code == 200 and len(r.content) > 1500:
                bio = io.BytesIO(r.content)
                bio.name = "photo.jpg"
                bot.send_photo(chat_id, bio)
                sent += 1
        except Exception:
            pass

# ============================================================
# PAYMENT QR
# ============================================================
def send_payment_qr(chat_id, amount=None):
    s = load_settings()
    upi = s.get("upi", "vansh111@naviaxis")
    price = amount if amount is not None else s.get("price", 19)
    qr = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=upi://pay?pa={upi}&am={price}&cu=INR"
    text = (f"💰 ᴘᴀʏᴍᴇɴᴛ\n\n💳 ᴜᴘɪ: <code>{esc(upi)}</code>\n"
            f"💰 ᴀᴍᴏᴜɴᴛ: ʀs.{sd(price)}\n\n👨‍💻 @ɪꜰʟᴇxᴄᴏᴅᴇʀʀ")
    markup = kb([[B("✅ I HAVE PAID", cb="paid")], [B("❌ CANCEL", cb="cancel_flow", style="danger")]])
    try:
        bot.send_photo(chat_id, qr, caption=text, parse_mode="HTML", reply_markup=markup)
    except Exception:
        sendm(chat_id, text, markup)

# ============================================================
# START / HELP
# ============================================================
@bot.message_handler(commands=["start"])
def cmd_start(m):
    uid = m.from_user.id
    if not BOT_STATE["active"] and not is_admin(uid):
        return
    register_user(uid, m.from_user.username or "", m.from_user.first_name or "User")
    s = load_settings()
    txt = (f"⭐ ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ {esc(s.get('bot_name', 'FF BAN BOT'))} ⭐\n\n"
           f"👤 {esc(m.from_user.first_name or '')}\n\n"
           f"🔫 ʙᴀɴ ᴀᴄᴄᴏᴜɴᴛs\n🔍 ʙᴀɴ ᴄʜᴇᴄᴋ\n🎮 ᴘʟᴀʏᴇʀ ɪɴғᴏ\n📱 ɴᴜᴍʙᴇʀ ɪɴғᴏ\n\n"
           f"💰 ᴘʀɪᴄᴇ: ʀs.{sd(s.get('price', 19))}\n"
           f"🎁 ғʀᴇᴇ ᴛʀɪᴀʟ: 𝟷 ʙᴀɴ\n"
           f"👨‍💻 {esc(s.get('developer', DEV))}\n"
           f"🆘 {esc(s.get('support', DEV))}")
    img = s.get("welcome_image") or ""
    try:
        if img:
            bot.send_photo(uid, img, caption=txt, parse_mode="HTML", reply_markup=user_menu(uid))
        else:
            raise Exception("no img")
    except Exception:
        bot.send_message(uid, txt, parse_mode="HTML", reply_markup=user_menu(uid))

@bot.message_handler(commands=["help"])
def cmd_help(m):
    uid = m.from_user.id
    sendm(m.chat.id, "⭐ ʜᴏᴡ ᴛᴏ ᴜsᴇ\n\n1️⃣ ʙᴀɴ ᴀᴄᴄᴏᴜɴᴛ ᴅʙᴀᴏ\n2️⃣ ᴛᴏᴋᴇɴ ʙʜᴇᴊᴏ\n3️⃣ ʏᴇs ᴘʀᴇss ᴋᴀʀᴏ\n4️⃣ ᴀᴄᴄᴏᴜɴᴛ ʙᴀɴ 🔫\n\n👨‍💻 @ɪꜰʟᴇxᴄᴏᴅᴇʀʀ", user_menu(uid))

# ============================================================
# MAIN CALLBACK DISPATCHER
# ============================================================
@bot.callback_query_handler(func=lambda c: True)
def on_cb(c):
    try:
        bot.answer_callback_query(c.id)
    except Exception:
        pass
    uid = c.from_user.id
    data = c.data or ""
    chat_id = c.message.chat.id if c.message else None
    if chat_id is None:
        return
    if not BOT_STATE["active"] and not is_admin(uid):
        return
    s = load_settings()
    u = get_user(uid)

    if data == "ban_account":
        if u.get("banned"):
            _send_pe(chat_id, "❌ ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ!"); return
        if not (is_admin(uid) or u.get("unlimited") or u.get("uses", 0) < 1):
            sendm(chat_id, f"⚠️ ғʀᴇᴇ ᴛʀɪᴀʟ ᴜsᴇᴅ!\n💰 ʀs.{sd(s.get('price', 19))}",
                  kb([[B("💳 PAY NOW", cb="unlimited")]])); return
        state[uid] = "ban_token"
        _send_pe(chat_id, "🔑 sᴇɴᴅ ᴛʜᴇ ᴀᴄᴄᴇss ᴛᴏᴋᴇɴ:",
                 kb([[B("❌ CANCEL", cb="cancel_flow", style="danger")]]))
        bot.register_next_step_handler(c.message, handle_ban_token)

    elif data == "confirm_ban":
        info = state.get(uid)
        if not info or not isinstance(info, dict) or info.get("action") != "confirm":
            return
        state.pop(uid, None)
        anim = show_processing(chat_id, "purple")
        try:
            r = requests.get(BAN_API.format(token=info["token"]), timeout=30)
            res = r.json()
        except Exception as e:
            try: bot.delete_message(chat_id, anim.message_id)
            except Exception: pass
            sendm(chat_id, f"❌ ᴇʀʀᴏʀ: {esc(str(e))}")
            return
        try: bot.delete_message(chat_id, anim.message_id)
        except Exception: pass
        acc_id = res.get("id", "N/A"); acc_name = res.get("name", "N/A")
        acc_uid = res.get("uid", "N/A"); status = res.get("status", "UNKNOWN")
        if "BANNED" in str(status).upper():
            if not (is_admin(uid) or u.get("unlimited")):
                update_user(uid, "uses", u.get("uses", 0) + 1)
            bans = load_bans()
            bans.append({"uid": acc_uid, "name": acc_name, "account_id": acc_id, "status": status,
                         "banned_by": uid, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            save_bans(bans)
            try:
                bot.send_message(OWNER_ID, f"✅ ʙᴀɴɴᴇᴅ!\n👤 {uid}\n🔢 {acc_uid}")
            except Exception:
                pass
            _send_pe(chat_id, f"✅ ᴀᴄᴄᴏᴜɴᴛ ʙᴀɴɴᴇᴅ!\n\n🆔 {acc_id}\n👤 {acc_name}\n🔢 {acc_uid}\n\n👨‍💻 @ɪꜰʟᴇxᴄᴏᴅᴇʀʀ",
                     kb([[B("🔫 BAN ANOTHER", cb="ban_another")], [B("💎 GET UNLIMITED", cb="unlimited")]]))
        else:
            _send_pe(chat_id, f"❌ ʙᴀɴ ғᴀɪʟᴇᴅ!\n\n🆔 {acc_id}\n👤 {acc_name}\n🔢 {acc_uid}\n📌 {status}\n\n👨‍💻 @ɪꜰʟᴇxᴄᴏᴅᴇʀʀ")

    elif data == "ban_another":
        state[uid] = "ban_token"
        _send_pe(chat_id, "🔑 sᴇɴᴅ ᴛᴏᴋᴇɴ:",
                 kb([[B("❌ CANCEL", cb="cancel_flow", style="danger")]]))
        bot.register_next_step_handler(c.message, handle_ban_token)

    elif data == "cancel_ban":
        state.pop(uid, None)
        _send_pe(chat_id, "✅ ᴄᴀɴᴄᴇʟʟᴇᴅ!", user_menu(uid))

    elif data == "cancel_flow":
        state.pop(uid, None)
        _send_pe(chat_id, "↩️ ᴏᴋ, ᴄᴀɴᴄᴇʟ!", user_menu(uid))

    elif data == "ban_check":
        if u.get("banned"):
            _send_pe(chat_id, "❌ ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ!"); return
        bp = s.get("ban_price", 0)
        if bp > 0 and not (is_admin(uid) or u.get("ban_paid")):
            send_payment_qr(chat_id, bp)
            return
        state[uid] = "uid_bancheck"
        _send_pe(chat_id, "🔍 ᴜɪᴅ ʙʜᴇᴊᴏ:",
                 kb([[B("❌ CANCEL", cb="cancel_flow", style="danger")]]))
        bot.register_next_step_handler(c.message, handle_uid_bancheck)

    elif data == "player_info":
        if u.get("banned"):
            _send_pe(chat_id, "❌ ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ!"); return
        state[uid] = "uid_player"
        _send_pe(chat_id, "🎮 ᴘʟᴀʏᴇʀ ᴜɪᴅ ʙʜᴇᴊᴏ:",
                 kb([[B("❌ CANCEL", cb="cancel_flow", style="danger")]]))
        bot.register_next_step_handler(c.message, handle_uid_player)

    elif data == "number_info":
        if u.get("banned"):
            _send_pe(chat_id, "❌ ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ!"); return
        state[uid] = "number"
        _send_pe(chat_id, "📱 ɴᴜᴍʙᴇʀ ʙʜᴇᴊᴏ:",
                 kb([[B("❌ CANCEL", cb="cancel_flow", style="danger")]]))
        bot.register_next_step_handler(c.message, handle_number)

    elif data == "free_trial":
        if u.get("unlimited"):
            _send_pe(chat_id, "✅ ᴀʟʀᴇᴀᴅʏ ᴜɴʟɪᴍɪᴛᴇᴅ!"); return
        if u.get("uses", 0) >= 1:
            sendm(chat_id, f"⚠️ ᴜsᴇᴅ! ʀs.{sd(s.get('price', 19))}", kb([[B("💳 PAY NOW", cb="unlimited")]])); return
        _send_pe(chat_id, "🎁 ғʀᴇᴇ ᴛʀɪᴀʟ ᴀᴄᴛɪᴠᴇ!\n\n🔫 ʙᴀɴ ᴀᴄᴄᴏᴜɴᴛ ᴅʙᴀᴏ ᴀᴜʀ ᴛᴏᴋᴇɴ ʙʜᴇᴊᴏ\n\n👨‍💻 @ɪꜰʟᴇxᴄᴏᴅᴇʀʀ")

    elif data == "unlimited":
        send_payment_qr(chat_id)

    elif data == "paid":
        state[uid] = "screenshot"
        _send_pe(chat_id, "📸 sᴇɴᴅ ᴘᴀʏᴍᴇɴᴛ sᴄʀᴇᴇɴsʜᴏᴛ:",
                 kb([[B("❌ CANCEL", cb="cancel_flow", style="danger")]]))
        bot.register_next_step_handler(c.message, handle_screenshot)

    elif data == "token_guide":
        guide = f"🔑 ʜᴏᴡ ᴛᴏ ɢᴇᴛ ᴛᴏᴋᴇɴ\n\n{s.get('token_text', '')}"
        _send_pe(chat_id, guide)
        if os.path.exists("token_video.mp4"):
            try:
                with open("token_video.mp4", "rb") as f:
                    bot.send_video(chat_id, f, caption="🎬 ᴠɪᴅᴇᴏ ɢᴜɪᴅᴇ")
            except Exception:
                pass

    elif data == "support":
        sup = s.get("support", DEV)
        _send_pe(chat_id, f"📞 sᴜᴘᴘᴏʀᴛ\n\n{sup}",
                 kb([[B("📞 CONTACT", url=f"https://t.me/{sup.replace('@', '')}")], [B("◀️ BACK", cb="back_main")]]))

    elif data == "help":
        _send_pe(chat_id, "⭐ ʜᴇʟᴘ\n\n1️⃣ ʙᴀɴ ᴀᴄᴄᴏᴜɴᴛ\n2️⃣ ᴛᴏᴋᴇɴ ʙʜᴇᴊᴏ\n3️⃣ ʏᴇs ᴘʀᴇss\n4️⃣ ʙᴀɴ 🔫\n\n🎮 ᴘʟᴀʏᴇʀ ɪɴғᴏ\n📱 ɴᴜᴍʙᴇʀ ɪɴғᴏ\n🔍 ʙᴀɴ ᴄʜᴇᴄᴋ\n\n👨‍💻 @ɪꜰʟᴇxᴄᴏᴅᴇʀʀ")

    elif data == "about":
        _send_pe(chat_id, f"ℹ️ ᴀʙᴏᴜᴛ\n\n🤖 {esc(s.get('bot_name', 'FF BAN BOT'))}\n👨‍💻 ᴅᴇᴠ: {esc(s.get('developer', DEV))}\n🆘 {esc(s.get('support', DEV))}")

    elif data == "back_main":
        _send_pe(chat_id, "🏠 ᴍᴀɪɴ ᴍᴇɴᴜ", user_menu(uid))

    # ================= ADMIN PANEL =================
    elif data == "admin_panel":
        if not is_admin(uid): return
        _send_pe(chat_id, "👑 ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ", admin_menu())

    elif data == "total_bans":
        if not is_admin(uid): return
        bans = load_bans()
        t = f"🔫 ᴛᴏᴛᴀʟ ɪᴅs ʙᴀɴɴᴇᴅ: {sd(len(bans))}\n\n"
        for b in bans[-15:]:
            t += f"• {esc(b.get('name', '?'))} (UID {esc(b.get('uid', '?'))}) - {str(b.get('time', ''))[:16]}\n"
        _send_pe(chat_id, t if bans else "⭐ ᴋᴏɪ ʙᴀɴ ʀᴇᴄᴏʀᴅ ɴᴀʜɪ",
                 kb([[B("📄 FULL LIST (JSON)", cb="bans_json")], [B("◀️ BACK", cb="admin_panel")]]))

    elif data == "bans_json":
        if not is_admin(uid): return
        send_json_only(chat_id, {"total": len(load_bans()), "bans": load_bans()}, "ALL_BANS")

    elif data == "check_all_banned":
        if not is_admin(uid): return
        bans = load_bans()
        if not bans:
            _send_pe(chat_id, "⭐ ᴋᴏɪ ʙᴀɴ ʀᴇᴄᴏʀᴅ ɴᴀʜɪ"); return
        anim = show_processing(chat_id, "purple")
        results = {}
        n = len(bans)
        for i, b in enumerate(bans):
            try:
                r = requests.get(BANCHECK_API.format(uid=b["uid"]), timeout=10)
                d = r.json() if r.status_code == 200 else {"error": f"HTTP {r.status_code}"}
                results[b["uid"]] = d[0] if isinstance(d, list) and d else d
            except Exception as e:
                results[b["uid"]] = {"error": str(e)}
            if (i + 1) % 3 == 0:
                update_progress(anim, i + 1, n)
        try: bot.delete_message(chat_id, anim.message_id)
        except Exception: pass
        send_json_only(chat_id, {"total_checked": n, "results": results}, "CHECK_ALL_BANNED")

    elif data == "pending_users":
        if not is_admin(uid): return
        pend = load_pending()
        if not pend:
            _send_pe(chat_id, "✅ ᴋᴏɪ ᴘᴇɴᴅɪɴɢ ɴᴀʜɪ", kb([[B("◀️ BACK", cb="admin_panel")]])); return
        rows = []
        for p_uid, info in pend.items():
            rows.append([B(f"✅ {esc(info.get('name', 'User'))} {p_uid}", cb=f"apprv_{p_uid}"),
                         B("❌", cb=f"rejct_{p_uid}", style="danger")])
        rows.append([B("◀️ BACK", cb="admin_panel")])
        _send_pe(chat_id, "👥 ᴘᴇɴᴅɪɴɢ ᴜsᴇʀs", kb(rows))

    elif data.startswith("apprv_"):
        if not is_admin(uid): return
        p_uid = data.split("_", 1)[1]
        pend = load_pending()
        if p_uid in pend:
            del pend[p_uid]; save_pending(pend)
        update_user(p_uid, "unlimited", True)
        update_user(p_uid, "ban_paid", True)
        update_user(p_uid, "uses", 0)
        try:
            bot.send_message(int(p_uid), "🎉 ᴜɴʟɪᴍɪᴛᴇᴅ ᴀᴄᴛɪᴠᴇ! 🎉\n\n👨‍💻 @ɪꜰʟᴇxᴄᴏᴅᴇʀʀ")
        except Exception: pass
        _send_pe(chat_id, f"✅ {p_uid} ᴀᴘᴘʀᴏᴠᴇᴅ!")

    elif data.startswith("rejct_"):
        if not is_admin(uid): return
        p_uid = data.split("_", 1)[1]
        pend = load_pending()
        if p_uid in pend:
            del pend[p_uid]; save_pending(pend)
        _send_pe(chat_id, f"❌ {p_uid} ʀᴇᴊᴇᴄᴛᴇᴅ!")

    elif data == "all_users":
        if not is_admin(uid): return
        users = load_users()
        t = f"👥 ᴛᴏᴛᴀʟ: {sd(len(users))}\n\n"
        for u_id, d in users.items():
            st = "💎" if d.get("unlimited") else "🆓"
            bn = "🚫" if d.get("banned") else "✅"
            ad = "👑" if is_admin(int(u_id)) else ""
            t += f"• {esc(d.get('name', '?'))} (@{esc(d.get('username', '-'))}) {st}{bn}{ad}\n"
        _send_pe(chat_id, t)

    elif data == "stats":
        if not is_admin(uid): return
        users = load_users()
        _send_pe(chat_id, (f"📊 sᴛᴀᴛs\n\n👥 ᴜsᴇʀs: {sd(len(users))}\n"
                           f"🔫 ʙᴀɴs: {sd(len(load_bans()))}\n"
                           f"💰 ᴘᴇɴᴅɪɴɢ: {sd(len(load_pending()))}\n"
                           f"💎 ᴜɴʟɪᴍɪᴛᴇᴅ: {sd(sum(1 for x in users.values() if x.get('unlimited')))}\n"
                           f"💰 ᴘʀɪᴄᴇ: ʀs.{sd(s.get('price', 19))}\n"
                           f"🏦 {esc(s.get('upi', ''))}"))

    elif data == "data_export":
        if not is_admin(uid): return
        send_json_only(chat_id, {"users": load_users(), "pending": load_pending(),
                                 "bans": load_bans(), "settings": s, "admins": ADMIN_IDS}, "BOT_DATA")

    elif data == "set_price":
        if not is_admin(uid): return
        state[uid] = "set_price"
        _send_pe(chat_id, f"💰 ᴄᴜʀʀᴇɴᴛ: ʀs.{sd(s.get('price', 19))}\n🆕 ɴʏᴀ ᴘʀɪᴄᴇ ʙʜᴇᴊᴏ:",
                 kb([[B("❌ CANCEL", cb="cancel_flow", style="danger")]]))
        bot.register_next_step_handler(c.message, handle_set_price)

    elif data == "set_upi":
        if not is_admin(uid): return
        state[uid] = "set_upi"
        _send_pe(chat_id, f"🏦 ᴄᴜʀʀᴇɴᴛ: {esc(s.get('upi', ''))}\n🆕 ʙʜᴇᴊᴏ:",
                 kb([[B("❌ CANCEL", cb="cancel_flow", style="danger")]]))
        bot.register_next_step_handler(c.message, handle_set_upi)

    elif data == "set_token_text":
        if not is_admin(uid): return
        state[uid] = "set_token"
        _send_pe(chat_id, "🔑 ɴʏᴀ ᴛᴏᴋᴇɴ ᴛᴇxᴛ ʙʜᴇᴊᴏ:",
                 kb([[B("❌ CANCEL", cb="cancel_flow", style="danger")]]))
        bot.register_next_step_handler(c.message, handle_set_token)

    elif data == "token_video":
        if not is_admin(uid): return
        state[uid] = "token_video"
        _send_pe(chat_id, "🎬 ᴛᴏᴋᴇɴ ɢᴜɪᴅᴇ ᴠɪᴅᴇᴏ ʙʜᴇᴊᴏ:",
                 kb([[B("❌ CANCEL", cb="cancel_flow", style="danger")]]))
        bot.register_next_step_handler(c.message, handle_token_video)

    elif data == "set_welimg":
        if not is_admin(uid): return
        state[uid] = "set_welimg"
        _send_pe(chat_id, "🖼 ᴡᴇʟᴄᴏᴍᴇ ɪᴍᴀɢᴇ ʙʜᴇᴊᴏ (ᴘʜᴏᴛᴏ ʏᴀ ɪᴍᴀɢᴇ URL):",
                 kb([[B("❌ CANCEL", cb="cancel_flow", style="danger")]]))
        bot.register_next_step_handler(c.message, handle_set_welimg)

    elif data == "set_outfit_api":
        if not is_admin(uid): return
        state[uid] = "set_outfit"
        _send_pe(chat_id, "🌐 ɴʏᴀ ᴏᴜᴛғɪᴛ/ᴘʟᴀʏᴇʀ ᴀᴘɪ ʙʜᴇᴊᴏ:\n(ᴜsᴇ {uid})",
                 kb([[B("❌ CANCEL", cb="cancel_flow", style="danger")]]))
        bot.register_next_step_handler(c.message, handle_set_outfit)

    elif data == "set_ban_price":
        if not is_admin(uid): return
        state[uid] = "set_ban_price"
        _send_pe(chat_id, f"💵 ᴄᴜʀʀᴇɴᴛ ʙᴀɴ ᴘʀɪᴄᴇ: ʀs.{sd(s.get('ban_price', 0))}\n🆕 ʙʜᴇᴊᴏ (0 = ғʀᴇᴇ):",
                 kb([[B("❌ CANCEL", cb="cancel_flow", style="danger")]]))
        bot.register_next_step_handler(c.message, handle_set_ban_price)

    elif data == "set_ban_free":
        if not is_admin(uid): return
        s["ban_price"] = 0
        save_settings(s)
        _send_pe(chat_id, "✅ ʙᴀɴ ᴄʜᴇᴄᴋ ɴᴏᴡ ғʀᴇᴇ ғᴏʀ ᴇᴠᴇʀʏᴏɴᴇ! 🎉")

    elif data == "admins":
        if not is_admin(uid): return
        t = f"👑 ᴛᴏᴛᴀʟ ᴀᴅᴍɪɴs ({sd(len(ADMIN_IDS))})\n\n"
        for a in ADMIN_IDS:
            au = get_user(a)
            t += f"• {esc(au.get('name', '?'))} (@{esc(au.get('username', '-'))}) - {a}\n"
        _send_pe(chat_id, t)

    elif data == "all_commands":
        if not is_admin(uid): return
        _send_pe(chat_id, "📋 ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs\n\n"
                 "/approve ID\n/disapprove ID\n/ban ID\n/unban ID\n/users\n/checkall\n/data\n"
                 "/totaladmins\n/price <AMT>\n/upi <UPI>\n/developer <@>\n/addadmin ID\n"
                 "/setoutfitapi URL\n/setbanprice <AMT>\n/broadcastuser ID MSG\n/allbroadcast MSG")

    elif data == "broadcast":
        if not is_admin(uid): return
        state[uid] = "broadcast"
        _send_pe(chat_id, "📢 ᴀʟʟ ᴜsᴇʀs ᴋᴏ ʙʜᴇᴊɴᴇ ᴋᴀ ᴍᴇssᴀɢᴇ ʟɪᴋʜᴏ:",
                 kb([[B("❌ CANCEL", cb="cancel_flow", style="danger")]]))
        bot.register_next_step_handler(c.message, handle_broadcast)

    elif data == "bot_on":
        if not is_admin(uid): return
        BOT_STATE["active"] = True
        _send_pe(chat_id, "✅ 🟢 ʙᴏᴛ ᴏɴʟɪɴᴇ!")

    elif data == "bot_off":
        if not is_admin(uid): return
        BOT_STATE["active"] = False
        _send_pe(chat_id, "✅ 🔴 ʙᴏᴛ ᴏғғʟɪɴᴇ!")

# ============================================================
# FLOW HANDLERS
# ============================================================
def handle_ban_token(message):
    uid = message.from_user.id
    token = (message.text or "").strip()
    if len(token) < 30:
        _send_pe(message.chat.id, "❌ ɪɴᴠᴀʟɪᴅ ᴛᴏᴋᴇɴ!")
        return
    state[uid] = {"action": "confirm", "token": token}
    markup = kb([
        [B("✅ YES, I AM 100% SURE", cb="confirm_ban")],
        [B("❌ NO, CANCEL", cb="cancel_ban", style="danger")],
    ])
    _send_pe(message.chat.id, "⚠️ ᴄᴏɴғɪʀᴍᴀᴛɪᴏɴ\n\n⚠️ ᴛʜɪs ᴀᴄᴛɪᴏɴ ᴄᴀɴɴᴏᴛ ʙᴇ ᴜɴᴅᴏɴᴇ!", markup)

def handle_uid_bancheck(message):
    uid = message.from_user.id
    state.pop(uid, None)
    val = (message.text or "").strip()
    if not val.isdigit():
        _send_pe(message.chat.id, "❌ ɪɴᴠᴀʟɪᴅ ᴜɪᴅ!"); return
    anim = show_processing(message.chat.id, "purple")
    try:
        r = requests.get(BANCHECK_API.format(uid=val), timeout=15)
        data = r.json() if r.status_code == 200 else {"http_status": r.status_code, "raw": r.text[:300]}
    except Exception as e:
        data = {"error": str(e)}
    try: bot.delete_message(message.chat.id, anim.message_id)
    except Exception: pass
    if isinstance(data, list) and data:
        data = data[0]
    send_json_only(message.chat.id, data, f"BAN_CHECK_{val}")

def handle_uid_player(message):
    uid = message.from_user.id
    state.pop(uid, None)
    val = (message.text or "").strip()
    if not val.isdigit():
        _send_pe(message.chat.id, "❌ ɪɴᴠᴀʟɪᴅ ᴜɪᴅ!"); return
    anim = show_processing(message.chat.id, "purple")
    try:
        api = load_settings().get("outfit_api") or PLAYER_API
        api = api.replace("{uid}", val)
        r = requests.get(api, timeout=15)
        data = r.json() if r.status_code == 200 else {"http_status": r.status_code, "raw": r.text[:300]}
    except Exception as e:
        data = {"error": str(e)}
    try: bot.delete_message(message.chat.id, anim.message_id)
    except Exception: pass
    if isinstance(data, dict) and isinstance(data.get("data"), dict):
        data = data["data"]
    if isinstance(data, list) and data:
        data = data[0]
    send_json_only(message.chat.id, data, f"PLAYER_{val}")
    send_photos(message.chat.id, data)

def handle_number(message):
    uid = message.from_user.id
    state.pop(uid, None)
    val = (message.text or "").strip()
    if not val.isdigit():
        _send_pe(message.chat.id, "❌ ɪɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ!"); return
    anim = show_processing(message.chat.id, "red")  # 🔴 RED boxes
    try:
        r = requests.get(NUMBER_API.format(number=val), timeout=15)
        data = r.json() if r.status_code == 200 else {"http_status": r.status_code, "raw": r.text[:300]}
    except Exception as e:
        data = {"error": str(e)}
    try: bot.delete_message(message.chat.id, anim.message_id)
    except Exception: pass
    if isinstance(data, list) and data:
        data = data[0]
    send_json_only(message.chat.id, data, f"NUMBER_{val}")

def handle_screenshot(message):
    uid = message.from_user.id
    state.pop(uid, None)
    if not message.photo:
        _send_pe(message.chat.id, "❌ sᴇɴᴅ ᴀ ᴘʜᴏᴛᴏ!"); return
    file_id = message.photo[-1].file_id
    pend = load_pending()
    pend[str(uid)] = {"name": message.from_user.first_name or "User",
                      "username": message.from_user.username or "",
                      "status": "pending", "screenshot": file_id,
                      "requested": datetime.now().isoformat()}
    save_pending(pend)
    _send_pe(message.chat.id, "✅ ʀᴇᴄᴇɪᴠᴇᴅ! ⏳ ᴀᴅᴍɪɴ ᴀᴘᴘʀᴏᴠᴇ ᴋᴀʀᴇɢᴀ")
    for admin in ADMIN_IDS:
        try:
            bot.send_photo(admin, file_id,
                           caption=f"💰 ɴᴇᴡ ᴘᴀʏᴍᴇɴᴛ\n\n👤 {message.from_user.first_name}\n🆔 {uid}\n👾 @{message.from_user.username or '-'}",
                           reply_markup=kb([[B("✅ APPROVE", cb=f"apprv_{uid}")],
                                            [B("❌ DISAPPROVE", cb=f"rejct_{uid}", style="danger")]]))
        except Exception:
            pass

def handle_set_price(message):
    uid = message.from_user.id
    state.pop(uid, None)
    if not is_admin(uid): return
    try:
        price = int((message.text or "").strip())
        if price < 0:
            _send_pe(message.chat.id, "❌ ɴᴇɢᴀᴛɪᴠᴇ ɴᴀʜɪ ʜᴏ sᴀᴋᴛᴀ!"); return
        s = load_settings(); s["price"] = price; save_settings(s)
        _send_pe(message.chat.id, f"✅ ᴘʀɪᴄᴇ: ʀs.{sd(price)}")
    except Exception:
        _send_pe(message.chat.id, "❌ ɪɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ!")

def handle_set_upi(message):
    uid = message.from_user.id
    state.pop(uid, None)
    if not is_admin(uid): return
    val = (message.text or "").strip()
    if "@" not in val:
        _send_pe(message.chat.id, "❌ ɪɴᴠᴀʟɪᴅ ᴜᴘɪ!"); return
    s = load_settings(); s["upi"] = val; save_settings(s)
    _send_pe(message.chat.id, f"✅ ᴜᴘɪ: {val}")

def handle_set_token(message):
    uid = message.from_user.id
    state.pop(uid, None)
    if not is_admin(uid): return
    s = load_settings(); s["token_text"] = (message.text or "").strip(); save_settings(s)
    _send_pe(message.chat.id, "✅ ᴛᴏᴋᴇɴ ᴛᴇxᴛ sᴀᴠᴇᴅ!")

def handle_token_video(message):
    uid = message.from_user.id
    state.pop(uid, None)
    if not is_admin(uid): return
    if message.video:
        try:
            file_info = bot.get_file(message.video.file_id)
            downloaded = bot.download_file(file_info.file_path)
            with open("token_video.mp4", "wb") as f:
                f.write(downloaded)
            _send_pe(message.chat.id, "✅ ᴛᴏᴋᴇɴ ᴠɪᴅᴇᴏ sᴀᴠᴇᴅ!")
        except Exception as e:
            _send_pe(message.chat.id, f"❌ ᴇʀʀᴏʀ: {esc(str(e))}")
    else:
        _send_pe(message.chat.id, "❌ sᴇɴᴅ ᴀ ᴠɪᴅᴇᴏ!")

def handle_set_welimg(message):
    uid = message.from_user.id
    state.pop(uid, None)
    if not is_admin(uid): return
    s = load_settings()
    if message.photo:
        s["welcome_image"] = message.photo[-1].file_id
        save_settings(s)
        _send_pe(message.chat.id, "✅ ᴡᴇʟᴄᴏᴍᴇ ɪᴍᴀɢᴇ ᴜᴘᴅᴀᴛᴇᴅ!")
    elif (message.text or "").startswith("http"):
        s["welcome_image"] = message.text.strip()
        save_settings(s)
        _send_pe(message.chat.id, "✅ ᴡᴇʟᴄᴏᴍᴇ ɪᴍᴀɢᴇ URL ᴜᴘᴅᴀᴛᴇᴅ!")
    else:
        _send_pe(message.chat.id, "❌ sᴇɴᴅ ᴀ ᴘʜᴏᴛᴏ ʏᴀ ᴠᴀʟɪᴅ URL!")

def handle_set_outfit(message):
    uid = message.from_user.id
    state.pop(uid, None)
    if not is_admin(uid): return
    api = (message.text or "").strip()
    if not api.startswith("http"):
        _send_pe(message.chat.id, "❌ ɪɴᴠᴀʟɪᴅ ᴜʀʟ!"); return
    s = load_settings(); s["outfit_api"] = api; save_settings(s)
    _send_pe(message.chat.id, "✅ ᴏᴜᴛғɪᴛ ᴀᴘɪ sᴀᴠᴇᴅ!")

def handle_set_ban_price(message):
    uid = message.from_user.id
    state.pop(uid, None)
    if not is_admin(uid): return
    try:
        price = int((message.text or "").strip())
        if price < 0:
            _send_pe(message.chat.id, "❌ ɴᴇɢᴀᴛɪᴠᴇ ɴᴀʜɪ!"); return
        s = load_settings(); s["ban_price"] = price; save_settings(s)
        _send_pe(message.chat.id, f"✅ ʙᴀɴ ᴘʀɪᴄᴇ: ʀs.{sd(price)}")
    except Exception:
        _send_pe(message.chat.id, "❌ ɪɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ!")

def handle_broadcast(message):
    uid = message.from_user.id
    state.pop(uid, None)
    if not is_admin(uid): return
    msg_text = (message.text or "").strip()
    if not msg_text:
        _send_pe(message.chat.id, "❌ ᴇᴍᴘᴛʏ!"); return
    users = load_users()
    sent = failed = 0
    for u_id in users:
        try:
            bot.send_message(int(u_id), f"📢 {msg_text}")
            sent += 1
            time.sleep(0.05)
        except Exception:
            failed += 1
    _send_pe(message.chat.id, f"⭐ ᴅᴏɴᴇ! ✅ {sd(sent)} / {sd(len(users))} | ❌ {sd(failed)}")

# ============================================================
# SLASH COMMANDS (ADMIN)
# ============================================================
@bot.message_handler(commands=["approve"])
def cmd_approve(m):
    if not is_admin(m.from_user.id): return
    p = (m.text or "").split()
    if len(p) < 2: _send_pe(m.chat.id, "❌ /approve ID"); return
    try: target = int(p[1])
    except: _send_pe(m.chat.id, "❌ ɪɴᴠᴀʟɪᴅ ɪᴅ!"); return
    update_user(target, "unlimited", True); update_user(target, "ban_paid", True); update_user(target, "uses", 0)
    pend = load_pending()
    if str(target) in pend: del pend[str(target)]; save_pending(pend)
    try: bot.send_message(target, "🎉 ᴜɴʟɪᴍɪᴛᴇᴅ ᴀᴄᴛɪᴠᴇ! 🎉\n\n👨‍💻 @ɪꜰʟᴇxᴄᴏᴅᴇʀʀ")
    except Exception: pass
    _send_pe(m.chat.id, f"✅ {target} ᴀᴘᴘʀᴏᴠᴇᴅ!")

@bot.message_handler(commands=["disapprove"])
def cmd_disapprove(m):
    if not is_admin(m.from_user.id): return
    p = (m.text or "").split()
    if len(p) < 2: _send_pe(m.chat.id, "❌ /disapprove ID"); return
    try: target = int(p[1])
    except: _send_pe(m.chat.id, "❌ ɪɴᴠᴀʟɪᴅ ɪᴅ!"); return
    pend = load_pending()
    if str(target) in pend: del pend[str(target)]; save_pending(pend)
    _send_pe(m.chat.id, f"❌ {target} ʀᴇᴊᴇᴄᴛᴇᴅ!")

@bot.message_handler(commands=["ban"])
def cmd_ban(m):
    if not is_admin(m.from_user.id): return
    p = (m.text or "").split()
    if len(p) < 2: _send_pe(m.chat.id, "❌ /ban ID"); return
    try: target = int(p[1])
    except: _send_pe(m.chat.id, "❌ ɪɴᴠᴀʟɪᴅ ɪᴅ!"); return
    update_user(target, "banned", True)
    _send_pe(m.chat.id, f"✅ {target} ʙᴀɴɴᴇᴅ!")

@bot.message_handler(commands=["unban"])
def cmd_unban(m):
    if not is_admin(m.from_user.id): return
    p = (m.text or "").split()
    if len(p) < 2: _send_pe(m.chat.id, "❌ /unban ID"); return
    try: target = int(p[1])
    except: _send_pe(m.chat.id, "❌ ɪɴᴠᴀʟɪᴅ ɪᴅ!"); return
    update_user(target, "banned", False)
    _send_pe(m.chat.id, f"✅ {target} ᴜɴʙᴀɴɴᴇᴅ!")

@bot.message_handler(commands=["users", "checkall"])
def cmd_users(m):
    if not is_admin(m.from_user.id): return
    users = load_users()
    t = f"👥 ᴛᴏᴛᴀʟ: {sd(len(users))}\n\n"
    for u_id, d in users.items():
        st = "💎" if d.get("unlimited") else "🆓"
        bn = "🚫" if d.get("banned") else "✅"
        ad = "👑" if is_admin(int(u_id)) else ""
        t += f"• {esc(d.get('name', '?'))} (@{esc(d.get('username', '-'))}) {st}{bn}{ad}\n"
    _send_pe(m.chat.id, t)

@bot.message_handler(commands=["data"])
def cmd_data(m):
    if not is_admin(m.from_user.id): return
    send_json_only(m.chat.id, {"users": load_users(), "pending": load_pending(),
                               "bans": load_bans(), "settings": load_settings(), "admins": ADMIN_IDS}, "BOT_DATA")

@bot.message_handler(commands=["totaladmins"])
def cmd_totaladmins(m):
    if not is_admin(m.from_user.id): return
    t = f"👑 ᴛᴏᴛᴀʟ ᴀᴅᴍɪɴs ({sd(len(ADMIN_IDS))})\n\n"
    for a in ADMIN_IDS:
        au = get_user(a)
        t += f"• {esc(au.get('name', '?'))} (@{esc(au.get('username', '-'))}) - {a}\n"
    _send_pe(m.chat.id, t)

@bot.message_handler(commands=["price"])
def cmd_price(m):
    if not is_admin(m.from_user.id): return
    p = (m.text or "").split()
    if len(p) < 2:
        _send_pe(m.chat.id, f"💰 ᴄᴜʀʀᴇɴᴛ: ʀs.{sd(load_settings().get('price', 19))}\n/price <AMT>"); return
    try:
        price = int(p[1])
        if price < 0: _send_pe(m.chat.id, "❌ ɴᴇɢᴀᴛɪᴠᴇ ɴᴀʜɪ!"); return
        s = load_settings(); s["price"] = price; save_settings(s)
        _send_pe(m.chat.id, f"✅ ᴘʀɪᴄᴇ: ʀs.{sd(price)}")
    except Exception:
        _send_pe(m.chat.id, "❌ ɪɴᴠᴀʟɪᴅ!")

@bot.message_handler(commands=["upi"])
def cmd_upi(m):
    if not is_admin(m.from_user.id): return
    p = (m.text or "").split()
    if len(p) < 2:
        _send_pe(m.chat.id, f"🏦 ᴄᴜʀʀᴇɴᴛ: {load_settings().get('upi', '')}\n/upi <UPI>"); return
    val = p[1]
    if "@" not in val: _send_pe(m.chat.id, "❌ ɪɴᴠᴀʟɪᴅ!"); return
    s = load_settings(); s["upi"] = val; save_settings(s)
    _send_pe(m.chat.id, f"✅ ᴜᴘɪ: {val}")

@bot.message_handler(commands=["developer"])
def cmd_dev(m):
    if not is_admin(m.from_user.id): return
    p = (m.text or "").split()
    if len(p) < 2:
        _send_pe(m.chat.id, f"👨‍💻 ᴄᴜʀʀᴇɴᴛ: {load_settings().get('developer', DEV)}\n/developer <@>"); return
    val = p[1]
    s = load_settings(); s["developer"] = val; s["support"] = val; save_settings(s)
    _send_pe(m.chat.id, f"✅ ᴅᴇᴠ: {val}")

@bot.message_handler(commands=["addadmin"])
def cmd_addadmin(m):
    if not is_admin(m.from_user.id): return
    p = (m.text or "").split()
    if len(p) < 2: _send_pe(m.chat.id, "❌ /addadmin ID"); return
    try: target = int(p[1])
    except: _send_pe(m.chat.id, "❌ ɪɴᴠᴀʟɪᴅ ɪᴅ!"); return
    if target in ADMIN_IDS: _send_pe(m.chat.id, "⚠️ ᴀʟʀᴇᴀᴅʏ ᴀᴅᴍɪɴ"); return
    ADMIN_IDS.append(target)
    _send_pe(m.chat.id, f"✅ {target} ᴀᴅᴍɪɴ ʙᴀɴᴀʏᴀ!")

@bot.message_handler(commands=["setoutfitapi"])
def cmd_setoutfit(m):
    if not is_admin(m.from_user.id): return
    p = (m.text or "").split()
    if len(p) < 2: _send_pe(m.chat.id, "❌ /setoutfitapi URL"); return
    api = p[1].strip()
    if not api.startswith("http"): _send_pe(m.chat.id, "❌ ɪɴᴠᴀʟɪᴅ ᴜʀʟ!"); return
    s = load_settings(); s["outfit_api"] = api; save_settings(s)
    _send_pe(m.chat.id, "✅ ᴏᴜᴛғɪᴛ ᴀᴘɪ sᴀᴠᴇᴅ!")

@bot.message_handler(commands=["setbanprice"])
def cmd_setbanprice(m):
    if not is_admin(m.from_user.id): return
    p = (m.text or "").split()
    if len(p) < 2:
        _send_pe(m.chat.id, f"💵 ᴄᴜʀʀᴇɴᴛ: ʀs.{sd(load_settings().get('ban_price', 0))}\n/setbanprice <AMT>"); return
    try:
        price = int(p[1])
        if price < 0: _send_pe(m.chat.id, "❌ ɴᴇɢᴀᴛɪᴠᴇ ɴᴀʜɪ!"); return
        s = load_settings(); s["ban_price"] = price; save_settings(s)
        _send_pe(m.chat.id, f"✅ ʙᴀɴ ᴘʀɪᴄᴇ: ʀs.{sd(price)}")
    except Exception:
        _send_pe(m.chat.id, "❌ ɪɴᴠᴀʟɪᴅ!")

@bot.message_handler(commands=["broadcastuser"])
def cmd_broadcastuser(m):
    if not is_admin(m.from_user.id): return
    p = (m.text or "").split(maxsplit=2)
    if len(p) < 3: _send_pe(m.chat.id, "❌ /broadcastuser ID MSG"); return
    try:
        bot.send_message(int(p[1]), f"📢 {p[2]}")
        _send_pe(m.chat.id, f"✅ sᴇɴᴛ!")
    except Exception:
        _send_pe(m.chat.id, "❌ ғᴀɪʟᴇᴅ!")

@bot.message_handler(commands=["allbroadcast"])
def cmd_allbroadcast(m):
    if not is_admin(m.from_user.id): return
    p = (m.text or "").split(maxsplit=1)
    if len(p) < 2: _send_pe(m.chat.id, "❌ /allbroadcast MSG"); return
    users = load_users()
    sent = failed = 0
    for u_id in users:
        try:
            bot.send_message(int(u_id), f"📢 {p[1]}")
            sent += 1
            time.sleep(0.05)
        except Exception:
            failed += 1
    _send_pe(m.chat.id, f"⭐ ✅ {sd(sent)} | ❌ {sd(failed)}")

# ============================================================
# FLASK WEBHOOK
# ============================================================
@app.route('/', methods=['GET'])
def index():
    return "✅ FF BAN BOT RUNNING"

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    try:
        if request.headers.get('content-type') == 'application/json':
            update = types.Update.de_json(request.get_data().decode('utf-8'))
            bot.process_new_updates([update])
            return '', 200
    except Exception as e:
        print("Webhook error:", e)
    return '', 403

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("✅ BOT STARTED")
    print("✅ OWNER:", OWNER_ID)
    print("✅ USERS:", len(load_users()))
    try:
        bot.remove_webhook()
    except Exception as e:
        print("webhook remove:", e)
    try:
        hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
        if hostname:
            bot.set_webhook(url=f"https://{hostname}/{BOT_TOKEN}")
            print("✅ WEBHOOK SET")
        else:
            print("⚠️ NO HOSTNAME, POLLING")
            bot.infinity_polling()
            raise SystemExit(0)
    except Exception as e:
        print("fallback:", e)
        bot.infinity_polling()
        raise SystemExit(0)
    app.run(host='0.0.0.0', port=PORT)