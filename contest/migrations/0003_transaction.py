# Generated by Django 2.2.3 on 2019-08-28 17:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0002_auto_20190823_0331'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField()),
                ('reason', models.CharField(choices=[('PR', 'Problem Request'), ('PS', 'Problem Solving'), ('DL', 'Duel'), ('MF', 'Mafia')], max_length=1)),
                ('decreased_from', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='decreases', related_query_name='decrease', to='contest.Team')),
                ('increased_to', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='increases', related_query_name='increase', to='contest.Team')),
            ],
        ),
    ]
