from rest_framework import serializers


class EmployeeSerializer(serializers.Serializer):
    id=serializers.IntegerField(read_only=True)
    email=serializers.EmailField()
    password=serializers.CharField(max_length=255,write_only=True)
    ismanager=serializers.BooleanField()
    age=serializers.IntegerField()
    