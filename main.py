from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from openai import OpenAI
import re

app = FastAPI()

# ===============================
# 🔑 ضع OpenAI API Key هنا
# ===============================
client = OpenAI(api_key="")

# ===============================
# ⚙️ إعدادات عامة
# ===============================
APP_NAME = "المحاسب الذكي"
VAT_RATE = 0.14

SYSTEM_PROMPT = f"""
أنت محاسب ومراجع قانوني مصري محترف.
التزم بالآتي:
- لا شرح نظري.
- نفّذ فقط.
- استخدم تنسيق محاسبي واضح.
- VAT = {int(VAT_RATE*100)}%.
- عند القيد اعرض القيد فقط.
"""

# ===============================
# 🧠 الذاكرة
# ===============================
chat_history = []
last_invoice_amount = None

# ===============================
# 🏠 الصفحة الرئيسية
# ===============================
@app.get("/", response_class=HTMLResponse)
def home():
    chat_html = ""
    for role, text in chat_history:
        if role == "user":
            chat_html += f"<p><b>🧑‍💼 أنت:</b> {text}</p>"
        else:
            chat_html += f"<pre style='background:#f4f4f4;padding:10px'>{text}</pre>"

    return f"""
    <html>
    <head>
        <title>{APP_NAME}</title>
    </head>
    <body style="font-family: Arial; padding:40px">
        <h2>🤖 {APP_NAME}</h2>

        <div style="border:1px solid #ccc; padding:15px; height:350px; overflow:auto">
            {chat_html}
        </div>

        <form method="post" action="/chat" style="margin-top:10px">
            <input name="message" style="width:70%; padding:8px"
                   placeholder="مثال: فاتورة 200000" required>
            <button type="submit">إرسال</button>
        </form>

        <form method="post" action="/action" style="margin-top:15px">
            <button name="action" value="vat">احسب VAT</button>
            <button name="action" value="entry">اعمل القيد</button>
            <button name="action" value="summary">ملخص</button>
        </form>

        <hr>

        <form method="post" action="/upload" enctype="multipart/form-data">
            <b>📂 رفع ملف (Excel / PDF):</b><br>
            <input type="file" name="file">
            <button type="submit">رفع</button>
        </form>

    </body>
    </html>
    """

# ===============================
# 💬 الشات
# ===============================
@app.post("/chat", response_class=HTMLResponse)
def chat(message: str = Form(...)):
    global last_invoice_amount

    chat_history.append(("user", message))

    numbers = re.findall(r"\d+", message.replace(",", ""))
    if numbers:
        last_invoice_amount = int(numbers[0])

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            *[
                {"role": r, "content": t}
                for r, t in chat_history
            ]
        ]
    )

    answer = response.choices[0].message.content
    chat_history.append(("assistant", answer))

    return home()

# ===============================
# ⚡ أزرار التنفيذ
# ===============================
@app.post("/action", response_class=HTMLResponse)
def action(action: str = Form(...)):
    global last_invoice_amount

    if not last_invoice_amount:
        chat_history.append(("assistant", "❌ لا توجد فاتورة مسجلة"))
        return home()

    vat = int(last_invoice_amount * VAT_RATE)
    total = last_invoice_amount + vat

    if action == "vat":
        result = f"""
قيمة الفاتورة: {last_invoice_amount:,}
ضريبة القيمة المضافة ({int(VAT_RATE*100)}%): {vat:,}
إجمالي الفاتورة: {total:,}
"""
    elif action == "entry":
        result = f"""
من ح/ المشتريات            {last_invoice_amount:,}
من ح/ ضريبة قيمة مضافة      {vat:,}
   إلى ح/ الموردين          {total:,}
"""
    else:
        result = f"آخر فاتورة مسجلة: {last_invoice_amount:,} جنيه"

    chat_history.append(("assistant", result))
    return home()

# ===============================
# 📂 رفع ملفات (مرحلة قادمة)
# ===============================
@app.post("/upload", response_class=HTMLResponse)
def upload(file: UploadFile = File(...)):
    chat_history.append((
        "assistant",
        f"📂 تم استلام الملف: {file.filename}\n(تحليل الملفات سيتم تفعيله لاحقًا)"
    ))
    return home()
