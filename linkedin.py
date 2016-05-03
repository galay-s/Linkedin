# -*- coding: utf-8 -*-
import requests
import json
from bs4 import BeautifulSoup
import smtplib
import settings
import time


class LinkedIn(object):

    def __init__(self, login, password):
        """Инициализация"""

        self._login = login
        self._password = password
        self._client = requests.Session()

        # Login
        page = self.__login()
        self._csrfToken_ajax = self.__get_csrfToken_ajax(page)

    def __login(self):
        """Логинимся"""

        page = self._client.get(settings.HOMEPAGE_URL).content
        soup = BeautifulSoup(page, "html.parser")
        csrf = soup.find(id="loginCsrfParam-login")['value']
        login_information = {
            'isJsEnabled': 'false',
            'source_app': '',
            'tryCount': '',
            'clickedSuggestion': 'false',
            'session_key': self._login,
            'session_password': self._password,
            'loginCsrfParam': csrf
        }
        page_in = self._client.post(settings.LOGIN_URL, data=login_information)

        return page_in.content

    def get_page(self, url):
        """Возвращает страницу url"""

        page = self._client.get(url).content

        return page

    def get_page_soup(self, url):
        """Возвращает страницу в виде soup"""

        page = self.get_page(url)
        soup = BeautifulSoup(page, "html.parser")

        return soup

    def __get_all_conversations(self):
        """Возвращает информацию(json) по всем перепискам"""

        soup = self.get_page_soup(settings.MESSAGE_URL)
        info_tag = soup.find(id="inbox-main-content").contents[0]
        info_json = json.loads(info_tag)
        all_conversations = info_json['conversations']['conversationsBefore']

        return all_conversations

    def __get_conversations_id(self):
        """Возвращает список номеров переписок. Один номер это
        сообщения от одного пользователя.
        """

        conversations_id = []
        all_conversations = self.__get_all_conversations()
        for convBef in all_conversations:
            conversations_id.append(convBef['threadId'])

        return conversations_id

    def __get_conversation(self, conversation_id):
        """Получает полные данные(json) одной переписки в которой
        может быть несколько сообщений
        """

        url = "".join([settings.THREAD, conversation_id])
        soup = self.get_page_soup(url)
        info_tag = soup.find(id="inbox-main-content").contents[0]
        info_json = json.loads(info_tag)
        conversation = info_json['selectedThreadInfo']

        return conversation

    def is_read(self, message):
        """Проверяет прочитано ли сообщение. Возвращает True если прочитано"""

        return message['read']

    def get_conversation_messages(self, conversation_id):
        """Возвращает сообщения(json) одной переписки"""

        conversation = self.__get_conversation(conversation_id)

        return conversation['messages']

    def __get_message(self, msg):
        """Возвращает одно сообщение"""

        message = " ".join([
            '_FROM_:',
            msg['sender']['firstName'].encode('utf-8'),
            msg['sender']['lastName'].encode('utf-8'),
            '\n']
        )
        message += '_SUBJECT_: ' + msg['subject'].encode('utf-8') + '\n'
        message += msg['body'].encode('utf-8') + '\n'
        message += time.ctime(msg['timestamp'] / 1000) + '\n\n'

        return message

    def get_all_messages(self):
        """Возвращает все сообщения всех переписок"""

        all_messages = '\n'
        conversations_id = self.__get_conversations_id()
        for conversation_id in conversations_id:
            messages = self.get_conversation_messages(conversation_id)
            for message in messages:
                # if not self.is_read(message):  # just not read messages
                all_messages += self.__get_message(message)
            self.set_read(conversation_id)

        return all_messages

    def __get_csrfToken_ajax(self, page):
        """Возвращает csrfToken для запросов ajax"""

        soup = BeautifulSoup(page, "html.parser")
        csrfToken_ajax = \
            soup.find(attrs={"name": "lnkd-track-error"})['content']

        return csrfToken_ajax[32:]

    def __create_url(self, conversation_id, csrfToken_ajax):
        """Вспомагательная ф-я для создания url"""

        url = \
            settings.CONVERSATIONS + \
            conversation_id + \
            settings.CONVERSATIONS_PARAM +\
            csrfToken_ajax

        return url

    def set_unread(self, conversation_id):
        """Ставит признак 'Непрочитан' для переписки"""

        url = self.__create_url(conversation_id, self._csrfToken_ajax)
        data = {"patch": {"$set": {"read": False}}}
        self._client.post(url, json=data)

    def set_read(self, conversation_id):
        """Ставит признак 'Прочитан' для переписки"""

        url = self.__create_url(conversation_id, self._csrfToken_ajax)
        data = {"patch": {"$set": {"read": True}}}
        self._client.post(url, json=data)

    def delete_conversation(self, conversation_id):
        """Удаляет переписку"""

        url = self.__create_url(conversation_id, self._csrfToken_ajax)
        self._client.delete(url)

    def send(self, users_id, subject, message):
        """ Отправка сообщения"""

        data = {
            'ajaxSubmit': 'Send+Message',
            'subject': subject,
            'body': message,
            'fromName': '',
            'showRecipeints': 'showRecipeints',
            'fromEmail': '',
            'connectionIds': users_id,
            'connectionNames': '',
            'allowEditRcpts': "true",
            'addMoreRcpts': "false",
            'itemID': '',
            'openSocialAppBodySuffix': '',
            'st': '',
            'viewerDestinationUrl': '',
            'csrfToken': 'ajax:' + self._csrfToken_ajax.encode('utf-8'),
            'sourceAlias': '',
            'goback': ''
        }
        self._client.post(settings.SEND_URL, data=data)


def send_mail(message):
    """Отправка сообщений на почту"""

    try:
        server = smtplib.SMTP(settings.SMTP)
        # Выводим на консоль лог работы с сервером (для отладки)
        server.set_debuglevel(1)
        # Переводим соединение в защищенный режим (Transport Layer Security)
        server.starttls()
        server.login(settings.LOGIN_FROM, settings.MAIL_PASS)
        server.sendmail(settings.MAIL_FROM, settings.MAIL_TO, message)
    finally:
        server.quit()


if __name__ == '__main__':
    parser = LinkedIn(settings.LOGIN_LINKEDIN, settings.PASS_LINKEDIN)
    all_messages = parser.get_all_messages()
    send_mail(all_messages)
