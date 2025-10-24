# Generated manually for serviceman-skills relationship

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_skill_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicemanprofile',
            name='skills',
            field=models.ManyToManyField(blank=True, related_name='servicemen', to='users.skill'),
        ),
    ]

