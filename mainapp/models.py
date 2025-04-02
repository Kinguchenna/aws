from django.db import models
from userauths.models import User
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.safestring import mark_safe

# Create your models here.

class DeliveryLocation(models.Model):
    location = models.CharField(max_length=255, unique=True)
    deliveries = models.IntegerField(blank=True, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.location


class Product(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Product name
    weight = models.FloatField()  # Weight of the product
    old_price = models.DecimalField(max_digits=10, decimal_places=2)  # Old price
    new_price = models.DecimalField(max_digits=10, decimal_places=2)  # New price
    in_stock = models.BooleanField(default=True)  # Whether the product is in stock
    qty = models.PositiveIntegerField()  # Quantity of product in stock
    date = models.DateTimeField(auto_now_add=True)  # Date added
    image = models.ImageField(upload_to='products/', null=True, blank=True)  # Image field
    description = models.TextField()  # Product description
    product_type = models.CharField(max_length=100)  # Type of the product
    sku = models.CharField(max_length=100, unique=True)  # SKU (Stock Keeping Unit)
    mfg = models.CharField(max_length=255)  # Manufacturer (MFG)
    tags = models.ManyToManyField('Tag', blank=True)  # Tags associated with the product
    care_instructions = models.TextField(blank=True, null=True)  # Care instructions
    additional_info = models.TextField(blank=True, null=True)  # Additional information

    def save(self, *args, **kwargs):
        if self.image:
            # Open the image
            image = Image.open(self.image)

            # Resize the image to a fixed size (e.g., 300x300) using the new LANCZOS filter
            image = image.resize((300, 300), Image.Resampling.LANCZOS)

            # Save the image to a BytesIO object
            image_io = BytesIO()
            image.save(image_io, format='JPEG')

            # Create an InMemoryUploadedFile
            image_file = InMemoryUploadedFile(image_io, None, self.image.name, 'products/jpeg', image_io.tell(), None)

            # Assign the resized image back to the image field
            self.image = image_file

        # Call the parent class save method for Product
        super(Product, self).save(*args, **kwargs)

    def image_tag(self):
        return mark_safe(f'<img src="{self.image.url}" width="150" height="150" style="object-fit: cover;" />')

    image_tag.short_description = 'Image Preview'

    def __str__(self):
        return self.name
    
class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Tag name
    
    def __str__(self):
        return self.name
    


class ProductImage(models.Model):
    product = models.ForeignKey('Product', related_name='images', on_delete=models.CASCADE)  # Link to the Product model
    image = models.ImageField(upload_to='product_images/')  # Store images in the 'product_images/' folder
    alt_text = models.CharField(max_length=255, blank=True, null=True)  # Optional alt text for the image
    is_primary = models.BooleanField(default=False)  # Mark one image as the primary image for the product
    created_at = models.DateTimeField(auto_now_add=True)  # Date when the image was uploaded


    def save(self, *args, **kwargs):
        # Resize the image before saving
        if self.image:
            image = Image.open(self.image)
            # Resize the image to a fixed size (e.g., 300x300) using the new LANCZOS filter
            image = image.resize((300, 300), Image.Resampling.LANCZOS)

            # Save the image to a BytesIO object
            image_io = BytesIO()
            image.save(image_io, format='JPEG')
            image_file = InMemoryUploadedFile(image_io, None, self.image.name, 'product_images/jpeg', image_io.tell(), None)
            self.image = image_file

        super(ProductImage, self).save(*args, **kwargs)

    def image_tag(self):
        return mark_safe(f'<img src="{self.image.url}" width="150" height="150" style="object-fit: cover;" />')

    image_tag.short_description = 'Image Preview'

    def __str__(self):
        return f"Image for {self.product.name}"

    class Meta:
        ordering = ['-created_at'] 


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Category name, e.g., "Electronics"
    description = models.TextField(blank=True, null=True)  # Optional description for the category
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of when the category was created
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']  # Optionally order categories alphabetically by name


class Subcategory(models.Model):
    category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.CASCADE)  # Link to a category
    name = models.CharField(max_length=255)  # Subcategory name, e.g., "Mobile Phones"
    description = models.TextField(blank=True, null=True)  # Optional description for the subcategory
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of when the subcategory was created

    def __str__(self):
        return f"{self.name} ({self.category.name})"  # Display both subcategory and category names

    class Meta:
        ordering = ['name']  # Optionally order subcategories alphabetically by name



class BlogPost(models.Model):
    title = models.CharField(max_length=255)  # Blog post title
    slug = models.SlugField(unique=True)  # URL-friendly version of the title
    content = models.TextField()  # The main content of the blog post
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to the user who authored the post
    categories = models.ManyToManyField(Category, related_name='blog_posts', blank=True)  # Categories of the post
    tags = models.ManyToManyField(Tag, related_name='blog_posts', blank=True)  # Tags for the post
    featured_image = models.ImageField(upload_to='blog_images/', blank=True, null=True)  # Optional featured image
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of when the post was created
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp of when the post was last updated
    published_at = models.DateTimeField(blank=True, null=True)  # Date and time when the post was published
    is_published = models.BooleanField(default=False)  # Flag to indicate if the post is published or not

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-published_at']  # Optionally order blog posts by latest published
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.title.replace(" ", "-").lower()  # Automatically generate slug
        super().save(*args, **kwargs)


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')  # User who posted the comment
    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')  # The blog post being commented on
    content = models.TextField()  # The actual content of the comment
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the comment was created
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp when the comment was last updated
    is_approved = models.BooleanField(default=False)  # Flag to indicate if the comment is approved or pending moderation

    def __str__(self):
        return f"Comment by {self.user.username} on {self.blog_post.title}"

    class Meta:
        ordering = ['-created_at']