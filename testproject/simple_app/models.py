# coding: utf-8

from django.db import models
from django.contrib.auth.models import User


class Topping(models.Model):

    name = models.CharField(max_length=50, blank=False, unique=True)

    def __str__(self):
        return self.name


class Pizza(models.Model):

    name = models.CharField(max_length=50, blank=False, unique=True)
    toppings = models.ManyToManyField(Topping)

    def __str__(self):
        return self.name


class Message(models.Model):

    title = models.CharField(max_length=50, blank=False)
    text = models.TextField(blank=False)

    def __str__(self):
        return self.text


class Owner(models.Model):

    name = models.CharField(max_length=50, blank=False)

    def __str__(self):
        return self.name


class VirtualMachine(models.Model):

    name = models.CharField(max_length=50, blank=False)
    cpus = models.IntegerField()
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    so = models.CharField(max_length=100, blank=False)
    started = models.BooleanField()

    def __str__(self):
        return self.name

