from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.contrib.auth import get_user_model

class BlogConfig(AppConfig):
    name = 'blog'
    
    # Django 3.2+ yêu cầu khai báo default_auto_field
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        # Khi app được load, kết nối signal post_migrate
        # Signal này sẽ chạy sau khi migrate toàn project
        post_migrate.connect(create_default_superuser, sender=self)


def create_default_superuser(sender, **kwargs):
    # Lấy đúng model User đã custom (không import trực tiếp)
    User = get_user_model()

    # Kiểm tra xem superuser 'admin' đã tồn tại chưa
    if not User.objects.filter(username='admin').exists():
        # Nếu chưa có thì tạo mới superuser với các field custom
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            name='Super Admin',
            gender='Nam',
            birth='1990-01-01',
            mark=0
        )

