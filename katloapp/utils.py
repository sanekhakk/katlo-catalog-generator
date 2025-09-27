import qrcode
import io
from urllib.parse import quote_plus

def build_whatsapp_link(number: str, message: str):
    clean = number.replace('+','').replace(' ','')
    return f"https://wa.me/{clean}?text={quote_plus(message)}"

def generate_qr_image_bytes(target_url: str):
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(target_url)
    qr.make(fit=True)
    img = qr.make_image()
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf