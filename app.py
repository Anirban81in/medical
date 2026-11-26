from flask import Flask, request, redirect, session
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = "jai-medical-secret"

LANG = {
    "en": {"title": "Jai Medical", "home": "Home", "medicines": "Medicines", "az": "Medicines A-Z", "health": "Healthcare", "cart": "My Cart", "payment": "Payment / Checkout", "admin": "Admin Panel", "orders": "My Orders", "flash": "Flash Cards", "add": "Add to Cart +", "search": "Search medicine...", "total": "Total", "checkout_btn": "Proceed to Payment", "coupon": "Coupon Code", "apply": "Apply", "pay_now": "Pay Now", "all": "All Medicines", "antibiotic": "Antibiotics", "fever": "Fever & Pain", "vitamin": "Vitamins", "diabetes": "Diabetes Care", "welcome": "Welcome to Jai Medical - Genuine Medicines, Fast Delivery"},
    "bn": {"title": "জয় মেডিকেল", "home": "হোম", "medicines": "ঔষধ", "az": "ঔষধ A-Z", "health": "হেলথকেয়ার", "cart": "আমার কার্ট", "payment": "পেমেন্ট / চেকআউট", "admin": "অ্যাডমিন প্যানেল", "orders": "আমার অর্ডার", "flash": "ফ্ল্যাশ কার্ড", "add": "কার্টে যোগ করুন +", "search": "ঔষধ খুঁজুন...", "total": "মোট", "checkout_btn": "পেমেন্টে যান", "coupon": "কুপন কোড", "apply": "লাগান", "pay_now": "এখন পে করুন", "all": "সব ঔষধ", "antibiotic": "অ্যান্টিবায়োটিক", "fever": "জ্বর ও ব্যথা", "vitamin": "ভিটামিন", "diabetes": "ডায়াবেটিস কেয়ার", "welcome": "জয় মেডিকেলে স্বাগতম - আসল ঔষধ, দ্রুত ডেলিভারি"}
}

MEDICINES = [
    {"id": 1, "name": "Amoxicillin 500mg", "bn_name": "অ্যামোক্সিসিলিন ৫০০", "letter": "A", "price": 85, "category": "Antibiotic", "stock": 50, "use": "Infection / Jor, Sordi, Gala Betha", "dose": "1 tablet - Dine 2 bar, 5 din"},
    {"id": 2, "name": "Azithromycin 250mg", "bn_name": "অ্যাজিথ্রোমাইসিন ২৫০", "letter": "A", "price": 120, "category": "Antibiotic", "stock": 30, "use": "Throat Infection / Cough", "dose": "1 tablet - Dine 1 bar, 3 din"},
    {"id": 3, "name": "Betadine Solution", "bn_name": "বেটাডিন", "letter": "B", "price": 95, "category": "First Aid", "stock": 40, "use": "Kata / Gha - Jibanu Nasok", "dose": "Dine 2 bar lagao"},
    {"id": 4, "name": "Cetirizine 10mg", "bn_name": "সেটিরিজিন ১০", "letter": "C", "price": 25, "category": "Allergy", "stock": 100, "use": "Sordi / Hanchi / Allergy", "dose": "1 tablet - Rate 1 bar"},
    {"id": 5, "name": "Crocin 650mg", "bn_name": "ক্রোসিন ৬৫০", "letter": "C", "price": 30, "category": "Fever", "stock": 100, "use": "Jor / Matha Betha", "dose": "1 tablet - Jor thakle, 6 ghonta por por"},
    {"id": 6, "name": "Dolo 650", "bn_name": "ডোলো ৬৫০", "letter": "D", "price": 28, "category": "Fever", "stock": 100, "use": "Jor / Gaye Betha", "dose": "1 tablet - Jor thakle"},
    {"id": 7, "name": "Glycomet 500mg", "bn_name": "গ্লাইকোমেট ৫০০", "letter": "G", "price": 65, "category": "Diabetes", "stock": 50, "use": "Sugar / Diabetes", "dose": "Doctor er poramorsho moto"},
    {"id": 8, "name": "Zincovit Syrup", "bn_name": "জিঙ্কোভিট সিরাপ", "letter": "Z", "price": 110, "category": "Vitamin", "stock": 45, "use": "Durbolota / Vitamin er ovab", "dose": "1 chamoch - Dine 1 bar"},
]
COUPONS = {"JAI10": 10, "FIRST20": 20, "SAVE50": 50}
ORDERS = []
LETTERS = [chr(i) for i in range(65, 91)]
ADMIN_PASSWORD = "admin123"
UPI_ID = "jaimedical@okhdfc"
# Tomar Advertisement Video link ekhane bosao - ekhon sample video deoa ache
AD_VIDEO_URL = "https://www.w3schools.com/html/mov_bbb.mp4"

