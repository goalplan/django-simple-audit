# coding: utf-8
from django.contrib import admin

from .models import Message, Owner, Pizza, Topping, VirtualMachine


@admin.register(Pizza)
class PizzaAdmin(admin.ModelAdmin):
    list_display = ('name',)
    filter_horizontal = ('toppings',)


@admin.register(Topping)
class ToppingAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('title', 'text')


@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(VirtualMachine)
class VirtualMachineAdmin(admin.ModelAdmin):
    list_display = ('name', 'cpus', 'owner')
