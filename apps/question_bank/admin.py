from django.contrib import admin
from .models import QuestionBank, QuestionBankChoice


class QuestionBankChoiceInline(admin.TabularInline):
    model = QuestionBankChoice
    extra = 4
    fields = ['choice_text', 'is_correct', 'order']


@admin.register(QuestionBank)
class QuestionBankAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'question_type', 'difficulty', 'marks', 'created_by', 'is_active']
    list_filter = ['question_type', 'difficulty', 'is_active']
    search_fields = ['question_text', 'tags', 'created_by__username']
    inlines = [QuestionBankChoiceInline]
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Question Information', {
            'fields': ('question_text', 'question_type', 'difficulty', 'marks')
        }),
        ('Categorization', {
            'fields': ('tags',)
        }),
        ('Additional Information', {
            'fields': ('explanation', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if hasattr(request.user, 'role') and request.user.role == 'teacher':
            return qs.filter(created_by=request.user)
        return qs


@admin.register(QuestionBankChoice)
class QuestionBankChoiceAdmin(admin.ModelAdmin):
    list_display = ['question', 'choice_text', 'is_correct', 'order']
    list_filter = ['is_correct']
    search_fields = ['choice_text', 'question__question_text']
