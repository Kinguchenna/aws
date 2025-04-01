from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from shortuuid.django_fields import ShortUUIDField



class User(AbstractUser):
    ACCOUNT_TYPE_CHOICES = [
        ('user', 'User'),
        ('seller', 'Seller'),
        ('vendor', 'Vendor'),
    ]
    
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE_CHOICES, default='user')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    slug = models.CharField(max_length=15, blank=True, default='slug')
    vendor_name = models.CharField(max_length=255, blank=True, null=True)  # New field for vendor name
    vendor_address = models.CharField(max_length=1255, blank=True, null=True)  # New field for vendor name
    profile_image = models.ImageField(upload_to='user_images/', blank=True, null=True)  # Optional user image
    date_of_birth = models.DateField(blank=True, null=True)

    # Location Data 
    city = models.CharField(max_length=1255, blank=True, null=True)
    country = models.CharField(max_length=1255, blank=True, null=True)
    ip = models.CharField(max_length=1255, blank=True, null=True)
    region = models.CharField(max_length=1255, blank=True, null=True)
    location = models.CharField(max_length=1255, blank=True, null=True)
    




    
    # Add related_name attributes to avoid conflicts
    groups = models.ManyToManyField(Group, related_name='custom_user_groups', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_permissions', blank=True)

    def __str__(self):
        return self.username

class ResetCode(models.Model):
    rsid = ShortUUIDField(unique=True, length=10, max_length=20, prefix='rsid', alphabet='1234567890abcd')
    code = models.CharField(max_length=900, default="code")
    username = models.CharField(max_length=100, default="username")
    email = models.CharField(max_length=100, default="email")
    date = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        verbose_name_plural = "ResetCode"
    
    def __str__(self):
       return self.email
    


        
class Profiles(models.Model):
    # user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, related_name='profile')
    mobile = models.CharField(max_length=15, blank=True, null=True)
    country_code = models.CharField(max_length=5, blank=True, null=True)
    age = models.CharField(max_length=5, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)  # Ensure MEDIA_ROOT is set up for file handling
    address = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)  # Date of Birth
    bio = models.TextField(blank=True, null=True)
    gender = models.TextField(blank=True, null=True)
    gender_visible = models.TextField(blank=True, null=True)
    about = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    account_type = models.CharField(max_length=50, blank=True, null=True)
    height = models.CharField(max_length=50, blank=True, null=True)
    marital_status = models.CharField(max_length=20, blank=True, null=True, choices=[
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
    ])

    def __str__(self):
        return f"{self.user.username}'s Profile"