from django import forms
from .models import SlidePenjualan, Pemesanan, Jasa, KategoriPenjualan, Produk



#### INI BAGIAN SLIDEPENJUALAN
class SlidePenjualanForm(forms.ModelForm):
    class Meta:
        model = SlidePenjualan
        fields = ['judul', 'deskripsi', 'gambar']
        widgets = {
            
            'judul': forms.TextInput(attrs={
                'class': 'form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2',  
                'placeholder': 'Masukkan Isi SlidePenjualan',
                'required': True, 
            }),
            'deskripsi': forms.TextInput(attrs={
                'class': 'form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2',  
                'placeholder': 'Masukkan Isi SlidePenjualan',
                'required': True, 
            }),
            'gambar': forms.ClearableFileInput(attrs={
                'class': 'file-input mt-1 block w-full text-gray-700 border border-gray-300 rounded-md shadow-sm focus:ring focus:ring-blue-200 py-2',
                
            }),
            
        }

##### INI BAGIAN PEMESANAN
class PemesananForm(forms.ModelForm):
    class Meta:
        model = Pemesanan
        fields = ['no_pemesanan', 'nama_pemesanan']
        widgets = {
            'no_pemesanan': forms.TextInput(attrs={
                'class': 'form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2',  
                'placeholder': 'Masukkan Judul Pemesanan',
                'required': True, 
            }),
            'nama_pemesanan': forms.TextInput(attrs={
                'class': 'form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2',  
                'placeholder': 'Masukkan Isi Pemesanan',
                'required': True, 
            }),
            
        }

##### INI BAGIAN PRODUK POPULER
class JasaForm(forms.ModelForm):
    class Meta:
        model = Jasa
        fields = ['deskripsi', 'gambar']
        widgets = {
            'deskripsi': forms.TextInput(attrs={
                'class': 'form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2',  
                'placeholder': 'Masukkan Isi ProdukPopuler',
                'required': True, 
            }),
            'gambar': forms.ClearableFileInput(attrs={
                'class': 'file-input mt-1 block w-full text-gray-700 border border-gray-300 rounded-md shadow-sm focus:ring focus:ring-blue-200 py-2',
                
            }),
            
        }

##### INI BAGIAN KATEGORI PENJUALAN
class KategoriPenjualanForm(forms.ModelForm):
    class Meta:
        model = KategoriPenjualan
        fields = ['nama', 'gambar', 'filter']
        widgets = {
            'nama': forms.TextInput(attrs={
                'class': 'form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2',  
                'placeholder': 'Masukkan Nama KategoriPenjualan',
                'required': True, 
            }),
            'gambar': forms.ClearableFileInput(attrs={
                'class': 'file-input mt-1 block w-full text-gray-700 border border-gray-300 rounded-md shadow-sm focus:ring focus:ring-blue-200 py-2',
                
            }),
            'filter': forms.TextInput(attrs={
                'class': 'form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2',  
                'placeholder': 'Masukkan Filter KategoriPenjualan',
                'required': True, 
            }),
            
            
        }

#### BAGIAN PRODUK

class ProdukForm(forms.ModelForm):
    class Meta:
        model = Produk
        fields = ['kategoripenjualan', 'nama', 'deskripsi', 'harga', 'gambar', 'gambar2', 'gambar3','gambar3', 'aktif']
        widgets = {
            'kategoripenjualan': forms.Select(attrs={
                'class': 'form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2',
                'required': True,
            }),
            'nama': forms.TextInput(attrs={
                'class': 'form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2',
                'placeholder': 'Masukkan Nama Produk',
                'required': True,
            }),
            'deskripsi': forms.Textarea(attrs={
                'class': 'form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2',
                'placeholder': 'Masukkan Deskripsi Produk',
                'required': True,
            }),
            'harga': forms.TextInput(attrs={
                'class': 'form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2',
                'placeholder': 'Masukkan Harga Produk',
                'required': True,
            }),
            'gambar': forms.ClearableFileInput(attrs={
                'class': 'file-input mt-1 block w-full text-gray-700 border border-gray-300 rounded-md shadow-sm focus:ring focus:ring-blue-200 py-2',
            }),
            'gambar2': forms.ClearableFileInput(attrs={
                'class': 'file-input mt-1 block w-full text-gray-700 border border-gray-300 rounded-md shadow-sm focus:ring focus:ring-blue-200 py-2',
            }),
            'gambar3': forms.ClearableFileInput(attrs={
                'class': 'file-input mt-1 block w-full text-gray-700 border border-gray-300 rounded-md shadow-sm focus:ring focus:ring-blue-200 py-2',
            }),
            'gambar4': forms.ClearableFileInput(attrs={
                'class': 'file-input mt-1 block w-full text-gray-700 border border-gray-300 rounded-md shadow-sm focus:ring focus:ring-blue-200 py-2',
            }),
            'aktif': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-6 w-6 text-blue-600 focus:ring focus:ring-blue-200',
            }),
        }