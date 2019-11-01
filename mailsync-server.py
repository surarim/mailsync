#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------------------------
# Обновление почтовых ящиков в базе mail, таблице relay_recipient из zimbra
#------------------------------------------------------------------------------------------------

from datetime import datetime
import os, psycopg2, paramiko
config = [] # Список параметров файла конфигурации

#------------------------------------------------------------------------------------------------

# Функция получения значений параметров конфигурации
def get_config(key):
  global config
  result = ''
  if not config:
    # Чтение файла конфигурации
    try:
      if os.path.isfile('/etc/mailsync/mailsync.conf'):
        configfile = open('/etc/mailsync/mailsync.conf')
      else:
        configfile = open('mailsync.conf')
    except IOError as error:
      log_write(error)
    else:
      for line in configfile:
        param = line.partition('=')[::2]
        if param[0].strip().isalpha() and param[0].strip().find('#') == -1:
          # Получение параметра
          config.append(param[0].strip())
          config.append(param[1].strip())
  try:
    result = config[config.index(key)+1]
  except ValueError as err:
    log_write('Config parameter '+str(key)+' not found, stoping server')
    exit(1)
  return result

#------------------------------------------------------------------------------------------------

# Функция записи в лог файл
def log_write(message):
  # Подготовка лог файла
  if not os.path.isfile(get_config('Log')):
    logdir = os.path.dirname(get_config('Log'))
    if not os.path.exists(logdir):
      os.makedirs(logdir)
    open(get_config('Log'),'a').close()
  else:
    # Проверка размера лог файла
    log_size = os.path.getsize(get_config('Log'))
    # Если лог файл больще 10М, делаем ротацию
    if log_size > 1024**2*10:
      try:
        os.remove(get_config('Log')+'.old')
      except:
        pass
      os.rename(get_config('Log'), get_config('Log')+'.old')
  # Запись в лог файл
  with open(get_config('Log'),'a') as logfile:
    logfile.write(str(datetime.now()).split('.')[0]+' '+message+'\n')

#------------------------------------------------------------------------------------------------

def run():
  # Получение списка почтовых ящиков из zimbra
  ssh = paramiko.SSHClient()
  ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  log_write('Sync mailboxes...')
  ssh.connect(hostname=get_config('ZimbraHost'), username=get_config('ZimbraUser'), password=get_config('ZimbraPasswd'))
  stdin, stdout, stderr = ssh.exec_command('su - zimbra -c "zmprov -l gaa"')
  mailboxes_zimbra = (stdout.read() + stderr.read()).decode()
  ssh.close()
  # Чтение текущих ящиков на posfix
  conn = psycopg2.connect("host='localhost' dbname="+get_config('MailDatabase')+" user="+get_config('MailUser')+" password="+get_config('MailPasswd'))
  cursor = conn.cursor()
  cursor.execute("select * from relay_recipient;")
  mailboxes_local=''
  for row in cursor:
    mailboxes_local += row[0]+'\n'
  # Чтение таблицы локальных исключений
  cursor.execute("select * from mailboxes_localonly;")
  mailboxes_localonly=''
  for row in cursor:
    mailboxes_localonly += row[0]+'\n'
  # Удаление локальных ящиков, которые более не присутствуют на zimbra
  for line in mailboxes_local.splitlines():
    if mailboxes_zimbra.find(line) == -1 or line in mailboxes_localonly:
      try:
        cursor.execute("delete from relay_recipient where mailbox like %s;",(line,))
      except psycopg2.Error as error:
        print(format(error))
        exit(1)
      log_write('Deleted '+line)
  # Добавление новых локальных ящиков, которые есть на zimbra
  for line in mailboxes_zimbra.splitlines():
    if mailboxes_local.find(line) == -1 and line not in mailboxes_localonly:
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
