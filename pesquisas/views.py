from django.core.paginator import Paginator
from django.db.models import F, Q
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from .models import DocCategory, DocTag, Document, Organisation


def document_search(request):
    queryset = Document.objects.filter(status='publish').select_related(
        'category',
    ).prefetch_related('organisations', 'tags')

    q = request.GET.get('q', '').strip()
    organisation_id = request.GET.get('organizacao', '').strip()
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
            | Q(authorship__icontains=q)
            | Q(organisations__name__icontains=q)
            | Q(category__name__icontains=q)
            | Q(tags__name__icontains=q)
        ).distinct()

    if organisation_id:
        queryset = queryset.filter(organisations__id=organisation_id)

    if category_id:
        queryset = queryset.filter(category_id=category_id)

    if tag_id:
        queryset = queryset.filter(tags__id=tag_id)

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

    context = {
        'page_obj': page_obj,
        'total_results': paginator.count,
        'querystring': querystring,
        'filters': {
            'q': q,
            'organizacao': organisation_id,
            'categoria': category_id,
            'tag': tag_id,
            'data_inicio': date_from,
            'data_fim': date_to,
        },
        'organisations': Organisation.objects.all(),
        'categories': DocCategory.objects.all(),
        'tags': DocTag.objects.all(),
        'has_active_filters': any([
            q, organisation_id, category_id, tag_id, date_from, date_to,
        ]),
    }
    return render(request, 'pesquisas/index.html', context)


def document_open(request, pk):
    """Contabiliza o clique no botão "Abrir" e redireciona ao destino.

    Reaproveita o campo ``download_count`` do documento, incrementando-o de
    forma atômica, e redireciona para a URL resolvida por ``access_url``
    (link direto externo ou link interno). Documentos inexistentes, não
    publicados ou sem URL de destino resultam em 404.
    """
    document = get_object_or_404(Document, pk=pk, status='publish')

    url = document.access_url
    if not url:
        raise Http404('Documento sem link de destino.')

    Document.objects.filter(pk=pk).update(
        download_count=F('download_count') + 1,
    )

    return HttpResponseRedirect(url)
