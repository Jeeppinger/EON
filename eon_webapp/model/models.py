from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import datetime
from django.db.models import signals
from django.dispatch import Signal
from forum.models import Thread
from group.models import Group
from django.contrib.postgres.fields import ArrayField
import subprocess

LANGUAGES = ["C","Python","R"]
LANGUAGE_CHOICES = [(str(i), LANGUAGES[i]) for i in range(len(LANGUAGES))]

def content_file_name(instance, filename):
    return '/'.join(['content', instance.user.username, filename])

# Create your models here.
class UserModel(models.Model):
    model_name = models.CharField(max_length=30)
    owner = models.ForeignKey(User,on_delete=models.CASCADE)
    code_language = models.CharField(max_length=30, choices=LANGUAGE_CHOICES,default=0)
    folder_location = models.CharField(max_length=128)
    description = models.TextField(max_length=256)
    executable_file_name = models.CharField(max_length=30)
    created_on = models.DateTimeField(auto_now_add=True)
    thread = models.ForeignKey(Thread,on_delete=models.CASCADE)
    group = models.ManyToManyField(Group)
    is_github = models.BooleanField(default=False,verbose_name="Is this a github repo?")
    git_repo_link = models.CharField(max_length=128, default="")
    tags = ArrayField(models.CharField(max_length=200), blank=True,verbose_name="tags (comma separated list)", default=list)
    views = models.IntegerField(default=0)

    # TODO: add this: EONid = models.CharField(max_length=256)

    def get_absolute_url(self):
        #return reverse('model_index')
        return reverse('Display-UserModel', kwargs={'pk':self.pk})
        #def Some_url(self):


    def __str__(self):
        return str(self.pk)

    def SaveGraphDiscriptions(self):
        print("Coming soon")

def UserModel_post_save(sender, instance, created, *args, **kwargs):
    """Argument explanation:

       sender - The model class. (MyModel)
       instance - The actual instance being saved.
       created - Boolean; True if a new record was created.

       *args, **kwargs - Capture the unneeded `raw` and `using`(1.3) arguments.
    """
    if created:
        if int(instance.code_language)==0: # 0=="C" in languages dict
            print("COMPILING C CODE IN: %s\n" %instance.folder_location)
            subprocess.run(["make","-C",instance.folder_location])
signals.post_save.connect(UserModel_post_save, sender=UserModel)
