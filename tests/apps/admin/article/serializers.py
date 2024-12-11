from unfazed.serializer import Serializer

from .models import Article


class ArticleSerializer(Serializer):
    class Meta:
        model = Article
