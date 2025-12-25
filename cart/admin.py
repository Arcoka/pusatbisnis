from django.contrib import admin

from .models import Cart, SlidePenjualan, Pemesanan, Jasa, KategoriPenjualan, Produk
admin.site.register(Cart) 

@admin.register(SlidePenjualan)
class SlidePenjualanAdmin(admin.ModelAdmin):
    list_display=('id', 'judul', 'deskripsi','gambar')
    prepopulated_fields = {"slug": ("judul",)}

@admin.register(Pemesanan)
class PemesananAdmin(admin.ModelAdmin):
    list_display=('id', 'no_pemesanan', 'nama_pemesanan')
    prepopulated_fields = {"slug": ("no_pemesanan",)}

@admin.register(Jasa)
class Jasa(admin.ModelAdmin):
    list_display=('id', 'deskripsi', 'gambar')
    prepopulated_fields = {"slug": ("deskripsi",)}

@admin.register(KategoriPenjualan)
class KategoriPenjualanAdmin(admin.ModelAdmin):
    list_display=('id', 'nama', 'gambar', 'filter', 'aktif')
    prepopulated_fields = {"slug": ("nama",)} #membuat slug otomatis

@admin.register(Produk)
class ProdukAdmin(admin.ModelAdmin):
    list_display=('id',  'nama', 'deskripsi', 'gambar')
    prepopulated_fields = {"slug": ("nama",)}

# @admin.register(ProdukDeskripsi)
# class ProdukDeskripsiAdmin(admin.ModelAdmin):
#     list_display=('id',  'nama', 'deskripsi', 'gambar')
#     prepopulated_fields = {"slug": ("nama",)}