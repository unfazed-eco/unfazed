import pytest

from tests.apps.admin.article.models import Article


async def test_jsontext_field() -> None:
    article = Article(
        title="test", author="test", content="test", extra={"test": "test"}
    )
    await article.save()

    assert article.extra == {"test": "test"}  # type: ignore

    with pytest.raises(ValueError):
        article.extra = b"test"  # type: ignore
        await article.save()

    article.extra = "test"
    await article.save()

    ins = await Article.get(id=article.id)

    assert ins.extra == "test"
