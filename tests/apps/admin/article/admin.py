from unfazed.contrib.admin.registry import ModelAdmin, register
from unfazed.serializer import Serializer

from .models import Article


class ArticleSerializer(Serializer):
    class Meta:
        model = Article


@register(ArticleSerializer)
class ArticleAdmin(ModelAdmin):
    pass
