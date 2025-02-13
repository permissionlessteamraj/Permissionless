import logging
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# Define a dictionary to keep track of active chat pairs
active_chats = {}

def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\! Use /chat to start a random chat\.',
        reply_markup=ForceReply(selective=True),
    )

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Use /chat to start a random chat and /stop to end it.')

def chat(update: Update, context: CallbackContext) -> None:
    """Start a random chat with another user."""
    user_id = update.message.from_user.id
    if user_id in active_chats:
        update.message.reply_text('You are already in a chat. Use /stop to end it.')
        return
    
    for uid, partner_id in active_chats.items():
        if partner_id is None:
            active_chats[uid] = user_id
            active_chats[user_id] = uid
            context.bot.send_message(chat_id=uid, text="You are now chatting with a random user. Say hi!")
            update.message.reply_text("You are now chatting with a random user. Say hi!")
            return
    
    active_chats[user_id] = None
    update.message.reply_text("Waiting for a random user to join the chat...")

def stop(update: Update, context: CallbackContext) -> None:
    """End the current chat."""
    user_id = update.message.from_user.id
    if user_id in active_chats:
        partner_id = active_chats[user_id]
        if partner_id:
            context.bot.send_message(chat_id=partner_id, text="The user has ended the chat.")
            active_chats[partner_id] = None
        active_chats.pop(user_id)
        update.message.reply_text("You have ended the chat.")
    else:
        update.message.reply_text("You are not in a chat.")

def handle_message(update: Update, context: CallbackContext) -> None:
    """Handle messages sent by users."""
    user_id = update.message.from_user.id
    if user_id in active_chats:
        partner_id = active_chats[user_id]
        if partner_id:
            context.bot.send_message(chat_id=partner_id, text=update.message.text)
        else:
            update.message.reply_text("Waiting for a random user to join the chat...")
    else:
        update.message.reply_text("Use /chat to start a random chat.")

def main() -> None:
    """Start the bot."""
    # Replace 'YOUR_TOKEN' with your bot's token
    updater = Updater("8107028742:AAEKrzOlYVqGiUijKmol1anXsOD6Nc8iaJg")

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("chat", chat))
    dispatcher.add_handler(CommandHandler("stop", stop))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
