from django.urls import path

from .views import ResponseListCreateAPIView, ResponseUpdateDeleteView

# TODO : create path for adding replies to the responses (create parent response for the reply)
urlpatterns = [
    path(
        "article/<uuid:article_id>/",
        ResponseListCreateAPIView.as_view(),
        name="article-responses",
    ),
    path("<uuid:id>/", ResponseUpdateDeleteView.as_view(), name="response-detail"),
]
