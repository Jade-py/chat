# base/models.py
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models


class MyUserManager(BaseUserManager):
    def create_user(self, code, password=None, **extra_fields):
        user = self.model(email=code, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, code, password=None, **extra_fields):
        return self.create_user(code, password, **extra_fields)


class tblusers(AbstractBaseUser, PermissionsMixin):
    id =  models.IntegerField(primary_key=True)
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    contactno = models.CharField(max_length=15)
    email = models.EmailField(db_column='emailid', unique=True)
    password = models.CharField(max_length=50)
    usertype = models.CharField(max_length=20)
    createdon = models.DateTimeField()
    createdby = models.IntegerField()
    updatedon = models.DateTimeField()
    updatedby = models.IntegerField()
    isdeleted = models.BooleanField(default=False)
    isagreement = models.BooleanField(default=False)
    ispasswordset = models.BooleanField(default=False)
    wards = models.TextField()
    token = models.CharField(max_length=100)
    token_expiry = models.DateField()
    last_login = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'code'
    REQUIRED_FIELDS = []

    objects = MyUserManager()

    class Meta:
        db_table = 'tblusers'
        managed = True


class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.department.name}"

class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    to_department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    readers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="read_messages",
        blank=True,
        through='MessageReaders'
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat with {self.to_department}"

class MessageReaders(models.Model):
    message = models.ForeignKey('Message', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        db_table = 'base_message_readers'
        unique_together = ('message', 'user')
        managed = False  # Django should not try to create/alter this table


class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