def get_lang(): return session.get("lang", "en")
def get_cart():
    cart = session.get("cart", {})
    if isinstance(cart, list): cart = {}
    items = []
    for mid_str, qty in cart.items():
        med = next((m for m in MEDICINES if m["id"] == int(mid_str)), None)
        if med: items.append({**med, "qty": qty, "subtotal": med["price"]*qty})
    return items, sum(i["subtotal"] for i in items), sum(i["qty"] for i in items)
def calc_bill(total):
    pct = COUPONS.get(session.get("coupon",""), 0)
    discount = total * pct // 100
    delivery = 40 if total > 0 else 0
    return discount, delivery, total - discount + delivery, pct

STYLE = """
<link href="https://fonts.googleapis.com/css2?family=UnifrakturMaguntia&family=Cinzel:ital@1&family=Playfair+Display:ital,wght@1,600;1,800&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Playfair Display','Cinzel',serif;font-style:italic;background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 25%, #a18cd1 50%, #fbc2eb 75%, #ffecd2 100%);background-attachment:fixed;min-height:100vh;}
h1,h2,h3{font-family:'UnifrakturMaguntia','Cinzel',serif;font-style:italic;letter-spacing:1px;color:#2d0a4e;}
/* MEDICINE NAME - BOLD ITALICS */
.med-name{font-weight:900 !important;font-style:italic !important;font-size:22px !important;color:#2d0a4e;font-family:'Playfair Display',serif;text-shadow:1px 1px 0 #ffccff;}
.med-name-bn{font-weight:900 !important;font-style:italic !important;font-size:23px !important;color:#800080;}
.topbar{position:fixed;top:0;left:0;right:0;height:90px;background:linear-gradient(90deg,#6a11cb,#2575fc,#ff6a00,#ee0979);box-shadow:0 4px 20px rgba(0,0,0,0.3);z-index:1000;display:flex;align-items:center;justify-content:center;text-align:center;}
.topbar-center{display:flex;flex-direction:column;align-items:center;justify-content:center;}
.topbar h2{color:white;font-size:32px;text-shadow:2px 2px 5px #000;margin:0;}
.topbar small{color:#ffe600;font-weight:bold;font-size:13px;}
.topbar-right{position:absolute;right:20px;top:50%;transform:translateY(-50%);}
.topbar-left{position:absolute;left:20px;top:50%;transform:translateY(-50%);}
.sidebar{width:280px;background:linear-gradient(180deg,#2d0a4e,#7b2ff7,#ff6a00);color:white;height:calc(100vh - 90px);position:fixed;top:90px;left:0;padding:20px;overflow-y:auto;box-shadow:4px 0 20px rgba(0,0,0,0.3);}
.sidebar a{color:white;text-decoration:none;display:block;padding:11px;border-radius:10px;font-style:italic;font-weight:bold;} .sidebar a:hover{background:rgba(255,255,255,0.25);transform:scale(1.02);}
.submenu{display:none;margin-left:15px;background:rgba(0,0,0,0.25);border-radius:10px;} .menu-item:hover .submenu{display:block;}
.az-grid{display:flex;flex-wrap:wrap;gap:5px;padding:10px;} .az-grid a{background:white;color:#6a11cb;width:32px;height:32px;text-align:center;padding:6px 0;font-weight:bold;}
.main{margin-left:280px;padding:25px;width:calc(100% - 280px);min-height:calc(100vh - 90px);}
.card{background:rgba(255,255,255,0.95);padding:18px;border-radius:18px;box-shadow:0 8px 25px rgba(106,17,203,0.25);margin-bottom:15px;display:flex;justify-content:space-between;align-items:center;border-left:6px solid #ff6a00;}
.btn{background:linear-gradient(90deg,#6a11cb,#ff6a00);color:white;padding:10px 18px;border:none;border-radius:25px;cursor:pointer;text-decoration:none;display:inline-block;font-style:italic;font-weight:bold;box-shadow:0 4px 10px rgba(0,0,0,0.2);}
.btn-red{background:linear-gradient(90deg,#ee0979,#ff6a00);} .btn-blue{background:linear-gradient(90deg,#2575fc,#6a11cb);} .btn-orange{background:linear-gradient(90deg,#ff9a00,#ff6a00);}
input,select{padding:12px;width:100%;margin:8px 0;border:2px solid #a18cd1;border-radius:12px;font-style:italic;font-family:'Playfair Display',serif;}
.qty-btn{background:#ffe600;width:32px;height:32px;border-radius:50%;font-size:18px;font-weight:bold;text-decoration:none;color:#2d0a4e;text-align:center;display:inline-block;line-height:32px;}
.lang-btn{background:#800080 !important;color:white !important;padding:10px 18px;border-radius:25px;text-decoration:none;font-weight:bold;margin:3px;display:inline-block;border:2px solid #ffccff;box-shadow:0 4px 10px rgba(128,0,128,0.5);font-style:italic;}
.lang-btn:hover{background:#ff00ff !important;}
.lang-box{background:#800080;padding:12px;border-radius:15px;text-align:center;border:2px solid #ffccff;}
.lang-box p{color:white;font-size:13px;margin-bottom:6px;}
.stat{background:white;padding:20px;border-radius:18px;flex:1;text-align:center;box-shadow:0 8px 20px rgba(0,0,0,0.15);border-top:5px solid #800080;}
table{width:100%;background:white;border-collapse:collapse;border-radius:12px;overflow:hidden;} th{background:#800080;color:white;padding:12px;text-align:left;} td{padding:12px;border-bottom:1px solid #eee;text-align:left;}
.content-wrap{margin-top:90px;display:flex;width:100%;}
/* AD VIDEO */
.ad-box{background:#000;border-radius:18px;overflow:hidden;box-shadow:0 10px 30px rgba(0,0,0,0.4);margin-bottom:18px;position:relative;border:3px solid #ffe600;}
.ad-box video{width:100%;height:220px;object-fit:cover;display:block;}
.ad-label{position:absolute;top:10px;left:10px;background:#ff0000;color:white;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:bold;z-index:2;}
.ad-caption{background:linear-gradient(90deg,#800080,#ff6a00);color:white;text-align:center;padding:8px;font-size:15px;font-weight:bold;}
.flash-container{display:flex;flex-wrap:wrap;gap:20px;justify-content:center;}
.flash-card{width:260px;height:320px;perspective:1000px;cursor:pointer;}
.flash-inner{position:relative;width:100%;height:100%;transition:transform 0.7s;transform-style:preserve-3d;}
.flash-card:hover .flash-inner{transform:rotateY(180deg);}
.flash-front,.flash-back{position:absolute;width:100%;height:100%;backface-visibility:hidden;border-radius:20px;padding:20px;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;box-shadow:0 10px 30px rgba(0,0,0,0.3);}
.flash-front{background:linear-gradient(135deg,#6a11cb,#2575fc);color:white;}
.flash-back{background:linear-gradient(135deg,#ff6a00,#ee0979);color:white;transform:rotateY(180deg);}
.flash-front h2{color:white;font-size:26px;} .flash-back h3{color:#ffe600;}
</style>
"""

