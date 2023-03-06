from django.db import models


class BaseManager(models.Manager):
    def get_or_none(self, **kwargs):
        try:
            return self.get_queryset().get(**kwargs)
        except self.model.DoesNotExist:
            return None


class ContestInfo(models.Model):
    objects = BaseManager()
    screen_name = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    finish_time = models.DateTimeField()

    def __str__(self):
        return self.screen_name


class TaskInfo(models.Model):
    objects = BaseManager()
    contest = models.ForeignKey(ContestInfo, on_delete=models.CASCADE)
    assignment = models.CharField(max_length=30)
    screen_name = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.screen_name


class ResultInfo(models.Model):
    objects = BaseManager()
    task = models.ForeignKey(TaskInfo,  on_delete=models.CASCADE)
    user_name = models.CharField(max_length=50)
    score = models.BigIntegerField(default=-1)

    def __str__(self):
        return self.user_name
