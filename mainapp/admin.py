from django.contrib import admin

# Register your models here.

from .models import DeliveryLocation, Product, Tag, ProductImage, Category, Subcategory, BlogPost, Comment

@admin.register(DeliveryLocation)
class DeliveryLocationAdmin(admin.ModelAdmin):
    list_display = ('location', 'deliveries')  # Display location and deliveries in the admin panel
    search_fields = ('location',)  # Enable search by location
    list_filter = ('deliveries',)  # Add filtering by number of deliveries


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3  # Number of empty forms to display by default (can be adjusted)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'weight', 'old_price', 'new_price', 'in_stock', 'qty', 'date', 'sku')
    search_fields = ('name', 'sku')
    list_filter = ('in_stock', 'tags', 'sku')
    inlines = [ProductImageInline]

admin.site.register(Product, ProductAdmin)

admin.site.register(Tag)
admin.site.register(ProductImage)


class SubcategoryInline(admin.TabularInline):
    model = Subcategory
    extra = 1  # Number of empty subcategory rows to show by default

class CategoryAdmin(admin.ModelAdmin):
    inlines = [SubcategoryInline]  # Add subcategories inline with categories

admin.site.register(Category, CategoryAdmin)
admin.site.register(Subcategory)


class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published_at', 'is_published')
    list_filter = ('is_published', 'categories', 'tags', 'author')
    search_fields = ('title', 'content', 'author__username', 'tags__name')
    prepopulated_fields = {'slug': ('title',)}  # Automatically populate the slug field
    ordering = ('-published_at',)


admin.site.register(BlogPost, BlogPostAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'blog_post', 'content', 'created_at', 'is_approved')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('user__username', 'blog_post__title', 'content')
    actions = ['approve_comments', 'disapprove_comments']

    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
    approve_comments.short_description = "Approve selected comments"

    def disapprove_comments(self, request, queryset):
        queryset.update(is_approved=False)
    disapprove_comments.short_description = "Disapprove selected comments"

admin.site.register(Comment, CommentAdmin)
