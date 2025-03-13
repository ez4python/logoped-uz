from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **kwargs):
        if not phone_number:
            raise ValueError("The phone-number field must be set!")
        user = self.model(phone_number=phone_number, **kwargs)
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_superuser(self, phone_number, password=None, **kwargs):
        kwargs.setdefault("is_staff", True)
        kwargs.setdefault("is_superuser", True)
        return self.create_user(phone_number, password, **kwargs)
