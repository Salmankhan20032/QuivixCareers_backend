from rest_framework import serializers
from .models import CustomUser, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = UserProfile
        fields = ["profile_picture", "university", "major", "interest"]

    def validate_profile_picture(self, value):
        if value and value.size > 3 * 1024 * 1024:
            raise serializers.ValidationError("Profile picture must be less than 3 MB.")
        return value

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.profile_picture:
            representation["profile_picture"] = instance.profile_picture.url
        return representation


class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = CustomUser
        fields = ["email", "full_name", "nationality", "password", "password2"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password": "Passwords must match."})
        return data

    def create(self, validated_data):
        validated_data.pop("password2")
        user = CustomUser.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()

    class Meta:
        model = CustomUser
        fields = ["id", "email", "full_name", "nationality", "profile"]
