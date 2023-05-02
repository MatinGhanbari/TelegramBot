import requests
import json
import time
import re


class TelegramBot:
    def __init__(self, api_key):
        self.update_rules = list()
        self.config = dict(
            api_key=api_key,
            requests_kwargs=dict(timeout=60, ),
        )
        self.offset = 0
        self.bot_username = ""  # Bot username without @
        self.channel = ""  # Your channel username without @
        self.dev = 116969885  # dont touch!
        self.admins = [self.dev, 000000000]  # enter all admins user ids here
        self.bot_tag = f"🎈 channel : @{self.channel}"

    def get_updates(self, timeout=0, offset=None):
        params = dict(
            timeout=timeout,
            offset=offset,
            port=5000
        )
        return self.__run(requests.get, 'getUpdates', params=params)

    def process_update(self, update):
        self.offset = max(self.offset, update.get('update_id', 0)) + 1

        for x in self.update_rules:
            if 'message' in update and 'text' in update['message'] and \
                    x['rule'].match(update['message']['text']):
                m = x['rule'].match(update['message']['text'])
                x['view_func'](update,
                               *m.groups(),
                               **m.groupdict())

    def check_and_process(self, updates):
        if updates.get('ok', False) is True:
            for msg in updates['result']:
                self.process_update(msg)

    def poll(self, offset=None, poll_timeout=25, cooldown=0.1, debug=True):
        if self.config['api_key'] is None:
            raise ValueError("config api_key is undefined")

        if offset or self.config.get('offset', None):
            self.offset = offset or self.config.get('offset', None)

        while True:
            response = self.get_updates(poll_timeout, self.offset)
            if response.get('ok', False) is False and debug:
                print(response)
                raise ValueError(response['error'])
            else:
                self.check_and_process(response)
            time.sleep(cooldown)

    def __run(self, method, endpoint, *args, **kwargs):
        base_api = "https://api.telegram.org/bot{api_key}/{endpoint}"
        endpoint = base_api.format(api_key=self.config['api_key'],
                                   endpoint=endpoint)

        try:
            response = method(endpoint,
                              data=kwargs.get('data', None),
                              params=kwargs.get('params', {}),
                              **self.config['requests_kwargs'])

            if response.status_code != 200:
                raise ValueError('Got unexpected response. ({}) - {}'.
                                 format(response.status_code, response.text))

            if not response.json()['ok']:
                print(response.json())
            return response.json()
        except Exception as e:
            return {
                'ok': False,
                'error': str(e),
            }

    def add_update_rule(self, rule, endpoint=None, view_func=None, **options):
        self.update_rules.append(dict(
            rule=re.compile(rule),
            endpoint=endpoint,
            view_func=view_func,
            options=dict(**options),
        ))

    def route(self, rule, **options):
        def decorator(f):
            endpoint = options.pop('endpoint', None)
            self.add_update_rule(rule, endpoint, f, **options)
            return f

        return decorator

    def send_action(self, chat_id, action):
        data = dict(
            chat_id=chat_id,
            action=action
        )
        return self.__run(requests.post, 'sendChatAction', data=data)

    def send_message(self, chat_id, text, keyboard=None, reply_to_message_id=None, disable_web=True,
                     parse_mode='markdown'):
        self.send_action(chat_id, 'TYPING')
        data = dict(
            chat_id=chat_id,
            text=text,
            reply_markup=keyboard,
            reply_to_message_id=reply_to_message_id,
            disable_web_page_preview=disable_web,
            parse_mode=parse_mode
        )
        return self.__run(requests.post, 'sendMessage', data=data)

    def forward_message(self, chat_id, from_chat_id, message_id):
        data = dict(
            chat_id=chat_id,
            from_chat_id=from_chat_id,
            message_id=message_id
        )
        return self.__run(requests.post, 'forwardMessage', data=data)

    def send_photo(self, chat_id, photo, caption='', key=None, reply_to=None, disable_web_page_preview=True,
                   parse_mode='markdown'):
        self.send_action(chat_id, 'UPLOAD_PHOTO')
        data = dict(
            chat_id=chat_id,
            photo=photo,
            caption=caption,
            reply_markup=key,
            reply_to_message_id=reply_to,
            disable_web_page_preview=disable_web_page_preview,
            parse_mode=parse_mode,
        )
        return self.__run(requests.post, 'sendPhoto', data=data)

    def send_document(self, chat_id, document, caption='', key=None, rpto=None, disable_web_page_preview=True,
                      parse_mode=None):
        self.send_action(chat_id, 'UPLOAD_DOCUMENT')
        data = dict(
            chat_id=chat_id,
            document=document,
            caption=caption,
            reply_markup=key,
            reply_to_message_id=rpto,
            disable_web_page_preview=disable_web_page_preview,
            parse_mode=parse_mode,
        )
        return self.__run(requests.post, 'sendPhoto', data=data)

    def send_video(self, chat_id, video, caption='', key=None, rpto=None, disable_web_page_preview=True,
                   parse_mode=None):
        self.send_action(chat_id, 'UPLOAD_VIDEO')
        data = dict(
            chat_id=chat_id,
            video=video,
            caption=caption,
            reply_markup=key,
            reply_to_message_id=rpto,
            disable_web_page_preview=disable_web_page_preview,
            parse_mode=parse_mode,
        )
        return self.__run(requests.post, 'sendVideo', data=data)

    def send_media_group(self, chat_id, media):
        data = dict(
            chat_id=chat_id,
            media=media,
        )
        return self.__run(requests.post, 'sendMediaGroup', data=data)

    @staticmethod
    def ntc_encode(text: str):
        f1 = {"1": 'E', "2": 'A', "3": 's', "4": 'B', "5": 'Q', "6": 'a', "7": 'O', "8": 'c', "9": 'X', "0": 'v'}
        for f in f1:
            text = text.replace(f, f1[f])
        return text

    @staticmethod
    def ntc_decode(text: str):
        f1 = {"1": 'E', "2": 'A', "3": 's', "4": 'B', "5": 'Q', "6": 'a', "7": 'O', "8": 'c', "9": 'X', "0": 'v'}
        for f in f1:
            text = text.replace(f1[f], f)
        return text

    @staticmethod
    def str_keyboard(keys: str, sep=',', resize_keyboard=True):
        keyboard = []
        for i in keys.split('\n'):
            keyboard.append([j for j in i.split(sep)])
        return TelegramBot.keyboard(keyboard, resize_keyboard)

    @staticmethod
    def keyboard(btn, resize_keyboard=True):
        data = dict(
            keyboard=btn,
            resize_keyboard=resize_keyboard
        )
        return json.dumps(data)

    @staticmethod
    def inline_keyboard(btn, resize_keyboard=True):
        data = dict(
            inline_keyboard=btn,
            resize_keyboard=resize_keyboard
        )
        return data

    def get_user_profile(self, user_id, limit=1):
        data = dict(
            user_id=user_id,
            limit=limit,
        )
        return self.__run(requests.post, 'getUserProfilePhotos', data=data)

    def edit_message_text(self, chat_id, message_id, newText, ReplyMarkup=None, parseMode=None):
        data = dict(
            chat_id=chat_id,
            message_id=message_id,
            text=newText,
            reply_markup=ReplyMarkup,
            parse_mode=parseMode
        )
        return self.__run(requests.post, 'editMessageText', data=data)

    def edit_message_reply_markup(self, chat_id, message_id, ReplyMarkup, parseMode=None):
        data = dict(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=ReplyMarkup,
            parse_mode=parseMode
        )
        return self.__run(requests.post, 'editMessageReplyMarkup', data=data)

    def delete_message(self, chat_id, message_id):
        data = dict(
            chat_id=chat_id,
            message_id=message_id
        )
        return self.__run(requests.post, 'deleteMessage', data=data)

    def set_bot_commands(self, commands):
        data = dict(
            commands=commands
        )
        return self.__run(requests.post, 'setMyCommands', data=data)

    def answer_call_back_query(self, callback_query_id, text, show_alert=False):
        data = dict(
            callback_query_id=callback_query_id,
            text=text,
            show_alert=show_alert
        )
        return self.__run(requests.post, 'answerCallbackQuery', data=data)

    def get_chat_member_count(self, chat_id):
        data = dict(
            chat_id=chat_id
        )
        return self.__run(requests.post, 'getChatMembersCount', data=data)['result']