from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from core_apps.articles.models import Article
from core_apps.search.documents import ArticleDocument


@receiver(post_save, sender=Article)
def update_document(sender, instance=None, created=False, **kwargs):
    """Update the ArticleDocument in the elasticsearch when an article instance is updated or created."""
    ArticleDocument().update(instance)


@receiver(post_delete, sender=Article)
def delete_document(sender, instance=None, created=False, **kwargs):
    """Update the ArticleDocument in the elasticsearch when an article instance is deleted."""
    ArticleDocument().delete(instance, ignore=404)
