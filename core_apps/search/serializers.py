from django_elasticsearch_dsl_drf.serializers import DocumentSerializer

from .documents import ArticleDocument


class ArticleElasticSearchSerializer(DocumentSerializer):
    class Meta:
        document = ArticleDocument
        fields = [
            "id",
            "title",
            "created_at",
            "body",
            "description",
            "tags",
            "author_first_name",
            "author_last_name",
            "banner_image",
        ]
