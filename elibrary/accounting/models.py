from django.db import models
from django.contrib.auth.models import User


class Author(models.Model):
    # one author can write several works, and one work can be written by several authors -- ManyToMany relationship
    author_name = models.CharField(max_length=100)
    author_surname = models.CharField(max_length=100)


class FictionBook(models.Model):
    work_author = models.ManyToManyField(Author,
                                         related_name='fiction_book_authors')  # ???
    title = models.CharField(max_length=300)


class ScienceBook(models.Model):
    work_author = models.ManyToManyField(Author,
                                         related_name='science_book_authors')  # ???
    title = models.CharField(max_length=300)
    publisher = models.CharField(max_length=200)
    edition = models.PositiveSmallIntegerField()
    publishing_year = models.DateField(auto_now=False, auto_now_add=False)
    isbn = models.CharField(max_length=200)


class Article(models.Model):
    work_author = models.ManyToManyField(Author,
                                         related_name='article_authors')    # ???
    title = models.CharField(max_length=300)
    journal = models.CharField(max_length=300)
    impact_factor = models.PositiveSmallIntegerField()
    volume = models.PositiveSmallIntegerField()
    article_number = models.PositiveSmallIntegerField()
    pages = models.CharField(max_length=20)    # CharField because of range: "aaa-bbb" pages
    publishing_year = models.DateField(auto_now=False, auto_now_add=False)
    doi = models.CharField(max_length=200)


class LibraryUnit(models.Model):
    fiction_book_unit_type = models.OneToOneField(FictionBook, on_delete=models.CASCADE)
    science_book_unit_type = models.OneToOneField(ScienceBook, on_delete=models.CASCADE)
    article_unit_type = models.OneToOneField(Article, on_delete=models.CASCADE)
    unit_available = models.BooleanField()


class UnitStatus(models.Model):
    library_user = models.ForeignKey(User, on_delete=models.CASCADE)
    library_unit = models.ForeignKey(LibraryUnit, on_delete=models.CASCADE)
    date_issue = models.DateTimeField()
    date_return_nominal = models.DateTimeField()
    date_return_actual = models.DateTimeField()
    # two different "date return" to check if user late in library unit return


class LibraryUserInfo(models.Model):
    library_user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number = models.PositiveIntegerField()


class LibraryUserAddress(models.Model):
    library_user_info = models.OneToOneField(LibraryUserInfo, on_delete=models.CASCADE)
    building_number = models.PositiveSmallIntegerField()
    apartment_number = models.PositiveSmallIntegerField()


class CitiesList(models.Model):
    city_info = models.OneToOneField(LibraryUserAddress, on_delete=models.CASCADE)
    city_name = models.CharField(max_length=200)


class StreetsList(models.Model):
    street_info = models.OneToOneField(LibraryUserAddress, on_delete=models.CASCADE)
    street_name = models.CharField(max_length=200)
