<div style="text-align: center;">
    <h1>Telegram 机器人模板<br>[ Pyrogram version ]</h1>
    <img src="https://telegra.ph/file/4621c1419e443ebb01b2b.jpg" style="width: 100%;" alt="image1"/>
</div>


---

<div style="text-align:center">
<h1><b>关于这个存储库？</b></h1>
</div>

该存储库用作使用 Python 创建新 Telegram 机器人的模板。
它旨在为那些从头开始新项目的人节省时间，并为那些刚接触 Telegram API 并想要学习和理解基本文件结构的人提供有用的资源。
该存储库包含一个可插入样板，易于使用并针对您自己的项目进行自定义。
您可以使用存储库作为模板或 fork 它来开始新项目。
以下是该存储库的一些功能：

- 完全异步：此存储库中的代码利用 httpx、aiofiles、pyrogram 和 mongodb motor 等库来实现完全异步执行。 
  这意味着代码可以同时执行多个任务，从而提高机器人的性能和效率。
- 内置功能：该存储库包含一系列预构建的插件、函数和装饰器，可帮助您入门。
  一些示例包括用于广播、粘贴、检查垃圾邮件计数器、评估/执行代码、检查数据库和服务器统计信息等的命令。
- 定制插件：此存储库中的代码设计为模块化和可扩展的，允许您通过创建和集成插件轻松向机器人添加新功能。
- 速率限制：为了防止 FloodWait 错误，此存储库中的代码包含速率限制功能，该功能使用漏桶算法和 pyrate_limiter 库来限制用户在给定时间段内可以发出的请求数量。
- MongoDB 支持：此存储库中的代码包括对在 MongoDB 数据库中存储数据的支持，使您可以轻松跟踪与机器人关联的用户和渠道。

---

<div style="text-align:center">
<h1><b>更多信息</b></h1>
</div>

<img src="https://telegra.ph/file/db914ce03059dca6e2e02.gif" style="float: right; width: 150px;" alt="animated-image">


<p>
<b>该机器人使用基于 MTProto 协议的 Pyrogram 框架与 Telegram API 进行通信。 </b>
<br>
<br>
Pyrogram 是一个现代、优雅、更快的异步 MTProto API<a href="https://docs.pyrogram.org/topics/mtproto-vs-botapi">（MTProto 与 botapi）</a> 框架。
<br>
<br>
<a href="https://docs.pyrogram.org/"><strong>Pyrogram 文档</strong></a> | <a href="https://t.me/pyrogramchat"><strong>Pyrogram 群组</strong></a> | <a href="https://core.telegram.org/api"><strong>Telegram API 文档</strong></a>
<br>
<br>其他一些库和框架：<a href="https://github.com/python-telegram-bot/python-telegram-bot"><strong>Python Telegram Bot</strong></a> | <a href="https://github.com/LonamiWebs/Telethon"><strong>Telethon</strong></a> | <a href="https://core.telegram.org/bots/samples"><strong>List of libraries and frameworks using various type of languages.</strong></a>
<br>
<br>
Join <a href="https://t.me/ani_support"><strong>Discussion Group</strong></a> if you have any suggestion or bugs to discuss.
<p>

---

<div style="text-align:center"> 
<h1><b>屏幕截图</b></h1>
</div>

