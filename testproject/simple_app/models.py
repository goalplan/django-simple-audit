# coding: utf-8
import uuid

from django.db import models
from django.contrib.auth.models import User


class Topping(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, blank=False, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Pizza(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, blank=False, unique=True)
    toppings = models.ManyToManyField(Topping)

    def __str__(self):
        return self.name


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=50, blank=False)
    text = models.TextField(blank=False)

    def __str__(self):
        return self.text


class Owner(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, blank=False)

    def __str__(self):
        return self.name


class VirtualMachine(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, blank=False)
    cpus = models.IntegerField()
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    so = models.CharField(max_length=100, blank=False)
    started = models.BooleanField()

    EXCLUDE_FIELDS_FROM_AUDIT = ['started']

    def __str__(self):
        return self.name
