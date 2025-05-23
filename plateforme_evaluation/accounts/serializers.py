# accounts/serializers.py

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, StudentProfile, ProfessorProfile


class StudentProfileSerializer(serializers.ModelSerializer):
    """Sérialiseur pour le profil étudiant."""
    
    class Meta:
        model = StudentProfile
        fields = ['student_id', 'academic_level']


class ProfessorProfileSerializer(serializers.ModelSerializer):
    """Sérialiseur pour le profil professeur."""
    
    class Meta:
        model = ProfessorProfile
        fields = ['faculty_id', 'department', 'specialization']


class UserSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les informations de l'utilisateur."""
    
    student_profile = StudentProfileSerializer(read_only=True)
    professor_profile = ProfessorProfileSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name', 
            'role', 'profile_picture', 'is_active', 'date_joined',
            'student_profile', 'professor_profile'
        ]
        read_only_fields = ['id', 'date_joined', 'is_active']
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class UserCreateSerializer(serializers.ModelSerializer):
    """Sérialiseur pour la création d'utilisateur."""
    
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['email', 'password', 'password2', 'first_name', 'last_name', 'role']
    
    def validate(self, attrs):
        """Valide que les deux mots de passe correspondent."""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})
        return attrs
    
    def create(self, validated_data):
        """Crée un nouvel utilisateur avec le mot de passe encrypté."""
        # Supprime password2 car il n'est pas nécessaire pour la création
        validated_data.pop('password2')
        
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=validated_data.get('role', User.Role.STUDENT)
        )
        
        return user


class PasswordChangeSerializer(serializers.Serializer):
    """Sérialiseur pour le changement de mot de passe."""
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Le mot de passe actuel est incorrect.")
        return value


class StudentProfileUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    profile_picture = serializers.ImageField(source='user.profile_picture', required=False)

    class Meta:
        model = StudentProfile
        fields = ['first_name', 'last_name', 'student_id', 'academic_level', 'profile_picture']
    
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        
        # Mise à jour de l'utilisateur
        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()
        
        # Mise à jour du profil étudiant
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance


class ProfessorProfileUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    profile_picture = serializers.ImageField(source='user.profile_picture', required=False)

    class Meta:
        model = ProfessorProfile
        fields = ['first_name', 'last_name', 'faculty_id', 'department', 'specialization', 'profile_picture']
    
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        
        # Mise à jour de l'utilisateur
        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()
        
        # Mise à jour du profil professeur
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance
    

class ThemePreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['theme_preference']

    def update(self, instance, validated_data):
        instance.theme_preference = validated_data.get('theme_preference', instance.theme_preference)
        instance.save()
        return instance    