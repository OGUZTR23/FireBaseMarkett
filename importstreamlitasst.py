import streamlit as st
import qrcode
from io import BytesIO
import random
import string
import firebase_admin
from firebase_admin import credentials, db

# --- Firebase Ayarları: Streamlit secrets üzerinden al ---
firebase_config = {
    "type": st.secrets["firebase"]["type"],
    "project_id": st.secrets["firebase"]["project_id"],
    "private_key_id": st.secrets["firebase"]["private_key_id"],
    "private_key": st.secrets["firebase"]["private_key"].replace('\\n', '\n'),
    "client_email": st.secrets["firebase"]["client_email"],
    "client_id": st.secrets["firebase"]["client_id"],
    "auth_uri": st.secrets["firebase"]["auth_uri"],
    "token_uri": st.secrets["firebase"]["token_uri"],
    "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
    "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"]
}

# --- Firebase'e Bağlan ---
cred = credentials.Certificate(firebase_config)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://esp32-3c20c-default-rtdb.europe-west1.firebasedatabase.app/'
    })

# --- Yardımcı Fonksiyonlar ---
def generate_id(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_qr_code(data):
    qr = qrcode.make(data)
    buf = BytesIO()
    qr.save(buf, format="PNG")
    buf.seek(0)
    return buf

# --- Streamlit Arayüzü ---
st.title("🛒 Akıllı Market Sepeti - Liste Paylaş")

isim = st.text_input("İsminizi girin:")
urunler = st.text_area("Alışveriş listenizi yazın (her satıra 1 ürün)")

if st.button("Listeyi Kaydet ve QR Oluştur"):
    if isim and urunler:
        user_id = generate_id()
        urun_listesi = urunler.strip().split('\n')

        # Firebase'e veri kaydet
        ref = db.reference(f"sepetler/{user_id}")
        ref.set({
            "kullanici": isim,
            "urunler": urun_listesi
        })

        # QR kod oluştur
        qr_url = f"https://akillimarket.com/sepet/{user_id}"  # Örnek URL
        qr_img = generate_qr_code(qr_url)

        # Sonuçları göster
        st.success(f"✅ Sepet başarıyla kaydedildi!\n📦 Sepet ID: `{user_id}`")
        st.image(qr_img, caption="🧾 Bu QR kodu sepete okut!")
        st.code(qr_url, language="text")
    else:
        st.warning("⚠️ Lütfen isminizi ve ürün listenizi girin.")