| ![](https://te.legra.ph/file/565b3f47e0886fc93e75c.jpg) | ![](https://te.legra.ph/file/e6e16e6f3a1d07524a23b.jpg) |
|---------------------------------------------------------|---------------------------------------------------------|
| ![](https://te.legra.ph/file/29f7e8163406f63bfb4f8.jpg) | ![](https://te.legra.ph/file/c26991c1eaae34920216c.jpg) |

---

<div style="text-align:center"> 
<h1><b>机器人的部署和使用</b></h1>
<p><b>( VPS 或本地主机 )</b></p>
</div>

( 如果您不想在机器人中使用数据库，请检查没有数据库分支。 )

在服务器中升级、更新和设置所需的软件包。

```
sudo apt-get update && sudo apt-get upgrade -y
sudo apt install python3-pip -y
sudo pip3 install -U pip
```

克隆 GitHub 存储库并在服务器中启动机器人。

```
git clone https://github.com/sanjit-sinha/Telegram-Bot-Boilerplate && cd Telegram-Bot-Boilerplate 
pip3 install -U -r requirements.txt
```

现在输入 `nano config.env` 编辑配置变量，然后按 <kbd>ctrl</kbd>+<kbd>o</kbd> 和保存 <kbd> 
ctrl</kbd>+<kbd>x</kbd>。
<br>
<br>

<details open="open">
<summary><strong>设置配置变量文件 ( config.env )</strong></summary>
<br>
<ul>
 <li>从 <a href="https://my.telegram.org/auth">Telegram.org</a> 获取您的 API_ID 和 API_HASH，从<a href="https://t.me/botfather"> Botfather </a>获取 BOT_TOKEN 。只需使用 /info 命令并从结果中复制 ID 值，即可从 <a href="https://t.me/MissRose_bot">MissRoseBot</a> 获取 sudo 用户和所有者的用户 ID 。</li>
  <li>要获取获取 MONGO_URI 的指南，请点击 <a href="https://graph.org/How-to-create-mongodb-URI-01-01">此处</a></li>
  </ul>
</details>

现在只需输入 `bash start` 或 `python3 -m TelegramBot`

<img src="https://telegra.ph/file/03a650af46de1bcc27756.png" style="float: right; width: 150px;" alt="image">

一旦您从服务器注销，机器人就会停止工作。您可以使用 screen 或 tmux 在服务器中 24*7 运行机器人。

```
sudo apt install tmux -y
tmux && bash start
```

现在，即使您注销，机器人也将 24*7 运行在服务器上。[点击此处了解 tmux 和 screen 高级命令。](https://grizzled-cobalt-5da.notion.site/Terminal-Multiplexers-to-run-your-command-24-7-3b2f3fd15922411dbb9a46986bd0e116)

<details open="open">
<summary><strong>基本 Bot 命令及其用法</strong></summary>
<ul>
<br>
	<li>
	<i><b>Users Commands</b></i><br><br>
	/start - To get the start message.<br>
	/help - Alias command for start. <br>
	/ping - Ping the telegram api server<br>
	/paste - Paste the text in katb.in
	</li>
<br>
	<li>
	<i><b>Sudo User Commands </b></i><br><br>
	/speedtest - Check the internet speed of bot server.<br>
	/serverstats - Get the stats of bot server.<br>
	/stats - Alias command for serverstats.<br>
	/dbstats - Get the stats of bot database. 
	</li>
<br>
	<li>
	<i><b>Developer Commands </b></i><br><br> 
	/shell - To run the terminal commands via bot.<br>
	/py - To run the python commands via bot. <br>
	/update - To update the bot to latest commit from repository. <br> 
	/restart - Restart the bot. <br>
	/log - To get the log file of bot. <br>
	/broadcast - broadcast the message to bot users and chat. 
</ul>
</details>
<br>

---

<div style="text-align:center">
<h1><img src="https://telegra.ph/file/c182d98c9d2bc0295bc86.png" width="45" alt="image"><b>  
项目结构 </b></h1>
</div>

```
├── Dockerfile                          
├── LICENSE
├── README.md
├── config.env                         ( For storing all the  environment variables)
├── requirements.txt                   ( For keeping all the library name wich project is using)
├── TelegramBot
│   │
│   ├── __init__.py                   ( Initializing the bot from here.)
│   ├── __main__.py                   ( Starting the bot from here.)
│   ├── config.py                     ( Importing and storing all envireonment variables from config.env)
│   ├── logging.py                    ( Help in logging and get log file)
│   │
│   ├── assets                        ( An assets folder to keep all type of assets like thumbnail, font, constants, etc.)
│   │   └── __init__.py
│   │   ├── font.ttf
│   │   └── template.png
│   │
│   ├── database                      (Sperate folder to manage database related stuff for bigger projects.)
│   │   ├── __init__.py
│   │   ├── database.py              (contain functions related to handle database operations all over the bor)
│   │   └── MongoDb.py               (Contain a MongoDB class to handle CRUD operations on MongoDB collection )
│   │  
│   ├── helpers                       ( Contain all the file wich is imported and  used all over the code. It act as backbone of code.)
│   │   ├── __init__.py
│   │   ├── filters.py 
│   │   ├── decorators.py            ( Contain all the python decorators)
│   │   ├── ratelimiter.py           (Contain RateLimiter class that handle ratelimiting part of the bot.)
│   │   └── functions.py             ( Contain all the functions wich is used all over the code. )
│   │
│   ├── plugins                       ( plugins folder contain all the plugins commands via wich user interact)  
│   │   ├── __init__.py 
│   │   ├── developer
│   │   │   ├── __init__.py
│   │   │   ├── terminal.py
│   │   │   └── updater.py
│   │   │
│   │   ├── sudo
│   │   │   ├── __init__.py
│   │   │   ├── speedtest.py
│   │   │   ├── dbstats.py
│   │   │   └── serverstats.py
│   │   │   
│   │   └── users
│   │       ├── __init__.py
│   │       ├── alive.py
│   │       └── start.py
│   │      
│   └── version.py         
└── start                             ( A start file containing bash script to start the bot using bash start)
```

<details>
   <summary>Some important articles and Links which will help you to understand the code better.</summary>
   <ul>
    <br>
    <li> <a href="https://stackoverflow.com/questions/448271/what-is-init-py-for#:~:text=The%20__init__.py%20file%20makes%20Python,directories%20containing%20it%20as%20modules">What is __init__.py</a>│ <a href="https://youtu.be/cONc0NcKE7s">( YouTube video )</a></li>         
    <li> <a href="https://www.geeksforgeeks.org/what-does-the-if-__name__-__main__-do/">What is __name__ = "__main__" in python?</a></li>
    <li><a href="https://realpython.com/python-logging/
">About python logging</a></li>
    <li><a href="https://www.educative.io/blog/python-concurrency-making-sense-of-asyncio">Python concurrent and asyncio</a></li>
    <li><a href="https://developer.vonage.com/blog/21/10/01/python-environment-variables-a-primer">What is Environment Variables (.env files) ?</a></li>  
    <li><a href="https://www.programiz.com/python-programming/decorator
">About Python decorator</a></li>
    <li> <a href="https://stackoverflow.com/questions/4042905/what-is-main-py">What is __main__.py</a> </li> 
       <li><a href="https://learnpython.com/blog/python-requirements-file">What is requirements.txt and why should we use it?</a></li>
     <li> <a href="https://geekflare.com/dockerfile-tutorial/">What iS Dockerfile?</a> </li>
     <li> <a href="https://developerexperience.io/practices/license-in-repository">what is License in a repository?</a> │<a href="https://choosealicense.com/">choosealicense.</a></li> 
     <li><a href="https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes">What is README.md?</a> │ <a href="https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax">( writing format for GitHub readme ) </a>│ <a href="https://readme.so ">( website which will help you in writing readme ) </a>│website to get png images which  can be used in making readme:- <a href="https://shields.io/">shields.io│</a> <a href="https://www.flaticon.com/">flaticon.com</a></li>

</ul>
</details>

---

<div style="text-align:center">
<h1><b>Basic structure for building your own plugin.</b></h1>
</div>

```py
from TelegramBot.helpers.decorators import ratelimiter
from pyrogram import Client, filters
from pyrogram.types import Message


@Client.on_message(filters.command(["hello", "hi"]))
@ratelimiter
async def hello(client: Client, message: Message):
    """
    simple plugin to demonstrate in readme.
    """
    return await message.reply_text("world")
```

---

<div style="text-align:center">
<h1><b>Credits and Contribution</b></h1>
</div>

<img src="https://telegra.ph/file/b26313d73e4d05de84a85.png" style="float: right; width: 150px;" alt="image">
<p>
Codes and structure of this bot is heavily inspired by open source projects like <a href="https://github.com/TeamYukki/YukkiMusicBot"><strong>YukkiMusicbot</strong></a> | <a href="https://github.com/UsergeTeam/Userge"><strong>Userge</strong></a> | <a href="https://github.com/EverythingSuckz/TG-FileStreamBot"><strong>TG-FileStreamBot etc.</strong></a>.
<br>
<br>
 Special Thanks to <br>
• <a href="https://github.com/delivrance"><strong>Dan</strong></a> for creating <a href="https://github.com/pyrogram/pyrogram"><strong>Pyrogram.</strong></a><br>
• <a href="https://github.com/starry69"> Starry</a> for guiding and acute repository. <br>
• <a href="https://github.com/annihilatorrrr">Annihilator</a> for helping me out with pyrogram stuff.

<br>
<br>
Any type of suggestions, pointing out bug or contribution is highly appreciated. :)
</p>

---

<div style="text-align:center">
<h1><b>Copyright and License</b></h1>
</div>
<br>
<img src="https://telegra.ph/file/b5850b957f081cfe5f0a6.png" style="float: right; width: 110px;" alt="image">

* copyright (C) 2023 by [Sanjit sinha](https://github.com/sanjit-sinha)
* Licensed under the terms of the [MIT License](https://github.com/sanjit-sinha/Telegram-Bot-Boilerplate/blob/main/LICENSE)

<div style="text-align:center">
<img src="https://img.shields.io/badge/License-MIT-green.svg" alt="image">
</div>

---

