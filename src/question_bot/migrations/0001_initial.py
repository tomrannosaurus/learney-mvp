# Generated by Django 3.2.2 on 2021-06-24 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AnswerModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=128)),
                ('question_id', models.CharField(max_length=16)),
                ('question_type', models.CharField(max_length=16)),
                ('question_text', models.TextField(max_length=1024)),
                ('answer_type', models.CharField(max_length=16)),
                ('correct_answer', models.TextField(blank=True, default='', max_length=256)),
                ('feedback', models.TextField(max_length=1024)),
                ('time_asked', models.CharField(max_length=32)),
                ('answered', models.BooleanField(default=False)),
                ('answer_given', models.TextField(blank=True, default='', max_length=256)),
                ('correct', models.BooleanField(blank=True, null=True)),
                ('time_answered', models.DateTimeField(auto_now=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='QuestionLastAskedModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=128)),
                ('time_asked', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='SlackBotUserModel',
            fields=[
                ('user_id', models.CharField(max_length=128, primary_key=True, serialize=False)),
                ('num_questions_per_day', models.IntegerField(default=5)),
                ('relative_question_time', models.TimeField()),
                ('timezone', models.CharField(max_length=16)),
                ('utc_time_to_send', models.TimeField()),
                ('on_slack', models.BooleanField()),
                ('slack_user_id', models.CharField(blank=True, default='', max_length=64)),
                ('on_learney', models.BooleanField()),
                ('goal_set', models.BooleanField(default=False)),
                ('active', models.BooleanField(default=True)),
                ('active_since', models.DateField(auto_now=True, null=True)),
                ('signup_date', models.DateField(auto_now_add=True)),
                ('paid', models.BooleanField(default=False)),
            ],
        ),
    ]
