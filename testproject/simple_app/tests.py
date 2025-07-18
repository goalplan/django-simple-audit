"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from simple_audit import m2m_audit
from simple_audit import settings as audit_settings
from simple_audit.models import Audit

from .models import Pizza, Topping, Owner, VirtualMachine


class SimpleTest(TestCase):

    def setUp(self):
        self.topping_onion = Topping.objects.get_or_create(name="onion")[0]
        self.topping_egg = Topping.objects.get_or_create(name="egg")[0]

        self.content_type_topping = ContentType.objects.get_for_model(Topping)
        self.content_type_pizza = ContentType.objects.get_for_model(Pizza)
        self.content_type_virtual_machine = ContentType.objects.get_for_model(VirtualMachine)

    @staticmethod
    def sort_dict_collection(list_):
        """ Takes a list of dictionaries and orders them by key """
        return sorted(list_, key=lambda x: list(x.keys())[0])

    def test_add_topping_and_search_audit(self):
        """tests add a topping"""
        topping = Topping.objects.get_or_create(name="potato")[0]

        # topping created
        self.assertTrue(topping.pk)
        # audit recorded?
        self.assertTrue(Audit.objects.get(operation=0,
                                          content_type=self.content_type_topping,
                                          object_id=topping.pk,
                                          description="Added potato"))

    def test_add_pizza_without_toppings(self):
        """test add pizza without topping"""
        pizza = Pizza.objects.get_or_create(name="mussarela")[0]

        # pizza created?
        self.assertTrue(pizza.pk)
        # toppings added?
        self.assertEqual(pizza.toppings.all().count(), 0)
        # audit recorded?
        self.assertTrue(Audit.objects.get(operation=0,
                                          content_type=self.content_type_pizza,
                                          object_id=pizza.pk,
                                          description="Added mussarela"))

    def test_add_pizza_with_toppings_with_audit_enabled(self):
        """test add pizza with topping"""

        self.assertTrue(settings.DJANGO_SIMPLE_AUDIT_M2M_FIELDS)
        audit_settings.DJANGO_SIMPLE_AUDIT_M2M_FIELDS = settings.DJANGO_SIMPLE_AUDIT_M2M_FIELDS

        pizza = Pizza.objects.get_or_create(name="peperoni")[0]

        # pizza created?
        self.assertTrue(pizza.pk)
        # toppings added?
        pizza.toppings.add(self.topping_onion)

        self.assertEqual(pizza.toppings.all().count(), 1)

        # audit recorded?
        self.assertTrue(Audit.objects.get(operation=0,
                                          content_type=self.content_type_pizza,
                                          object_id=pizza.pk,
                                          description="Added peperoni"))

        # m2m audit recorded?
        # u"field toppings.1.id: was changed from None to 1\nfield toppings.1.name: was changed from None to 'calabresa'"
        desc = "field toppings.%s.id: was changed from None to %s\nfield toppings.%s.name: was changed from None to '%s'" % (
            self.topping_onion.id,
            self.topping_onion.id,
            self.topping_onion.id,
            self.topping_onion.name)

        self.assertTrue(Audit.objects.get(operation=1,
                                          content_type=self.content_type_pizza,
                                          object_id=pizza.pk,
                                          description=desc))

    def test_m2m_dict_diff_with_new_and_old_state_different(self):
        """
        test where old state and new state contains different elements
        """

        new_state = {u'toppings': [{u'id': 1, 'name': u'ceboloa'},
                                   {u'id': 5, 'name': u'cogumelo'},
                                   {u'id': 6, 'name': u'abobrinha'},
                                   {u'id': 8, 'name': u'codorna'},
                                   {u'id': 9, 'name': u'banana'},
                                   {u'id': 10, 'name': u'abacaxi'},
                                   ]}

        old_state = {u'toppings': [{u'id': 1, 'name': u'ceboloa'},
                                   {u'id': 5, 'name': u'cogumelo'},
                                   {u'id': 6, 'name': u'abobrinha'},
                                   {u'id': 8, 'name': u'codorna'},
                                   {u'id': 9, 'name': u'banana'},
                                   {u'id': 11, 'name': u'abacate'},
                                   ]}

        expected_response = [{u'toppings.10.id': [None, 10], u'toppings.10.name': [None, u'abacaxi']},
                             {u'toppings.11.id': [11, None], u'toppings.11.name': [u'abacate', None]}]

        expected_response = self.sort_dict_collection(expected_response)

        diff = m2m_audit.m2m_dict_diff(old_state, new_state)
        diff = self.sort_dict_collection(diff)

        self.assertEqual(diff, expected_response)

    def test_m2m_dict_diff_with_empty_new_state(self):
        """
        test where new state is an empty dict
        """

        new_state = {}

        old_state = {u'toppings': [{u'id': 1, 'name': u'ceboloa'},
                                   {u'id': 5, 'name': u'cogumelo'},
                                   {u'id': 6, 'name': u'abobrinha'},
                                   {u'id': 8, 'name': u'codorna'},
                                   {u'id': 9, 'name': u'banana'},
                                   {u'id': 11, 'name': u'abacate'},
                                   ]}

        expected_response = [{u'toppings.11.id': [11, None], u'toppings.11.name': [u'abacate', None]},
                             {u'toppings.5.id': [5, None], u'toppings.5.name': [u'cogumelo', None]},
                             {u'toppings.6.id': [6, None], u'toppings.6.name': [u'abobrinha', None]},
                             {u'toppings.1.id': [1, None], u'toppings.1.name': [u'ceboloa', None]},
                             {u'toppings.8.id': [8, None], u'toppings.8.name': [u'codorna', None]},
                             {u'toppings.9.id': [9, None], u'toppings.9.name': [u'banana', None]}]

        expected_response = self.sort_dict_collection(expected_response)

        diff = m2m_audit.m2m_dict_diff(old_state, new_state)
        diff = self.sort_dict_collection(diff)

        self.assertEqual(diff, expected_response)

    def test_m2m_dict_diff_with_empty_old_state(self):
        """
        test where old state is an empty dict
        """

        new_state = {u'toppings': [{u'id': 1, 'name': u'ceboloa'},
                                   {u'id': 5, 'name': u'cogumelo'},
                                   {u'id': 6, 'name': u'abobrinha'},
                                   {u'id': 8, 'name': u'codorna'},
                                   {u'id': 9, 'name': u'banana'},
                                   {u'id': 10, 'name': u'abacaxi'},
                                   ]}

        old_state = {}

        expected_response = [{u'toppings.10.id': [None, 10], u'toppings.10.name': [None, u'abacaxi']},
                             {u'toppings.5.id': [None, 5], u'toppings.5.name': [None, u'cogumelo']},
                             {u'toppings.6.id': [None, 6], u'toppings.6.name': [None, u'abobrinha']},
                             {u'toppings.1.id': [None, 1], u'toppings.1.name': [None, u'ceboloa']},
                             {u'toppings.8.id': [None, 8], u'toppings.8.name': [None, u'codorna']},
                             {u'toppings.9.id': [None, 9], u'toppings.9.name': [None, u'banana']}]

        expected_response = self.sort_dict_collection(expected_response)

        diff = m2m_audit.m2m_dict_diff(old_state, new_state)
        diff = self.sort_dict_collection(diff)

        self.assertEqual(diff, expected_response)

    def test_m2m_dict_diff_with_old_and_new_state_the_same(self):
        """
        test where old state and new state are the same. no change detected!
        """

        new_state = {u'toppings': [{u'id': 1, 'name': u'ceboloa'},
                                   {u'id': 5, 'name': u'cogumelo'},
                                   {u'id': 6, 'name': u'abobrinha'},
                                   {u'id': 8, 'name': u'codorna'},
                                   {u'id': 9, 'name': u'banana'},
                                   {u'id': 10, 'name': u'abacaxi'},
                                   ]}

        old_state = {u'toppings': [{u'id': 1, 'name': u'ceboloa'},
                                   {u'id': 5, 'name': u'cogumelo'},
                                   {u'id': 6, 'name': u'abobrinha'},
                                   {u'id': 8, 'name': u'codorna'},
                                   {u'id': 9, 'name': u'banana'},
                                   {u'id': 10, 'name': u'abacaxi'},
                                   ]}

        expected_response = []

        diff = m2m_audit.m2m_dict_diff(old_state, new_state)

        self.assertEqual(diff, expected_response)

    def test_m2m_dict_multiple_field_diff(self):
        """
        test where old state and new state contains multiple fields,
        with one field having a changed value
        """

        new_state = {
            u'foo': [
                {u'id': 1, 'name': u'bar'
                 }
            ],
            u'toppings': [
                {u'id': 1, 'name': u'ceboloa'},
                {u'id': 5, 'name': u'cogumelo'},
                {u'id': 6, 'name': u'abobrinha'},
                {u'id': 8, 'name': u'codorna'},
                {u'id': 9, 'name': u'banana'},
                {u'id': 10, 'name': u'abcdef'},
            ]
        }

        old_state = {
            u'foo': [
                {u'id': 1, 'name': u'bar'
                 }
            ],
            u'toppings': [
                {u'id': 1, 'name': u'ceboloa'},
                {u'id': 5, 'name': u'cogumelo'},
                {u'id': 6, 'name': u'abobrinha'},
                {u'id': 8, 'name': u'codorna'},
                {u'id': 9, 'name': u'banana'},
                {u'id': 10, 'name': u'abcdesccc'},
            ]
        }

        expected_response = [{u'toppings.10.name': [u'abcdesccc', u'abcdef']}]

        diff = m2m_audit.m2m_dict_diff(old_state, new_state)
        self.assertEqual(diff, expected_response)

    def test_field_changes_for_nullable_values(self):
        """tests add a topping with none description"""
        topping = Topping.objects.create(name="jalapeno")

        last_audit = Audit.objects.filter(content_type=self.content_type_topping,
                                          object_id=topping.pk).order_by('-date').first()

        # description have not change because it is still None
        assert not last_audit.field_changes.filter(field='description').exists()

        topping.description = 'Some description'
        topping.save()

        last_audit = Audit.objects.filter(content_type=self.content_type_topping,
                                          object_id=topping.pk).order_by('-date').first()

        field_change = last_audit.field_changes.get(field='description')
        assert field_change.old_value is None
        assert field_change.new_value == 'Some description'

        topping.description = None
        topping.save()

        last_audit = Audit.objects.filter(content_type=self.content_type_topping,
                                          object_id=topping.pk).order_by('-date').first()

        field_change = last_audit.field_changes.get(field='description')
        assert field_change.old_value == 'Some description'
        assert field_change.new_value is None

    def test_field_changes_for_foreign_key_values(self):
        """tests field changes for foreign key value"""
        owner = Owner.objects.create(name='Ionel')
        vm = VirtualMachine.objects.create(name='VM1', cpus=4, owner=owner, started=True)

        last_audit = Audit.objects.filter(content_type=self.content_type_virtual_machine,
                                          object_id=vm.pk).order_by('-date').first()

        field_change = last_audit.field_changes.get(field='owner')
        assert field_change.old_value is None
        assert field_change.new_value == str(owner.id)

    def test_field_changes_for_excluded_fields(self):
        """tests field changes for foreign key value"""
        owner = Owner.objects.create(name='Ionel')
        vm = VirtualMachine.objects.create(name='VM1', cpus=4, owner=owner, started=True)

        last_audit = Audit.objects.filter(content_type=self.content_type_virtual_machine,
                                          object_id=vm.pk).order_by('-date').first()

        assert last_audit.field_changes.filter(field='name').exists()
        assert last_audit.field_changes.filter(field='cpus').exists()
        assert last_audit.field_changes.filter(field='owner').exists()
        assert not last_audit.field_changes.filter(field='started').exists()
