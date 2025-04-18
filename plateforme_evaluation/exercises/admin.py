from django.contrib import admin
from .models import Category, Exercise, ExerciseFile, Solution, ExerciseGroup

class ExerciseFileInline(admin.TabularInline):
    model = ExerciseFile
    extra = 1

class SolutionInline(admin.TabularInline):
    model = Solution
    extra = 1

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'professor', 'difficulty_level', 'is_active')
    list_filter = ('category', 'difficulty_level', 'is_active')
    search_fields = ('title', 'description')
    inlines = [ExerciseFileInline, SolutionInline]
    readonly_fields = ('deadline',)  # Empêche l'édition manuelle
    list_display = ('title', 'time_limit', 'formatted_deadline')
    
    def formatted_deadline(self, obj):
        return obj.deadline.strftime("%d/%m/%Y %H:%M") if obj.deadline else "-"
    formatted_deadline.short_description = "Deadline Calculé"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name', 'description')

@admin.register(ExerciseGroup)
class ExerciseGroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'professor', 'start_date', 'end_date', 'is_active')
    filter_horizontal = ('exercises',)
    list_filter = ('is_active', 'professor')
    search_fields = ('title', 'description')

@admin.register(ExerciseFile)
class ExerciseFileAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'exercise', 'file_type', 'is_statement')
    list_filter = ('file_type', 'is_statement')
    search_fields = ('file_name', 'exercise__title')

@admin.register(Solution)
class SolutionAdmin(admin.ModelAdmin):
    list_display = ('exercise', 'created_at', 'updated_at')
    search_fields = ('exercise__title', 'description')