from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='session_key',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
    ]
