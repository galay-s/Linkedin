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

        html = self._client.get(settings.HOMEPAGE_URL).content
        soup = BeautifulSoup(html, "html.parser")
        csrf = soup.find(id="loginCsrfParam-login")['value']
        login_information = {
            'isJsEnabled': 'false',
            'source_app': '',
            'tryCount': '',
            'clickedSuggestion': 'false',
            'session_key': self._login,
            'session_password': self._password,
            'loginCsrfParam': csrf,
          }
        page = self._client.post(settings.LOGIN_URL, data=login_information)

        return page.content

    def get_page(self, url):
        """Возвращает страницу url"""

        html = self._client.get(url).content

        return html

    def get_page_soup(self, url):
        """Возвращает страницу url в виде soup"""

        html = self.get_page(url)
        soup = BeautifulSoup(html, "html.parser")

        return soup

    def __get_conversationsBefore(self):
        """Возвращает информацию(json) по всем перепискам(threadId)."""

        soup = self.get_page_soup(settings.MESSAGE_URL)
        info_tag = soup.find(id="inbox-main-content").contents[0]
        info_json = json.loads(info_tag)
        conversationsBefore = info_json['conversations']['conversationsBefore']

        return conversationsBefore

    def __get_list_threadsId(self):
        """Возвращает список номеров переписок(threadId). Один номер это сообщения
        от одного пользователя.
        """

        threadsId = []
        conversationsBefore = self.__get_conversationsBefore()
        for convBef in conversationsBefore:
            threadsId.append(convBef['threadId'])

        return threadsId

    def __get_threadId(self, threadId):
        """Получает полные данные(json) одной переписки(threadId) в которой может быть
        несколько сообщений
        """

        url = "".join([settings.THREAD, threadId])
        soup = self.get_page_soup(url)
        info_tag = soup.find(id="inbox-main-content").contents[0]
        info_json = json.loads(info_tag)
        selectedThreadInfo = info_json['selectedThreadInfo']

        return selectedThreadInfo

    def is_read(self, message):
        """Проверяет прочитано ли сообщение. Возвращает True если прочитано"""

        return message['read']

    def get_thread_messages(self, threadId):
        """Возвращает сообщения(json) одной переписки"""

        selectedThreadInfo = self.__get_threadId(threadId)

        return selectedThreadInfo['messages']

    def __create_message_body(self, message):
        """Формирует одно сообщение для письма"""

        body = " ".join([
                          '_FROM_:',
                          message['sender']['firstName'].encode('utf-8'),
                          message['sender']['lastName'].encode('utf-8'),
                          '\n'])
        body += '_SUBJECT_: ' + message['subject'].encode('utf-8') + '\n'
        body += message['body'].encode('utf-8') + '\n'
        body += time.ctime(message['timestamp']/1000) + '\n\n'

        return body

    def create_mail_body(self):
        """Формирует письмо со всеми сообщениями в linkedin"""

        body = '\n'
        list_threadsId = self.__get_list_threadsId()
        for threadId in list_threadsId:
            messages = self.get_thread_messages(threadId)
            for message in messages:
                # if not self.is_read(message):
                body += self.__create_message_body(message)
            # self.set_read(threadId)

        return body

    def __get_csrfToken_ajax(self, page):
        """Возвращает csrfToken для запросов ajax"""

        soup = BeautifulSoup(page, "html.parser")
        csrfToken_ajax = soup.find(
            attrs={"name": "lnkd-track-error"})['content']
        return csrfToken_ajax[32:]

    def __create_url(self, threadId, csrfToken_ajax):
        """Вспомагательная ф-я для создания url"""

        url = settings.CONVERSATIONS +\
            threadId + settings.CONVERSATIONS_PARAM + csrfToken_ajax
        return url

    def set_unread(self, threadId):
        """Ставит признак 'Непрочитан' для переписки"""

        url = self.__create_url(threadId, self._csrfToken_ajax)
        data = {"patch": {"$set": {"read": False}}}
        self._client.post(url, json=data)

    def set_read(self, threadId):
        """Ставит признак 'Прочитан' для переписки"""

        url = self.__create_url(threadId, self._csrfToken_ajax)
        data = {"patch": {"$set": {"read": True}}}
        self._client.post(url, json=data)

    def del_conversation(self, threadId):
        """Удаляет переписку"""

        url = self.__create_url(threadId, self._csrfToken_ajax)
        self._client.delete(url)

    def send(self, connectionIds, subject, msg):
        """ Отправка сообщения в Linkedin"""

        data = {
                'ajaxSubmit': 'Send+Message',
                'subject': subject,
                'body': msg,
                'fromName': '',
                'showRecipeints': 'showRecipeints',
                'fromEmail': '',
                'connectionIds': connectionIds,
                'connectionNames': '',
                'allowEditRcpts': "true",
                'addMoreRcpts': "false",
                'itemID': '',
                'openSocialAppBodySuffix': '',
                'st': '',
                'viewerDestinationUrl': '',
                'csrfToken': 'ajax:' + self._csrfToken_ajax.encode('utf-8'),
                'sourceAlias': '',
                'goback': ''}
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
    user = LinkedIn(settings.LOGIN_LINKEDIN, settings.PASS_LINKEDIN)
    body = user.create_mail_body()
    send_mail(body)
