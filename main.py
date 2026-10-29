import re # Matnlarni qolipga tekshirish uchun modul
import dns.resolver
import os # Port va muhit o'zgaruvchilarini o'qish uchun yangi modul qo'shildi
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
    andoza = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(andoza, email):
        return False
    
    try:
        domen = email.split('@')[1]
        dns.resolver.resolve(domen, 'MX')
        return True
    except Exception:
        return False

# --- MARSHRUTLAR ---

@app.route('/')
def home():
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
        
        yaroqli = False
        turi = ""
        
        if "@" in aloqa:
            turi = "Elektron pochta"
            if pochta_to_grimi(aloqa):
                yaroqli = True
        else:
            turi = "Telefon raqam"
            tozalangan_nomer = re.sub(r"[\s\-()]", "", aloqa)
            if telefon_to_grimi(tozalangan_nomer):
                yaroqli = True
                aloqa = tozalangan_nomer
        
        if not yaroqli:
            xato_matni = f"Kiritilgan {turi} haqiqiy yoki to'g'ri formatda emas! Iltimos, qayta tekshiring."
            return render_template_string(CONTACT_HTML, error=True, xato_sababi=xato_matni)
        
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
    tanlangan_mahsulot = next((m for m in MAHSULOTLAR if m["id"] == m_id), None)
    if tanlangan_mahsulot:
        return render_template_string(MAHSULOT_DETAL_HTML, mahsulot=tanlangan_mahsulot)
    return "<h1>Mahsulot topilmadi!</h1>", 404

# TUZATILDI: Render serverida tashqi tarmoqqa ochiladigan va portni dinamik oladigan qism qo'shildi
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5002))
    app.run(debug=False, host='0.0.0.0', port=port)
