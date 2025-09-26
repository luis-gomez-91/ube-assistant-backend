# core/serializers/malla_serializers.py
from rest_framework import serializers

class AsignaturaSerializer(serializers.Serializer):
    asignatura = serializers.CharField()
    horas = serializers.FloatField()
    creditos = serializers.IntegerField(required=False, allow_null=True)

class DataMallaSerializer(serializers.Serializer):
    nivel_malla = serializers.CharField()
    asignaturas = AsignaturaSerializer(many=True)

class MallaSerializer(serializers.Serializer):
    status = serializers.CharField()
    data = DataMallaSerializer(many=True)
