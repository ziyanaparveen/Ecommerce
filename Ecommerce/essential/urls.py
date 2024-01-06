from django.urls import path
from .import views



urlpatterns = [
    
    path('',views.index,name='index'),
    path('add_product/',views.addProduct,name='add_product'),
    path('product_desc/<str:pk>/',views.productDesc,name='product_desc'),
    path('add_to_cart/<str:pk>/',views.add_to_cart,name='add_to_cart'),
    path('orderlist/',views.orderlist,name='orderlist'),
    path('add_item/<int:pk>/',views.add_item,name='add_item'),
    path('remove_item/<int:pk>/',views.remove_item,name='remove_item'),
    path('checkout_page/',views.checkout_page,name='checkout_page'),
    path('payment/',views.payment,name='payment'),
    path('handlerequest/',views.handlerequest,name='handlerequest'),
    path('invoice/',views.invoice,name='invoice'),
    path('update_product/<int:pk>/',views.updateProduct,name='update_product'),
    path('delete_product/<int:pk>/',views.deleteProduct,name='delete_product'),
]