def topbar():
    return """<div class='topbar'>
  <div class='topbar-left'><span style='font-size:35px;'>💊</span></div>
  <div class='topbar-center'>
    <img src='https://cdn-icons-png.flaticon.com/512/2966/2966482.png' style='width:38px;height:38px;border-radius:50%;border:2px solid white;'>
    <h2>JAI MEDICAL</h2>
    <small>✨ Genuine Medicines • Fast Delivery • Howrah ✨</small>
  </div>
  <div class='topbar-right'><a href='/cart' style='background:#ffe600;color:#2d0a4e;padding:8px 15px;border-radius:20px;text-decoration:none;font-weight:bold;'>🛒 Cart</a></div>
</div>"""

def sidebar(t):
    return f"""<div class="sidebar">
  <div class='lang-box'><p>🌐 Language / ভাষা</p><a class="lang-btn" href="/lang/en">English</a> <a class="lang-btn" href="/lang/bn">বাংলা</a></div><br>
  <h2 style='color:white;'>💊 {t['title']}</h2><br>
  <a href="/">🏠 {t['home']}</a>
  <a href="/flashcards">🃏 {t['flash']} - Flash Cards</a>
  <div class="menu-item"><a href="#">💊 {t['medicines']} ▼</a><div class="submenu"><a href="/?cat=All">{t['all']}</a><a href="/?cat=Antibiotic">{t['antibiotic']}</a><a href="/?cat=Fever">{t['fever']}</a><a href="/?cat=Vitamin">{t['vitamin']}</a><a href="/?cat=Diabetes">{t['diabetes']}</a></div></div>
  <div class="menu-item"><a href="#">🔤 {t['az']} ▼</a><div class="submenu"><div class="az-grid">{''.join([f'<a href="/?letter={l}">{l}</a>' for l in LETTERS])}</div></div></div>
  <div class="menu-item"><a href="#">🩺 {t['health']} ▼</a><div class="submenu"><a href="/?cat=First Aid">First Aid</a><a href="/?cat=Allergy">Allergy</a></div></div>
  <a href="/cart">🛒 {t['cart']}</a><a href="/checkout">💳 {t['payment']}</a><a href="/orders">📦 {t['orders']}</a><a href="/admin?force_login=1">🔐 {t['admin']}</a></div>"""

