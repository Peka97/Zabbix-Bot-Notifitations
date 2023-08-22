# Zabbix-Bot-Notifitations

## Содержание
- [Стэк](#стэк)
- [Установка](#установка)
- [Начало работы](#начало-работы)
- [Тестирование](#тестирование)
- [FAQ](#faq)

## Стэк
 - Python 3.10.12
 - Requests 2.29.0
 - Aiogram 2.25.1
 - Pillow 9.5.0
 - XmlToDict 0.13.0
 - Openpyxl 3.1.2
 - Tabulate 0.9.0
   
<sub>Полный стек представлен в requirements.txt</sub>

## Установка
Перед началом установки подготовим выполним следующие команды:
Установим Python версии 3.10 из любого репозитория, а так же виртуальное окружение под него:
```sh
$ sudo apt install software-properties-common -y
$ sudo add-apt-repository ppa:deadsnakes/ppa
$ sudo apt install python3.10
$ sudo apt-get install python3.10-venv
```

Проверим доступные версии Python:
```sh
$ cd /usr/bin/
$ ls | grep python
```

Установим alias для новой версии Python при необходимости, чтобы всегда запускать под Python 3.10:
```sh
$ alias python3='/usr/bin/python3.10'
```

Перейдём в каталог, указанный в документации ZabbixApi, для дальнейшей работы:
```sh
$ cd /usr/lib/zabbix/alertscripts
```

Создаём виртуальное окружение, активируем его и обновим pip:
```sh
$ python3 -m venv .venv
$ . .venv/bin/activate
$ pip install --upgrade pip
```

Теперь мы готовы к работе с репозиторием. Копируем репозиторий в текущую директорию и переходим на нужную ветку:
```sh
$ git clone https://github.com/Peka97/Zabbix-Bot-Notifitations.git .
$ git switch dev_personal
```

Переименовываем файл `example_config.py` в `config.py` и прописываем конфигурацию согласно позициям в классе.
Для персональной рассылки нам нужны будут поля `ADMINS`, `API_TOKEN`, `zabbix_api_login`, `zabbix_api_pass`, `zabbix_api_url`.

В Zabbix выставляем способ уведомления через скрипт, прописываем путь до скрипта `send_to_bot.sh`. Именно bash скрипт будет получать все переданные поля из Zabbix, запускать виртуальное окружение и передавать их на выполнение в `send_to_bot.py`.

Скрипт отправки уведомлений из zabbix уже будет работать. Перейдём к запуску бота на постоянной основе.
Использовать будем системный менеджер `systemd`. Установим его:
```sh
$ apt-get install systemd
```

Перейдём в нужный каталог и создадим `bot.service` в системе:
```sh
$ cd /etc/systemd/system
$ touch bot.service
$ nano bot.service
```

Прописываем в файле следующее:
```sh
[Unit]
Description=Telegram Alert Zabbix Bot
After=syslog.target
After=network.target

[Service]
Type=simple
User=zabbix
WorkingDirectory=/usr/lib/zabbix/alertscripts
ExecStart=/usr/lib/zabbix/alertscripts/.venv/bin/python3 /usr/lib/zabbix/alertscripts/bot.py
RestartSec=10
Restart=always

[Install]
WantedBy=multi-user.target
```

Затем запускаем созданный нами сервис и проверяем его работу:
```sh
$ systemctl daemon-reload
$ systemctl enable bot.service
$ systemctl start bot.service
$ systemctl status bot.service
```

Если ошибок нет, то можем проверить работу бота: напишем в Telegram боту `/inventory_hosts` или `/inventory_group`.
Если нам приходит от него сообщение, то мы всё сделали правильно.


## Начало работы
Устанавливаем нужные поля в способах уведомлений Zabbix.


## Тестирование
Для тестирования работы скрипта уведомления можно использовать файл `for_test.py`.
Для тестирования внутренних функций бота предусмотрен файл `test.py` с Unit-тестами.

## FAQ
Q - В процессе установки скрипта и выполнения команды Linux из инструкции падает ошибка `Permisson denied`. Что делать?<br>
A - Выполните команду из под `root`, прописав перед ней `sudo`.
<hr>
Q - Скрипт при запуске пишет, что такого файла\директории не существует. При этом в системе он совершенно точно есть. Почему так?<br>
A - Zabbix имеет недостаточно прав для чтения и просмотра, потому не может их открыть. Проблему легко исправить с помощью `sudo chmod`.
