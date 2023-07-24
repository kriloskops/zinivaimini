from django.db import models
from django_mysql.models import ListTextField

# Create your models here.


class Player(models.Model):
    username = models.CharField(max_length=30, unique=True)
    score = models.IntegerField(default=0)
    
    def __str__(self):
        return self.username


class Question(models.Model):
    question = models.CharField(max_length=200)
    answer_1 = models.CharField(max_length=30)
    answer_2 = models.CharField(max_length=30)
    answer_3 = models.CharField(max_length=30)
    answer_4 = models.CharField(max_length=30)
    correct_answer = models.CharField(max_length=30)

    day = models.SmallIntegerField(default=0)
    order_num = models.SmallIntegerField()

    def __str__(self):
        return self.question

    


class Reply(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.CharField(max_length=30)
    day = models.SmallIntegerField()

    def __str__(self):
        return f"{self.player}: {self.question.question[:15]}{'...?' if len(self.question.question)>15 else ''}"