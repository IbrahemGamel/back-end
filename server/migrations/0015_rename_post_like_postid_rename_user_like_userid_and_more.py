# Generated by Django 4.2.13 on 2024-12-14 01:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0014_rename_owner_like_user_rename_owner_post_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='like',
            old_name='post',
            new_name='postid',
        ),
        migrations.RenameField(
            model_name='like',
            old_name='user',
            new_name='userid',
        ),
        migrations.RenameField(
            model_name='post',
            old_name='user',
            new_name='userid',
        ),
    ]
