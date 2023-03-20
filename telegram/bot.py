import requests
import time
import config.credentials as cfg_credentials


class BotHandler:
    """
    класс для работы с телеграм ботом (отправка сообщений, файлов)
    это просто базовый набор методов/возможностей работы с ботом, мы же будем пользоваться 
    не всеми, а например отправкой сообщений или файлов
    """
    def __init__(self):
        bot_api_url = cfg_credentials.BOT_API_URL
        self.token = cfg_credentials.BOT_TOKEN
        self.api_url = f"{bot_api_url}{self.token}"
        self.chat_id = cfg_credentials.CHAT_ID
        self.last_update_id = 0

    def get_updates(self, offset=None, timeout=30):
        method = 'getUpdates'
        if self.last_update_id > 0:
            params = {'timeout': timeout, 'offset': self.last_update_id}
            resp = requests.get(self.api_url + method, params)
            result_json = resp.json()['result']
        else:
            params = {'timeout': timeout, 'offset': offset}
            resp = requests.get(self.api_url + method, params)
            result_json = resp.json()['result']
        return result_json

    def send_message(self, text):
        params = {'chat_id': self.chat_id, 'text': text, "parse_mode": "Markdown"}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp

    def send_post(self, channel_id, text):
        params = {'chat_id': channel_id, 'text': text, "parse_mode": "Markdown"}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp

    def send_file(self, channel_id, document, caption):
        files = {'document': open(document, 'rb')}
        resp = requests.post(self.api_url + 'sendDocument?chat_id=' + channel_id + f'&caption={caption}', files=files)
        return resp

    def send_photo(self, channel_id, document, caption):
        files = {'photo': open(document, 'rb')}
        resp = requests.post(self.api_url + 'sendPhoto?chat_id=' + channel_id + f'&caption={caption}', files=files)
        return resp

    def get_last_update(self):
        try:
            get_result = self.get_updates()
            new_updates = []
            last_update = get_result[-1]
            if last_update['update_id'] > self.last_update_id:
                for update in get_result:
                    if update['update_id'] > self.last_update_id:
                        new_updates.append(update)

            self.last_update_id = last_update['update_id']
            return new_updates
        except Exception:
            time.sleep(60)
            get_result = self.get_updates()
            new_updates = []
            last_update = get_result[-1]
            if last_update['update_id'] > self.last_update_id:
                for update in get_result:
                    if update['update_id'] > self.last_update_id:
                        new_updates.append(update)

            self.last_update_id = last_update['update_id']
            return new_updates

    def forward(self, mess):
        try:
            chat_id = mess['message']['chat']['id']
            message_id = mess['message']['message_id']
            method = 'forwardMessage'
            params = {'chat_id': self.chat_id, 'from_chat_id': chat_id, 'message_id': message_id}
            resp = requests.get(self.api_url + method, params)
            return resp
        except KeyError:
            print('KeyError on mess')
            print(mess)
