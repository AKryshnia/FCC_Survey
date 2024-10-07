import os
import re
import textwrap
import matplotlib.pyplot as plt
import io
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.cache import cache
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_protect
from matplotlib.colors import rgb2hex
from transliterate import translit

from .forms import SurveyForm, EnterpriseForm, EnterpriseUpdateForm, CustomUserCreationForm
from .models import SurveyResponse, Enterprise
from weasyprint import HTML, CSS

import logging

logger = logging.getLogger(__name__)

from django.http import HttpResponse
from django.template.loader import render_to_string, get_template


from .tasks import create_plot


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username'].replace(' ', '')
            form.cleaned_data['username'] = username
            user = form.save(commit=False)
            user.username = username
            user.save()
            login(request, user)
            return redirect('index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username'].replace(' ', '_')
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            # Return an 'invalid login' error message.
            return render(request, 'login.html', {'error': 'Invalid login credentials'})
    else:
        return render(request, 'login.html')


def user_logout(request):
    logout(request)
    return redirect('login')


@login_required
def index(request):
    user = request.user
    if user.is_superuser:
        user_enterprises = Enterprise.objects.filter(user=user)
        other_enterprises = Enterprise.objects.exclude(user=user)
    else:
        user_enterprises = Enterprise.objects.filter(user=user)
        other_enterprises = []

    context = {
        'user_enterprises': user_enterprises,
        'other_enterprises': other_enterprises,
    }
    return render(request, 'index.html', context)


def user_profile(request, user_id):
    if request.user.is_superuser:
        user = get_object_or_404(User, id=user_id)
    else:
        user = get_object_or_404(User, id=user_id, user=request.user)
    
    enterprises = Enterprise.objects.filter(user=user)
    return render(request, 'user_profile.html', {'user': user, 'enterprises': enterprises})


def user_list(request):
    users = User.objects.all()
    return render(request, 'user_list.html', {'users': users})


def your_view(request):
    create_plot.delay()
    return HttpResponse("Plot creation started")


@login_required
def add_enterprise(request):
    if request.method == 'POST':
        form = EnterpriseForm(request.POST)
        if form.is_valid():
            enterprise = form.save(commit=False)
            enterprise.user = request.user
            enterprise.save()
            survey_url = request.build_absolute_uri(reverse('survey', args=[enterprise.id]))
            messages.success(request, 'Предприятие успешно сохранено.')
            return render(request, 'add_enterprise_success.html', {'enterprise': enterprise,
                                                                   'survey_url': survey_url})
        else:
            messages.error(request, 'Произошла ошибка при сохранении предприятия.')
    else:
        form = EnterpriseForm()
    return render(request, 'add_enterprise.html', {'form': form})


@login_required
def enterprise_detail(request, enterprise_id):
    if request.user.is_superuser:
        enterprise = get_object_or_404(Enterprise, id=enterprise_id)
    else:
        enterprise = get_object_or_404(Enterprise, id=enterprise_id, user=request.user)
    
    has_records = SurveyResponse.objects.filter(enterprise=enterprise).exists()
    survey_url = request.build_absolute_uri(reverse('survey', args=[enterprise.id]))
    
    context = {
        'enterprise': enterprise,
        'has_records': has_records,
        'survey_url': survey_url,
    }
    return render(request, 'enterprise_detail.html', context)


def is_superuser(user):
    return user.is_superuser

@user_passes_test(is_superuser)
def enterprise_list(request):
    enterprises = Enterprise.objects.all()
    return render(request, 'enterprise_list.html', {'enterprises': enterprises})


def edit_enterprise(request, enterprise_id):
    enterprise = get_object_or_404(Enterprise, id=enterprise_id)
    if request.method == 'POST':
        form = EnterpriseForm(request.POST, instance=enterprise)
        if form.is_valid():
            form.save()
            logger.info("Enterprise updated successfully")
            return redirect('edit_enterprise_success', enterprise_id=enterprise.id)
        else:
            logger.error(form.errors)
    else:
        form = EnterpriseForm(instance=enterprise)
    return render(request, 'edit_enterprise.html', {'form': form, 'enterprise': enterprise})


def enterprise_edited(request, enterprise_id):
    enterprise = get_object_or_404(Enterprise, id=enterprise_id)
    return render(request, 'edit_enterprise_success.html', {'enterprise': enterprise})


