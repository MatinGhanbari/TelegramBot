from TelegramBot import TelegramBot

bot = TelegramBot('6108965851:AAE4LTk5K-HzTRCPQUhXIqizgUIB-U6apGA')

@bot.route('/start')
def start(update):
    message = update['message']
    from_id = message['from']['id']

    bot.send_message(from_id, "started!")


@bot.route('/great')
def great(update):
    message = update['message']
    from_id = message['from']['id']
    first_name = message['from']['first_name']
    last_name = message['from']['last_name']

    bot.send_message(from_id, f"Hello {first_name} {last_name}!")

bot.poll()
