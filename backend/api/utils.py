# isort: skip_file
import io

from django.db.models import Sum
from django.http import FileResponse
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status, views
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from api.serializers import RecipeMiniSerializer
from recipes.models import ReciIngredi, Recipe


def flag_add_delete(request, pk, model):
    if not request.user.pk:
        return Response(
            {'errors': 'Недоступно анонимным пользователям.'},
            status=status.HTTP_400_BAD_REQUEST)
    user = request.user
    recipe = get_object_or_404(Recipe, pk=pk)
    object = model.objects.filter(user=user, recipe=recipe)
    if request.method == 'POST':
        if object:
            return Response({'errors': 'Рецепт уже добавлен.'},
                            status=status.HTTP_400_BAD_REQUEST)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeMiniSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    if request.method == 'DELETE':
        if not object:
            return Response({'errors': 'Нельзя удалить, не был добавлен.'},
                            status=status.HTTP_400_BAD_REQUEST)
        model.objects.get(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(
        {'errors': 'Не удалось.'}, status=status.HTTP_400_BAD_REQUEST)


class CartPDFExportView(views.APIView):
    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        shopping_list = ReciIngredi.objects.filter(
            recipe__cart__user=user).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            amount=Sum('amount')
        ).order_by()
        pdfmetrics.registerFont(
            TTFont('PTSansRegular', 'PTSans-Regular.ttf', 'UTF-8'))
        pdfmetrics.registerFont(
            TTFont('PTSansBold', 'PTSans-Bold.ttf', 'UTF-8'))
        font = 'PTSansRegular'
        boldfont = 'PTSansBold'
        buffer = io.BytesIO()
        pdf_file = canvas.Canvas(buffer)
        pdf_file.setFont(font, 10)
        pdf_file.drawString(
            230,
            810,
            'СЕРВИС РЕЦЕПТОВ FOODGRAM'
        )
        pdf_file.setFont(boldfont, 26)
        pdf_file.drawString(
            200,
            750,
            'Список покупок:'
        )
        pdf_file.setFont(font, 14)
        from_bottom = 700
        for number, ingredient in enumerate(shopping_list, start=1):
            pdf_file.drawString(
                60,
                from_bottom,
                (f'{number}.  {ingredient["ingredient__name"]} - '
                 f'{ingredient["amount"]} '
                 f'{ingredient["ingredient__measurement_unit"]}')
            )
            from_bottom -= 30
            if from_bottom <= 50:
                from_bottom = 700
                pdf_file.showPage()
                pdf_file.setFont(font, 10)
                pdf_file.drawString(
                    230,
                    810,
                    'СЕРВИС РЕЦЕПТОВ FOODGRAM')
                pdf_file.setFont(font, 14)
        pdf_file.showPage()
        pdf_file.save()
        buffer.seek(0)
        return FileResponse(
            buffer, as_attachment=True, filename='shopping_list.pdf')