@app.route("/")
def home():
    lang=get_lang(); t=LANG[lang]
    letter=request.args.get("letter"); cat=request.args.get("cat"); q=request.args.get("q","").lower()
    items=MEDICINES
    if letter: items=[m for m in items if m["letter"]==letter]
    if cat and cat!="All": items=[m for m in items if m["category"]==cat]
    if q: items=[m for m in items if q in m["name"].lower() or q in m["bn_name"]]
    cart=session.get("cart",{})
    if isinstance(cart,list): cart={}
    _,total,count=get_cart()
    # CHANGED: Flash Cards Dekho button removed, AD VIDEO added above search
    html=STYLE+topbar()+"<div class='content-wrap'>"+sidebar(t)+f"<div class='main'><h1>{t['welcome']}</h1><br>"
    # --- ADVERTISEMENT VIDEO ABOVE SEARCH ---
    html+=f"""
    <div class='ad-box'>
      <span class='ad-label'>📢 ADVERTISEMENT</span>
      <video autoplay muted loop playsinline controls>
        <source src='{AD_VIDEO_URL}' type='video/mp4'>
        Your browser does not support video.
      </video>
      <div class='ad-caption'>🎉 JAI MEDICAL - JAI10 Coupon e 10% OFF | Free Delivery ₹500+ Order e 🎉</div>
    </div>
    """
    html+=f"<form><input name='q' placeholder='{t['search']}' value='{request.args.get('q','')}'></form><br><div style='text-align:right;'><a class='btn btn-red' href='/cart'>🛒 {t['cart']} ({count}) - ₹{total}</a></div><br>"
    for m in items:
        name=m["bn_name"] if lang=="bn" else m["name"]
        name_class="med-name-bn" if lang=="bn" else "med-name"
        qty=cart.get(str(m["id"]),0)
        btn=f"<div><a class='qty-btn' href='/decrease/{m['id']}'>-</a> <b>{qty}</b> <a class='qty-btn' href='/add/{m['id']}'>+</a></div>" if qty else f"<a class='btn' href='/add/{m['id']}'>{t['add']}</a>"
        html+=f"<div class='card'><div><b class='{name_class}'>{name}</b><br><small>{m['category']} | Stock: {m['stock']} | {m['use']}</small><br><b>₹{m['price']}</b></div>{btn}</div>"
    return html+"</div></div>"

@app.route("/flashcards")
def flashcards():
    lang=get_lang(); t=LANG[lang]
    html=STYLE+topbar()+"<div class='content-wrap'>"+sidebar(t)+f"<div class='main'><h1>🃏 {t['flash']} - Medicine Flash Cards</h1><p>Card er upor mouse nile / touch korle ultabe - Dose ar Use dekhte parbe!</p><br><div class='flash-container'>"
    for m in MEDICINES:
        name=m["bn_name"] if lang=="bn" else m["name"]
        name_class="med-name-bn" if lang=="bn" else "med-name"
        html+=f"""
        <div class='flash-card'><div class='flash-inner'>
          <div class='flash-front'><div style='font-size:50px;'>💊</div><h2 class='{name_class}' style='color:white;text-shadow:2px 2px 5px #000;'>{name}</h2><p>{m['category']}</p><h2 style='color:#ffe600;'>₹{m['price']}</h2><p style='margin-top:10px;'>👆 Hover kore ultao</p><a class='btn' href='/add/{m['id']}' style='background:white;color:#6a11cb;margin-top:10px;'>Add to Cart +</a></div>
          <div class='flash-back'><h3>💡 Kiser Oshudh?</h3><p>{m['use']}</p><br><h3>💊 Dose</h3><p>{m['dose']}</p><br><p>Stock: {m['stock']}</p><p>Price: ₹{m['price']}</p></div>
        </div></div>
        """
    html+="</div></div></div>"
    return html

