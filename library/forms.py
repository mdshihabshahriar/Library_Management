from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile,Review,Book

class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email','password1','password2']
        
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['balance']
        
class DepositForm(forms.Form):
    amount = forms.DecimalField(max_digits=10,decimal_places=2)
    
class BorrowBookForm(forms.Form):
    book_id = forms.IntegerField(widget=forms.HiddenInput())

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['review']
        
class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = '__all__'