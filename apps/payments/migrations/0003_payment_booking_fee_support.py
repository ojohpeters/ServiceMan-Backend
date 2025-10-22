# Generated manually for booking fee payment support

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0001_initial'),
        ('payments', '0002_initial'),
    ]

    operations = [
        # Make service_request nullable to support booking fee payments
        # that are created BEFORE a service request exists
        migrations.AlterField(
            model_name='payment',
            name='service_request',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='services.servicerequest'
            ),
        ),
        # Add is_emergency field to track booking type
        migrations.AddField(
            model_name='payment',
            name='is_emergency',
            field=models.BooleanField(
                default=False,
                help_text='Whether this is for an emergency booking'
            ),
        ),
    ]

