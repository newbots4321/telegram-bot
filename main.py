from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import time
import datetime

TOKEN = "8320944724:AAHnhVQ5sD7P4HWuz7l4TXxQiNBx_EJNC3o"
ADS_LINK = "https://www.effectivegatecpm.com/bupvhwz5?key=eaedd439f3f1d2db330f017cf0cb29ca"

JOIN_REWARD = 3
PROMOTER_DEDUCT = 3
ADS_REWARD = 10
DAILY_BONUS = 15

users = {}
channels = []
user_task = {}
completed = {}
ads_unlocked = {}
daily_claim = {}
join_time = {}
ad_time = {}
ad_used = {}

def keyboard():
    return ReplyKeyboardMarkup(
        [
            ["💰 Earn Coins","🚀 Promote Channel"],
            ["👛 My Coins","🎁 Daily Bonus"],
            ["📺 Watch Ads"]
        ],
        resize_keyboard=True
    )

def clean_link(link):

    if link.startswith("@"):
        return link

    if "t.me/" in link:
        return "@"+link.split("t.me/")[1].replace("+","")

    return None


async def start(update:Update, context:ContextTypes.DEFAULT_TYPE):

    user = update.effective_user.id

    if user not in users:
        users[user]=0
        completed[user]=[]

    await update.message.reply_text(
        "🔥 Channel Promotion Bot",
        reply_markup=keyboard()
    )


async def message(update:Update, context:ContextTypes.DEFAULT_TYPE):

    user = update.effective_user.id
    text = update.message.text

    if user not in users:
        users[user]=0
        completed[user]=[]

    # -------- EARN COINS --------

    if text=="💰 Earn Coins":

        task=None

        for ch in channels:
            if ch["owner"]!=user and ch["link"] not in completed[user]:
                task=ch
                break

        if not task:
            await update.message.reply_text("No tasks available")
            return

        user_task[user]=task
        join_time[user]=time.time()

        buttons=[
            [InlineKeyboardButton(
                "📢 Join Channel",
                url=f"https://t.me/{task['link'].replace('@','')}"
            )],
            [InlineKeyboardButton("✅ Continue",callback_data="continue_join")]
        ]

        await update.message.reply_text(
            "Join channel then press CONTINUE after few seconds",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    # -------- PROMOTE CHANNEL --------

    elif text=="🚀 Promote Channel":

        if users[user] < 10:
            await update.message.reply_text(
                "❌ Minimum 10 coins required"
            )
            return

        await update.message.reply_text(
            "Send channel username or link"
        )

    elif text.startswith("@") or "t.me/" in text:

        link=clean_link(text)

        if not link:
            await update.message.reply_text("Invalid link")
            return

        channels.append({
            "link":link,
            "owner":user
        })

        await update.message.reply_text("✅ Channel promoted")

    # -------- WATCH ADS --------

    elif text=="📺 Watch Ads":

        if not ads_unlocked.get(user):

            await update.message.reply_text(
                "❌ Watch Ads unlock after joining a channel"
            )
            return

        if ad_used.get(user):
            await update.message.reply_text(
                "⚠️ Ad already completed.\nJoin new channel to unlock ads again."
            )
            return

        ad_time[user]=time.time()

        buttons=[
            [InlineKeyboardButton("▶️ Open Ad",url=ADS_LINK)],
            [InlineKeyboardButton("✅ I Watched Ad",callback_data="ad_done")]
        ]

        await update.message.reply_text(
            "Open ad and watch for 6 seconds",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    # -------- DAILY BONUS --------

    elif text=="🎁 Daily Bonus":

        today=str(datetime.date.today())

        if daily_claim.get(user)==today:
            await update.message.reply_text("Already claimed today")
            return

        daily_claim[user]=today
        users[user]+=DAILY_BONUS

        await update.message.reply_text("🎉 +15 Coins")

    # -------- MY COINS --------

    elif text=="👛 My Coins":

        await update.message.reply_text(
            f"💰 Your Coins: {users[user]}"
        )


async def buttons(update:Update, context:ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    user = query.from_user.id
    data = query.data

    # -------- CONTINUE JOIN --------

    if data=="continue_join":

        if user not in user_task:
            await query.answer("No task")
            return

        if time.time() - join_time.get(user,0) < 5:
            await query.answer("Wait few seconds")
            return

        task=user_task[user]
        channel=task["link"]
        owner=task["owner"]

        if channel not in completed[user]:

            completed[user].append(channel)

            users[user]+=JOIN_REWARD
            users[owner]=max(users.get(owner,0)-PROMOTER_DEDUCT,0)

            ads_unlocked[user]=True
            ad_used[user]=False

            del user_task[user]

            await query.message.reply_text(
                f"✅ Task Completed\n+{JOIN_REWARD} Coins\n📺 Watch Ads Unlocked"
            )

    # -------- AD DONE --------

    elif data=="ad_done":

        if ad_used.get(user):
            await query.answer("Ad already claimed")
            return

        if time.time() - ad_time.get(user,0) < 6:
            await query.answer("Watch ad for 6 seconds")
            return

        users[user]+=ADS_REWARD

        ads_unlocked[user]=False
        ad_used[user]=True

        await query.message.reply_text(
            f"🎉 +{ADS_REWARD} Coins Added\n\nJoin new channel to unlock ads again"
        )

        await query.answer()


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start",start))
app.add_handler(MessageHandler(filters.TEXT,message))
app.add_handler(CallbackQueryHandler(buttons))

app.run_polling()
