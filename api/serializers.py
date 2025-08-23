from rest_framework import serializers




class AttachTokenBotSerializer(serializers.Serializer):
    telegram_id = serializers.IntegerField()
    token = serializers.CharField(max_length=128)
    username = serializers.CharField(max_length=32, required=False, allow_blank=True)
    first_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=255, required=False, allow_blank=True)




class AttachTokenMiniAppSerializer(serializers.Serializer):
    init_data = serializers.CharField()
    token = serializers.CharField(max_length=128)