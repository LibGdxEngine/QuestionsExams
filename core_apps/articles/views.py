import logging

from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from django.http import Http404
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import ArticleFilter
from .models import Article, ArticleView, Clap
from .pagination import ArticlePagination
from .permissions import IsOwnerOrReadOnly
from .renderers import ArticleJSONRenderer, ArticlesJSONRenderer
from .serializers import ArticleSerializer, ClapSerializer

User = get_user_model()

logger = logging.getLogger(__name__)


class ArticleListCreateView(generics.ListCreateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = ArticlePagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = ArticleFilter
    ordering_fields = ["created_at", "updated_at"]
    renderer_classes = [ArticlesJSONRenderer]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        logger.info(
            f"Article Created: {serializer.data.get('title')} by {self.request.user.email}"
        )


class ArticleRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsOwnerOrReadOnly, IsAuthenticated]
    lookup_field = "id"
    renderer_classes = [ArticleJSONRenderer]
    parser_classes = [MultiPartParser, FormParser]

    def perform_update(self, serializer):
        instance = serializer.save(author=self.request.user)
        if "banner_image" in self.request.FILES:
            if (
                instance.banner_image
                and instance.banner_image.name != "/default_banner.png"
            ):
                default_storage.delete(instance.banner_image.path)
            instance.banner_image = self.request.FILES["banner_image"]
            instance.save()

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Http404:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(instance)

        viewer_ip = request.META.get("REMOTE_ADDR", None)
        ArticleView.record_view(
            article=instance, user=request.user, viewer_ip=viewer_ip
        )
        return Response(serializer.data)


class ClapArticleView(generics.CreateAPIView, generics.DestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = ClapSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        article_id = kwargs.get("id", None)
        article = get_object_or_404(Article, id=article_id)

        if Clap.objects.filter(article=article, user=user).exists():
            return Response(
                {"detail": "You have already Clapped to this article"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        clap = Clap.objects.create(article=article, user=user)
        clap.save()
        return Response(
            {"detail": "Successfully clapped to this article"},
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request, *args, **kwargs):
        user = request.user
        article_id = kwargs.get("id", None)
        article = get_object_or_404(Article, id=article_id)

        clap = get_object_or_404(Clap, article=article, user=user)
        clap.delete()
        return Response({"detail": "Clap removed"}, status=status.HTTP_204_NO_CONTENT)
