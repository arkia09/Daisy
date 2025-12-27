from django.db import models
from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, InlinePanel
from datetime import datetime
from modelcluster.models import ParentalKey, ParentalManyToManyField
from wagtail.snippets.models import register_snippet
from django import forms
from taggit.models import TaggedItemBase
from modelcluster.contrib.taggit import ClusterTaggableManager


# Create your models here.
class BlogIndexPage(Page):
    description = RichTextField(blank=True)

    content_panels = Page.content_panels + [FieldPanel("description")]
    def get_context(self, request):
        context = super().get_context(request)
        blogposts = self.get_children().live().order_by("-first_published_at")

        context["blogposts"] = blogposts

        return context

class BlogPostTag(TaggedItemBase):
    content_object = ParentalKey("BlogPostPage", related_name="tagged_items", on_delete=models.CASCADE)

class BlogPostPage(Page):
    date = models.DateTimeField("Post Date", default= datetime.now)
    intro = RichTextField(blank=True)
    body = RichTextField(blank = True)
    authors = ParentalManyToManyField("blog.Author", blank=True)
    tags = ClusterTaggableManager(through=BlogPostTag, blank=True)

    def main_image(self):
        thumbnail_image = self.image_gallery.first()
        if thumbnail_image:
            return thumbnail_image.images
        else:
            return None
        
    content_panels = Page.content_panels + [FieldPanel("date"),
                                            FieldPanel("authors", widget=forms.CheckboxSelectMultiple),
                                            FieldPanel("intro"),
                                            FieldPanel("body"),
                                            FieldPanel("tags"),
                                            InlinePanel("image_gallery", label="gallery images")]




class BlogPageImagesGallery(Orderable):
    page = ParentalKey(BlogPostPage, related_name="image_gallery", on_delete=models.CASCADE)
    images = models.ForeignKey("wagtailimages.Image", related_name="+", on_delete=models.CASCADE)
    caption = models.CharField(max_length=100, blank=True)
    panels = [FieldPanel("images"), FieldPanel("caption")]


@register_snippet
class Author(models.Model):
    name = models.CharField(max_length=255)
    author_image = models.ForeignKey("wagtailimages.Image", related_name="+", on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    

class TagIndexPage(Page):
    def get_context(self, request):
        tag = request.GET.get("tag")
        blogposts = BlogPostPage.objects.filter(tags__name=tag).distinct()

        context = super().get_context(request)
        context["blogposts"] = blogposts
        return context

