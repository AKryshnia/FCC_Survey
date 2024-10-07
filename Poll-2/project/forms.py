from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Enterprise


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = 'Введите до 150 символов без пробелов, только буквы, цифры и @/./+/-/_'
        self.fields['password1'].help_text = (
            'Ваш пароль не должен быть слишком похож на другую вашу личную информацию.<br>'
            'Ваш пароль должен содержать не менее 8 символов.<br>'
            'Ваш пароль не может быть широко используемым паролем.<br>'
            'Ваш пароль не может быть полностью числовым.'
        )
        self.fields['password2'].help_text = 'Введите тот же пароль, что и раньше, для подтверждения.'


class EnterpriseForm(forms.ModelForm):
    class Meta:
        model = Enterprise
        fields = ['name', 'employees']
        labels = {
            'name': 'Название',
            'employees': 'Количество сотрудников',
        }


class SurveyForm(forms.Form):
    enterprise = forms.ModelChoiceField(queryset=Enterprise.objects.all(), widget=forms.HiddenInput(), required=True)
    POSITION_LEVEL_CHOICES = [
        ('Мастер / бригадир', 'Мастер / бригадир'),
        ('Начальник отдела', 'Начальник отдела'),
        ('Руководитель высшего уровня', 'Руководитель высшего уровня'),
        ('Руководитель дирекции / департамента / управления', 'Руководитель дирекции / департамента / управления'),
        ('Секретарь / Помощник руководителя', 'Секретарь / Помощник руководителя'),
        ('Специалист', 'Специалист'),
    ]
    position_level = forms.ChoiceField(choices=POSITION_LEVEL_CHOICES, widget=forms.RadioSelect, required=True)
    
    PROGRAM_GOAL_UNDERSTANDING_CHOICES = [
        ('Да', 'Да'),
        ('Нет', 'Нет'),
    ]
    program_goal_understanding = forms.ChoiceField(choices=PROGRAM_GOAL_UNDERSTANDING_CHOICES,
                                                   widget=forms.RadioSelect, required=True)
    
    ROLE_UNDERSTANDING_CHOICES = [
        ('Да, я понимаю, что мне необходимо будет сделать', 'Да, я понимаю, что мне необходимо будет сделать'),
        ('Нет, мне не понятны мои задачи', 'Нет, мне не понятны мои задачи'),
    ]
    role_understanding = forms.ChoiceField(choices=ROLE_UNDERSTANDING_CHOICES, widget=forms.RadioSelect, required=True)
    
    SUPERVISOR_SUPPORT_CHOICES = [
        ('Да, мой руководитель объяснил мне мою роль в Программе и создал условия для моего участия',
         'Да, мой руководитель объяснил мне мою роль в Программе и создал условия для моего участия'),
        ('Да, мой руководитель объяснил мне мою роль в Программе, но не создал условия для моего участия',
         'Да, мой руководитель объяснил мне мою роль в Программе, но не создал условия для моего участия'),
        (
            'Нет, мой руководитель не объяснил мне мою роль в Программе, и он против того, чтобы я отвлекался от своих '
            'регулярных задач',
            'Нет, мой руководитель не объяснил мне мою роль в Программе, и он против того, чтобы я отвлекался от своих '
            'регулярных задач'),
    ]
    supervisor_support = forms.ChoiceField(choices=SUPERVISOR_SUPPORT_CHOICES, widget=forms.RadioSelect, required=True)
    
    PROGRAM_ENCOURAGEMENT_CHOICES = [
        ('Да, согласен', 'Да, согласен'),
        ('Нет, не согласен', 'Нет, не согласен'),
    ]
    program_encouragement = forms.ChoiceField(choices=PROGRAM_ENCOURAGEMENT_CHOICES, widget=forms.RadioSelect,
                                              required=True)
    
    PROGRAM_IMPACT_CHOICES = [
        ('Да, согласен', 'Да, согласен'),
        ('Нет, не согласен', 'Нет, не согласен'),
    ]
    program_impact = forms.ChoiceField(choices=PROGRAM_IMPACT_CHOICES, widget=forms.RadioSelect, required=True)
    
    INTERACTION_ASSESSMENT_CHOICES = [
        ('Взаимодействие эффективное – мы понимаем друг друга, у нас впереди много работ и задач',
         'Взаимодействие эффективное – мы понимаем друг друга, у нас впереди много работ и задач'),
        ('Взаимодействие неэффективное, мы говорим на разных языках, не понимаем друг друга',
         'Взаимодействие неэффективное, мы говорим на разных языках, не понимаем друг друга'),
        (
            'Трудно оценить (эксперты недавно появились на предприятии или я не совсем понимаю, что именно происходит)',
            'Трудно оценить (эксперты недавно появились на предприятии или я не совсем понимаю, что именно происходит)'),
    ]
    interaction_assessment = forms.ChoiceField(choices=INTERACTION_ASSESSMENT_CHOICES, widget=forms.RadioSelect,
                                               required=True)
    
    PROGRAM_PRIORITY_CHOICES = [
        ('Первый (повышение производительности – моя основная функция на текущий момент, проектные задачи приоритетны)',
         'Первый (повышение производительности – моя основная функция на текущий момент, проектные задачи приоритетны)'),
        ('Второй (сначала мои прямые должностные обязанности, а затем задачи по повышению производительности)',
         'Второй (сначала мои прямые должностные обязанности, а затем задачи по повышению производительности)'),
        ('Третий (времени на задачи Программы у меня не хватает)', 'Третий (времени на задачи Программы у меня не '
                                                                   'хватает)'),
        ('Ниже третьего (я почти не занимаюсь работой в Программе)', 'Ниже третьего (я почти не занимаюсь работой в '
                                                                     'Программе)'),
    ]
    program_priority = forms.ChoiceField(choices=PROGRAM_PRIORITY_CHOICES, widget=forms.RadioSelect, required=True)
    
    PROGRAM_INFORMATION_CHOICES = [
        ('Вполне достаточно: я получаю всю необходимую информацию', 'Вполне достаточно: я получаю всю необходимую '
                                                                    'информацию'),
        ('Нет, недостаточно: есть еще много того, что мне необходимо знать, чтобы качественно выполнять свои задачи '
         'по повышению производительности труда', 'Нет, недостаточно: есть еще много того, что мне необходимо знать, '
                                                  'чтобы качественно выполнять свои задачи по повышению '
                                                  'производительности труда'),
        ('Нет, недостаточно, но знаю, как и у кого эту информацию можно получить', 'Нет, недостаточно, но знаю, как и '
                                                                                   'у кого эту информацию можно '
                                                                                   'получить'),
        ('Мне не нужна лишняя информация', 'Мне не нужна лишняя информация'),
        ('Затрудняюсь ответить', 'Затрудняюсь ответить'),
    ]
    program_information = forms.ChoiceField(choices=PROGRAM_INFORMATION_CHOICES, widget=forms.RadioSelect,
                                            required=True)
    
    KNOWLEDGE_APPLICATION_CHOICES = [
        ('Могу, самостоятельно', 'Могу, самостоятельно'),
        ('Могу, с помощью методических рекомендаций/материалов обучения', 'Могу, с помощью методических '
                                                                          'рекомендаций/материалов обучения'),
        ('Могу, при помощи Руководителя проекта/эксперта ФЦК', 'Могу, при помощи Руководителя проекта/эксперта ФЦК'),
        ('Не могу', 'Не могу'),
    ]
    knowledge_application = forms.ChoiceField(choices=KNOWLEDGE_APPLICATION_CHOICES, widget=forms.RadioSelect,
                                              required=True)
    
    PROGRAM_EXPECTATIONS_CHOICES = [
        ('Перспектив карьерного роста', 'Перспектив карьерного роста'),
        ('Изменения материального вознаграждения', 'Изменения материального вознаграждения'),
        ('Профессиональный и личностный рост', 'Профессиональный и личностный рост'),
        ('Получение признания и уважения от коллег и руководства',
         'Получение признания и уважения от коллег и руководства'),
        ('Ничего хорошего я не ожидаю, работа по повышению производительности для меня — это лишняя нагрузка',
         'Ничего хорошего я не ожидаю, работа по повышению производительности для меня — это лишняя нагрузка'),
    ]
    program_expectations = forms.ChoiceField(choices=PROGRAM_EXPECTATIONS_CHOICES, widget=forms.RadioSelect,
                                             required=True)
    
    PROGRAM_OBSTACLES_CHOICES = [
        ('Слишком сжатые сроки внедрения', 'Слишком сжатые сроки внедрения'),
        ('Нехватка времени', 'Нехватка времени'),
        ('Бюрократия', 'Бюрократия'),
        ('Большой объем информации, ограниченные знания и опыт внедрения производственных систем',
         'Большой объем информации, ограниченные знания и опыт внедрения производственных систем'),
        ('Слабая материально-техническая обеспеченность', 'Слабая материально-техническая обеспеченность'),
        ('Отсутствие справочных материалов (методичек, инструкций), доступных для сотрудников',
         'Отсутствие справочных материалов (методичек, инструкций), доступных для сотрудников'),
        ('Отсутствие поддержки руководства', 'Отсутствие поддержки руководства'),
    ]
    program_obstacles = forms.ChoiceField(choices=PROGRAM_OBSTACLES_CHOICES, widget=forms.RadioSelect, required=True)
    additional_comments = forms.CharField(widget=forms.Textarea, required=False, label="Дополнительные комментарии")
  

class EnterpriseUpdateForm(forms.ModelForm):
    class Meta:
        model = Enterprise
        fields = ['survey_date', 'conclusions', 'recommendations']
        widgets = {
            'survey_date': forms.DateInput(attrs={'type': 'date'}),
            'conclusions': forms.Textarea(attrs={'rows': 5}),
            'recommendations': forms.Textarea(attrs={'rows': 5}),
        }
        labels = {
            'survey_date': 'Дата проведения опроса',
            'conclusions': 'Выводы',
            'recommendations': 'План корректирующих мероприятий',
        }
