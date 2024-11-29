from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from web.services.cbr_key_indicators import get_combined_financial_rates


class CrbRatesView(APIView):
    def get(self, request):
        try:
            combined_rates = get_combined_financial_rates()

            return Response(combined_rates, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)})
