#!/usr/bin/env python3
"""
🌿 Telegram Bot: «Не знаю, з чого почати» — Tina.easy
Квіз з 7 питань → результат: Енергія / Тіло / Дохід
"""
import asyncio
import html
import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ConversationHandler, ContextTypes
)

# ═══════════════════════════════════════════════════════════
#  НАЛАШТУВАННЯ — всі змінні через Railway Variables
# ═══════════════════════════════════════════════════════════
BOT_TOKEN    = os.getenv("BOT_TOKEN", "")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "")

# Відео-кружечки (file_id завантажуються через /getid)
VIDEO_NOTE_INTRO      = os.getenv("VIDEO_NOTE_INTRO", "")
VIDEO_NOTE_Q2         = os.getenv("VIDEO_NOTE_Q2", "")
VOICE_Q3              = os.getenv("VOICE_Q3", "")
VIDEO_NOTE_PRERESULT  = os.getenv("VIDEO_NOTE_PRERESULT", "")
VIDEO_NOTE_ENERGY     = os.getenv("VIDEO_NOTE_ENERGY", "")
VIDEO_NOTE_BODY       = os.getenv("VIDEO_NOTE_BODY", "")
VIDEO_NOTE_INCOME     = os.getenv("VIDEO_NOTE_INCOME", "")

# Картинка до фінального повідомлення (file_id або URL)
FINAL_IMAGE = os.getenv("FINAL_IMAGE", "")

# Посилання результатів
LINK_ENERGY = "https://t.me/Tinaeasy_bot"
LINK_BODY   = "https://t.me/tina_hudni_easy"
LINK_INCOME = "https://t.me/tina_easy/33"

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.INFO
)
log = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
#  СТАНИ РОЗМОВИ
# ═══════════════════════════════════════════════════════════
(WELCOME, Q1, Q2, Q3, Q4, Q5, Q6, Q7, RESULT) = range(9)

# ═══════════════════════════════════════════════════════════
#  ВАРІАНТИ ВІДПОВІДЕЙ З БАЛАМИ
#  Формат: (текст_кнопки, категорія)
#  Категорії: "E" = Енергія, "B" = Тіло, "I" = Дохід
# ═══════════════════════════════════════════════════════════
Q1_OPTS = [
    ("😔 Я страшенно втомилася",           "E"),
    ("💆 Нарешті зайнятися собою",         "B"),
    ("💰 Знайти спосіб більше заробляти",  "I"),
    ("🌀 Я ніби заплуталася",              "E"),
    ("🕊 Хочу, щоб стало легше",           "E"),
]

Q2_OPTS = [
    ("⏳ Постійно відкладаю",              "E"),
    ("🔄 Починаю, але здаюся",             "E"),
    ("❓ Не знаю, за що братися",          "E"),
    ("😶 Роблю, але нічого не змінюється", "E"),
]

Q3_OPTS = [
    ("😴 Постійна втома",                  "E"),
    ("💼 Робота",                          "I"),
    ("🏠 Домашні справи та сім'я",         "E"),
    ("💸 Гроші",                           "I"),
    ("🪞 Здоров'я або зовнішній вигляд",   "B"),
    ("🌊 Відчуття, що всього забагато",    "E"),
]

Q4_OPTS = [
    ("😩 Постійної втоми",                 "E"),
    ("🪞 Невдоволення своїм тілом",        "B"),
    ("💳 Фінансової напруги",              "I"),
    ("🧭 Відчуття, що стою на місці",      "E"),
    ("🌀 Всього цього одночасно",          "E"),
]

Q5_OPTS = [
    ("🛋 Відпочивала б",                   "E"),
    ("💅 Зайнялася б собою",               "B"),
    ("📈 Пошукала б додатковий дохід",     "I"),
    ("🤷 Навіть не знаю",                  "E"),
]

Q6_OPTS = [
    ("⚡ «У мене знову є сили»",            "E"),
    ("🌸 «Я подобаюся собі в дзеркалі»",   "B"),
    ("💚 «Стало легше з грошима»",          "I"),
    ("🎯 «Нарешті відчуваю контроль»",      "E"),
]

