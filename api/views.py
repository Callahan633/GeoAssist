from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import ViewSet

from .serializers import LoginSerializer, RegistrationSerializer, PlaceSerializer, DateSerializer
from .models import Place


class RegistrationAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                'token': serializer.data.get('token', None),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class PlaceCreatingAPIView(APIView):
    permission_classes = [IsAuthenticated]
    place_serializer = PlaceSerializer
    date_serializer = DateSerializer

    def post(self, request):
        place_serializer = self.place_serializer(context={'request': request}, data=request.data)
        date_serializer = self.date_serializer(context={'request': request}, data=request.data)
        date_serializer.is_valid(raise_exception=True)

        try:
            place_serializer.is_valid(raise_exception=True)
            place_serializer.save()
            date_serializer.save()
        except ValidationError:
            date_serializer.save()
        
        return Response(
            {
                'place': place_serializer.data.get('name', None)
            },
            status=status.HTTP_201_CREATED,
        )


class SetPlaceFavouriteAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PlaceSerializer

    def patch(self, request):
        serializer = self.serializer_class(context={'request': request}, data=request.data, partial=True)
        name = serializer.initial_data.get('name', None)
        try:
            place = Place.objects.get(name=name, user_id=request.user)
        except Place.DoesNotExist:
            return Response(
                {
                    'error': "This user hadn't ever been at this place"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if place.is_favourite is False:
            place.is_favourite = True
            place.save()
            return Response(
                {
                    'place': serializer.initial_data.get('name', None),
                    'is_favourite': place.is_favourite
                },
                status=status.HTTP_200_OK
            )
        place.is_favourite = False
        place.save()
        return Response(
            {
                'place': serializer.initial_data.get('name', None),
                'is_favourite': place.is_favourite
            },
            status=status.HTTP_200_OK
        )


class GetFavouritePlacesAPIView(ViewSet):
    queryset = Place.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = PlaceSerializer

    def retrieve(self, request, *args, **kwargs):
        favourites_list = self.queryset.filter(user_id=request.user, is_favourite=True)
        print(request.user.uuid)
        print(favourites_list)
        serializer = self.serializer_class(favourites_list, many=True)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
