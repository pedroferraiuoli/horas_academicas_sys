from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


def paginate_queryset(qs, *, page, per_page=15):
    paginator = Paginator(qs, per_page)

    try:
        return paginator.page(page)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)
