import django.db.models.deletion
import licensing.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Upgrades the License and Device models to support:
    - Component-based licensing (JSONField)
    - Auto-generated SMRT-XXXX keys
    - Device revocation, last_validated, port change to 5000
    - License notes field
    - Tier choice labels updated
    """

    dependencies = [
        ('licensing', '0003_remove_installation_client_license_device_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # ── License model upgrades ─────────────────────────────────────
        migrations.AddField(
            model_name='license',
            name='components',
            field=models.JSONField(
                default=list, blank=True,
                help_text='List of component IDs licensed. Leave empty to use tier defaults.'
            ),
        ),
        migrations.AddField(
            model_name='license',
            name='notes',
            field=models.TextField(blank=True, help_text='Internal admin notes'),
        ),
        migrations.AlterField(
            model_name='license',
            name='key',
            field=models.CharField(
                default=licensing.models._generate_key,
                max_length=64, unique=True,
                help_text='License key (e.g. SMRT-XXXX-XXXX-XXXX-XXXX)'
            ),
        ),
        migrations.AlterField(
            model_name='license',
            name='tier',
            field=models.CharField(
                choices=[('LITE', 'Smarty Lite'), ('PRO', 'Smarty Pro'), ('ENTERPRISE', 'Smarty Enterprise')],
                default='LITE', max_length=20
            ),
        ),
        migrations.AlterField(
            model_name='license',
            name='expiry_date',
            field=models.DateTimeField(
                null=True, blank=True,
                help_text='Leave blank for perpetual/lifetime license'
            ),
        ),

        # ── Device model upgrades ──────────────────────────────────────
        migrations.AddField(
            model_name='device',
            name='local_ip',
            field=models.GenericIPAddressField(null=True, blank=True, protocol='both'),
        ),
        migrations.AddField(
            model_name='device',
            name='public_ip',
            field=models.GenericIPAddressField(null=True, blank=True, protocol='both'),
        ),
        migrations.AddField(
            model_name='device',
            name='port',
            field=models.IntegerField(default=5000),
        ),
        migrations.AddField(
            model_name='device',
            name='version',
            field=models.CharField(max_length=50, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='device',
            name='last_validated',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='device',
            name='is_revoked',
            field=models.BooleanField(default=False, help_text='Revoke to force re-activation'),
        ),
        migrations.AlterField(
            model_name='device',
            name='name',
            field=models.CharField(max_length=255, default='Smarty Installation'),
        ),
        migrations.AlterUniqueTogether(
            name='device',
            unique_together={('license', 'hardware_id')},
        ),
    ]
