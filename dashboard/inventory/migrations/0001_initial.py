# Generated by Django 2.1.5 on 2019-01-13 11:16

import dashboard.core.abstract_models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Camera',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Date created')),
                ('date_updated', models.DateTimeField(auto_now=True, verbose_name='Date updated')),
                ('name', dashboard.core.abstract_models.EntityNameField(db_index=True, max_length=80, unique=True, verbose_name='Camera Name')),
                ('description', dashboard.core.abstract_models.DescrField(blank=True, max_length=1024, null=True, verbose_name='Description')),
                ('state', models.PositiveSmallIntegerField(choices=[(0, 'Disabled'), (1, 'Enabled')], default=1, verbose_name='State')),
                ('address', models.URLField(help_text='IP address or FQDN', verbose_name='Address')),
                ('user_name', models.CharField(blank=True, max_length=30, null=True, verbose_name='User Name')),
                ('password', models.CharField(blank=True, max_length=30, null=True, verbose_name='Password')),
            ],
            options={
                'verbose_name': 'Camera',
                'verbose_name_plural': 'Cameras',
                'ordering': ['name'],
            },
            bases=(dashboard.core.abstract_models.ObjectIdentityNameMixin, models.Model),
        ),
        migrations.CreateModel(
            name='RecorderArguments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Date created')),
                ('date_updated', models.DateTimeField(auto_now=True, verbose_name='Date updated')),
                ('order_no', models.PositiveSmallIntegerField(verbose_name='Order Number')),
                ('argument', models.CharField(max_length=127, verbose_name='Argument')),
                ('is_template', models.BooleanField(default=False, help_text='True if argument is a template (django)', verbose_name='Is Template')),
            ],
            options={
                'verbose_name': 'RecorderArgument',
                'verbose_name_plural': 'RecorderArguments',
                'ordering': ['recorder_profile', 'order_no'],
            },
            bases=(dashboard.core.abstract_models.ObjectIdentityWeakMixin, models.Model),
        ),
        migrations.CreateModel(
            name='RecorderProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Date created')),
                ('date_updated', models.DateTimeField(auto_now=True, verbose_name='Date updated')),
                ('name', dashboard.core.abstract_models.EntityNameField(db_index=True, max_length=80, unique=True, verbose_name='Recorder Profile')),
                ('description', dashboard.core.abstract_models.DescrField(blank=True, max_length=1024, null=True, verbose_name='Description')),
                ('method', models.PositiveSmallIntegerField(choices=[(1, 'VideoLAN'), (2, 'VideoLAN Snapshot'), (3, 'HTTP Get')], verbose_name='Method')),
                ('interval', models.PositiveSmallIntegerField(default=0, help_text='Record interval (in seconds). Means interval between snapshots or video record piece length', validators=[django.core.validators.MaxValueValidator(3600)], verbose_name='Record interval')),
                ('filename_template', models.CharField(help_text='Record filename template (django)', max_length=255, verbose_name='Filename template')),
                ('url_template', models.CharField(help_text='URL template (django)', max_length=255, verbose_name='URL template')),
                ('recycle_timeout', models.PositiveSmallIntegerField(default=0, help_text='Record recycle timeout (in hours).', verbose_name='Record recycle timeout')),
            ],
            options={
                'verbose_name': 'RecorderProfile',
                'verbose_name_plural': 'RecorderProfiles',
                'ordering': ['name'],
            },
            bases=(dashboard.core.abstract_models.ObjectIdentityNameMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Date created')),
                ('date_updated', models.DateTimeField(auto_now=True, verbose_name='Date updated')),
                ('name', dashboard.core.abstract_models.EntityNameField(db_index=True, max_length=80, unique=True, verbose_name='Schedule Name')),
                ('description', dashboard.core.abstract_models.DescrField(blank=True, max_length=1024, null=True, verbose_name='Description')),
            ],
            options={
                'verbose_name': 'Schedule',
                'verbose_name_plural': 'Schedules',
                'ordering': ['name'],
            },
            bases=(dashboard.core.abstract_models.ObjectIdentityNameMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ScheduleIntervals',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Date created')),
                ('date_updated', models.DateTimeField(auto_now=True, verbose_name='Date updated')),
                ('start_time', models.TimeField(verbose_name='Start Time')),
                ('end_time', models.TimeField(verbose_name='End Time')),
                ('week_days', models.PositiveSmallIntegerField(default=255, validators=[django.core.validators.MaxValueValidator(127)], verbose_name='Days of week Bitmask')),
                ('schedule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='intervals', to='inventory.Schedule', verbose_name='Schedule')),
            ],
            options={
                'verbose_name': 'Schedule Interval',
                'verbose_name_plural': 'Schedule Intervals',
                'ordering': ['start_time', 'end_time'],
            },
            bases=(dashboard.core.abstract_models.ObjectIdentityWeakMixin, models.Model),
        ),
        migrations.AddField(
            model_name='recorderarguments',
            name='recorder_profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='arguments', to='inventory.RecorderProfile', verbose_name='Recorder Profile'),
        ),
        migrations.AddField(
            model_name='camera',
            name='recorder_profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cameras', to='inventory.RecorderProfile', verbose_name='Recorder Profile'),
        ),
        migrations.AddField(
            model_name='camera',
            name='recorder_profile2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='cameras2', to='inventory.RecorderProfile', verbose_name='Recorder Profile (secondary)'),
        ),
        migrations.AddField(
            model_name='camera',
            name='schedule',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cameras', to='inventory.Schedule', verbose_name='Schedule'),
        ),
        migrations.AlterUniqueTogether(
            name='scheduleintervals',
            unique_together={('schedule', 'start_time', 'end_time')},
        ),
        migrations.AlterUniqueTogether(
            name='recorderarguments',
            unique_together={('recorder_profile', 'order_no')},
        ),
    ]
