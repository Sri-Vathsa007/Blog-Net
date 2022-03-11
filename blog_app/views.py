from django.shortcuts import render,get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import ListView
from .models import Post
from .forms import CommentForm
from django.views import View

# Create your views here.
class StartingPageView(ListView):
    template_name = "blog_app/home_page.html"
    model = Post
    ordering = ["-date"]
    context_object_name = "latest_post"

    def get_queryset(self):
        queryset = super().get_queryset()
        data = queryset[:3]
        return data

# def home_page(request):
#     latest_post= Post.objects.all().order_by("-date")[:3]
#     return render(request,"blog_app/home_page.html",{
#         "latest_post":latest_post
#     })


class AllPostsView(ListView):
    template_name = "blog_app/all-posts.html"
    model = Post
    ordering = ["-date"]
    context_object_name = "all_posts"

# def posts(request):
#     all_posts = Post.objects.all().order_by("-date")
#     return render(request,"blog_app/all-posts.html",{
#         "all_posts":all_posts
#     })

class SinglePostView(View):
    def is_stored_post(self,request,post_id):
        stored_post = request.session.get("stored_post")
        if stored_post is not None:
            is_saved_for_later = post_id in stored_post
        else:
            is_saved_for_later = False

        return is_saved_for_later


    def get(self, request, slug):
        post = Post.objects.get(slug=slug)
        context = {
            "identified_post":post,
            "post_tags":post.tags.all(),
            "comment_form":CommentForm(),
            "comments":post.comments.all().order_by("-id"),
            "saved_for_later":self.is_stored_post(request,post.id)
        }
        return render(request,"blog_app/post-detail.html", context)


    def post(self,request,slug):
        comment_form = CommentForm(request.POST)
        post = Post.objects.get(slug=slug)


        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.save()
            return HttpResponseRedirect(reverse("post-detail-page",args=[slug]))

        context = {
            "identified_post":post,
            "post_tags":post.tags.all(),
            "comment_form":comment_form,
            "comments":post.comments.all().order_by("-id"),
            "saved_for_later":self.is_stored_post(request,post.id)
        }
        return render(request, "blog_app/post-detail.html", context)


    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context["post_tags"] = self.object.tags.all()
    #     context["comment_form"] = CommentForm()
    #     return context

# def post_detail(request,slug):
#     identified_post= get_object_or_404(Post, slug=slug)
#     return render(request,"blog_app/post-detail.html",{
#         "identified_post":identified_post,
#         "post_tags":identified_post.tags.all()
#     })

class ReadLaterView(View):
    def get(self,request):
        stored_post = request.session.get("stored_post")
        context = {}

        if stored_post is None or len(stored_post)==0:
            context["identified_post"] = []
            context["has_posts"] = False
        else:
            identified_post = Post.objects.filter(id__in=stored_post)
            context["identified_post"] = identified_post
            context["has_posts"] = True

        return render(request,"blog_app/stored-posts.html",context)

    def post(self,request):
        stored_post = request.session.get("stored_post")

        if stored_post is None:
            stored_post = []

        post_id = int(request.POST["post_id"])

        if post_id not in stored_post:
            stored_post.append(post_id)
        else:
            stored_post.remove(post_id)

        request.session["stored_post"] = stored_post

        return HttpResponseRedirect("/")
