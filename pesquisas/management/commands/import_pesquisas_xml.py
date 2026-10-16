import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from pesquisas.models import DocCategory, DocTag, Document, Organisation

NS = {
    'content': 'http://purl.org/rss/1.0/modules/content/',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'wp': 'http://wordpress.org/export/1.2/',
}


class Command(BaseCommand):
    help = 'Importa documentos do arquivo WordPress XML (rncdpesquisas.xml).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            default='rncdpesquisas.xml',
            help='Caminho para o arquivo XML de exportação.',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Remove todos os documentos antes de importar.',
        )

    def handle(self, *args, **options):
        xml_path = Path(options['file'])
        if not xml_path.is_absolute():
            xml_path = Path.cwd() / xml_path

        if not xml_path.exists():
            self.stderr.write(self.style.ERROR(f'Arquivo não encontrado: {xml_path}'))
            return

        if options['clear']:
            Document.objects.all().delete()
            self.stdout.write('Documentos existentes removidos.')

        tree = ET.parse(xml_path)
        items = tree.getroot().find('channel').findall('item')

        created = 0
        updated = 0
        skipped = 0

        for item in items:
            post_type = self._text(item, 'wp:post_type')
            status = self._text(item, 'wp:status')
            if post_type != 'dlp_document' or status != 'publish':
                skipped += 1
                continue

            wp_post_id = self._int(item, 'wp:post_id')
            title = self._text(item, 'title') or f'Documento {wp_post_id}'
            slug = self._text(item, 'wp:post_name') or slugify(title) or f'doc-{wp_post_id}'

            meta = self._meta(item)
            published_at = self._parse_datetime(self._text(item, 'wp:post_date'))

            organisation_names = []
            category_name = None
            file_type = ''
            tag_names = []

            for category in item.findall('category'):
                domain = category.get('domain')
                value = (category.text or '').strip()
                if not value:
                    continue
                if domain == 'doc_author':
                    organisation_names.append(value)
                elif domain == 'doc_categories':
                    category_name = value
                elif domain == 'file_type':
                    file_type = value
                elif domain == 'doc_tags':
                    tag_names.append(value)

            category = None
            if category_name:
                category, _ = DocCategory.objects.get_or_create(name=category_name)

            defaults = {
                'title': title,
                'slug': slug,
                'internal_link': self._text(item, 'link') or '',
                'direct_link': meta.get('_dlp_direct_link_url', ''),
                'link_type': meta.get('_dlp_document_link_type', 'url') or 'url',
                'creator': self._text(item, 'dc:creator') or '',
                'category': category,
                'file_type': file_type,
                'file_size': meta.get('_dlp_document_file_size', ''),
                'download_count': self._int_value(meta.get('_dlp_download_count', '0')),
                'published_at': published_at,
                'status': status,
            }

            document, was_created = Document.objects.update_or_create(
                wp_post_id=wp_post_id,
                defaults=defaults,
            )

            if organisation_names:
                organisations = []
                for org_name in organisation_names:
                    organisation, _ = Organisation.objects.get_or_create(name=org_name)
                    organisations.append(organisation)
                document.organisations.set(organisations)
            else:
                document.organisations.clear()

            if tag_names:
                tags = []
                for tag_name in tag_names:
                    tag, _ = DocTag.objects.get_or_create(name=tag_name)
                    tags.append(tag)
                document.tags.set(tags)
            else:
                document.tags.clear()

            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f'Importação concluída: {created} criados, {updated} atualizados, {skipped} ignorados.'
        ))

    def _text(self, item, tag):
        element = item.find(tag, NS) if ':' in tag else item.find(tag)
        if element is not None and element.text:
            return element.text.strip()
        return ''

    def _int(self, item, tag):
        value = self._text(item, tag)
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def _meta(self, item):
        data = {}
        for meta in item.findall('wp:postmeta', NS):
            key = self._text(meta, 'wp:meta_key')
            value = self._text(meta, 'wp:meta_value')
            if key:
                data[key] = value
        return data

    def _int_value(self, value):
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0

    def _parse_datetime(self, value):
        if not value:
            return None
        try:
            dt = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            if timezone.is_naive(dt):
                return timezone.make_aware(dt, timezone.get_current_timezone())
            return dt
        except ValueError:
            return None
