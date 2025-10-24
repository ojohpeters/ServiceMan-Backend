# Generated manually for skills management system

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_servicemanprofile_approval_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('category', models.CharField(choices=[('TECHNICAL', 'Technical'), ('MANUAL', 'Manual Labor'), ('CREATIVE', 'Creative'), ('PROFESSIONAL', 'Professional Services'), ('OTHER', 'Other')], default='OTHER', max_length=20)),
                ('description', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['category', 'name'],
            },
        ),
        migrations.AddIndex(
            model_name='skill',
            index=models.Index(fields=['category', 'is_active'], name='users_skill_cat_active_idx'),
        ),
        migrations.AddIndex(
            model_name='skill',
            index=models.Index(fields=['name'], name='users_skill_name_idx'),
        ),
    ]

