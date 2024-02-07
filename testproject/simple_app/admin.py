# coding: utf-8
from .models import Message, Owner, VirtualMachine, Pizza, Topping
from django.contrib import admin


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


