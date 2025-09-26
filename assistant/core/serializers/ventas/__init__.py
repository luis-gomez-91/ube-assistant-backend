# core/serializers/ventas/__init__.py
from rest_framework import serializers

class ResponseSerializer(serializers.Serializer):
    status = serializers.CharField()

class ErrorSerializer(ResponseSerializer):
    message = serializers.CharField()

class MatricularSerializer(ResponseSerializer):
    message = serializers.CharField()

class MessageRequestSerializer(serializers.Serializer):
    mensaje = serializers.CharField()
