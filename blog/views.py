from django.shortcuts import render, render_to_response, get_object_or_404
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Count
from .models import Blog, BlogType
from read_statistics.utils import read_statistics_once_read


def get_blog_list_common_date(request, blog_all_list):
    page_num = request.GET.get('page', 1)   # get page num, default page 1
    paginator = Paginator(blog_all_list, settings.EACH_PAGE_BLOGS_NUMBER)    # one page blogs_number_each_page blogs
    page_of_blogs = paginator.get_page(page_num)
    
    # get current page, show most 5 pages
    current_page_num = page_of_blogs.number
    page_range = list(range(max(1, current_page_num-2), min(paginator.num_pages, current_page_num+2)+1))

    # tag......
    if page_range[0] -1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')
    
    # the first and the last page(if there's tag, there must be extra page)
    if page_range[0] !=1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)
    
    
    # get the count of different dates
    blog_dates = Blog.objects.dates('create_time', 'month', order='DESC')
    blog_dates_dict = {}
    for blog_date in blog_dates:
        blog_count = Blog.objects.filter(create_time__year=blog_date.year, create_time__month=blog_date.month).count()
        blog_dates_dict[blog_date] = blog_count

    context = {}
    context['blogs'] = page_of_blogs.object_list
    context['page_of_blogs'] = page_of_blogs
    context['page_range'] = page_range
    context['blog_types'] = BlogType.objects.annotate(blog_count=Count('blog')) # get the count of different types of blogs
    context['blog_dates'] = blog_dates_dict
    return context


def blog_list(request):
    blog_all_list = Blog.objects.all()

    context = get_blog_list_common_date(request, blog_all_list)
    
    return render(request, 'blog/blog_list.html', context)


def blogs_with_type(request, blog_type_pk):
    blog_type = get_object_or_404(BlogType, pk=blog_type_pk)
    blog_all_list = Blog.objects.filter(blog_type=blog_type)
    
    context = get_blog_list_common_date(request, blog_all_list)
    context['blog_type'] = blog_type
 
    return render(request, 'blog/blogs_with_type.html', context)


def blogs_with_date(request, year, month):
    blog_all_list = Blog.objects.filter(create_time__year=year, create_time__month=month)
    
    context = get_blog_list_common_date(request, blog_all_list)
    context['blogs_with_date'] = '%s-%s' % (year, month)

    return render(request, 'blog/blogs_with_date.html', context)


def blog_detail(request, blog_pk):
    blog = get_object_or_404(Blog, pk=blog_pk)

    read_cookie_key = read_statistics_once_read(request, blog)
    
    context = {}
    context['blog'] = blog
    context['previous_blog'] = Blog.objects.filter(create_time__gt=blog.create_time).last()
    context['next_blog'] = Blog.objects.filter(create_time__lt=blog.create_time).first()
    response = render(request, 'blog/blog_detail.html', context)    # 相应
    response.set_cookie(read_cookie_key, 'true')    # 阅读cookie标记
    return response