@app.route("/lang/<l>")
def set_lang(l):
    session["lang"]="bn" if l=="bn" else "en"
    return redirect("/")

@app.route("/add/<int:mid>")
def add(mid):
    cart=session.get("cart",{})
    if isinstance(cart,list): cart={}
    cart[str(mid)]=cart.get(str(mid),0)+1; session["cart"]=cart
    return redirect(request.referrer or "/")

@app.route("/decrease/<int:mid>")
def decrease(mid):
    cart=session.get("cart",{})
    if isinstance(cart,list): cart={}
    if str(mid) in cart:
        cart[str(mid)]-=1
        if cart[str(mid)]<=0: del cart[str(mid)]
    session["cart"]=cart
    return redirect(request.referrer or "/")

@app.route("/remove/<int:mid>")
def remove(mid):
    cart=session.get("cart",{})
    if isinstance(cart,dict): cart.pop(str(mid),None)
    session["cart"]=cart
    return redirect("/cart")

@app.route("/cart", methods=["GET","POST"])
def cart_page():
    lang=get_lang(); t=LANG[lang]
    if request.method=="POST":
        code=request.form.get("coupon","").strip().upper()
        if code in COUPONS: session["coupon"]=code; session["coupon_msg"]="Coupon Applied! ✅"
        else: session["coupon"]=""; session["coupon_msg"]="Invalid Coupon ❌"
        return redirect("/cart")
    items,total,count=get_cart()
    discount,delivery,payable,pct=calc_bill(total)
    html=STYLE+topbar()+"<div class='content-wrap'>"+sidebar(t)+f"<div class='main'><h1>🛒 {t['cart']}</h1><br>"
    for it in items:
        name=it["bn_name"] if lang=="bn" else it["name"]
        name_class="med-name-bn" if lang=="bn" else "med-name"
        html+=f"<div class='card'><div><b class='{name_class}'>{name}</b><br>₹{it['price']} x {it['qty']} = <b>₹{it['subtotal']}</b></div><div><a class='qty-btn' href='/decrease/{it['id']}'>-</a> <b>{it['qty']}</b> <a class='qty-btn' href='/add/{it['id']}'>+</a> <a class='btn btn-red' href='/remove/{it['id']}'>X</a></div></div>"
    if items:
        html+=f"""<div class='card'><div style='width:100%;'><form method='POST' style='display:flex;gap:10px;'><input name='coupon' placeholder='{t['coupon']} - Try JAI10 / FIRST20' value='{session.get('coupon','')}'><button class='btn btn-orange'>{t['apply']}</button></form><p style='color:green;'>{session.get('coupon_msg','')}</p><p>Subtotal: ₹{total} | Discount ({pct}%): -₹{discount} | Delivery: ₹{delivery}</p><h2>{t['total']}: ₹{payable}</h2></div></div><a class='btn' style='padding:12px 25px;' href='/checkout'>{t['checkout_btn']} →</a>"""
    else: html+="<p>Cart empty</p>"
    return html+"</div></div>"

