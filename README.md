# Django_Survey_App
Django-based enterprise-scale survey project

Этот Джанго-сервис предназначен для предприятий, проводящих анкетирование по системе оптимизации производства.  
С работающим вариантом можно ознакомиться по адресу https://fcc.svartha.ru  
В данном репозитории содержатся файлы для деплоя на сервере, не включены папки логов и staticfiles.  

**Как работает сервис**  
*Пользователь попадает на главную страницу, может зарегистрироваться или ввести свой логин/пароль, если уже зарегистрирован  
*После входа пользователь попадает на страницу, где ему доступны несколько вариантов дальнейших действий:  
1. Можно создать предприятие (вводится название и количество сотрудников, которые должны пройти анкетирование)
2. Можно посмотреть карточки уже созданных предприятий
3. Можно выйти  
*При создании нового предприятия формируется его карточка, где генерируется ссылка на анкету для отправки сотрудникам  
*Сотруднику не нужно регистрироваться в системе, чтобы заполнить анкету, введенные данные сохраняются в базе анонимно  
*После того, как хотя бы один сотрудник заполнил анкету, в карточке предприятия можно посмотреть статистику,  перейдя по соответствующей кнопке  
*Статистика формируется с диаграммами по каждому вопросу анкеты для наглядной визуализации  
*После оценки статистики можно внести свои выводы и меры по улучшению, для этого предусмотрены соответствующие поля. Эти поля предварительно заполнены стандартным текстом и являются редактируемыми  
*Статистику можно выгрузить в пдф, она сохраняется по шаблону statistics_name_of_your_enterprise.pdf  
