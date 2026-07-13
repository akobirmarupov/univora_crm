from rest_framework import serializers

from crm.models import Company, Stage


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            'id',
            'name',
            'industry',
            'website',
            'address',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
 
 
 
class StageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = [
            "id", 
            "name", 
            "order", 
            "created_at", 
            "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]