Q7_OPTS = [
    ("⏱ 10–15 хвилин на день",             "E"),
    ("🕐 До 30 хвилин",                     "B"),
    ("🔥 Готова викладатись на максимум",   "I"),
]

ALL_QUESTIONS = [Q1_OPTS, Q2_OPTS, Q3_OPTS, Q4_OPTS, Q5_OPTS, Q6_OPTS, Q7_OPTS]

# ═══════════════════════════════════════════════════════════
#  ТЕКСТИ
# ═══════════════════════════════════════════════════════════
WELCOME_TEXT = (
    "Я поставлю тобі кілька запитань і в кінці скажу, "
    "<b>з чого я б почала на твоєму місці.</b>\n\n"
    "Не як експерт, а як подруга за чашечкою кави ☕"
)

TEXT_BETWEEN_Q2_Q3 = (
    "Дякую ❤️ Тепер хочу краще зрозуміти, <b>як ти зараз живеш.</b>"
)

TEXT_BETWEEN_Q3_Q4 = (
    "Дякую ❤️ Саме тому я дивлюся на відповіді не окремо, а в сукупності."
)

PRERESULT_TEXT = (
    "Дякую ❤️ Я подивилася на всі твої відповіді разом.\n\n"
    "Зараз покажу, з чого б я почала на твоєму місці 👇"
)

FINAL_TEXT = (
    "❤️ І запам'ятай одну річ.\n\n"
    "Тобі не потрібно зараз проходити все одразу.\n\n"
    "Tina.easy побудована не навколо принципу «роби більше».\n\n"
    "Навпаки — ми шукаємо <b>одну сферу, яка зараз найбільше впливає "
    "на твоє життя</b>, і починаємо саме з неї.\n\n"
    "А коли відчуєш, що готова рухатися далі, поруч залишаться й інші маршрути:\n"
    "🔋 Енергія  🩷 Тіло  💰 Дохід\n\n"
    "Не потрібно змінювати все життя за один день.\n"
    "<b>Потрібно правильно обрати свій перший крок.</b> ❤️"
)

RESULTS = {
    "E": {
        "text": (
            "Дякую ❤️\n\n"
            "Я подивилася на твої відповіді в цілому.\n\n"
            "Якби ми зараз сиділи за чашкою кави, я б сказала тобі: "
            "<b>не берися зараз за все одразу. Почни з енергії.</b>\n\n"
            "У твоїх відповідях дуже багато сигналів про те, що саме нестача "
            "ресурсу зараз може заважати тобі рухатися далі.\n\n"
            "І коли ми спочатку повертаємо собі сили, інші зміни стають "
            "набагато реальнішими.\n\n"
            "Тому я б почала саме звідси ❤️\n\n"
            "👇🏼   👇🏼   👇🏼"
        ),
        "button": "🔵 Перейти до маршруту «Енергія» 🔋",
        "link": LINK_ENERGY,
        "video_env": "VIDEO_NOTE_ENERGY",
        "label": "🔋 Енергія",
    },
    "B": {
        "text": (
            "Дякую ❤️\n\n"
            "Я подивилася на твої відповіді, і якби ти зараз запитала мене: "
            "«З чого мені почати?», я б сказала — <b>з тіла.</b>\n\n"
            "І не тому, що зовнішність важливіша за все інше.\n\n"
            "А тому, що саме ця тема зараз найбільше займає твою увагу "
            "і впливає на те, як ти себе почуваєш.\n\n"
            "Давай не будемо намагатися змінити все життя одразу.\n\n"
            "Зробимо перший крок саме тут ❤️\n\n"
            "👇🏼   👇🏼   👇🏼"
        ),
        "button": "🔴 Перейти до маршруту «Тіло» 💃🏻",
        "link": LINK_BODY,
        "video_env": "VIDEO_NOTE_BODY",
        "label": "🩷 Тіло",
    },
    "I": {
        "text": (
            "Дякую ❤️\n\n"
            "Якби ми зараз говорили особисто, я б сказала тобі: "
            "<b>почни з доходу.</b>\n\n"
            "Не тому, що гроші вирішують абсолютно все.\n\n"
            "А тому, що постійна фінансова напруга дуже легко проникає "
            "в усі інші сфери життя — забирає увагу, сили й навіть бажання "
            "щось починати.\n\n"
            "Тому замість того, щоб одночасно виправляти все, "
            "я б спочатку розібралася саме з цим питанням.\n\n"
            "Подивимося, які можливості можуть підійти саме тобі ❤️\n\n"
            "👇🏼   👇🏼   👇🏼"
        ),
        "button": "🟢 Перейти до маршруту «Дохід» 💰",
        "link": LINK_INCOME,
        "video_env": "VIDEO_NOTE_INCOME",
        "label": "💰 Дохід",
    },
}