def enterprise_added(request):
    return render(request, 'add_enterprise_success.html')


def survey(request, enterprise_id):
    enterprise = get_object_or_404(Enterprise, id=enterprise_id)
    
    if request.method == 'POST':
        form = SurveyForm(request.POST)
        
        if form.is_valid():
            # Получаем значение поля enterprise из cleaned_data
            enterprise = form.cleaned_data['enterprise']
            response = SurveyResponse(
                enterprise=enterprise,
                position_level=form.cleaned_data['position_level'],
                program_goal_understanding=form.cleaned_data['program_goal_understanding'],
                role_understanding=form.cleaned_data['role_understanding'],
                supervisor_support=form.cleaned_data['supervisor_support'],
                program_encouragement=form.cleaned_data['program_encouragement'],
                program_impact=form.cleaned_data['program_impact'],
                interaction_assessment=form.cleaned_data['interaction_assessment'],
                program_priority=form.cleaned_data['program_priority'],
                program_information=form.cleaned_data['program_information'],
                knowledge_application=form.cleaned_data['knowledge_application'],
                program_expectations=form.cleaned_data['program_expectations'],
                program_obstacles=form.cleaned_data['program_obstacles'],
                additional_comments=form.cleaned_data['additional_comments'],
            )
            response.save()
            return redirect('survey_thanks')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Ошибка в поле '{form.fields[field].label}': {error}")
    else:
        form = SurveyForm()
    
    context = {
        'form': form,
        'enterprise': enterprise,
        'hide_messages': True,  # Добавляем переменную для скрытия сообщений
    }
    
    return render(request, 'poll_page.html', context)


def survey_thanks(request):
    return render(request, 'survey_thanks.html')


def generate_pie_chart(data: dict, title: str, figsize: tuple = (4, 4)) -> tuple:
    if not isinstance(data, dict):
        raise TypeError("Data must be a dictionary")
    
    if not data:
        raise ValueError("Data dictionary cannot be empty")
    
    plt.ioff()  # Отключение интерактивности
    plt.figure(figsize=figsize)
    labels = list(data.keys())
    values = list(data.values())
    wedges, texts, autotexts = plt.pie(values, autopct=lambda pct: f'{pct:.0f}%', startangle=140, textprops={'color': 'w'})
    plt.title(title, fontsize=12)  # Уменьшение размера шрифта заголовка
    plt.tight_layout()  # Автоматическое подбор размеров
    
    # сохранение диаграммы в формате svg для корректного отображения в скачиваемом пдф
    buffer = io.BytesIO()
    plt.savefig(buffer, format='svg', transparent=True)
    buffer.seek(0)
    svg_data = buffer.getvalue().decode('utf-8')
    buffer.close()
    
    plt.close()  # Закрытие фигуры
    
    colors = [rgb2hex(w.get_facecolor()[:3]) for w in wedges]
 
    return svg_data, colors


