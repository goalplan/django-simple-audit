# -*- coding:utf-8 -*_
from __future__ import absolute_import
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from django.utils.html import escape
from django.urls import reverse
from django.shortcuts import redirect
from django.urls import path
from .models import Audit
from .signal import MODEL_LIST


class ContentTypeListFilter(SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _("Object")
    parameter_name = "content_type__id__exact"

    def lookups(self, request, model_admin):
        """
            Returns a list of tuples. The first element in each
            tuple is the coded value for the option that will
            appear in the URL query. The second element is the
            human-readable name for the option that will appear
            in the right sidebar.
            """
        return [
            (ct.pk, ct.name)
            for ct in ContentType.objects.get_for_models(*MODEL_LIST).values()
        ]

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            return queryset.filter(content_type_id=self.value())
        else:
            return queryset


@admin.register(Audit)
class AuditAdmin(admin.ModelAdmin):
    search_fields = (
        "description",
        "audit_request__request_id",
        "obj_description",
        "object_id",
    )
    list_display = (
        "format_date",
        "audit_content",
        "operation",
        "audit_user",
        "audit_description",
    )
    list_filter = ("operation", ContentTypeListFilter)

    def get_urls(self):
        urls = super(AuditAdmin, self).get_urls()
        my_urls = [
            path(
                "revert/<int:audit_id>/",
                self.admin_site.admin_view(self.revert_change),
                name="simple_audit_audit_revert",
            )
        ]
        return my_urls + urls

    def revert_change(self, request, audit_id):
        audit = Audit.objects.get(pk=audit_id)
        if audit.operation == Audit.CHANGE:
            audit_obj = audit.content_object
            for change in audit.field_changes.all():
                setattr(audit_obj, change.field, change.old_value)
            audit_obj.save(force_insert=False)
        elif audit.operation == Audit.DELETE:
            audit_obj = audit.content_type.model_class()(pk=audit.object_id)
            for change in audit.field_changes.all():
                setattr(audit_obj, change.field, change.new_value)
            audit_obj.save(force_insert=True)

        return redirect("admin:simple_audit_audit_changelist")

    @admin.display(
        description=_("Date"),
        ordering="date",
    )
    def format_date(self, obj):
        return obj.date.strftime("%d/%m/%Y %H:%M")


    @admin.display(
        description=_("Description")
    )
    def audit_description(self, audit):
        desc = "<br/>".join(escape(audit.description or "").split("\n"))
        return desc


    @admin.display(
        description=_("Current Content")
    )
    def audit_content(self, audit):
        obj_string = audit.obj_description or str(audit.content_object)

        return (
            "<a title='%(filter)s' href='%(base)s?content_type__id__exact=%(type_id)s&object_id__exact=%(id)s'>%(type)s: %(obj)s</a>"
            % {
                "filter": _("Click to filter"),
                "base": reverse("admin:simple_audit_audit_changelist"),
                "type": audit.content_type,
                "type_id": audit.content_type.id,
                "obj": obj_string,
                "id": audit.object_id,
            }
        )


    @admin.display(
        description=_("User"),
        ordering="audit_request__user",
    )
    def audit_user(self, audit):
        if audit.audit_request:
            return u"<a title='%s' href='%s?user=%d'>%s</a>" % (
                _("Click to filter"),
                reverse("admin:simple_audit_audit_changelist"),
                audit.audit_request.user.id,
                audit.audit_request.user,
            )
        else:
            return u"%s" % (_("unknown"))


    def queryset(self, request):
        request.GET = request.GET.copy()
        user_filter = request.GET.pop("user", None)
        qs = Audit.objects.prefetch_related("audit_request", "audit_request__user")
        if user_filter:
            qs = qs.filter(audit_request__user__in=user_filter)
        return qs

    def has_add_permission(self, request):
        return False


