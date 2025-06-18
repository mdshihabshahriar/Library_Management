from django.urls import path
from .views import RegisterView, LoginView, LogoutView, HomeView,BookListView, BookDetailView, BorrowBookView, ReturnBookView,BorrowHistoryView, DepositeMoneyView, ReviewBookView, AddBookView

urlpatterns = [
    path('',HomeView.as_view(),name='home'), 
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('book/', BookListView.as_view(), name='book_list'),
    path('book/<int:pk>/', BookDetailView.as_view(), name='book_detail'),
    path('borrow/', BorrowBookView.as_view(), name='borrow_book'),
    path('return/<int:transaction_id>/', ReturnBookView.as_view(), name='return_book'),
    path('history/', BorrowHistoryView.as_view(), name='borrow_history'),
    path('deposit/', DepositeMoneyView.as_view(), name='deposit_money'),
    path('add_book/', AddBookView.as_view(), name='add_book'),
    path('book/<int:book_id>/review/', ReviewBookView.as_view(), name='review_book_add'),
    path('book/<int:book_id>/review/', ReviewBookView.as_view(), name='review_book'),   
]