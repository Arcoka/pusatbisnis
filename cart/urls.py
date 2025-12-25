from django.urls import path 
from . import views 

urlpatterns = [ 
    path('', views.berandapenjualan, name='berandapenjualan'),

    # Slide Penjualan Admin
    path('slidepenjualanadmin/', views.slidepenjualanadmin, name='slidepenjualanadmin'),
    path('form-slidepenjualan/', views.formslidepenjualanadmin, name='formslidepenjualanadmin'),
    path('edit-slidepenjualan/<str:token>/', views.editslidepenjualanadmin, name='editslidepenjualanadmin'),
    path('berandapenjualan/delete-slidepenjualan/<str:token>/', views.deleteslidepenjualanadmin, name='deleteslidepenjualanadmin'),

    # Pesan Admin
    path('berandapenjualan/pesan/', views.pesanadmin, name='pesanadmin'),
    path('berandapenjualan/pesan/delete/<str:token>/', views.delete_pesanadmin, name='delete_pesanadmin'),

    # Like Admin
    path('berandapenjualan/like/', views.likeadmin, name='likeadmin'),
    path('berandapenjualan/like/delete/<str:token>/', views.delete_likeadmin, name='delete_likeadmin'),
    
    # Jasa Admin
    path('jasaadmin/', views.jasaadmin, name='jasaadmin'),
    path('form-jasa/', views.formjasaadmin, name='formjasaadmin'),
    path('edit-jasa/<str:token>/', views.editjasaadmin, name='editjasaadmin'),
    path('berandapenjualan/delete-jasa/<str:token>/', views.deletejasaadmin, name='deletejasaadmin'),

    # Produk Admin
    path('produkadmin/', views.produkadmin, name='produkadmin'),
    path('berandapenjualan/form-produk/', views.formprodukadmin, name='formprodukadmin'),
    path('berandapenjualan/edit-produk/<str:token>/', views.editprodukadmin, name='editprodukadmin'),
    path('berandapenjualan/delete-produk/<str:token>/', views.deleteprodukadmin, name='deleteprodukadmin'),
    # Fallback by ID when token is missing
    path('berandapenjualan/edit-produk-id/<int:pk>/', views.editprodukadmin_by_id, name='editprodukadmin_by_id'),
    path('berandapenjualan/delete-produk-id/<int:pk>/', views.deleteprodukadmin_by_id, name='deleteprodukadmin_by_id'),
    # Pesan form (public)
    path('produk/pesan/<str:token>/', views.pesan_produk, name='pesan_produk'),
    path('produk/pesan-id/<int:pk>/', views.pesan_produk_by_id, name='pesan_produk_by_id'),

    # Like action (public)
    path('produk/like/<str:token>/', views.like_produk, name='like_produk'),
    path('produk/like-id/<int:pk>/', views.like_produk_by_id, name='like_produk_by_id'),

    # Backward-compatible aliases
    path('produk/tertarik/<str:token>/', views.tertarik_produk, name='tertarik_produk'),
    path('produk/tertarik-id/<int:pk>/', views.tertarik_produk_by_id, name='tertarik_produk_by_id'),
    # Aliases under admin penjualan prefix so links like /administrator/penjualan/produk/... also work
    path('berandapenjualan/produk/pesan/<str:token>/', views.pesan_produk),
    path('berandapenjualan/produk/pesan-id/<int:pk>/', views.pesan_produk_by_id),
    path('berandapenjualan/produk/like/<str:token>/', views.like_produk),
    path('berandapenjualan/produk/like-id/<int:pk>/', views.like_produk_by_id),
    path('berandapenjualan/produk/tertarik/<str:token>/', views.tertarik_produk),
    path('berandapenjualan/produk/tertarik-id/<int:pk>/', views.tertarik_produk_by_id),
    
    # Kategori Penjualan Admin
    path('kategoripenjualanadmin/', views.kategoripenjualanadmin, name='kategoripenjualanadmin'),
    path('form-kategoripenjualan/', views.formkategoripenjualanadmin, name='formkategoripenjualanadmin'),
    path('edit-kategoripenjualan/<str:token>/', views.editkategoripenjualanadmin, name='editkategoripenjualanadmin'),
    path('berandapenjualan/delete-kategoripenjualan/<str:token>/', views.deletekategoripenjualanadmin, name='deletekategoripenjualanadmin'),
]