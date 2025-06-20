from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from django.views import View
from django.views.generic import ListView, DetailView, FormView
from django.contrib import messages
from .models import Book, Category, Transaction
from .forms import RegistrationForm, DepositForm, BorrowBookForm, ReviewForm, UserProfileForm, BookForm
from datetime import date
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse_lazy
from django.views.generic import TemplateView

class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        books = Book.objects.all()

        category_id = self.request.GET.get('category')
        if category_id:
            books = books.filter(category__id=category_id)

        context['books'] = books
        context['categories'] = Category.objects.all()
        context['user'] = self.request.user 
        return context
    
class RegisterView(FormView):
    template_name = 'register.html'
    success_url = reverse_lazy('login')

    def get(self, request, *args, **kwargs):
        return self.render_to_response({
            'user_form': RegistrationForm(),
            'profile_form': UserProfileForm()
        })

    def post(self, request):
        user_form = RegistrationForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password1'])
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            
            send_mail(
                'Welcome to Our Library',
                f'Hello {user.username},\n\nThank you for registering at our Library Management System.\n\nWe are happy to have you on board!',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
            )

            messages.success(request, 'Account created successfully. Please log in')
            return redirect(self.get_success_url())

        else:
            for form in [user_form, profile_form]:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Error in {field}: {error}")

        return self.render_to_response({
            'user_form': user_form,
            'profile_form': profile_form
        })
        
class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, 'Login Successful')
                return redirect('book_list')
            else:
                messages.error(request, 'Invalid credentials')
        else:
            messages.error(request, 'Please provide both username and password.')

        return render(request, 'login.html')
    
class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, 'Logout Successful')
        return redirect('login')
    
class BookListView(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'book_list.html'
    context_object_name = 'books'

    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category__id=category_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['user_balance'] = self.request.user.profile.balance
        return context

class BorrowBookView(LoginRequiredMixin, View):
    def post(self, request):
        form = BorrowBookForm(request.POST)
        if form.is_valid():
            book_id = form.cleaned_data['book_id']
            book = get_object_or_404(Book, id=book_id)
            user_profile = request.user.profile
            if user_profile.balance >= book.borrowing_price:
                transaction = Transaction.objects.create(user=request.user, book=book, amount=book.borrowing_price)
                user_profile.balance -= book.borrowing_price
                user_profile.save()
                send_mail(
                    'Book Borrow Successful',
                    f'Hello {request.user},\n\nYou have successfully borrowed "{book}".\n\n This book of price {book.borrowing_price} Taka.\n\nThank you!',
                    settings.DEFAULT_FROM_EMAIL,
                    [self.request.user.email]
                )
                messages.success(request, 'Book borrowed successfully')
            else:
                messages.error(request, 'Insufficient balance')
        return redirect('book_list')
    
class ReturnBookView(View):
    def post(self, request, *args, **kwargs):
        transaction_id = kwargs['transaction_id']
        transaction = get_object_or_404(Transaction, pk=transaction_id)
        borrowing_price = transaction.amount  
        user_profile = transaction.user.profile
        user_profile.balance += borrowing_price
        user_profile.save()
        transaction.balance_after_borrow = user_profile.balance
        transaction.return_date = date.today()
        transaction.save()
        send_mail(
            'Book Return Successful',
            f'Hello {request.user.username},\n\nYou have successfully returned the book "{transaction.book.title}".\n\nThank you!',
            settings.DEFAULT_FROM_EMAIL,
            [request.user.email],
        )

        messages.success(request, 'Book returned successfully')
        return redirect('borrow_history')

class BorrowHistoryView(LoginRequiredMixin, ListView):
    template_name = 'borrow_history.html'
    context_object_name = 'transactions'

    def get_queryset(self):
        return self.request.user.transactions.all()

    def post(self, request, *args, **kwargs):
        transaction_id = request.POST.get('transaction_id')
        if transaction_id:
            transaction = Transaction.objects.get(pk=transaction_id)
            transaction.return_date = date.today()
            transaction.save()
        return redirect('borrow_history')

class DepositeMoneyView(LoginRequiredMixin, FormView):
    template_name = 'deposit.html'
    form_class = DepositForm
    success_url = reverse_lazy('book_list')

    def form_valid(self, form):
        amount = form.cleaned_data['amount']
        self.request.user.profile.balance += amount
        self.request.user.profile.save()
        send_mail(
            'Deposit Successful',
            f'You have successfully deposited {amount} Taka to your account.\n\nThank you!',
            settings.DEFAULT_FROM_EMAIL,
            [self.request.user.email]
        )
        messages.success(self.request, 'Deposit successful')
        return super().form_valid(form)

class ReviewBookView(LoginRequiredMixin, View):
    template_name = 'review_book.html'

    def get(self, request, book_id):
        book = get_object_or_404(Book, id=book_id)
        form = ReviewForm()
        return render(request, self.template_name, {'form': form, 'book': book})

    def post(self, request, book_id):
        book = get_object_or_404(Book, id=book_id)
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            review.user = request.user
            review.save()
            return redirect('book_detail', pk=book.id)
        return render(request, self.template_name, {'form': form, 'book': book})

class BookDetailView(LoginRequiredMixin, DetailView):
    model = Book
    template_name = 'book_detail.html'
    context_object_name = 'book'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = self.get_object()
        user = self.request.user
        context['user'] = user
        context['has_borrowed'] = user.profile.has_borrowed(book)
        context['reviews'] = book.reviews.all()  
        return context
    
class AddBookView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        # শুধু staff বা superuser পারবে access করতে
        return self.request.user.is_staff or self.request.user.is_superuser

    def get(self, request):
        form = BookForm()
        return render(request, 'add_book.html', {'form': form})

    def post(self, request):
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book added successfully')
            return redirect('book_list')
        else:
            messages.error(request, 'Failed to add book. Please check the form.')

        return render(request, 'add_book.html', {'form': form})