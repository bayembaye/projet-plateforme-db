# Generated by Django 5.1.7 on 2025-04-13 21:19

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('theme_preference', models.CharField(choices=[('light', 'Clair'), ('dark', 'Sombre'), ('system', 'Système')], default='system', max_length=10, verbose_name='préférence de thème')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='adresse email')),
                ('role', models.CharField(choices=[('STUDENT', 'Étudiant'), ('PROFESSOR', 'Professeur')], default='STUDENT', max_length=10, verbose_name='rôle')),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='profile_pictures/', verbose_name='photo de profil')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='créé le')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='mis à jour le')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'utilisateur',
                'verbose_name_plural': 'utilisateurs',
            },
        ),
        migrations.CreateModel(
            name='ProfessorProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('faculty_id', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='numéro faculté')),
                ('department', models.CharField(blank=True, max_length=100, verbose_name='département')),
                ('specialization', models.CharField(blank=True, max_length=200, verbose_name='spécialisation')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='professor_profile', to=settings.AUTH_USER_MODEL, verbose_name='utilisateur')),
            ],
            options={
                'verbose_name': 'profil professeur',
                'verbose_name_plural': 'profils professeurs',
            },
        ),
        migrations.CreateModel(
            name='StudentPerformance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True)),
                ('average_score', models.FloatField()),
                ('class_average', models.FloatField()),
                ('improvement_rate', models.FloatField(blank=True, null=True)),
                ('category_breakdown', models.JSONField(default=dict)),
                ('submission_count', models.PositiveIntegerField(default=0)),
                ('late_submissions', models.PositiveIntegerField(default=0)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='performances', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'performance étudiant',
                'verbose_name_plural': 'profils étudiants',
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='StudentProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_id', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='numéro étudiant')),
                ('academic_level', models.CharField(blank=True, max_length=100, verbose_name='niveau académique')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='student_profile', to=settings.AUTH_USER_MODEL, verbose_name='utilisateur')),
            ],
            options={
                'verbose_name': 'profil étudiant',
                'verbose_name_plural': 'profils étudiants',
            },
        ),
    ]
