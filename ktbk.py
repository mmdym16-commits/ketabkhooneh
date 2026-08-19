import pandas as pd
import random
from collections import Counter
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = 8919993932:AAHZZQ1oLnKlQBQ_f5rlNkUkKKxhFXY5I5c
bot = telebot.TeleBot(TOKEN)

user_data = {}

# بارگذاری دیتابیس
try:
    df = pd.read_excel("database.xlsx")
    df = df.dropna(how='all')
    print(f"✅ {len(df)} مطلب بارگذاری شد!")
except:
    df = pd.DataFrame(columns=['id', 'title', 'content', 'file_type', 'file_id', 'tags', 'category'])

def get_main_menu():
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton("🔍 جستجو", callback_data="search"),
        InlineKeyboardButton("🏷 تگ‌ها", callback_data="tag_search"),
        InlineKeyboardButton("📂 دسته‌بندی", callback_data="categories"),
        InlineKeyboardButton("🎲 تصادفی", callback_data="random")
    ]
    keyboard.add(*buttons)
    return keyboard

def send_media(chat_id, row):
    """ارسال فایل با توضیحات"""
    file_id = row['file_id']
    file_type = row['file_type']
    
    caption = f"📖 *{row['title']}*\n\n"
    if pd.notna(row['content']):
        caption += f"{row['content']}\n\n"
    caption += f"🏷 تگ‌ها: {row['tags']}\n"
    caption += f"📂 دسته: {row['category']}"
    
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("❤️ ذخیره", callback_data=f"save_{row['id']}"))
    
    # ارسال بر اساس نوع فایل
    if file_type == "photo":
        bot.send_photo(chat_id, file_id, caption=caption, parse_mode='Markdown', reply_markup=keyboard)
    elif file_type == "video":
        bot.send_video(chat_id, file_id, caption=caption, parse_mode='Markdown', reply_markup=keyboard)
    elif file_type == "document":
        bot.send_document(chat_id, file_id, caption=caption, parse_mode='Markdown', reply_markup=keyboard)
    elif file_type == "audio":
        bot.send_audio(chat_id, file_id, caption=caption, parse_mode='Markdown', reply_markup=keyboard)
    elif file_type == "animation":
        bot.send_animation(chat_id, file_id, caption=caption, parse_mode='Markdown', reply_markup=keyboard)

def show_results_page(chat_id, results, page=0):
    if results.empty:
        bot.send_message(chat_id, "❌ نتیجه‌ای پیدا نشد!")
        return
    
    total_pages = (len(results) - 1) // 3 + 1
    if page >= total_pages:
        page = total_pages - 1
    if page < 0:
        page = 0
    
    start = page * 3
    end = min(start + 3, len(results))
    current_page = results.iloc[start:end]
    
    user_data[chat_id] = {'results': results, 'page': page}
    
    for _, row in current_page.iterrows():
        send_media(chat_id, row)
    
    if total_pages > 1:
        nav_keyboard = InlineKeyboardMarkup()
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("⬅️ قبلی", callback_data=f"page_{page-1}"))
        nav_buttons.append(InlineKeyboardButton(f"📄 {page+1}/{total_pages}", callback_data="none"))
        if page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton("➡️ بعدی", callback_data=f"page_{page+1}"))
        nav_keyboard.add(*nav_buttons)
        bot.send_message(chat_id, "📌 صفحات:", reply_markup=nav_keyboard)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        f"🧪 *به ربات علمی خوش اومدی!*\n📚 {len(df)} مطلب با مدیا داریم.",
        parse_mode='Markdown',
        reply_markup=get_main_menu()
    )

@bot.message_handler(func=lambda msg: True)
def handle_search(message):
    keyword = message.text.strip()
    if len(keyword) < 2:
        bot.reply_to(message, "❌ حداقل ۲ کاراکتر وارد کن!")
        return
    
    results = df[
        df['title'].str.contains(keyword, case=False, na=False) |
        df['content'].str.contains(keyword, case=False, na=False) |
        df['tags'].str.contains(keyword, case=False, na=False)
    ]
    
    if results.empty:
        bot.reply_to(message, "❌ مطلبی پیدا نشد!")
        return
    
    bot.reply_to(message, f"✅ {len(results)} نتیجه:")
    show_results_page(message.chat.id, results)

