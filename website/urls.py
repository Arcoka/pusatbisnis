from django.urls import path 
from .import views 
from .views import login_view, logout_view, berita_list, berita_detail, user_login, user_logout, user_register

  # Pastikan ini ada

urlpatterns = [ 
    path('', views.beranda, name='home'), 
    path('visimisi', views.visimisi, name='visimisi'),
    path('profil/', views.profil, name='profil'),
    path('faq/', views.faq, name='faq'), 
    path('berita/<slug:slug>/', berita_detail, name='berita_detail'),
    path('beritalist/', views.berita_list, name='berita_list'),
    path('hubungi-kami/', views.hubungi_kami, name='hubungi_kami'),
    path('kontak/', views.kontak, name='kontak'),
    path('daftar-tenant/', views.daftar_tenant, name='daftar_tenant'),
    path('layanan/', views.layanan, name='layanan'),
    path('modelinkubasi/', views.modelinkubasi, name='modelinkubasi'),
    path('seleksi/', views.seleksi, name='seleksi'),
    path('tenantinkubator/', views.tenantinkubator, name='tenantinkubator'),
    path('toggle-aktif/<int:id>/', views.toggle_aktif, name='toggle_aktif'),
    path('baground/', views.baground, name='baground'),
    path('daftar-layanan/', views.submit_layanan, name='submit_layanan'),
    path('jenislayanan/', views.jenislayanan, name='jenislayanan'),
    path('konfirmasi-layanan/<slug:slug>/', views.konfirmasi_layanan, name='konfirmasi_layanan'),
    # Auth (admin)
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),  
    # Auth (user)
    path('masuk/', user_login, name='user_login'),
    path('keluar/', user_logout, name='user_logout'),
    path('daftar/', user_register, name='user_register'),

    ######_-------BAGIAN PENJUALAN
    path('penjualan', views.berandapenjualan, name='penjualan'),  
    path('produk_detail/<slug:slug>/', views.produk_detail, name='produk_detail'),

    # Telegram testing endpoint
    path('telegram-test/', views.telegram_test, name='telegram_test'),

    
    
    ]