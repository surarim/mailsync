![Alt text](mailsync.png?raw=true "Title")
# mailsync
### Система обновления почтовых ящиков на postfix шлюзе из внутреннего сервера на zimbra
### Version 0.04 (early development)
<hr>
Обновление осуществляется в сторону postfix шлюза, для поддержания актуального списка почтовых ящиков.
<br>
Получение списка почтовых ящиков на zimbra происходит через ssh соединение и команду zmprov, а обновление на postfix осуществляется в базе PostgreSQL. Postfix должен быть предварительно настроен на получение списка ящиков из базы PostgreSQL.
<br>
Протестировано и собрано с использованием следующих компонентов:
<ul>
  <li>postfix: 3.4.7</li>
  <li>PostgreSQL: 12.0 </li>
  <li>Python: 3.8.0</li>
  <li>psycopg2: 2.8.4</li>
  <li>paramiko: 2.6.0</li>
 </ul>
