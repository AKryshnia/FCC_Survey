from django.contrib import admin
from .models import SurveyResponse, Enterprise
from .forms import SurveyForm
import csv
from django.http import HttpResponse


class SurveyResponseAdmin(admin.ModelAdmin):
    model = SurveyResponse
    list_display = (
        'id', 'enterprise', 'position_level', 'program_goal_understanding', 'role_understanding', 'supervisor_support',
        'program_encouragement', 'program_impact', 'interaction_assessment', 'program_priority',
        'program_information', 'knowledge_application', 'program_expectations', 'program_obstacles',
        'additional_comments',
    )
    list_filter = (
        'enterprise', 'position_level', 'program_goal_understanding', 'role_understanding', 'supervisor_support',
        'program_encouragement', 'program_impact', 'interaction_assessment', 'program_priority',
        'program_information', 'knowledge_application', 'program_expectations', 'program_obstacles',
    )
    search_fields = (
        'enterprise__name', 'position_level', 'program_goal_understanding', 'role_understanding', 'supervisor_support',
        'program_encouragement', 'program_impact', 'interaction_assessment', 'program_priority',
        'program_information', 'knowledge_application', 'program_expectations', 'program_obstacles',
        'additional_comments',
    )
    # readonly_fields = ('enterprise', 'position_level')
    actions = ['export_as_csv']
    
    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="survey_responses.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Enterprise', 'Position Level', 'Program Goal Understanding', 'Additional Comments'])
        for obj in queryset:
            writer.writerow(
                [obj.id, obj.enterprise, obj.position_level, obj.program_goal_understanding, obj.additional_comments])
        return response
    
    export_as_csv.short_description = "Экспортировать в CSV"
    
    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name in SurveyForm.base_fields and hasattr(SurveyForm.base_fields[db_field.name], 'choices'):
            kwargs['choices'] = SurveyForm.base_fields[db_field.name].choices
        return super().formfield_for_choice_field(db_field, request, **kwargs)


actions = ['mark_as_reviewed']


def mark_as_reviewed(self, request, queryset):
    updated = queryset.update(reviewed=True)  # Устанавливаем поле reviewed как True
    self.message_user(request, f"{updated} записей были отмечены как проверенные.")


mark_as_reviewed.short_description = "Отметить как проверенные"


class SurveyResponseInline(admin.TabularInline):
    model = SurveyResponse
    extra = 0


class EnterpriseAdmin(admin.ModelAdmin):
    model = Enterprise
    list_display = ('name', 'employees', 'num_responses')
    list_filter = ('name', 'employees')
    search_fields = ('name', 'employees')
    inlines = [SurveyResponseInline]  # Отображение ответов на опросы для предприятия
    
    def num_responses(self, obj):
        return obj.surveyresponse_set.count()
    
    num_responses.short_description = 'Количество ответов'
    
    def employees(self, obj):
        return obj.employees
    
    employees.short_description = 'Количество сотрудников'


admin.site.register(SurveyResponse, SurveyResponseAdmin)
admin.site.register(Enterprise, EnterpriseAdmin)