S.Hossein, [19-Aug-26 3:28]
# ========== مدیریت دکمه‌ها ==========
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id = call.message.chat.id
    data = call.data
    bot.answer_callback_query(call.id)
    
    if data == "search":
        bot.edit_message_text("🔍 کلمه مورد نظر رو بفرست:", chat_id, call.message.message_id)
    
    elif data == "tag_search":
        all_tags = []
        for tags in df['tags'].dropna():
            all_tags.extend([t.strip() for t in str(tags).split(',')])
        top_tags = Counter(all_tags).most_common(15)
        
        keyboard = InlineKeyboardMarkup(row_width=2)
        for tag, count in top_tags:
            keyboard.add(InlineKeyboardButton(f"#{tag} ({count})", callback_data=f"tag_{tag}"))
        keyboard.add(InlineKeyboardButton("🔙 برگشت", callback_data="back"))
        bot.edit_message_text("🏷️ تگ‌ها:", chat_id, call.message.message_id, reply_markup=keyboard)
    
    elif data == "categories":
        categories = df['category'].dropna().unique()
        keyboard = InlineKeyboardMarkup(row_width=2)
        for cat in categories:
            count = len(df[df['category'] == cat])
            keyboard.add(InlineKeyboardButton(f"📁 {cat} ({count})", callback_data=f"cat_{cat}"))
        keyboard.add(InlineKeyboardButton("🔙 برگشت", callback_data="back"))
        bot.edit_message_text("📂 دسته‌بندی:", chat_id, call.message.message_id, reply_markup=keyboard)
    
    elif data == "random":
        if df.empty:
            bot.edit_message_text("❌ مطلبی نیست!", chat_id, call.message.message_id)
            return
        row = df.sample(1).iloc[0]
        bot.delete_message(chat_id, call.message.message_id)
        send_media(chat_id, row)
    
    elif data == "back":
        bot.edit_message_text("🧪 منوی اصلی:", chat_id, call.message.message_id, reply_markup=get_main_menu())
    
    elif data.startswith("tag_"):
        tag = data.replace("tag_", "")
        results = df[df['tags'].str.contains(tag, case=False, na=False)]
        if results.empty:
            bot.edit_message_text(f"❌ #{tag} پیدا نشد!", chat_id, call.message.message_id)
            return
        bot.edit_message_text(f"🏷️ #{tag}: {len(results)} مطلب", chat_id, call.message.message_id)
        show_results_page(chat_id, results)
    
    elif data.startswith("cat_"):
        category = data.replace("cat_", "")
        results = df[df['category'] == category]
        bot.edit_message_text(f"📂 {category}: {len(results)} مطلب", chat_id, call.message.message_id)
        show_results_page(chat_id, results)
    
    elif data.startswith("page_"):
        page = int(data.replace("page_", ""))
        if chat_id in user_data:
            results = user_data[chat_id]['results']
            show_results_page(chat_id, results, page)
    
    elif data.startswith("save_"):
        bot.answer_callback_query(call.id, "❤️ ذخیره شد!", show_alert=False)

# ========== دریافت file_id ==========
@bot.message_handler(content_types=['photo', 'video', 'document', 'audio', 'animation'])
def get_file_id(message):
    if message.photo:
        file_id = message.photo[-1].file_id
        f_type = "photo"
    elif message.video:
        file_id = message.video.file_id
        f_type = "video"
    elif message.document:
        file_id = message.document.file_id
        f_type = "document"
    elif message.audio:
        file_id = message.audio.file_id
        f_type = "audio"
    elif message.animation:
        file_id = message.animation.file_id
        f_type = "animation"
    
    bot.reply_to(
        message,
        f"✅ file_id دریافت شد!\nنوع: {f_type}\n\n{file_id}\n\n📝 این رو توی دیتابیس بذار.",
        parse_mode='Markdown'
    )

if name == "__main__":
    print("🤖 ربات مدیا روشن شد!")
    bot.infinity_polling() 
    @bot.message_handler(content_types=['photo', 'video', 'document', 'audio', 'animation'])
def get_file_id(message):
    if message.photo:
        file_id = message.photo[-1].file_id
        file_type = "عکس"
    elif message.video:
        file_id = message.video.file_id
        file_type = "ویدیو"
    elif message.document:
        file_id = message.document.file_id
        file_type = "فایل"
    elif message.audio:
        file_id = message.audio.file_id
        file_type = "صوت"
    elif message.animation:
        file_id = message.animation.file_id
        file_type = "گیف"
    else:
        return
    
    bot.reply_to(
        message,
        f"✅ {file_type} دریافت شد!\n\n"
        f"{file_id}\n\n"
        f"📝 این کد رو توی ستون file_id بذار.",
        parse_mode='Markdown'
    )