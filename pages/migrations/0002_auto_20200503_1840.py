# Generated by Django 3.0 on 2020-05-03 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='labreport',
            name='methods_intro',
            field=models.TextField(default='Enter a long description of the experiment', verbose_name='-verbose'),
        ),
    ]
