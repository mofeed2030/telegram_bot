from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler
import requests

TELEGRAM_BOT_API_KEY = "7742652921:AAFBoxQwK_vZbxSump5cfaCOxeGhC6NfpvI"
CHANNEL_USERNAME = "@moatader"
NUMVERIFY_API_KEY = "103afb6945e64c77975bf141826aad43"

async def start(update: Update, context: CallbackContext) -> None:
    welcome_message = (
        "أهلاً وسهلاً بكم في بوت معرفة موقع رقم الجوال!\n"
        "للبدء، يرجى اتباع الخطوات التالية:\n"
        "1. اضغط على زر 'ابدأ'\n"
        "2. اشترك في القناة\n"
        "3. أدخل الرقم مع الرمز الدولي\n"
        "/location 967771232556\n\n"
        "أولاً اضغط على زر 'ابدأ'"
    )
    await update.message.reply_text(welcome_message)
    print("Start command received")
    keyboard = [[InlineKeyboardButton("ابدأ", callback_data='start')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('مرحبًا! اضغط على الزر لبدء الاستخدام.', reply_markup=reply_markup)

async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user = query.from_user
    await query.answer()

    print(f"User ID: {user.id}")  # طباعة معرف المستخدم

    if not is_user_subscribed(user.id):
        print(f"User {user.id} is not subscribed.")  # طباعة رسالة لغير المشتركين
        keyboard = [[InlineKeyboardButton("اشترك في القناة", url="https://t.me/moatader")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="يرجى الاشتراك في القناة قبل البدء.", reply_markup=reply_markup)
    else:
        print(f"User {user.id} is subscribed.")  # طباعة رسالة للمشتركين
        await query.edit_message_text(text="لقد بدأت الآن باستخدام البوت! الرجاء إرسال رقم الجوال المراد البحث عن معلومات عنه مع الرمز الدولي.")

def is_user_subscribed(user_id: int) -> bool:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_API_KEY}/getChatMember?chat_id={CHANNEL_USERNAME}&user_id={user_id}"
    response = requests.get(url)
    data = response.json()
    print(data)  # طباعة استجابة الخدمة
    if 'result' in data:
        return data['result']['status'] in ['member', 'administrator', 'creator']
    return False

async def location(update: Update, context: CallbackContext) -> None:
    print("Location command received")
    phone_number = " ".join(context.args)
    if not phone_number:
        await update.message.reply_text('الرجاء إرسال رقم جوال للبحث عنه.')
        return
    
    data = get_phone_info(phone_number)
    print(data)
    
    if data and data['valid']:
        response_message = (
            f"الدولة: {data['country_name']}\n"
            f"الشركة: {data['carrier']}\n"
            f"الخط: {data['line_type']}"
        )
        if data['location']:
            response_message += f"\nالموقع: {data['location']}"
        
        await update.message.reply_text(response_message)
    else:
        await update.message.reply_text('لم يتم العثور على معلومات عن الرقم.')

def get_phone_info(phone_number: str) -> dict:
    base_url = "http://apilayer.net/api/validate"
    params = {
        'access_key': NUMVERIFY_API_KEY,
        'number': phone_number,
        'country_code': '',  # اتركه فارغًا لأن الخدمة ستتعرف تلقائيًا
        'format': 1
    }
    response = requests.get(base_url, params=params)
    print(response.text)
    try:
        return response.json()
    except ValueError:
        return {}

def main() -> None:
    application = Application.builder().token(TELEGRAM_BOT_API_KEY).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button, pattern='^start$'))
    application.add_handler(CommandHandler("location", location))

    application.run_polling()

if __name__ == '__main__':
    main()