from django.db import models
from django.contrib.auth.models import User


class Author(models.Model):
    # one author can write several works, and one work can be written by several authors -- ManyToMany relationship
    author_name = models.CharField(max_length=100)
    author_surname = models.CharField(max_length=100)

    def __str__(self):
        name_surname = str(self.author_name) + " " + str(self.author_surname)
        return name_surname

    class Meta:
        verbose_name_plural = '1. Authors'    # number is used for custom ordering in the admin page


class FictionBook(models.Model):
    work_author = models.ManyToManyField(Author,
                                         related_name='fiction_book_authors')  # ???
    title = models.CharField(max_length=300)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = '2. Fiction books'


class ScienceBook(models.Model):
    work_author = models.ManyToManyField(Author,
                                         related_name='science_book_authors')  # ???
    title = models.CharField(max_length=300)
    publisher = models.CharField(max_length=200)
    edition = models.PositiveSmallIntegerField(default=1)
    publishing_year = models.DateField(auto_now=False, auto_now_add=False)
    isbn = models.CharField(max_length=200)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = '3. Science books'


class Article(models.Model):
    work_author = models.ManyToManyField(Author,
                                         related_name='article_authors')    # ???
    title = models.CharField(max_length=300)
    journal = models.CharField(max_length=300)
    impact_factor = models.PositiveSmallIntegerField(default=1)
    volume = models.PositiveSmallIntegerField(default=1)
    article_number = models.PositiveSmallIntegerField(default=1)
    pages = models.CharField(max_length=20)    # CharField because of range: "aaa-bbb" pages
    publishing_year = models.DateField(auto_now=False, auto_now_add=False)
    doi = models.CharField(max_length=200)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = '4. Articles'


class LibraryUnit(models.Model):
    fiction_book_unit_type = models.OneToOneField(FictionBook, on_delete=models.CASCADE)
    science_book_unit_type = models.OneToOneField(ScienceBook, on_delete=models.CASCADE)
    article_unit_type = models.OneToOneField(Article, on_delete=models.CASCADE)
    unit_available = models.BooleanField(default=True)


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

    def __str__(self):
        return self.library_user.__str__()

    class Meta:
        verbose_name_plural = '5. Library user info'


class LibraryUserAddress(models.Model):
    library_user_info = models.OneToOneField(LibraryUserInfo, on_delete=models.CASCADE)
    building_number = models.PositiveSmallIntegerField()
    apartment_number = models.PositiveSmallIntegerField()

    class Meta:
        verbose_name_plural = '6. Library user addresses'


class CitiesList(models.Model):
    city_info = models.OneToOneField(LibraryUserAddress, on_delete=models.CASCADE)
    city_name = models.CharField(max_length=200)

    class Meta:
        verbose_name_plural = '7. Cities list'


class StreetsList(models.Model):
    street_info = models.OneToOneField(LibraryUserAddress, on_delete=models.CASCADE)
    street_name = models.CharField(max_length=200)

    class Meta:
        verbose_name_plural = '8. Streets list'

