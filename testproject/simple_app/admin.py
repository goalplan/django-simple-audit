# coding: utf-8
from django.contrib import admin

from .models import Message, Owner, Pizza, Topping, VirtualMachine


class PizzaAdmin(admin.ModelAdmin):
    list_display = ('name',)
    filter_horizontal = ('toppings',)


class ToppingAdmin(admin.ModelAdmin):
    list_display = ('name', )


class MessageAdmin(admin.ModelAdmin):
    list_display = ('title', 'text')


class OwnerAdmin(admin.ModelAdmin):
    list_display = ('name',)


class VirtualMachineAdmin(admin.ModelAdmin):
    list_display = ('name', 'cpus', 'owner')


admin.site.register(Message, MessageAdmin)
admin.site.register(Owner, OwnerAdmin)
admin.site.register(VirtualMachine, VirtualMachineAdmin)
admin.site.register(Pizza, PizzaAdmin)
admin.site.register(Topping, ToppingAdmin)
