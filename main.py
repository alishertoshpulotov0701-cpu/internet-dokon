import re # Matnlarni qolipga tekshirish uchun modul
import dns.resolver
from flask import Flask, render_template_string, request
from flask_mail import Mail, Message
from templates import INDEX_HTML, ABOUT_HTML, CONTACT_HTML, MAHSULOT_DETAL_HTML

app = Flask(__name__)

# --- POCHTA SOZLAMALARI ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'alishertoshpulotov0701@gmail.com'
app.config['MAIL_PASSWORD'] = 'epgjocpbofwfxeic' 
app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']
# Sizning pochtangiz

mail = Mail(app)

MAHSULOTLAR = [
    {
        "id": 1,
        "nomi": "Alisher Navoiy asarlari",
        "narxi": "35 000 so'm",
        "tavsifi": "Ajoyib kitob to'plami",
        "rasm": "/static/kitob.jpg"
    },
    {
        "id": 2,
        "nomi": "kompyuter sichqonchasi",
        "narxi": "50 000 so'm",
        "tavsifi": "Simsiz qulay sichqoncha",
        "rasm": "/static/sichqoncha.jpg"
    }
]
def telefon_to_grimi(nomer):
    """ O'zbekiston raqamlarini tekshirish: +998901234567 yoki 998901234567 formatida """
    andoza = r"^(\+?998)?\d{9}$"
    return bool(re.match(andoza, nomer))

def pochta_to_grimi(email):
    """ Pochta formati va uning domeni (masalan gmail.com) mavjudligini tekshirish """
    # 1. Sintaksisni tekshirish (kombinatsiya to'g'riligi)
    andoza = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(andoza, email):
        return False
    
    # 2. Domenning haqiqiyligini DNS orqali tekshirish (soxta pochtalarni tutish uchun)
    try:
        domen = email.split('@')[1]
        dns.resolver.resolve(domen, 'MX') # Domen elektron xat qabul qila oladimi?
        return True
    except Exception:
        return False

# --- MARSHRUTLAR ---

@app.route('/')
def home():
    # Bosh sahifaga mahsulotlar ro'yxatini uzatamiz
    return render_template_string(INDEX_HTML, mahsulotlar=MAHSULOTLAR)

@app.route('/about')
def about():
    return render_template_string(ABOUT_HTML)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        ism = request.form.get('ism')
        aloqa = request.form.get('aloqa').strip()
        xabar_matni = request.form.get('xabar')
        
        # Kiritilgan ma'lumot pochta yoki telefon ekanini aniqlaymiz
        yaroqli = False
        turi = ""
        
        if "@" in aloqa:
            turi = "Elektron pochta"
            if pochta_to_grimi(aloqa):
                yaroqli = True
        else:
            turi = "Telefon raqam"
            # Bo'shliqlar va chiziqchalarni tozalab tekshiramiz
            tozalangan_nomer = re.sub(r"[\s\-()]", "", aloqa)
            if telefon_to_grimi(tozalangan_nomer):
                yaroqli = True
                aloqa = tozalangan_nomer # Tozalangan formatni pochtaga jo'natamiz
        
        # Agar tekshiruvdan o'tmasa, foydalanuvchiga xato xabarini ko'rsatamiz
        if not yaroqli:
            xato_matni = f"Kiritilgan {turi} haqiqiy yoki to'g'ri formatda emas! Iltimos, qayta tekshiring."
            return render_template_string(CONTACT_HTML, error=True, xato_sababi=xato_matni)
        
        # Ma'lumotlar to'g'ri bo'lsa, pochtaga yuboramiz
        msg = Message(
            subject=f"Yangi Xabar: {ism} dan",
            recipients=[app.config['MAIL_USERNAME']],
            body=f"Mijoz ismi: {ism}\nBog'lanish turi: {turi}\nMa'lumoti: {aloqa}\nXabar:\n{xabar_matni}"
        )
        
        try:
            mail.send(msg)
            return render_template_string(CONTACT_HTML, success=True)
        except Exception as e:
            return render_template_string(CONTACT_HTML, error=True, xato_sababi="Server xatoligi. Keyinroq urunib ko'ring.")
            
    return render_template_string(CONTACT_HTML)

@app.route('/mahsulot/<int:m_id>')
def mahsulot_sahifasi(m_id):
    # ID bo'yicha kerakli mahsulotni ro'yxatdan qidirib topamiz
    tanlangan_mahsulot = next((m for m in MAHSULOTLAR if m["id"] == m_id), None)
    
    if tanlangan_mahsulot:
        # Topilsa, mahsulot detal shablonini ko'rsatamiz
        return render_template_string(MAHSULOT_DETAL_HTML, mahsulot=tanlangan_mahsulot)
        
    return "<h1>Mahsulot topilmadi!</h1>", 404

if __name__ == '__main__':
    # Server portini 5001 qilib ishga tushiramiz
    app.run(debug=True, port=5002)