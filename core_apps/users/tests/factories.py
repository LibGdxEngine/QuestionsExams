import factory
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from faker import Factory as FakerFactory

from core_apps.profiles.models import FavoriteList

faker = FakerFactory.create()

User = get_user_model()


@factory.django.mute_signals(post_save)
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    first_name = factory.lazy_attribute(lambda x: faker.first_name())
    last_name = factory.lazy_attribute(lambda x: faker.last_name())
    email = factory.LazyAttribute(lambda x: faker.email())
    password = factory.LazyAttribute(lambda x: faker.password())
    is_active = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        manager = cls._get_manager(model_class)
        if "is_superuser" in kwargs:
            return manager.create_superuser(*args, **kwargs)
        else:
            return manager.create_user(*args, **kwargs)

    @classmethod
    def create_with_favorite_list(cls, **kwargs):
        user = cls()
        user.save()
        fvls = FavoriteList.objects.create(user=user, name='My Favorites')
        fvls.save()
        return user