def prepare_survey_data(enterprise):
    responses = SurveyResponse.objects.filter(enterprise=enterprise).select_related('enterprise')
    
    questions = {
        'position_level': {
            'name': 'Распределение должностей',
            'title': '1. Пожалуйста, укажите уровень Вашей должности',
            'choices': ['Мастер / бригадир', 'Начальник отдела', 'Руководитель высшего уровня',
                        'Руководитель дирекции / департамента / управления', 'Секретарь / Помощник руководителя',
                        'Специалист'],
            'good_choices': [],
            'bad_choices': [],
            'conclusions': {},
        },
        'program_goal_understanding': {
            'name': 'Понимание целей внедрения программы на предприятии',
            'title': '2. Понимаете ли Вы цель(-и) Программы на нашем предприятии?',
            'choices': ['Да', 'Нет'],
            'good_choices': ['Да'],
            'bad_choices': ['Нет'],
            'conclusions': {'good': '{{ good_choice_percentage }}% респондентов понимают цель внедрения Программы.',
                            'bad': '{{ bad_choice_percentage }}% респондентов не понимают цель внедрения Программы.'},
        },
        'role_understanding': {
            'name': 'Понимание роли в Программе',
            'title': '3. Понимаете ли Вы свою роль в Программе: ясны ли Вам задачи, которые Вам необходимо выполнить, '
                     'мероприятия в которых нужно принять участие?',
            'choices': ['Да, я понимаю, что мне необходимо будет сделать', 'Нет, мне не понятны мои задачи'],
            'good_choices': ['Да, я понимаю, что мне необходимо будет сделать'],
            'bad_choices': ['Нет, мне не понятны мои задачи'],
            'conclusions': {'good': '{{ good_choice_percentage }}% респондентов отметили, что задачи в проекте понятны.',
                            'bad': '{{ bad_choice_percentage }}% респондентов отметили, что не понимают задачи в проекте.'},
        },
        'supervisor_support': {
            'name': 'Вовлеченность руководства и сотрудников предприятия в реализацию проекта',
            'title': '4. Понимает ли Ваш непосредственный руководитель степень Вашего участия в Программе, '
                     'содействует ли он Вашему участию в Программе?',
            'choices': ['Да, мой руководитель объяснил мне мою роль в Программе и создал условия для моего участия',
                        'Да, мой руководитель объяснил мне мою роль в Программе, но не создал условия для моего '
                        'участия',
                        'Нет, мой руководитель не объяснил мне мою роль в Программе, и он против того, чтобы я '
                        'отвлекался от своих регулярных задач'],
            'good_choices': ['Да, мой руководитель объяснил мне мою роль в Программе и создал условия для моего '
                             'участия'],
            'bad_choices': ['Да, мой руководитель объяснил мне мою роль в Программе, но не создал условия для моего '
                            'участия', 'Нет, мой руководитель не объяснил мне мою роль в Программе, и он против того, '
                                       'чтобы я отвлекался от своих регулярных задач'],
            'conclusions': {'good': 'Руководитель в полном объеме понимает степень участия сотрудников в программе и создал условия для участия.',
                            'bad': 'Руководитель не в полном объеме понимает степень участия сотрудников в программе или не создал условия для участия.'},
        },
        'program_encouragement': {
            'name': 'Оценка поощрения участия в Программе',
            'title': '5. На нашем предприятии поощряется участие в Программе?',
            'choices': ['Да, согласен', 'Нет, не согласен'],
            'good_choices': ['Да, согласен'],
            'bad_choices': ['Нет, не согласен'],
            'conclusions': {'good': '{{ good_choice_percentage }}% сотрудников поощряются за участие в Программе.',
                            'bad': '{{ bad_choice_percentage }}% сотрудников не поощряются за участие в Программе.'},
        },
        'program_impact': {
            'name': 'Оценка эффективности Программы',
            'title': '6. Программа повышения производительности труда поможет в достижении целей нашего предприятия?',
            'choices': ['Да, согласен', 'Нет, не согласен'],
            'good_choices': ['Да, согласен'],
            'bad_choices': ['Нет, не согласен'],
            'conclusions': {'good': '{{ good_choice_percentage }}% сотрудников считают, что Программа поможет в достижении целей предприятия.',
                            'bad': '{{ bad_choice_percentage }}% сотрудников не считают, что Программа поможет в достижении целей предприятия.'},
        },
        'interaction_assessment': {
            'name': 'Оценка эффективности взаимодействия',
            'title': '7. Как Вы оцениваете взаимодействие рабочей группы и команды ФЦК?',
            'choices': ['Взаимодействие эффективное – мы понимаем друг друга, у нас впереди много работ и задач',
                        'Взаимодействие неэффективное, мы говорим на разных языках, не понимаем друг друга',
                        'Трудно оценить (эксперты недавно появились на предприятии или я не совсем понимаю, '
                        'что именно происходит)'],
            'good_choices': ['Взаимодействие эффективное – мы понимаем друг друга, у нас впереди много работ и задач'],
            'bad_choices': ['Взаимодействие неэффективное, мы говорим на разных языках, не понимаем друг друга',
                            'Трудно оценить (эксперты недавно появились на предприятии или я не совсем понимаю, '
                            'что именно происходит)'],
            'conclusions': {'good': 'Для {{ good_choice_percentage }}% сотрудников взаимодействие с консультантами эффективно.',
                            'bad': 'Для {{ bad_choice_percentage }}% сотрудников взаимодействие с консультантами неэффективно или пока трудно оценить, так как они появились на предприятии недавно.'},
        },
        'program_priority': {
            'name': 'Приоритет Программы в работе',
            'title': '8. Какой приоритет у Программы повышения производительности труда в Вашей работе?',
            'choices': [
                'Первый (повышение производительности – моя основная функция на текущий момент, '
                'проектные задачи приоритетны)',
                'Второй (сначала мои прямые должностные обязанности, а затем задачи по повышению производительности)',
                'Третий (времени на задачи Программы у меня не хватает)',
                'Ниже третьего (я почти не занимаюсь работой в Программе)'],
            'good_choices': ['Первый (повышение производительности – моя основная функция на текущий момент, '
                             'проектные задачи приоритетны)'],
            'bad_choices': ['Второй (сначала мои прямые должностные обязанности, а затем задачи по повышению '
                            'производительности)', 'Третий (времени на задачи Программы у меня не хватает)',
                            'Ниже третьего (я почти не занимаюсь работой в Программе)'],
            'conclusions': {'good': 'Для {{ good_choice_percentage }}% сотрудников Программа имеет первый приоритет.',
                            'bad': 'Для {{ bad_choice_percentage }}% сотрудников Программа имеет второй приоритет и ниже.'},
        },
        'program_information': {
            'name': 'Информированность о Программе',
            'title': '9. Достаточно ли информации о Программе Вы получаете?',
            'choices': ['Вполне достаточно: я получаю всю необходимую информацию',
                        'Нет, недостаточно: есть еще много того, что мне необходимо знать, чтобы качественно '
                        'выполнять свои задачи по повышению производительности труда',
                        'Нет, недостаточно, но знаю, как и у кого эту информацию можно получить',
                        'Мне не нужна лишняя информация', 'Затрудняюсь ответить'],
            'good_choices': ['Вполне достаточно: я получаю всю необходимую информацию'],
            'bad_choices': ['Нет, недостаточно: есть еще много того, что мне необходимо знать, чтобы качественно '
                            'выполнять свои задачи по повышению производительности труда', 'Нет, недостаточно, но знаю, как и у кого эту информацию можно получить',
                            'Мне не нужна лишняя информация',
                            'Затрудняюсь ответить'],
            'conclusions': {'good': '{{ good_choice_percentage }}% сотрудников считают, что получили всю необходимую информацию.',
                            'bad': '{{ bad_choice_percentage }}% сотрудников не считают, что получили достаточно информации.'},
        },
        'knowledge_application': {
            'name': 'Эффективность обучения',
            'title': '10. Можете ли вы применить знания и инструменты, полученные во время обучения?',
            'choices': ['Могу, самостоятельно', 'Могу, с помощью методических рекомендаций/материалов обучения',
                        'Могу, при помощи Руководителя проекта/эксперта ФЦК', 'Не могу'],
            'good_choices': ['Могу, самостоятельно'],
            'bad_choices': ['Могу, с помощью методических рекомендаций/материалов обучения',
                            'Могу, при помощи Руководителя проекта/эксперта ФЦК', 'Не могу'],
            'conclusions': {'good': '{{ good_choice_percentage }}% сотрудников считают, что смогут применить знания самостоятельно, либо с помощью методических рекомендаций / материалов для обучения.',
                            'bad': '{{ bad_choice_percentage }}% сотрудников считают, что не смогут применить знания самостоятельно.'},
        },
        'program_expectations': {
            'name': 'Ожидания от Программы',
            'title': '11. Что Вы ожидаете для себя по итогам участия в Программе повышения производительности труда?',
            'choices': ['Перспектив карьерного роста', 'Изменения материального вознаграждения',
                        'Профессиональный и личностный рост', 'Получение признания и уважения от коллег и руководства',
                        'Ничего хорошего я не ожидаю, работа по повышению производительности для меня — '
                        'это лишняя нагрузка'],
            'good_choices': ['Перспектив карьерного роста', 'Изменения материального вознаграждения',
                             'Профессиональный и личностный рост', 'Получение признания и уважения от коллег и руководства'],
            'bad_choices': ['Ничего хорошего я не ожидаю, работа по повышению производительности для меня — '
                            'это лишняя нагрузка'],
            'conclusions': {'good': '{{ good_choice_percentage }}% сотрудников ожидают от участия в Программе профессионального и личностного роста.',
                            'bad': '{{ bad_choice_percentage }}% сотрудников не ожидают от участия в Программе профессионального и личностного роста.'},
        },
        'program_obstacles': {
            'name': 'Препятствия',
            'title': '12. Что по Вашему мнению является препятствиями для своевременной реализации Программы?',
            'choices': ['Слишком сжатые сроки внедрения', 'Нехватка времени', 'Бюрократия',
                        'Большой объем информации, ограниченные знания и опыт внедрения производственных систем',
                        'Слабая материально-техническая обеспеченность',
                        'Отсутствие справочных материалов (методичек, инструкций), доступных для сотрудников',
                        'Отсутствие поддержки руководства'],
            'good_choices': [],
            'bad_choices': [],
            'conclusions': {'good': 'Наименее частые препятствия: {{ bottom_choices }}.',
                            'bad': 'Наиболее частые препятствия: {{ top_choices }}.'},
        },
    }
    
    figsize = (4, 4)  # Размер диаграммы
    width_per_char = 0.1  # Примерное значение ширины символа в дюймах
    
    for field, info in questions.items():
        max_width = int(figsize[0] / width_per_char)
        info['title'] = textwrap.fill(info['title'], width=max_width)
    
    charts = {}
    for field, info in questions.items():
        counts = {choice: 0 for choice in info['choices']}
        
        for response in responses:
            if hasattr(response, field):
                counts[getattr(response, field)] += 1
        
        # Создаем график с учетом всех вариантов ответов
        chart, colors = generate_pie_chart(counts, info['title'])
        
        # Расчет доли каждого варианта ответа
        total = sum(counts.values())
        percentages = {choice: (count / total) * 100 if total else 0 for choice, count in counts.items()}
        
        good_choices = info.get('good_choices', [])
        bad_choices = info.get('bad_choices', [])
        
        good_choice_percentage = sum(percentages.get(choice, 0) for choice in good_choices) if good_choices else None
        bad_choice_percentage = 100 - good_choice_percentage if good_choice_percentage is not None else None
        
        # Фильтруем только те варианты ответов, которые были выбраны
        filtered_counts = {choice: count for choice, count in counts.items() if count > 0}
        
        # Формирование выводов с использованием шаблонов строк
        conclusions = info.get('conclusions', {})
        good_conclusion = conclusions.get('good', '')
        bad_conclusion = conclusions.get('bad', '')
        
        if good_choice_percentage is not None:
            good_conclusion = re.sub(r'\{\{ good_choice_percentage \}\}', f'{good_choice_percentage:.0f}',
                                     good_conclusion)
            bad_conclusion = re.sub(r'\{\{ good_choice_percentage \}\}', f'{good_choice_percentage:.0f}',
                                    bad_conclusion)
        
        if bad_choice_percentage is not None:
            good_conclusion = re.sub(r'\{\{ bad_choice_percentage \}\}', f'{bad_choice_percentage:.0f}',
                                     good_conclusion)
            bad_conclusion = re.sub(r'\{\{ bad_choice_percentage \}\}', f'{bad_choice_percentage:.0f}',
                                    bad_conclusion)
        
        # Сортировка вариантов ответов по проценту и выбор первых трех и последних трех
        sorted_choices = sorted(percentages.items(), key=lambda x: x[1], reverse=True)
        top_choices = '; '.join([f'{choice} ({percentage:.0f}%)' for choice, percentage in sorted_choices[:3]])
        bottom_choices = '; '.join([f'{choice} ({percentage:.0f}%)' for choice, percentage in sorted_choices[-3:]])
        
        good_conclusion = re.sub(r'\{\{ top_choices \}\}', top_choices, good_conclusion)
        good_conclusion = re.sub(r'\{\{ bottom_choices \}\}', bottom_choices, good_conclusion)
        
        bad_conclusion = re.sub(r'\{\{ top_choices \}\}', top_choices, bad_conclusion)
        bad_conclusion = re.sub(r'\{\{ bottom_choices \}\}', bottom_choices, bad_conclusion)
        
        charts[field] = {
            'name': info.get('name', field),
            'chart': chart,
            'choices_with_colors': list(zip(info['choices'], colors)),  # Все варианты ответов для легенды
            'filtered_choices_with_colors': list(zip(filtered_counts.keys(), colors)),  # Выбранные варианты ответов
            'percentages': percentages,
            'good_choice_percentage': good_choice_percentage,
            'bad_choice_percentage': bad_choice_percentage,
            'good_choices': good_choices,
            'bad_choices': bad_choices,
            'good_conclusion': good_conclusion,
            'bad_conclusion': bad_conclusion,
            'top_choices': top_choices,
            'bottom_choices': bottom_choices,
        }
    
    return {
        'charts': charts,
        'questions': questions,
        'responses': responses,
        'enterprise': enterprise,
        'responses_count': responses.count(),
        'survey_date': enterprise.survey_date,
        'conclusions': enterprise.conclusions,
        'recommendations': enterprise.recommendations,
    }


