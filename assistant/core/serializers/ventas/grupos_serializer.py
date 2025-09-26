# core/serializers/grupos_serializers.py
from rest_framework import serializers

class GrupoDataSerializer(serializers.Serializer):
    carrera = serializers.CharField()
    nombre = serializers.CharField()
    fecha_inicio = serializers.CharField()
    fecha_fin = serializers.CharField()
    capacidad = serializers.IntegerField()
    sesion = serializers.CharField()
    modalidad = serializers.CharField()
    nivel = serializers.CharField()

class GruposSerializer(serializers.Serializer):
    status = serializers.CharField()
    data = GrupoDataSerializer(many=True)
