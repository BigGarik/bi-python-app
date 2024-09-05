import logging

import requests
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from web.services.rbc_news_parser import fetch_rss_feed, parse_rss_feed

logger = logging.getLogger(__name__)


class NewsFeedView(APIView):
    def get(self, request, format=None):
        url = "https://rssexport.rbc.ru/rbcnews/news/30/full.rss"  # замените на URL вашей RSS ленты
        try:
            rss_data = fetch_rss_feed(url)
            news_items = parse_rss_feed(rss_data)
            return Response(news_items, status=status.HTTP_200_OK)
        except requests.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