@csrf_protect
@login_required
def survey_statistics(request, enterprise_id, mode='default'):
    enterprise = get_object_or_404(Enterprise, id=enterprise_id)
    responses = SurveyResponse.objects.filter(enterprise=enterprise)
    response_count = responses.count()
    
    # Получение кэшированных данных или генерация новых
    context = cache.get_or_set(f'survey_data_{enterprise.id}', lambda: prepare_survey_data(enterprise), timeout=60 * 60)
    
    if request.method == 'POST':
        form = EnterpriseUpdateForm(request.POST, instance=enterprise)
        if form.is_valid():
            # Заменяем символы \n на фактические переносы строк перед сохранением
            form.instance.conclusions = form.cleaned_data['conclusions'].replace('\\n', '\n')
            form.instance.recommendations = form.cleaned_data['recommendations'].replace('\\n', '\n')
            
            form.save()
            cache.delete(f'survey_data_{enterprise.id}')  # Очистка кэша после сохранения
            messages.success(request, 'Данные успешно сохранены.')
            return redirect('statistics', enterprise_id=enterprise.id)
        else:
            messages.error(request, 'Произошла ошибка при сохранении данных.')
    else:
        form = EnterpriseUpdateForm(instance=enterprise)
    
    # Добавляем форму и режим в контекст
    context.update({
        'form': form,
        'mode': mode,
        'enterprise': enterprise,
        'responses': responses,
        'response_count': response_count,
    })
    
    # Рендерим соответствующий шаблон
    template = 'statistics.html' if mode == 'statistics' else 'result_page.html'
    return render(request, template, context)


