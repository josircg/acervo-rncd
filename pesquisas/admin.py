from django.contrib import admin

from .models import DocAuthor, DocCategory, DocTag, Document


@admin.register(DocAuthor)
class DocAuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(DocCategory)
class DocCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(DocTag)
class DocTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'doc_author',
        'category',
        'file_type',
        'link_type',
        'published_at',
        'status',
    )
    list_filter = ('status', 'link_type', 'category', 'doc_author', 'file_type', 'creator')
    search_fields = ('title', 'direct_link', 'internal_link', 'creator', 'slug')
    autocomplete_fields = ('doc_author', 'category')
    filter_horizontal = ('tags',)
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'published_at'
    fieldsets = (
        (None, {
            'fields': (
                'title',
                'slug',
                'status',
                'published_at',
                'wp_post_id',
            ),
        }),
        ('Classificação', {
            'fields': ('doc_author', 'category', 'file_type', 'tags', 'creator'),
        }),
        ('Links', {
            'fields': ('link_type', 'direct_link', 'internal_link', 'file_size', 'download_count'),
        }),
        ('Metadados', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at'),
        }),
    )