@app.route("/checkout", methods=["GET","POST"])
def checkout():
    lang=get_lang(); t=LANG[lang]
    items,total,count=get_cart()
    if not items: return redirect("/")
    discount,delivery,payable,pct=calc_bill(total)
    if request.method=="POST":
        method=request.form.get("payment")
        for it in items:
            for m in MEDICINES:
                if m["id"]==it["id"]: m["stock"]=max(0,m["stock"]-it["qty"])
        order={"id":"JAI"+str(uuid.uuid4())[:6].upper(),"txn":request.form.get("txn_id") or request.form.get("upi_txn") or "TXN"+str(uuid.uuid4())[:8].upper(),"date":datetime.now().strftime("%d-%m-%Y %H:%M"),"name":request.form.get("name"),"phone":request.form.get("phone"),"address":request.form.get("address"),"method":method,"items":items,"total":total,"discount":discount,"delivery":delivery,"payable":payable,"coupon":session.get("coupon",""),"status":"Paid" if method!="Cash on Delivery" else "COD - Pending"}
        ORDERS.append(order); session["cart"]={}; session["coupon"]=""; session["coupon_msg"]=""; session["last_order"]=order
        return redirect("/success")
    qr_url=f"https://api.qrserver.com/v1/create-qr-code/?size=220x220&data=upi://pay?pa={UPI_ID}&pn=Jai%20Medical&am={payable}&cu=INR"
    html=STYLE+topbar()+"<div class='content-wrap'>"+sidebar(t)+f"""<div class='main'><div style='background:white;padding:25px;border-radius:20px;max-width:520px;'><h1>💳 {t['payment']}</h1><br><p>Subtotal ₹{total} - Discount ₹{discount} + Delivery ₹{delivery} = <b>Payable ₹{payable}</b></p><br><form method='POST'><input name='name' placeholder='Full Name / পুরো নাম' required><input name='phone' placeholder='Phone Number' required><input name='address' placeholder='Delivery Address' required><label>Payment Method:</label><select name='payment' id='pm' onchange="showPay()"><option value='Cash on Delivery'>Cash on Delivery - ক্যাশ</option><option value='UPI'>UPI - GPay / PhonePe / Paytm</option><option value='Card'>Credit / Debit Card - Scan Barcode</option></select>
    <div id='upiBox' style='display:none;text-align:center;background:#f9f9f9;padding:15px;border-radius:10px;'><h3>📷 UPI QR Scan Koro</h3><img src='{qr_url}' width='200'><br><p><b>UPI ID: {UPI_ID}</b></p><p>Amount: ₹{payable}</p><input name='upi_txn' placeholder='UPI Transaction ID likho'></div>
    <div id='cardBox' style='display:none;text-align:center;background:#e8f8f5;padding:15px;border-radius:10px;'><h3>💳 Card Payment - Barcode Scan Koro</h3><p>Phone diye ei Barcode ta scan kore pay koro</p><img src='{qr_url}' width='220' style='border:5px solid white;box-shadow:0 2px 8px #ccc;'><br><br><p><b>JAI MEDICAL</b><br>UPI ID: {UPI_ID}<br>Amount: <b>₹{payable}</b></p><input name='txn_id' placeholder='Payment er por Transaction ID likho'><input name='card_no' placeholder='Card Number (optional)'><input name='cvv' placeholder='CVV (optional)'></div>
    <button class='btn' style='width:100%;padding:13px;font-size:16px;margin-top:10px;'>{t['pay_now']} ₹{payable}</button></form></div></div></div><script>function showPay(){{var v=document.getElementById('pm').value;document.getElementById('upiBox').style.display=v=='UPI'?'block':'none';document.getElementById('cardBox').style.display=v=='Card'?'block':'none';}}</script>"""
    return html

@app.route("/success")
def success():
    o=session.get("last_order")
    if not o: return redirect("/")
    return STYLE+topbar()+f"<div class='content-wrap'><div class='main' style='text-align:center;padding-top:60px;'><h1>✅ Payment Successful!</h1><br><p>Order ID: <b>{o['id']}</b></p><p>Txn: {o['txn']}</p><p>Paid: <b>₹{o['payable']}</b> via {o['method']}</p><p>{o['name']} - {o['address']}</p><p style='color:green;'>Stock updated! ✅</p><br><a class='btn' href='/'>Home</a> <a class='btn btn-blue' href='/orders'>My Orders</a></div></div>"

@app.route("/orders")
def orders_page():
    lang=get_lang(); t=LANG[lang]
    html=STYLE+topbar()+"<div class='content-wrap'>"+sidebar(t)+"<div class='main'><h1>📦 My Orders</h1><br>"
    for o in ORDERS: html+=f"<div class='card'><div><b class='med-name'>{o['id']}</b><br>{o['method']} | {o['name']} | {o['date']}</div><b>₹{o['payable']} - {o['status']}</b></div>"
    if not ORDERS: html+="<p>No orders yet</p>"
    return html+"</div></div>"

