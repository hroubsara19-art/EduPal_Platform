# Generated migration for video upload feature

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0034_test_subjectid'),
    ]

    operations = [
        migrations.AddField(
            model_name='lessoncontent',
            name='video_file',
            field=models.FileField(
                blank=True,
                help_text='فيديو تعليمي مرفوع يدوياً (MP4/WebM/MOV/AVI — بحد أقصى 500MB)',
                null=True,
                upload_to='lesson_videos/',
                validators=[
                    django.core.validators.FileExtensionValidator(['mp4', 'webm', 'mov', 'avi'])
                ]
            ),
        ),
        migrations.AddField(
            model_name='lessoncontent',
            name='video_title',
            field=models.CharField(
                blank=True,
                help_text='عنوان الفيديو التعليمي',
                max_length=200,
                null=True
            ),
        ),
    ]
