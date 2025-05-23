from django.db import migrations
import uuid

def fix_exercise_uuids(apps, schema_editor):
    Exercise = apps.get_model('exercises', 'Exercise')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Notification = apps.get_model('notifications', 'Notification')
    
    # Correction des UUID des exercices
    for exercise in Exercise.objects.all():
        try:
            uuid.UUID(str(exercise.id))  # Test de validité
        except ValueError:
            # Sauvegarde de l'ancien ID
            old_id = exercise.id
            # Génération d'un nouvel UUID
            exercise.id = uuid.uuid4()
            # Sauvegarde avec force_update pour éviter l'erreur sur le champ id
            exercise.save(force_update=True)
            
            # Correction des notifications liées
            exercise_type = ContentType.objects.get_for_model(Exercise)
            Notification.objects.filter(
                content_type=exercise_type,
                object_id=str(old_id)
            ).update(object_id=str(exercise.id))

class Migration(migrations.Migration):
    dependencies = [
        ('exercises', '0001_initial'),
        ('notifications', '0001_initial'),  # Nécessaire pour les notifications
        ('contenttypes', '__latest__'),    # Nécessaire pour ContentType
    ]

    operations = [
        migrations.RunPython(
            fix_exercise_uuids,
            reverse_code=migrations.RunPython.noop  # Opération irréversible
        ),
    ]