# core/serializers/carreras_serializers.py
from rest_framework import serializers

class PreciosSerializer(serializers.Serializer):
    inscripcion = serializers.FloatField(required=False, allow_null=True)
    matricula = serializers.FloatField(required=False, allow_null=True)
    numero_cuotas = serializers.IntegerField(required=False, allow_null=True)
    homologacion = serializers.FloatField(required=False, allow_null=True)

class CarreraSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nombre = serializers.CharField()
    sesiones = serializers.ListField(child=serializers.CharField())
    modalidades = serializers.ListField(child=serializers.CharField())
    precios = PreciosSerializer(required=False)

class DataCarrerasSerializer(serializers.Serializer):
    grado = CarreraSerializer(many=True)
    postgrado = CarreraSerializer(many=True)

class CarrerasSerializer(serializers.Serializer):
    status = serializers.CharField()
    data = DataCarrerasSerializer()
