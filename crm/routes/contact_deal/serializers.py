from rest_framework import serializers

from account.models import User
from crm.models import Company, Stage, Contact, Deal


class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'full_name', 'phone_number']


class CompanyShortSerializer(serializers.ModelSerializer): 
    class Meta:
        model = Company
        fields = ["id", "name"]


class StageShortSerializer(serializers.ModelSerializer): 
    class Meta:
        model = Stage
        fields = ["id", "name", "order"]
 
 
class ContactSerializer(serializers.ModelSerializer): 
    company = CompanyShortSerializer(read_only=True)
    company_id = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(),
        source="company",
        write_only=True,
        required=False,
        allow_null=True,
    )
    source_display = serializers.CharField(source="get_source_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
 
    class Meta:
        model = Contact
        fields = [
            "id",
            "full_name",
            "phone_number",
            "email",
            "company",
            "company_id",
            "source",
            "source_display",
            "status",
            "status_display",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
 
 
class ContactShortSerializer(serializers.ModelSerializer): 
    class Meta:
        model = Contact
        fields = ["id", "full_name", "phone_number"]
 
class DealSerializer(serializers.ModelSerializer):
    contact = ContactShortSerializer(read_only=True)
    contact_id = serializers.PrimaryKeyRelatedField(queryset=Contact.objects.all(), source="contact", write_only=True)
    stage = StageShortSerializer(read_only=True)
    stage_id = serializers.PrimaryKeyRelatedField(queryset=Stage.objects.all(), source="stage", write_only=True)
    manager = UserShortSerializer(read_only=True)
    manager_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),source="manager",write_only=True,required=False,allow_null=True,)

    class Meta:
        model = Deal
        fields = [
            "id", "name",
            "contact", "contact_id",
            "amount",
            "stage", "stage_id",
            "manager", "manager_id",
            "opened_at", "closed_at",
        ]
        read_only_fields = ["id", "opened_at", "closed_at"]

    def validate_amount(self, value):
        if value < 0:
            raise serializers.ValidationError("Summa manfiy bo'lishi mumkin emas.")
        return value