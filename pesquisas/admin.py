from django.contrib import admin

from .models import DocCategory, DocTag, Document, Organisation


class DocumentOrganisationInline(admin.TabularInline):
    """Documentos associados à organização (tabela intermediária do M2M)."""
    model = Document.organisations.through
    extra = 0
    autocomplete_fields = ('document',)
    verbose_name = 'Documento associado'
    verbose_name_plural = 'Documentos associados'


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'document_count')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = (DocumentOrganisationInline,)

    class Media:
        css = {'all': ('css/admin_organisation.css',)}

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('documents')

    @admin.display(description='Documentos')
    def document_count(self, obj):
        return obj.documents.count()


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
        'list_organisations',
        'category',
        'file_type',
        'link_type',
        'published_at',
        'status',
    )
    list_filter = ('status', 'link_type', 'category', 'organisations', 'file_type', 'creator')
    search_fields = ('title', 'direct_link', 'internal_link', 'creator', 'slug', 'doi', 'authorship')
    autocomplete_fields = ('organisations', 'category')
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
            'fields': ('organisations', 'authorship', 'category', 'file_type', 'tags', 'creator', 'doi'),
        }),
        ('Links e arquivo', {
            'fields': ('link_type', 'direct_link', 'internal_link', 'file', 'file_size', 'download_count'),
        }),
        ('Metadados', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at'),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('organisations')

    @admin.display(description='Organizações')
    def list_organisations(self, obj):
        return ', '.join(o.name for o in obj.organisations.all()) or '—'
