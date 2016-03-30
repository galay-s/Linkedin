# Linkedin
Loggin in Linkedin and parser

user = LinkedIn(LOGIN, PASSWORD)                """Входит в аккаунт"""\n

user.get_page(url)                              """Возвращает страницу url"""
user.get_page_soup(url)                         """Возвращает страницу url в виде soup"""
user.is_read(message)                           """Проверяет прочитано ли сообщение. Возвращает True если прочитано"""
user.get_thread_messages(threadId)              """Возвращает сообщения(json) одной переписки"""
user.create_mail_body()                         """Формирует письмо со всеми сообщениями в linkedin"""
user.set_unread(threadId)                       """Ставит признак 'Непрочитан' для переписки"""
user.set_read(threadId)                         """Ставит признак 'Прочитан' для переписки"""
user.del_conversation(threadId)                 """Удаляет переписку"""
user.send(connectionIds, subject, msg)          """ Отправка сообщения в Linkedin"""