def fetch_resource(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        raise ValueError(f"Failed to load resource: {url}")


def custom_url_fetcher(url):
    if url.startswith('http') or url.startswith('https'):
        content = fetch_resource(url)
        return {'mime_type': 'image/png', 'file_obj': io.BytesIO(content)}
    elif url.startswith('file://'):
        # Обработка локальных файлов
        file_path = url[7:]  # Убираем префикс 'file://'
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                return {'mime_type': 'application/octet-stream', 'file_obj': io.BytesIO(f.read())}
        else:
            raise ValueError(f"File not found: {file_path}")
    else:
        # Обработка относительных путей
        file_path = os.path.join(settings.STATIC_ROOT, url)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                return {'mime_type': 'application/octet-stream', 'file_obj': io.BytesIO(f.read())}
        else:
            raise ValueError(f"File not found: {file_path}")


def generate_pdf(request, enterprise_id):
    # Получаем объект предприятия
    enterprise = get_object_or_404(Enterprise, id=enterprise_id)
    
    # Подготавливаем данные для опроса
    context = prepare_survey_data(enterprise)
    
    # Обработка POST-запроса, если форма отправлена
    if request.method == 'POST':
        form = EnterpriseUpdateForm(request.POST, instance=enterprise)
        if form.is_valid():
            form.save()
            # Очистка кэша после обновления данных
            cache_key = f'survey_data_{enterprise.id}'
            cache.delete(cache_key)
            context.update({
                'survey_date': enterprise.survey_date,
                'conclusions': enterprise.conclusions,
                'recommendations': enterprise.recommendations,
            })
        else:
            messages.error(request, 'Произошла ошибка при сохранении данных.')
            return redirect('survey_statistics', enterprise_id=enterprise.id)
    
    # Транслитерация названия предприятия
    transliterated_name = translit(enterprise.name, 'ru', reversed=True)
    slugified_name = slugify(transliterated_name)
    
    # Формирование имени файла
    filename = f'statistics_{slugified_name}.pdf'
    
    # Рендеринг HTML
    html_string = render_to_string('generate_pdf.html', context)
    base_url = request.build_absolute_uri('/')
    
    # Генерация PDF
    pdf_file = HTML(string=html_string, base_url=base_url, url_fetcher=custom_url_fetcher).write_pdf(
        stylesheets=[CSS(string='@page { size: A4 landscape; margin: 1cm; }')]
    )
    
    # Возвращаем PDF в браузер
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="{filename}"'
    return response
