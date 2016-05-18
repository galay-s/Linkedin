# -*- coding: utf-8 -*-
# smtp сервера отправителя
SMTP = 'smtp.mail.ru'

# Почтовый ящик и пароль отправителя
MAIL_FROM = 'XXXXXXXX@mail.ru'
MAIL_PASS = 'XXXXXXXX'

# Логин отправителя
LOGIN_FROM = MAIL_FROM.split('@')[0]

# Почтовый ящик получателя
MAIL_TO = 'YYYYYYYYYY@mail.ru'

LOGIN_LINKEDIN = 'ZZZZZZZZ@mail.ru'
PASS_LINKEDIN = 'ZZZZZZZZ'


HOMEPAGE_URL = 'https://www.linkedin.com'

# Страница для входа
LOGIN_URL = 'https://www.linkedin.com/uas/login-submit'

# Страница для получения всех номеров
# threadsId(на каждого пользователя свой номер)
MESSAGE_URL = 'https://www.linkedin.com/messaging/?trk=hb-messages-hdr-item-msg-v2'

# Страница для получения сообщений по номеру пользователя(threadsId)
# ОБЯЗАТЕЛЬНО В КОНЦЕ СЛЕШ
THREAD = 'https://www.linkedin.com/messaging/thread/'

# Для пометки что сообщение прочитано/не прочитано, чтобы удалить сообщение
# используется ссылка:
# 'https://www.linkedin.com/messaging/conversations/'+ threadId+ '?csrfToken=ajax:' + csrfToken_ajax
# ОБЯЗАТЕЛЬНО В КОНЦЕ СЛЕШ
CONVERSATIONS = 'https://www.linkedin.com/messaging/conversations/'
CONVERSATIONS_PARAM = '?csrfToken=ajax:'

# Для отправки сообщения используется ссылка(если беседа уже создана):
# https://www.linkedin.com/messaging/conversations/6119134237808476160/messages?csrfToken=ajax%3A1109433405329279794
CONVERSATIONS_PARAM_SEND = '/messages?csrfToken=ajax:'

# Для отправки сообщения без созданного до этого диалога используем
# (так же можно использовать если беседа до этого создана):
# https://www.linkedin.com/msgToConns?displayCreate=
SEND_URL = "https://www.linkedin.com/msgToConns?displayCreate="
