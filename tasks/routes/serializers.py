from rest_framework import serializers

from tasks.models import Task, Activity
from crm.models import Contact, Deal
from account.models import User


from crm.routes.contact_deal.serializers import ContactShortSerializer, UserShortSerializer


class DealShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deal
        fields = ["id", "name", "amount"]


class TaskSerializer(serializers.ModelSerializer):
    contact = ContactShortSerializer(read_only=True)
    contact_id = serializers.PrimaryKeyRelatedField(queryset=Contact.objects.all(), source="contact",write_only=True, required=False, allow_null=True)
    deal = DealShortSerializer(read_only=True)
    deal_id = serializers.PrimaryKeyRelatedField(queryset=Deal.objects.all(), source="deal",write_only=True, required=False, allow_null=True,)
    assigned_to = UserShortSerializer(read_only=True)
    assigned_to_id = serializers.PrimaryKeyRelatedField(
    queryset=User.objects.all(), source="assigned_to",
    write_only=True, required=False, allow_null=True
)
    class Meta:
        model = Task
        fields = [
            "id", "description", "due_date",
            "contact", "contact_id",
            "deal", "deal_id",
            "assigned_to", "assigned_to_id",
            "is_done",
        ]
        read_only_fields = ["id"]

    def validate(self, attrs):
        contact = attrs.get("contact")
        deal = attrs.get("deal")
        if contact is None and deal is None:
            raise serializers.ValidationError(
                "Vazifa kamida bitta obyektga (contact yoki deal) bog'lanishi kerak."
            )
        return attrs


class ActivitySerializer(serializers.ModelSerializer):
    contact = ContactShortSerializer(read_only=True)
    contact_id = serializers.PrimaryKeyRelatedField(queryset=Contact.objects.all(), source="contact",write_only=True,)
    user = UserShortSerializer(read_only=True)
    activity_type_display = serializers.CharField(source="get_activity_type_display", read_only=True)

    class Meta:
        model = Activity
        fields = [
            "id",
            "contact", "contact_id",
            "user",
            "activity_type", "activity_type_display",
            "note",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]