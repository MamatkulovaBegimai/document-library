from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0002_document_uploaded_by'),
    ]

    operations = [
        migrations.CreateModel(
            name='Teacher',
            fields=[],
            options={
                'verbose_name': 'Преподаватель',
                'verbose_name_plural': 'Преподаватели',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('auth.user',),
        ),
    ]
