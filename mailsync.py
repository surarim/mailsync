#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------------------------
# Обновление почтовых ящиков в базе mail, таблице relay_recipient из zimbra
#------------------------------------------------------------------------------------------------

from datetime import datetime
import os, psycopg2, paramiko

# Общие параметры
Log = '/var/log/mailbase_sync.log'
local_mailboxes = 'mailsync_local_mailboxes'

# Параметры соединения с сервером zimbra
zimbra_host = 'zimbra.domain.ru'
zimbra_user = 'root'
zimbra_passwd = '123456'

# Параметры соединения с базой mail
mail_database = 'mail'
mail_user = 'postfix'
mail_passwd = '123456'

#------------------------------------------------------------------------------------------------

# Функция записи в лог файл
def log_write(message):
  # Подготовка лог файла
  if not os.path.isfile(Log):
    logdir = os.path.dirname(Log)
    if not os.path.exists(logdir):
      os.makedirs(logdir)
    open(Log,'a').close()
  else:
    # Проверка размера лог файла
    log_size = os.path.getsize(Log)
    # Если лог файл больще 10М, делаем ротацию
    if log_size > 1024**2*10:
      try:
        os.remove(Log+'.old')
      except:
        pass
      os.rename(Log, Log+'.old')
  # Запись в лог файл
  with open(Log,'a') as logfile:
    logfile.write(str(datetime.now()).split('.')[0]+' '+message+'\n')

def run():
  # Чтение файла исключений
  try:
    ignore_local_mailboxes = open(local_mailboxes).read()
  except IOError as error:
    log_write(error)

  # Получение списка почтовых ящиков
  ssh = paramiko.SSHClient()
  ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  log_write('Sync mailboxes...')
  ssh.connect(hostname=zimbra_host, username=zimbra_user, password=zimbra_passwd)
  stdin, stdout, stderr = ssh.exec_command('su - zimbra -c "zmprov -l gaa"')
  mailbox_zimbra = (stdout.read() + stderr.read()).decode()
  ssh.close()

  # Обновленние ящиков в базе mail, таблице relay_recipient
  conn = psycopg2.connect("host='localhost' dbname="+mail_database+" user="+mail_user+" password="+mail_passwd)
  cursor = conn.cursor()
  cursor.execute("select * from relay_recipient;")
  mailbox_local=''
  for row in cursor:
    mailbox_local += row[0]+'\n'

  # Удаление локальных ящиков, которые более не присутствуют на zimbra
  for line in mailbox_local.splitlines():
    if mailbox_zimbra.find(line) == -1 or line in ignore_local_mailboxes:
      try:
        cursor.execute("delete from relay_recipient where mailbox like %s;",(line,))
      except psycopg2.Error as error:
        print(format(error))
        exit(1)
      log_write('Deleted '+line)

  # Добавление новых локальных ящиков, которые есть на zimbra
  for line in mailbox_zimbra.splitlines():
    if mailbox_local.find(line) == -1 and line not in ignore_local_mailboxes:
      try:
        cursor.execute("insert into relay_recipient values (%s);",(line,))
      except psycopg2.Error as error:
        print(format(error))
        exit(1)
      log_write('Added '+line)
  conn.commit()
  conn.close()

#------------------------------------------------------------------------------------------------

# Запуск программы
if __name__ =='__main__':
  run()
  
