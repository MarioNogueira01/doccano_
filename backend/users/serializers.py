from django.contrib.auth import get_user_model
from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer as DefaultRegisterSerializer

class UserSerializer(serializers.ModelSerializer):
    # Campo "password" write_only
    password = serializers.CharField(write_only=True, required=False)
    groups = serializers.SerializerMethodField(read_only=True)
    groups_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True,
        help_text="Lista de IDs de grupos a associar ao utilizador"
    )

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
            "groups",
            "groups_ids",
            "password"
        ]

    def get_groups(self, obj):
        """Retorna a lista de nomes dos perfis (grupos) associados ao utilizador."""
        return [group.name for group in obj.groups.all()]

    def update(self, instance, validated_data):
        # Lógica para atualizar a senha se "password" vier no payload
        password = validated_data.pop("password", None)
        groups_ids = validated_data.pop("groups_ids", None)

        instance = super().update(instance, validated_data)

        if password:
            instance.set_password(password)

        if groups_ids is not None:
            instance.groups.set(groups_ids)

        instance.save()
        return instance


class CustomRegisterSerializer(DefaultRegisterSerializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    is_superuser = serializers.BooleanField(required=False, default=False)
    # Recebe uma lista de IDs de grupos aos quais o utilizador pertencerá
    groups = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
        help_text="Lista de IDs de grupos (perfis) a associar ao utilizador"
    )

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

        # Associar grupos se fornecidos
        groups_ids = self.validated_data.get("groups", [])
        if groups_ids:
            try:
                # Usamos set para substituir quaisquer grupos existentes
                user.groups.set(groups_ids)
            except Exception:
                # Se algum ID for inválido ignoramos silenciosamente ou poderíamos lançar erro
                pass

        return user
