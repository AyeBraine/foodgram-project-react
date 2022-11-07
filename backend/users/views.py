# isort: skip_file
from rest_framework import filters, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.pagination import AdjustablePagination
from api.serializers import SubscriptionsSerializer, UserReadSerializer
from users.models import Follow, User
from users.serializers import UserCreateSerializer, UserSuccessSerializer


class UserCreateView(views.APIView):
    """ Вью-класс для регистрации пользователя. """
    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            output = UserSuccessSerializer(request.data)
            return Response(output.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """ Вьюсет для списка карточек пользователей. """
    queryset = User.objects.all()
    serializer_class = UserReadSerializer
    pagination_class = AdjustablePagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,),
        methods=('get',)
    )
    def subscriptions(self, request):
        user = request.user
        queryset = Follow.objects.filter(user=user)
        cur_page = self.paginate_queryset(queryset)
        if queryset.exists():
            serializer = SubscriptionsSerializer(
                cur_page, many=True, context={'request': request})
            return self.get_paginated_response(
                serializer.data, status=status.HTTP_200_OK)
        return Response(
            'errors: Нет подписок.', status=status.HTTP_404_NOT_FOUND)

    @action(
        detail=True,
        permission_classes=(IsAuthenticated,),
        methods=('post', 'delete')
    )
    def subscribe(self, request, pk=None):
        user = request.user
        follow = get_object_or_404(User, id=pk)
        if self.request.method == 'POST':
            if Follow.objects.filter(user=user, following=follow).exists():
                return Response(
                    {'errors': 'Вы уже подписаны'},
                    status=status.HTTP_400_BAD_REQUEST)
            if user == follow:
                return Response(
                    {'errors': 'Подписка на самого себя невозможна.'},
                    status=status.HTTP_400_BAD_REQUEST)
            follow = Follow.objects.create(user=user, following=follow)
            serializer = SubscriptionsSerializer(
                follow, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if Follow.objects.filter(user=user, following=follow).exists():
            sub = get_object_or_404(Follow, user=user, following=follow)
            sub.delete()
            return Response('Вы успешно отписались.',
                            status=status.HTTP_204_NO_CONTENT)
        if user == follow:
            return Response({'errors': 'Отписка от самого себя невозможна.'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response({'errors': 'Подписки не существует.'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,),
        methods=('get',)
    )
    def me(self, request):
        user = request.user
        serializer = UserReadSerializer(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
