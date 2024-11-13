from unfazed.contrib.admin.registry import ModelAdmin, register
from unfazed.db.tortoise.serializer import TSerializer

from .models import Article


class ArticleSerializer(TSerializer):
    class Meta:
        model = Article


@register(ArticleSerializer)
class ArticleAdmin(ModelAdmin):
    pass
