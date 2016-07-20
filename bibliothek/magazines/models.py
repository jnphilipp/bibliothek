# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.template.defaultfilters import slugify
from languages.models import Language
from links.models import Link


class TextFieldSingleLine(models.TextField):
    pass


class Magazine(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    slug = models.SlugField(max_length=2048, unique=True)
    name = TextFieldSingleLine(unique=True)

    feed = models.ForeignKey(Link, on_delete=models.CASCADE, related_name='magazine_feed', blank=True, null=True)
    links = models.ManyToManyField(Link, related_name='magazines', blank=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        else:
            orig = Magazine.objects.get(pk=self.id)
            if orig.name != self.name:
                self.slug = slugify(self.name)
        super(Magazine, self).save(*args, **kwargs)


    def __str__(self):
        return self.name


    class Meta:
        ordering = ('name',)


class Issue(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    slug = models.SlugField(max_length=2048, unique=True)
    issue = TextFieldSingleLine(unique=True)
    magazine = models.ForeignKey(Magazine, on_delete=models.CASCADE, related_name='issues')
    published_on = models.DateField(blank=True, null=True)
    languages = models.ManyToManyField(Language, related_name='issues', blank=True)

    files = GenericRelation('files.File')
    cover_image = models.ImageField(upload_to='issues', blank=True, null=True)
    links = models.ManyToManyField(Link, related_name='issues', blank=True)

    acquisitions = GenericRelation('shelves.Acquisition')
    reads = GenericRelation('shelves.Read')


    def move_file(self, file):
        save_name = os.path.join('magazines', str(self.magazine.id), str(self.id), os.path.basename(file.file.name))

        current_path = os.path.join(settings.MEDIA_ROOT, file.file.name)
        new_path = os.path.join(settings.MEDIA_ROOT, save_name)

        if os.path.exists(current_path) and current_path != new_path:
            if not os.path.exists(os.path.dirname(new_path)):
                os.makedirs(os.path.dirname(new_path))
            shutil.move(current_path, new_path)
            file.file.name = save_name
            file.save()


    def move_cover_image(self):
        save_name = os.path.join('magazines', str(self.magazine.id), str(self.id), 'cover%s' % os.path.splitext(self.cover_image.name)[1])

        current_path = os.path.join(settings.MEDIA_ROOT, self.cover_image.name)
        new_path = os.path.join(settings.MEDIA_ROOT, save_name)

        if os.path.exists(current_path) and current_path != new_path:
            if not os.path.exists(os.path.dirname(new_path)):
                os.makedirs(os.path.dirname(new_path))
            shutil.move(current_path, new_path)
            self.cover_image.name = save_name


    def save(self, *args, **kwargs):
        if not 'magazines' in self.cover_image.name:
            self.move_cover_image()
        if not self.slug:
            self.slug = slugify('%s %s' % (self.magazine.name, self.issue))
        else:
            orig = Issue.objects.get(pk=self.id)
            if orig.issue != self.issue or orig.magazine.name != self.magazine.name:
                self.slug = slugify('%s %s' % (self.magazine.name, self.issue))
        super(Issue, self).save(*args, **kwargs)
        for file in self.files.all():
            if not 'magazines' in file.file:
                self.move_file(file)


    def __str__(self):
        return '%s %s' % (self.magazine.name, self.issue)


    class Meta:
        ordering = ('magazine', 'issue')
