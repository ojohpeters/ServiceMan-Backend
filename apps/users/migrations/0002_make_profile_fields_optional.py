# Generated manually to fix IntegrityError

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientprofile',
            name='address',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='clientprofile',
            name='phone_number',
            field=models.CharField(blank=True, default='', max_length=20),
        ),
        migrations.AlterField(
            model_name='servicemanprofile',
            name='phone_number',
            field=models.CharField(blank=True, default='', max_length=20),
        ),
    ]