# ═══════════════════════════════════════════════════════════
#  ДОПОМІЖНІ ФУНКЦІЇ
# ═══════════════════════════════════════════════════════════

def make_kb(opts, prefix) -> InlineKeyboardMarkup:
    """Клавіатура з одним вибором."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text, callback_data=f"{prefix}_{i}")]
        for i, (text, _) in enumerate(opts)
    ])


def e(text) -> str:
    return html.escape(str(text)) if text else "—"


def calc_result(scores: dict) -> str:
    """
    Пріоритет при рівності: Енергія > Тіло > Дохід
    """
    energy = scores.get("E", 0)
    body   = scores.get("B", 0)
    income = scores.get("I", 0)

    if energy >= body and energy >= income:
        return "E"
    if body >= income:
        return "B"
    return "I"


async def send_video_note(bot, chat_id: int, file_id: str, fallback: str):
    if file_id:
        await bot.send_video_note(chat_id, file_id)
    else:
        await bot.send_message(chat_id, f"🎥 <i>{e(fallback)}</i>", parse_mode="HTML")


async def send_voice(bot, chat_id: int, file_id: str, fallback: str):
    if file_id:
        await bot.send_voice(chat_id, file_id)
    else:
        await bot.send_message(chat_id, f"🎤 <i>{e(fallback)}</i>", parse_mode="HTML")


async def notify_admin(bot, user, result_key: str):
    """Надсилає адміну: хто пройшов і який результат."""
    if not ADMIN_CHAT_ID:
        return
    label = RESULTS[result_key]["label"]
    username = f"@{e(user.username)}" if user.username else "без username"
    text = (
        f"📊 <b>Нове проходження квізу</b>\n\n"
        f"👤 <b>Ім'я:</b> {e(user.first_name or '')} {e(user.last_name or '')}\n"
        f"📲 <b>Telegram:</b> {username}\n"
        f"🆔 <b>ID:</b> <code>{user.id}</code>\n\n"
        f"🎯 <b>Результат:</b> {label}"
    )
    try:
        await bot.send_message(ADMIN_CHAT_ID, text, parse_mode="HTML")
    except Exception as err:
        log.error("Помилка надсилання адміну: %s", err)


def get_question_text(num: int, total: int = 7) -> str:
    return f"❓ <b>Питання {num} / {total}</b>\n\n"


# ═══════════════════════════════════════════════════════════
#  ХЕНДЛЕР: отримання file_id (надсилати кружечок/голосове боту)
# ═══════════════════════════════════════════════════════════

async def cmd_getid(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if msg and msg.video_note:
        await msg.reply_text(
            f"📹 <b>VIDEO_NOTE file_id:</b>\n<code>{msg.video_note.file_id}</code>",
            parse_mode="HTML"
        )
    elif msg and msg.voice:
        await msg.reply_text(
            f"🎤 <b>VOICE file_id:</b>\n<code>{msg.voice.file_id}</code>",
            parse_mode="HTML"
        )
    elif msg and msg.photo:
        await msg.reply_text(
            f"🖼 <b>PHOTO file_id:</b>\n<code>{msg.photo[-1].file_id}</code>",
            parse_mode="HTML"
        )


# ═══════════════════════════════════════════════════════════
#  ХЕНДЛЕРИ РОЗМОВИ
# ═══════════════════════════════════════════════════════════

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    ctx.user_data.clear()
    ctx.user_data["scores"] = {"E": 0, "B": 0, "I": 0}
    chat_id = update.effective_chat.id

    # 1. Спочатку відео-кружечок вступний
    await send_video_note(
        ctx.bot, chat_id, VIDEO_NOTE_INTRO,
        "Привіт ❤️ Я Валентина, і дуже рада, що ти тут."
    )

    # 2. Потім текст привітання
    await ctx.bot.send_message(chat_id, WELCOME_TEXT, parse_mode="HTML")

    # 3. Кнопка «Почати» окремим повідомленням
    await ctx.bot.send_message(
        chat_id,
        "Поїхали ❤️",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🌿 Почати", callback_data="start_quiz")
        ]])
    )
    return WELCOME


async def welcome_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(
        get_question_text(1) +
        "Коли ти ввечері залишаєшся наодинці із собою, яка думка виникає найчастіше?",
        parse_mode="HTML",
        reply_markup=make_kb(Q1_OPTS, "q1")
    )
    return Q1


async def q1_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    idx = int(q.data.split("_")[1])
    ctx.user_data["scores"][Q1_OPTS[idx][1]] += 1

    await q.edit_message_text(
        get_question_text(2) +
        "Коли ти думаєш про зміни, що найчастіше відбувається?",
        parse_mode="HTML",
        reply_markup=make_kb(Q2_OPTS, "q2")
    )
    return Q2


async def q2_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    idx = int(q.data.split("_")[1])
    ctx.user_data["scores"][Q2_OPTS[idx][1]] += 1

    chat_id = q.message.chat_id

    # Текст між Q2 і Q3
    await q.edit_message_text(TEXT_BETWEEN_Q2_Q3, parse_mode="HTML")

    # Відео-кружечок
    await send_video_note(
        ctx.bot, chat_id, VIDEO_NOTE_Q2,
        "Знаєш, що я часто помічаю? Людина може роками думати, "
        "що їй просто бракує дисципліни..."
    )

    # Питання 3
    await ctx.bot.send_message(
        chat_id,
        get_question_text(3) + "Що зараз найчастіше забирає твої сили?",
        parse_mode="HTML",
        reply_markup=make_kb(Q3_OPTS, "q3")
    )
    return Q3


async def q3_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    idx = int(q.data.split("_")[1])
    ctx.user_data["scores"][Q3_OPTS[idx][1]] += 1

    chat_id = q.message.chat_id

    # Текст між Q3 і Q4
    await q.edit_message_text(TEXT_BETWEEN_Q3_Q4, parse_mode="HTML")

    # Голосове повідомлення
    await send_voice(
        ctx.bot, chat_id, VOICE_Q3,
        "Дякую ❤️ Є одна річ, яку я хочу, щоб ти зараз помітила..."
    )

    # Питання 4
    await ctx.bot.send_message(
        chat_id,
        get_question_text(4) +
        "Коли ти уявляєш своє життя через кілька місяців, чого найбільше хочеться позбутися?",
        parse_mode="HTML",
        reply_markup=make_kb(Q4_OPTS, "q4")
    )
    return Q4


async def q4_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    idx = int(q.data.split("_")[1])
    ctx.user_data["scores"][Q4_OPTS[idx][1]] += 1

    await q.edit_message_text(
        get_question_text(5) +
        "Якби в тебе з'явилася одна додаткова година щодня, на що ти б її використала?",
        parse_mode="HTML",
        reply_markup=make_kb(Q5_OPTS, "q5")
    )
    return Q5


async def q5_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    idx = int(q.data.split("_")[1])
    ctx.user_data["scores"][Q5_OPTS[idx][1]] += 1

    await q.edit_message_text(
        get_question_text(6) +
        "Через три місяці ти найбільше хотіла б сказати собі…",
        parse_mode="HTML",
        reply_markup=make_kb(Q6_OPTS, "q6")
    )
    return Q6


async def q6_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    idx = int(q.data.split("_")[1])
    ctx.user_data["scores"][Q6_OPTS[idx][1]] += 1

    await q.edit_message_text(
        get_question_text(7) +
        "Скільки часу ти реально готова приділяти змінам?",
        parse_mode="HTML",
        reply_markup=make_kb(Q7_OPTS, "q7")
    )
    return Q7


async def q7_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    idx = int(q.data.split("_")[1])
    ctx.user_data["scores"][Q7_OPTS[idx][1]] += 1

    chat_id = q.message.chat_id
    result_key = calc_result(ctx.user_data["scores"])
    result = RESULTS[result_key]

    # Текст перед результатом
    await q.edit_message_text(PRERESULT_TEXT, parse_mode="HTML")

    # Відео-кружечок перед результатом
    await send_video_note(
        ctx.bot, chat_id, VIDEO_NOTE_PRERESULT,
        "Дякую ❤️ Я подивилася на всі твої відповіді разом..."
    )

    # Пауза + повідомлення-очікування перед відео з результатом
    await asyncio.sleep(2)
    await ctx.bot.send_message(chat_id, "Зараз покажу ❤️ Готова?")
    await asyncio.sleep(12)

    # Відео-результат (Енергія / Тіло / Дохід)
    result_video_id = os.getenv(result["video_env"], "")
    await send_video_note(
        ctx.bot, chat_id, result_video_id,
        result["text"][:80] + "..."
    )

    # Текст результату + кольорова кнопка переходу
    await ctx.bot.send_message(
        chat_id,
        result["text"],
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(result["button"], url=result["link"])
        ]])
    )

    # Затримка перед фінальним повідомленням — щоб кнопка не губилась
    await asyncio.sleep(5)

    # Фінальне повідомлення: спочатку картинка (якщо є), потім текст
    if FINAL_IMAGE:
        await ctx.bot.send_photo(
            chat_id,
            photo=FINAL_IMAGE,
            caption=FINAL_TEXT,
            parse_mode="HTML"
        )
    else:
        await ctx.bot.send_message(
            chat_id,
            FINAL_TEXT,
            parse_mode="HTML"
        )

    # Сповіщення адміну
    await notify_admin(ctx.bot, update.effective_user, result_key)

    return ConversationHandler.END


async def cmd_cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Квіз зупинено. Напиши /start щоб почати знову. ❤️"
    )
    return ConversationHandler.END


# ═══════════════════════════════════════════════════════════
#  ЗАПУСК
# ═══════════════════════════════════════════════════════════

def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN не встановлено! Додай у Railway Variables.")

    from telegram.ext import MessageHandler, filters

    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", cmd_start)],
        states={
            WELCOME: [CallbackQueryHandler(welcome_cb, pattern="^start_quiz$")],
            Q1:      [CallbackQueryHandler(q1_cb,     pattern="^q1_")],
            Q2:      [CallbackQueryHandler(q2_cb,     pattern="^q2_")],
            Q3:      [CallbackQueryHandler(q3_cb,     pattern="^q3_")],
            Q4:      [CallbackQueryHandler(q4_cb,     pattern="^q4_")],
            Q5:      [CallbackQueryHandler(q5_cb,     pattern="^q5_")],
            Q6:      [CallbackQueryHandler(q6_cb,     pattern="^q6_")],
            Q7:      [CallbackQueryHandler(q7_cb,     pattern="^q7_")],
        },
        fallbacks=[CommandHandler("cancel", cmd_cancel)],
        allow_reentry=True,
    )

    # ⚠️ ConversationHandler реєструється ПЕРШИМ — має пріоритет
    app.add_handler(conv)

    # MessageHandler для /getid — тільки поза активною розмовою
    app.add_handler(MessageHandler(
        filters.VIDEO_NOTE | filters.VOICE | filters.PHOTO, cmd_getid
    ))

    log.info("🤖 Бот «Не знаю, з чого почати» запущено!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
