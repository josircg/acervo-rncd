from django.db import models
from django.utils.text import slugify


class DocAuthor(models.Model):
    name = models.CharField('Membro', max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Membro'
        verbose_name_plural = 'Membros'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name) or 'membro'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class DocCategory(models.Model):
    name = models.CharField('Categoria', max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name) or 'categoria'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class DocTag(models.Model):
    name = models.CharField('Tag', max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name) or 'tag'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Document(models.Model):
    LINK_TYPE_CHOICES = [
        ('url', 'URL externa'),
        ('file', 'Arquivo'),
        ('none', 'Sem link'),
    ]

    wp_post_id = models.PositiveIntegerField('ID WordPress', unique=True, null=True, blank=True)
    title = models.CharField('Título', max_length=500)
    slug = models.SlugField('Slug', max_length=500, unique=True)
    internal_link = models.URLField('Link interno', max_length=1000, blank=True)
    direct_link = models.URLField('Link direto', max_length=2000, blank=True)
    link_type = models.CharField('Tipo de link', max_length=20, choices=LINK_TYPE_CHOICES, default='url')
    creator = models.CharField('Cadastrado por', max_length=100, blank=True, db_index=True)
    doc_author = models.ForeignKey(
        DocAuthor,
        verbose_name='Membro',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents',
    )
    category = models.ForeignKey(
        DocCategory,
        verbose_name='Categoria',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents',
    )
    file_type = models.CharField('Tipo de arquivo', max_length=255, blank=True, db_index=True)
    tags = models.ManyToManyField(DocTag, verbose_name='Tags', blank=True, related_name='documents')
    file_size = models.CharField('Tamanho', max_length=50, blank=True)
    download_count = models.PositiveIntegerField('Downloads', default=0)
    published_at = models.DateTimeField('Data de publicação', null=True, blank=True, db_index=True)
    status = models.CharField('Status', max_length=20, default='publish', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at', 'title']
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
        indexes = [
            models.Index(fields=['status', '-published_at']),
        ]

    def __str__(self):
        return self.title

    @property
    def access_url(self):
        return self.direct_link or self.internal_link
