import re

from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User


class SurveyResponse(models.Model):
    enterprise = models.ForeignKey('Enterprise', on_delete=models.CASCADE)
    position_level = models.CharField(max_length=255)
    program_goal_understanding = models.CharField(max_length=255)
    role_understanding = models.CharField(max_length=255)
    supervisor_support = models.CharField(max_length=255)
    program_encouragement = models.CharField(max_length=255)
    program_impact = models.CharField(max_length=255)
    interaction_assessment = models.CharField(max_length=255)
    program_priority = models.CharField(max_length=255)
    program_information = models.CharField(max_length=255)
    knowledge_application = models.CharField(max_length=255)
    program_expectations = models.CharField(max_length=255)
    program_obstacles = models.CharField(max_length=255)
    additional_comments = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Poll Response #{self.id}"


class Enterprise(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=4096)
    employees = models.PositiveIntegerField()
    slug = models.SlugField(unique=True, blank=True, null=True)
    conclusions = models.TextField(blank=True, null=True)
    recommendations = models.TextField(blank=True, null=True)
    survey_date = models.DateField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug(self.clean_name(self.name))
        super().save(*args, **kwargs)
    
    def clean_name(self, name):
        # Удаляем кавычки и другие специальные символы, оставляя только буквы, цифры, пробелы и дефисы
        cleaned_name = re.sub(r'[^a-zA-Zа-яА-Я0-9\s]', '', name)
        return cleaned_name
    
    def generate_unique_slug(self, name):
        slug = slugify(name)
        unique_slug = slug
        num = 1
        while Enterprise.objects.filter(slug=unique_slug).exists():
            unique_slug = f"{slug}-{num}"
            num += 1
        return unique_slug
    
    def __str__(self):
        return self.name
    