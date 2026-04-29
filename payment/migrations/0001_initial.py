from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('licensing', '0004_device_local_ip_device_port_device_public_ip_and_more'),
    ]

    # Note: user FK dependency resolved dynamically via settings.AUTH_USER_MODEL
    # Run: python manage.py migrate payment

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id',            models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference',     models.CharField(max_length=64, unique=True, editable=False)),
                ('email',         models.EmailField()),
                ('plan',          models.CharField(max_length=20, choices=[('LITE','Smarty Lite'),('PRO','Smarty Pro'),('ENTERPRISE','Smarty Enterprise')])),
                ('usd_amount',    models.DecimalField(max_digits=10, decimal_places=2)),
                ('ghs_amount',    models.DecimalField(max_digits=12, decimal_places=2)),
                ('ghs_pesewas',   models.BigIntegerField()),
                ('exchange_rate', models.DecimalField(max_digits=10, decimal_places=4)),
                ('paystack_id',   models.CharField(max_length=128, blank=True, null=True)),
                ('status',        models.CharField(max_length=20, default='PENDING',
                                                   choices=[('PENDING','Pending'),('PAID','Paid'),('FAILED','Failed / Cancelled'),('REFUNDED','Refunded')])),
                ('created_at',    models.DateTimeField(auto_now_add=True)),
                ('paid_at',       models.DateTimeField(null=True, blank=True)),
            ],
            options={'ordering': ['-created_at'], 'verbose_name': 'Order'},
        ),
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(
                to='users.User',
                on_delete=django.db.models.deletion.SET_NULL,
                null=True, blank=True,
                related_name='orders',
            ),
        ),
        migrations.AddField(
            model_name='order',
            name='license',
            field=models.OneToOneField(
                to='licensing.License',
                on_delete=django.db.models.deletion.SET_NULL,
                null=True, blank=True,
                related_name='order',
            ),
        ),
    ]
