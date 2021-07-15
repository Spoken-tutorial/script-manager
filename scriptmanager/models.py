from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Script(models.Model):
	domain = models.CharField(max_length=255, null=True)
	foss = models.TextField(blank=True)
	foss_id = models.IntegerField(blank=True)
	tutorial = models.TextField(blank=True)
	tutorial_id = models.IntegerField(blank=True)
	outline = models.TextField(blank=True)
	language = models.TextField(blank=True)
	language_id = models.IntegerField(blank=True)
	suggested_title = models.CharField(max_length=255, null=True)
	status = models.BooleanField(default=False)
	data_file = models.FileField(upload_to='scripts')
	user = models.ForeignKey(User,related_name='user_id', null=True, on_delete=models.PROTECT)
	ordering = models.TextField(default='')
	published_by = models.ForeignKey(User, null=True, on_delete=models.PROTECT)
	published_on = models.DateTimeField(null=True)
	versionNo = models.PositiveIntegerField(null=True)
	editable = models.BooleanField(default=False)

	def __str__(self):
		return str(self.domain)+ ' - ' +str(self.foss_id) + ' - ' + str(self.tutorial_id)

class ScriptDetail(models.Model):
	cue = models.TextField(blank=True)
	narration = models.TextField(blank=True)
	order = models.PositiveIntegerField()
	prevRow = models.PositiveIntegerField(null=True)
	nextRow = models.PositiveIntegerField(null=True)
	script = models.ForeignKey(Script, on_delete = models.CASCADE)
	comment_status = models.BooleanField(default=False)

class Comment(models.Model):
	comment = models.TextField()
	user=models.ForeignKey(User, on_delete=models.PROTECT)
	script_details=models.ForeignKey(ScriptDetail, on_delete=models.CASCADE)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
	done = models.BooleanField(default=False)
	resolved = models.BooleanField(default=False)

	def __str__(self):
	 return str(self.user) + ' - ' + self.comment
