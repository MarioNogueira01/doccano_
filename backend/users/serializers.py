from django.contrib.auth import get_user_model
from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer as DefaultRegisterSerializer

class UserSerializer(serializers.ModelSerializer):
    # Campo "password" write_only
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "is_superuser",
            "is_staff",
            "email",
            "last_login",
            "password"
        ]

    def update(self, instance, validated_data):
        # Lógica para atualizar a senha se "password" vier no payload
        password = validated_data.pop("password", None)
        instance = super().update(instance, validated_data)
        if password:
            instance.set_password(password)
            instance.save()
        return instance


class CustomRegisterSerializer(DefaultRegisterSerializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    is_superuser = serializers.BooleanField(required=False, default=False)

    def save(self, request):
        user = super().save(request)
        user.first_name = self.validated_data.get("first_name", "")
        user.last_name = self.validated_data.get("last_name", "")
        
        # Only admins can create superusers
        if request.user.is_superuser:
            user.is_superuser = self.validated_data.get("is_superuser", False)
            if user.is_superuser:
                user.is_staff = True  # Superusers should also be staff
        
        user.save()
        return user
