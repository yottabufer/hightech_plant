from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status

from task.custom_user.serializers.user import UserRegistrationSerializer


class UserRegistrationAPIView(CreateAPIView):
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({"detail": "User created successfully."}, status=status.HTTP_201_CREATED, headers=headers)