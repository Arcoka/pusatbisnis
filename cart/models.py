from django.db import models
from django.template.defaultfilters import slugify
from ckeditor.fields import RichTextField
from django.contrib.auth import get_user_model

User = get_user_model()
from django.template.defaultfilters import slugify 

class Cart(models.Model):
    user = models.CharField(max_length=100)
    product = models.CharField(max_length=100)
    quantity = models.IntegerField()
    
    def __str__(self):
        return f"{self.user} - {self.product}"

class SlidePenjualan(models.Model):
    
    deskripsi = RichTextField(max_length=200, blank=True, null=True)
    judul = models.CharField(max_length=200, blank=True, null=True)
    gambar = models.ImageField(upload_to='gambar/slide', blank=False, null=True)
    aktif = models.BooleanField(default=True)
    token_slidepenjualan = models.CharField(max_length=300,  blank=True, null=True)
    tanggal_upload= models.DateTimeField(auto_now_add=True, null=True)
    slug = models.SlugField(max_length=200, null=True,blank=True, unique=True)
    class Meta:
        verbose_name_plural = 'Data SlidePenjualan'


class Pemesanan(models.Model):
    PILIHAN_OPSI = (
        ("tertarik", "Tertarik"),
        ("ingin_membeli", "Ingin membeli"),
        ("ingin_bertanya", "Ingin bertanya"),
    )
    no_pemesanan = models.CharField(max_length=200, blank=True, null=True)
    nama_pemesanan = models.CharField(max_length=200, blank=True, null=True)
    slug = models.SlugField(max_length=200, null=True,blank=True, unique=True)
    token_pemesanan = models.CharField(max_length=300,  blank=True, null=True)
    tanggal_upload= models.DateTimeField(auto_now_add=True, null=True)
    aktif = models.BooleanField(default=True)
    produk = models.ForeignKey('Produk', null=True, blank=True, on_delete=models.SET_NULL, related_name='pemesanan_set')
    pilihan = models.CharField(max_length=20, choices=PILIHAN_OPSI, default="tertarik")
    nama = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    no_telepon = models.CharField(max_length=50, blank=True, null=True)
    alamat = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name_plural = 'Data Pemesanan'

    def save(self, *args, **kwargs):  
        if not self.slug: 
            self.slug = slugify(self.nama_pemesanan) 
        return super().save(*args, **kwargs) 

class Jasa(models.Model):
    deskripsi = models.CharField(max_length=200, blank=True, null=True)
    gambar = models.ImageField(upload_to='gambar', blank=False, null=True)
    slug = models.SlugField(max_length=200, null=True,blank=True, unique=True)
    token_jasa = models.CharField(max_length=300,  blank=True, null=True)
    tanggal_upload= models.DateTimeField(auto_now_add=True, null=True)
    aktif = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = 'Data Jasa'

    def save(self, *args, **kwargs):  # new 
        if not self.slug: 
            self.slug = slugify(self.deskripsi) 
        return super().save(*args, **kwargs)

class KategoriPenjualan(models.Model):
    nama = models.CharField(max_length=200, blank=True, null=True)
    gambar = models.ImageField(upload_to='gambar', blank=False, null=True)
    filter = models.CharField(max_length=200, blank=True, null=True)
    aktif = models.BooleanField(default=True)
    token_kategoripenjualan = models.CharField(max_length=300, blank=True, null=True)
    tanggal_upload = models.DateTimeField(auto_now_add=True, null=True)
    slug = models.SlugField(max_length=200, null=True, blank=True, unique=True)
    
    class Meta:
        verbose_name_plural = 'Data Kategori Penjualan'
    
    def __str__(self):
        return self.nama
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nama)
        # Auto-generate filter based on slug
        if not self.filter:
            self.filter = f"filter-{self.slug}"
        return super().save(*args, **kwargs)
    
class Produk(models.Model):
    kategoripenjualan = models.ForeignKey(KategoriPenjualan, null=True, blank=True, related_name="produks", on_delete=models.SET_NULL)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='produk_tenant', null=True, blank=True, verbose_name='Pemilik Produk')
    nama = models.CharField(max_length=300, blank=True, null=True)
    deskripsi = RichTextField(blank=True, null=True)
    harga = models.CharField(max_length=300, blank=True, null=True)
    stok = models.PositiveIntegerField(default=0, help_text="Jumlah stok produk")
    gambar = models.ImageField(upload_to='gambar', blank=False, null=True)
    gambar2 = models.ImageField(upload_to='gambar', blank=True, null=True)
    gambar3 = models.ImageField(upload_to='gambar', blank=True, null=True)
    gambar4 = models.ImageField(upload_to='gambar', blank=True, null=True)
    aktif = models.BooleanField(default=True)
    slug = models.SlugField(max_length=200, blank=True, null=True, unique=True)
    tanggal_upload = models.DateTimeField(auto_now_add=True, null=True)
    token_produk = models.CharField(max_length=300, blank=True, null=True)
    
    class Meta:
        verbose_name_plural = 'Data Deskripsi'
        ordering = ['-tanggal_upload'] 

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nama)
        super().save(*args, **kwargs)
    
    
    
    

# class ProdukDeskripsi(models.Model):
#     kategoripenjualan = models.ForeignKey(KategoriPenjualan, null=True, blank=True, related_name="produks", on_delete=models.SET_NULL)
#     nama = models.CharField(max_length=300, blank=True, null=True)
#     deskripsi = RichTextField(blank=True, null=True)
#     harga = models.CharField(max_length=300, blank=True, null=True)
#     gambar = models.ImageField(upload_to='gambar', blank=False, null=True)
#     gambar2 = models.ImageField(upload_to='gambar', blank=True, null=True)
#     gambar3 = models.ImageField(upload_to='gambar', blank=True, null=True)
#     aktif = models.BooleanField(default=True)
#     slug = models.SlugField(max_length=200, blank=True, null=True, unique=True)
#     tanggal_upload = models.DateTimeField(auto_now_add=True, null=True)
#     token_produk = models.CharField(max_length=300, blank=True, null=True)

#     class Meta:
#         verbose_name_plural = 'Data Deskripsi'
#         ordering = ['-tanggal_upload'] 

#     def save(self, *args, **kwargs):
#         if not self.slug:
#             self.slug = slugify(self.nama)
#         super().save(*args, **kwargs)
    