from unfazed.serializer.tortoise import TSerializer

from .models import Article


class ArticleSerializer(TSerializer):
    class Meta:
        model = Article
