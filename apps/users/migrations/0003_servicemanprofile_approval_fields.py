# Generated manually for serviceman approval system

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_make_profile_fields_optional'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicemanprofile',
            name='is_approved',
            field=models.BooleanField(
                default=False,
                help_text='Admin approval status for serviceman application'
            ),
        ),
        migrations.AddField(
            model_name='servicemanprofile',
            name='approved_by',
            field=models.ForeignKey(
                blank=True,
                help_text='Admin who approved this serviceman',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='approved_servicemen',
                to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name='servicemanprofile',
            name='approved_at',
            field=models.DateTimeField(
                blank=True,
                help_text='When the serviceman was approved',
                null=True
            ),
        ),
        migrations.AddField(
            model_name='servicemanprofile',
            name='rejection_reason',
            field=models.TextField(
                blank=True,
                help_text='Reason for rejection (if applicable)'
            ),
        ),
        # Add index for performance
        migrations.AddIndex(
            model_name='servicemanprofile',
            index=models.Index(fields=['is_approved', 'created_at'], name='users_servi_is_appr_idx'),
        ),
    ]

