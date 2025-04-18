from django.db import migrations
import uuid

def fix_uuids(apps, schema_editor):
    Submission = apps.get_model('submissions', 'Submission')
    for sub in Submission.objects.all():
        try:
            uuid.UUID(str(sub.id))  # Vérifie que l'UUID est valide
        except ValueError:
            sub.id = uuid.uuid4()
            sub.save()

class Migration(migrations.Migration):
    dependencies = [
        ('submissions', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(fix_uuids),
    ]