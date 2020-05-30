from django.contrib import admin
from .models import *


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['author_name', 'author_surname']
    ordering = ['author_name']


@admin.register(ScienceBook)
class ScienceBookAdmin(admin.ModelAdmin):
    list_display = ['title', 'publisher', 'edition', 'publishing_year', 'isbn']
    ordering = ['title']
    filter_horizontal = ['work_author']    # two-sided areas for multiple choice (for ManyToMany)


@admin.register(FictionBook)
class FictionBookAdmin(admin.ModelAdmin):
    list_display = ['title']
    ordering = ['title']
    filter_horizontal = ['work_author']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'journal', 'impact_factor',
                    'volume', 'article_number', 'pages', 'publishing_year', 'doi']
    ordering = ['title']
    filter_horizontal = ['work_author']


@admin.register(LibraryUserInfo)
class LibraryUserInfoAdmin(admin.ModelAdmin):
    list_display = ['library_user', 'phone_number']
    ordering = ['library_user']


@admin.register(CitiesList)
class CitiesListAdmin(admin.ModelAdmin):
    list_display = ['city_name']


@admin.register(StreetsList)
class StreetsListAdmin(admin.ModelAdmin):
    list_display = ['street_name']


@admin.register(LibraryUserAddress)
class LibraryUserAddressAdmin(admin.ModelAdmin):
    list_display = ['building_number', 'apartment_number']
