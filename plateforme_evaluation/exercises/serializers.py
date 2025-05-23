from rest_framework import serializers
from .models import Exercise, ExerciseFile, Solution, ExerciseGroup, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ExerciseFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExerciseFile
        fields = '__all__'
        read_only_fields = ('uploaded_at',)

class SolutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Solution
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class ExerciseSerializer(serializers.ModelSerializer):
    files = ExerciseFileSerializer(many=True, read_only=True)
    solutions = SolutionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Exercise
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'professor')

class ExerciseGroupSerializer(serializers.ModelSerializer):
    exercises = ExerciseSerializer(many=True, read_only=True)
    
    class Meta:
        model = ExerciseGroup
        fields = '__all__'
        read_only_fields = ('created_at', 'professor')