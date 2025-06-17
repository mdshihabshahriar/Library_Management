from django.db import models
from django.contrib.auth.models import User
from datetime import date

class Category(models.Model):
    name = models.CharField(max_length = 150)
    
    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length = 100)
    description = models.TextField()
    image = models.ImageField(upload_to='books/',null=True,blank=True)
    category = models.ManyToManyField(Category)
    
    def __str__(self):
        return self.title
    
class Transaction(models.Model):
    user = models.ForeignKey(User, related_name='transactions', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    borrow_date = models.DateField(default=date.today)
    return_date = models.DateField(blank=True, null=True)
    balance_after_borrow = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def is_borrowed(self):
        return self.return_date is None
    
    def __str__(self):
        return f"Transaction #{self.id} - {self.user.username} borrowed {self.book.title}"
    
class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review by {self.user.username} on {self.book.title}'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name = 'profile')
    balance = models.DecimalField(max_digits = 10,decimal_places = 2,default = 0.00)
    borrowed_books = models.ManyToManyField(Book,related_name='borrowed_by',blank=True)
    
    def has_borrowed(self, book):
        return self.user.transactions.filter(book=book, return_date__isnull=True).exists()
    
    def __str__(self):
        return self.user.username