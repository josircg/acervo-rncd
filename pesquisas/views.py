from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render

from .models import DocAuthor, DocCategory, DocTag, Document


def document_search(request):
    queryset = Document.objects.filter(status='publish').select_related(
        'doc_author',
        'category',
    ).prefetch_related('tags')

    q = request.GET.get('q', '').strip()
    author_id = request.GET.get('autor', '').strip()
    category_id = request.GET.get('categoria', '').strip()
    tag_id = request.GET.get('tag', '').strip()
    file_type = request.GET.get('tipo_arquivo', '').strip()
    link_type = request.GET.get('tipo_link', '').strip()
    creator = request.GET.get('cadastrado_por', '').strip()
    date_from = request.GET.get('data_inicio', '').strip()
    date_to = request.GET.get('data_fim', '').strip()

    if q:
        queryset = queryset.filter(
            Q(title__icontains=q)
            | Q(direct_link__icontains=q)
            | Q(internal_link__icontains=q)
            | Q(creator__icontains=q)
            | Q(doc_author__name__icontains=q)
            | Q(category__name__icontains=q)
            | Q(tags__name__icontains=q)
        ).distinct()

    if author_id:
        queryset = queryset.filter(doc_author_id=author_id)

    if category_id:
        queryset = queryset.filter(category_id=category_id)

    if tag_id:
        queryset = queryset.filter(tags__id=tag_id)

    if file_type:
        queryset = queryset.filter(file_type=file_type)

    if link_type:
        queryset = queryset.filter(link_type=link_type)

    if creator:
        queryset = queryset.filter(creator__iexact=creator)

    if date_from:
        queryset = queryset.filter(published_at__date__gte=date_from)

    if date_to:
        queryset = queryset.filter(published_at__date__lte=date_to)

    paginator = Paginator(queryset, 25)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')
    querystring = query_params.urlencode()

    file_types = (
        Document.objects.filter(status='publish')
        .exclude(file_type='')
        .values_list('file_type', flat=True)
        .distinct()
        .order_by('file_type')
    )

    creators = (
        Document.objects.filter(status='publish')
        .exclude(creator='')
        .values_list('creator', flat=True)
        .distinct()
        .order_by('creator')
    )

    context = {
        'page_obj': page_obj,
        'total_results': paginator.count,
        'querystring': querystring,
        'filters': {
            'q': q,
            'autor': author_id,
            'categoria': category_id,
            'tag': tag_id,
            'tipo_arquivo': file_type,
            'tipo_link': link_type,
            'cadastrado_por': creator,
            'data_inicio': date_from,
            'data_fim': date_to,
        },
        'authors': DocAuthor.objects.all(),
        'categories': DocCategory.objects.all(),
        'tags': DocTag.objects.all(),
        'file_types': file_types,
        'creators': creators,
        'link_type_choices': Document.LINK_TYPE_CHOICES,
        'has_active_filters': any([
            q, author_id, category_id, tag_id, file_type,
            link_type, creator, date_from, date_to,
        ]),
    }
    return render(request, 'pesquisas/index.html', context)
