# Generated by Django 4.2.13 on 2024-12-14 01:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0011_rename_id_post_postid_rename_id_user_userid_like'),
    ]

    operations = [
        migrations.RenameField(
            model_name='like',
            old_name='likeID',
            new_name='id',
        ),
        migrations.RenameField(
            model_name='post',
            old_name='postID',
            new_name='id',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='userID',
            new_name='id',
        ),
    ]
