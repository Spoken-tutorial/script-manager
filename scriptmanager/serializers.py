
from rest_framework import serializers
from .models import Script, ScriptDetail, Comment
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, date, timedelta


class ScriptDetailSerializer(serializers.ModelSerializer):
  class Meta:
    model = ScriptDetail
    fields = ('id', 'cue', 'narration', 'order', 'comment_status', 'script')




class ScriptSerializer(serializers.ModelSerializer):
  slides = serializers.SerializerMethodField()
  versions = serializers.SerializerMethodField()

  # def __init__(self, *args, **kwargs):
  #   remove_fields = kwargs.pop('remove_fields', None)
  #   super(ScriptSerializer, self).__init__(*args, **kwargs)

  #   if remove_fields:
  #       # for multiple fields in a list
  #       for field_name in remove_fields:
  #           self.fields.pop(field_name)

  class Meta:
    model = Script
    fields = ('id', 'slides', 'status', 'tutorial', 'language', 'suggested_title', 'versionNo', 'versions', 'editable')

  def get_slides(self, instance):
    slides = []
    row = ScriptDetail.objects.get(script=instance, prevRow=None)
    slides.append(row)
    while row.nextRow:
      row = ScriptDetail.objects.get(pk=row.nextRow)
      slides.append(row)

    # slides = ScriptDetail.objects.filter(script=instance)
    # ordering = instance.ordering
    # if (len(ordering) != 0):
    #   ordering = ordering.split(',')
    #   ordering = list(map(int, ordering))
    #   slides = sorted(slides, key=lambda s: ordering.index(s.pk))

    return ScriptDetailSerializer(slides, many=True).data

  def get_versions(self, instance):
    versions = []
    scripts = Script.objects.filter(tutorial=instance.tutorial, language=instance.language).order_by('-versionNo')
    for scr in scripts:
      versions.append(scr.versionNo)
    return versions

class CommentSerializer(serializers.ModelSerializer):
  user = serializers.CharField()
  time = serializers.SerializerMethodField()

  class Meta:
    model = Comment
    fields = ('id', 'comment', 'user', 'script_details', 'time', 'done', 'resolved')

  def get_time(self, instance):
    time = datetime.now()
    created = instance.created
    if created.day == time.day and created.month == time.month and created.year == time.year and created.hour == time.hour:
      return str(time.minute - created.minute) + " minute(s) ago"
    elif created.day == time.day and created.month == time.month and created.year == time.year:
      return str(time.hour - created.hour) + " hour(s) ago"
    elif created.month == time.month and created.year == time.year:
      return str(time.day - created.day) + " day(s) ago"
    elif created.year == time.year:
      return str(time.month - created.month) + " month(s) ago"
    return date(day=created.day, month=created.month, year=created.year).strftime('%d %B %Y')


class ReversionSerializer(serializers.Serializer):
  reversion_id = serializers.IntegerField()
  id = serializers.IntegerField()
  cue = serializers.CharField()
  narration = serializers.CharField()
  order = serializers.CharField()
  script_id = serializers.CharField()
  date_time = serializers.DateTimeField()
  user = serializers.CharField()


class ScriptListSerializer(serializers.ModelSerializer):
  tid = serializers.ReadOnlyField(source='tutorial_id')
  fid = serializers.ReadOnlyField(source='foss_id')
  lid = serializers.ReadOnlyField(source='language_id')
  user = serializers.ReadOnlyField(source='user.username')
  published_by = serializers.ReadOnlyField(source='published_by.username')
  class Meta:
    model = Script
    fields = ('tid', 'fid','lid','domain', 'foss', 'language', 'tutorial', 'outline', 'status', 'user', 'published_by', 'published_on', 'suggested_title', 'versionNo', 'editable')

