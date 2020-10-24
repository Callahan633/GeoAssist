from django.contrib.auth import authenticate
from rest_framework import serializers, viewsets

from .models import User, Place, VisitDate


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True,
    )

    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'token', 'first_name', 'last_name')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class DateSerializer(serializers.ModelSerializer):

    class Meta:
        model = VisitDate
        fields = ('date_visited',)

    def create(self, validated_data):
        user = self.context['request'].user
        place = Place.objects.get(user=user, name=self.context['request'].data['name'])
        return VisitDate.objects.create_date_for_history(place, **validated_data)


class PlaceSerializer(serializers.ModelSerializer):

    dates = DateSerializer(source='visitdate_set', many=True, read_only=True)

    class Meta:
        model = Place
        fields = ('name', 'category', 'is_favourite', 'dates')

    def create(self, validated_data):
        user = self.context['request'].user
        return Place.objects.create_place_for_history(user, **validated_data)

    def update(self, instance, validated_data):
        return Place.objects.set_place_to_favourite(instance, **validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(max_length=128, write_only=True)

    username = serializers.CharField(max_length=255, read_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        email = data.get('email', None)
        password = data.get('password', None)

        if email is None:
            raise serializers.ValidationError(
                'An email address is required to log in.'
            )

        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.'
            )

        user = authenticate(username=email, password=password)

        if user is None:
            raise serializers.ValidationError(
                'A user with this email and password was not found.'
            )

        if not user.is_active:
            raise serializers.ValidationError(
                'This user has been deactivated.'
            )

        return {
            'token': user.token,
        }
