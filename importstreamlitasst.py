import streamlit as st
import qrcode
from io import BytesIO
import random
import string
import firebase_admin
from firebase_admin import credentials, db

# --- Firebase Setup ---
cred = credentials.Certificate("secrets.toml")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://esp32-3c20c-default-rtdb.europe-west1.firebasedatabase.app/'  # kendi proje URL'inle değiştir
    })

# --- Yardımcı Fonksiyonlar ---
def generate_id(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_qr_code(data):
    qr = qrcode.make(data)
    buf = BytesIO()
    qr.save(buf, format="PNG")
    return buf

# --- Streamlit UI ---
st.title("🛒 Akıllı Market Sepeti - Liste Paylaş")

isim = st.text_input("İsminizi girin:")
urunler = st.text_area("Alışveriş listenizi yazın (her satıra 1 ürün)")

if st.button("Listeyi Kaydet ve QR Oluştur"):
    if isim and urunler:
        user_id = generate_id()
        urun_listesi = urunler.strip().split('\n')

        # Firebase'e kaydet
        ref = db.reference(f"sepetler/{user_id}")
        ref.set({
            "kullanici": isim,
            "urunler": urun_listesi
        })

        # QR kod oluştur
        qr_url = f"https://akillimarket.com/sepet/{user_id}"  # ya da sadece ID
        qr_img = generate_qr_code(qr_url)

        st.success(f"Sepet başarıyla kaydedildi! Sepet ID: {user_id}")
        st.image(qr_img, caption="Bu QR kodu sepete okut!")
        st.code(qr_url, language="text")

    else:
        st.warning("Lütfen isminizi ve ürünlerinizi girin.")