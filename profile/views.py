import os
import html
import json
from django.contrib.auth.decorators import login_required
from authentication.models import User
from django.db.models import F
from django.shortcuts import render, HttpResponse
import boto3
from profile.utils import is_liked
from venue.models import Image, Tag
from venue.utils import in_bucket
S3_BUCKET = os.environ.get('S3_BUCKET')


def profile(request, username):
    about_text = html.escape(User.objects.get(username=username).about_text)
    current_user = request.user.username
    return render(request, 'profile/profile.html', {'uploader': username, 'about_text': about_text, 'current_user': current_user})


def category_view(request, username, category):
    uploader = User.objects.get(username=username)
    current_user = request.user.username
    if category == "all":
        images = Image.objects.filter(uploader_id=uploader.id)
    else:
        images = Image.objects.filter(tags__contains=[category.lower()], uploader_id=uploader.id)
    urls = {}
    for i in range(len(images)):
        image = images[i]
        image_id = str(image.id)
        key = image_id + "." + image.ext
        s3 = boto3.client('s3', region_name='eu-west-3')
        if in_bucket("resized/" + key, s3=s3):
            s3_key = "resized/" + key
        else:
            s3_key = key
        url = s3.generate_presigned_url(ClientMethod="get_object",
                                        Params={'Bucket': S3_BUCKET,
                                                'Key': s3_key},
                                        ExpiresIn=86400)
        urls[url] = {'key': image_id, 'idx': i}

    try:
        tag_description = Tag.objects.get(name=category.lower()).description
    except Tag.DoesNotExist:
        tag_description = ""

    return render(request, 'profile/category.html', {'urls': urls, 'category': category,
                                                     'description': tag_description, 'uploader': username,
                                                     'current_user': current_user})


def image(request, username, category):
    current_user = request.user.username
    s3 = boto3.client('s3', region_name='eu-west-3')
    urls = {}
    thumbnail_urls = {}
    medium_urls = {}
    selected = request.GET.get("selected")
    uploader = User.objects.get(username=username)
    if category == "all":
        images = Image.objects.filter(uploader_id=uploader.id)
    else:
        images = Image.objects.filter(tags__contains=[category.lower()], uploader_id=uploader.id)
    image_ids = []
    for i in range(images.count()):
        image = images[i]
        image_id = str(image.id)
        image_ids.append(image_id)
        title = image.title
        description = image.description
        liked = image_id in User.objects.get(username=current_user).liked_images
        url = s3.generate_presigned_url(ClientMethod="get_object",
                                        Params={'Bucket': S3_BUCKET,
                                                'Key': image_id + "." + image.ext},
                                        ExpiresIn=86400)
        medium_url = s3.generate_presigned_url(ClientMethod="get_object",
                                               Params={'Bucket': S3_BUCKET,
                                                       'Key': 'resized_med/' + image_id + "." + image.ext},
                                               ExpiresIn=86400)
        urls[i] = {"key": image_id, "idx": i, "title": title, 'url': url, 'medium_url': medium_url,
                   'description': description, 'liked': liked}
        thumbnail_url = s3.generate_presigned_url(ClientMethod="get_object",
                                                  Params={'Bucket': S3_BUCKET,
                                                          'Key': 'resized/' + image_id + "." + image.ext},
                                                  ExpiresIn=86400)
        thumbnail_urls[i] = {"key": image_id, "idx": i, "title": title, 'url': thumbnail_url,
                             'description': description, 'liked': liked}
    if selected not in image_ids:
        selected = '0'
    selected_title = Image.objects.get(id=int(selected)).title
    selected_description = Image.objects.get(id=int(selected)).description
    selected_liked = selected in User.objects.get(username=current_user).liked_images
    return render(request, 'profile/img-view.html', {'urls': urls, 'selected': selected,
                                                     'thumbnail_urls': thumbnail_urls, 'selected_title': selected_title,
                                                     'medium_urls': medium_urls, 'uploader': username,
                                                     'current_user': current_user, 'selected_liked': selected_liked,
                                                     'selected_description': selected_description})


@login_required()
def toggle_like(request):
    """Handles POST request which toggles the liking of a given image by the user"""
    image_id = request.POST.get("image_id")
    username = request.user.username
    user = User.objects.get(username=username)
    if is_liked(username, image_id):
        Image.objects.filter(id=int(image_id)).update(likes=F('likes') - 1)
        user.liked_images.remove(image_id)
        response = "Unliked"
    else:
        Image.objects.filter(id=int(image_id)).update(likes=F('likes') + 1)
        user.liked_images.append(image_id)
        response = "Liked"
    user.save()
    return HttpResponse(content=response, content_type="text/plain")


@login_required()
def edit_description(request):
    if request.method != "POST":
        return HttpResponse(status=405)
    tag_name = request.POST.get("tag").lower()
    if tag_name:
        Tag.objects.filter(name=tag_name, uploader_id=request.user.id).update(description=request.POST.get("description"))
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=400, content="tag not provided")


@login_required()
def edit_about_text(request):
    new_text = request.POST.get("about_text")
    if new_text:
        User.objects.filter(id=request.user.id).update(about_text=new_text)
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=400, content="new text not provided")


def get_metadata(request):
    image_id = request.GET.get("imageid")
    try:
        image_id_int = int(image_id)
    except ValueError:
        return HttpResponse(status=400, content="Invalid image id")
    try:
        liked = image_id in User.objects.get(id=request.user.id).liked_images
        description = Image.objects.get(id=image_id_int).description
    except Image.DoesNotExist:
        return HttpResponse(status=400, content="Invalid image id")
    return HttpResponse(status=200, content=json.dumps({"liked": liked, "description": description}),
                        content_type="application/json")


def about(request, username):
    return render(request, 'profile/about.html', {'uploader': username})

