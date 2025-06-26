# Generated manually for creating Version model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0018_alter_perspectiveanswer_created_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='Version',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateTimeField(auto_now_add=True)),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('open', 'Open'), ('closed', 'Closed')], default='open', max_length=10)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='versions', to='projects.project')),
            ],
            options={
                'verbose_name': 'Project Version',
                'verbose_name_plural': 'Project Versions',
                'ordering': ['-start_date'],
            },
        ),
    ] 