@app.route("/admin", methods=["GET","POST"])
def admin():
    if request.args.get("force_login")=="1": session.pop("is_admin",None)
    if request.method=="POST" and "password" in request.form:
        if request.form.get("password")==ADMIN_PASSWORD:
            session["is_admin"]=True
            return redirect("/admin")
        return STYLE+topbar()+"<div class='content-wrap'><div class='main'><h2 style='color:red;'>❌ Wrong Password!</h2><br><a class='btn' href='/admin?force_login=1'>Try Again</a></div></div>"
    if not session.get("is_admin"):
        return STYLE+topbar()+"""<div class='content-wrap'><div class='main' style='display:flex;justify-content:center;'><div style='background:white;padding:30px;border-radius:20px;max-width:400px;width:100%;text-align:center;'><img src='https://cdn-icons-png.flaticon.com/512/2966/2966482.png' width='80'><br><br><h1>🔐 Jai Medical Admin</h1><p>Protibar Password Lagbe</p><br><form method='POST'><input name='password' type='password' placeholder='Enter Admin Password' required><button class='btn' style='width:100%;padding:12px;'>Login</button></form><br><a href='/'>← Back to Website</a></div></div></div>"""
    if request.method=="POST" and "update_price" in request.form:
        mid=int(request.form.get("mid")); new_price=int(request.form.get("new_price"))
        for m in MEDICINES:
            if m["id"]==mid: m["price"]=new_price
        return redirect("/admin")
    if request.method=="POST" and "add_med" in request.form:
        new_id=max(m["id"] for m in MEDICINES)+1
        MEDICINES.append({"id":new_id,"name":request.form.get("name"),"bn_name":request.form.get("name"),"letter":request.form.get("name")[0].upper(),"price":int(request.form.get("price")),"category":request.form.get("category"),"stock":int(request.form.get("stock") or 50),"use":request.form.get("category"),"dose":"Doctor er poramorsho moto"})
        return redirect("/admin")
    total_sales=sum(o["payable"] for o in ORDERS); total_orders=len(ORDERS)
    cod=sum(1 for o in ORDERS if o["method"]=="Cash on Delivery"); upi=sum(1 for o in ORDERS if o["method"]=="UPI"); card=sum(1 for o in ORDERS if o["method"]=="Card")
    today_sales=sum(o["payable"] for o in ORDERS if o["date"].startswith(datetime.now().strftime("%d-%m-%Y")))
    html=STYLE+topbar()+f"""<div class='content-wrap'><div class='sidebar'><h2 style='color:white;'>💊 Jai Medical Admin</h2><a href='/'>🏠 View Website</a><a href='/admin?force_login=1'>🔐 Logout / Re-Login</a></div><div class='main'><h1>📊 Sales Dashboard</h1><br><div style='display:flex;gap:15px;flex-wrap:wrap;'><div class='stat'><h3>₹{total_sales}</h3><p>Total Sales</p></div><div class='stat'><h3>{total_orders}</h3><p>Total Orders</p></div><div class='stat'><h3>₹{today_sales}</h3><p>Today Sales</p></div><div class='stat'><h3>COD:{cod} | UPI:{upi} | Card:{card}</h3><p>Payment Split</p></div></div><br><h2>✏️ Update Price / Stock</h2><table><tr><th>Medicine</th><th>Current Price</th><th>New Price</th><th>Action</th></tr>"""
    for m in MEDICINES:
        html+=f"<tr><td><b class='med-name'>{m['name']}</b></td><td>₹{m['price']}</td><td><form method='POST' style='display:flex;gap:5px;'><input type='hidden' name='mid' value='{m['id']}'><input name='new_price' type='number' value='{m['price']}' style='width:100px;'><button class='btn' name='update_price'>Update</button></form></td><td>Stock: {m['stock']}</td></tr>"
    html+="</table><br><h2>➕ Add New Medicine</h2><form method='POST' style='background:white;padding:20px;border-radius:15px;'><input name='name' placeholder='Medicine Name' required><input name='price' type='number' placeholder='Price ₹' required><input name='category' placeholder='Category e.g. Fever'><input name='stock' type='number' placeholder='Stock'><button class='btn' name='add_med'>Add Medicine</button></form><br><h2>📦 All Orders / Sales</h2><table><tr><th>Order ID</th><th>Date</th><th>Customer</th><th>Payment</th><th>Amount</th><th>Status</th></tr>"
    for o in reversed(ORDERS):
        html+=f"<tr><td>{o['id']}</td><td>{o['date']}</td><td>{o['name']}<br>{o['phone']}</td><td>{o['method']}<br>Coupon: {o['coupon']}</td><td>₹{o['payable']}</td><td>{o['status']}</td></tr>"
    return html+"</table></div></div>"

if __name__=="__main__":
    app.run(debug=True)