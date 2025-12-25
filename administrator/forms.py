from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget
from django.utils import timezone
from datetime import timedelta
from .models import (
    Kategori,
    Berita,
    Agenda,
    Layanan,
    Kontak,
    Pesan,
    Slide,
    Baground,
    VisiMisi,
    Team,
    ModelInkubasi,
    Testimoni,
    Profil,
    Pesan,
    DaftarTenant,
    DaftarLayanan,
    TelegramRecipient,
)


class KategoriForm(forms.ModelForm):
    class Meta:
        model = Kategori
        fields = [
            "nama",
            "aktif",
        ]
        widgets = {
            "nama": forms.TextInput(
                attrs={
                    "class": "form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2",
                    "placeholder": "Masukkan nama kategori",
                    "required": True,
                }
            ),
            "aktif": forms.CheckboxInput(
                attrs={
                    "class": "form-checkbox h-6 w-6 text-blue-600 focus:ring focus:ring-blue-200",
                }
            ),
        }
        labels = {
            "nama": "Nama Kategori",
            "aktif": "Status Aktif",
        }


#### BAGIAN BERITAA


class BeritaForm(forms.ModelForm):
    # Pastikan field 'slug' tersedia di form meskipun readonly di admin.
    slug = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2",
                "placeholder": "Slug otomatis dari judul",
                "readonly": True,
            }
        ),
    )

    class Meta:
        model = Berita
        fields = [
            "kategori",
            "judul",
            "slug",
            "gambar",
            "gambar_1",
            "gambar_2",
            "gambar_3",
            "video",
            "isi_berita",
            "deskripsi",
            "tanggal",
            "tanggal_upload",
        ]
        widgets = {
            "kategori": forms.Select(
                attrs={
                    "class": "form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2",
                    "required": True,
                }
            ),
            "judul": forms.TextInput(
                attrs={
                    "class": "form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2",
                    "placeholder": "Masukkan Judul Berita",
                    "required": True,
                }
            ),
            "tanggal": forms.DateInput(
                attrs={
                    "class": "form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2",
                    "type": "date",
                    "required": True,
                    "placeholder": "Pilih Tanggal Berita",
                }
            ),
            "tanggal_upload": forms.DateTimeInput(
                attrs={
                    "class": "form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2",
                    "type": "datetime-local",
                    "placeholder": "Tanggal dan waktu upload (boleh dikosongkan)",
                }
            ),
            "aktif": forms.CheckboxInput(
                attrs={
                    "class": "form-checkbox h-6 w-6 text-blue-600 focus:ring focus:ring-blue-200",
                }
            ),
            "gambar": forms.ClearableFileInput(
                attrs={
                    "class": "file-input mt-1 block w-full text-gray-700 border border-gray-300 rounded-md shadow-sm focus:ring focus:ring-blue-200 py-2",
                }
            ),
            "gambar_1": forms.ClearableFileInput(
                attrs={
                    "class": "file-input mt-1 block w-full text-gray-700 border border-gray-300 rounded-md shadow-sm focus:ring focus:ring-blue-200 py-2",
                }
            ),
            "gambar_2": forms.ClearableFileInput(
                attrs={
                    "class": "file-input mt-1 block w-full text-gray-700 border border-gray-300 rounded-md shadow-sm focus:ring focus:ring-blue-200 py-2",
                }
            ),
            "gambar_3": forms.ClearableFileInput(
                attrs={
                    "class": "file-input mt-1 block w-full text-gray-700 border border-gray-300 rounded-md shadow-sm focus:ring focus:ring-blue-200 py-2",
                }
            ),
            "video": forms.ClearableFileInput(
                attrs={
                    "class": "file-input mt-1 block w-full text-gray-700 border border-gray-300 rounded-md shadow-sm focus:ring focus:ring-blue-200 py-2",
                    "accept": "video/*",
                }
            ),
            "isi_berita": forms.Textarea(
                attrs={
                    "class": "form-textarea mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2",
                    "placeholder": "Masukkan Isi Berita (opsional)",
                    "rows": 6,
                }
            ),
            "deskripsi": CKEditor5Widget(config_name="default"),
        }


class AgendaForm(forms.ModelForm):
    class Meta:
        model = Agenda
        fields = [
            "judul",
            "deskripsi",
            "konten",
            "tanggal_mulai",
            "tanggal_selesai",
            "tempat",
            "jenis_kegiatan",
            "status",
            "gambar",
            "kontak_person",
            "email_kontak",
            "telepon_kontak",
        ]
        widgets = {
            "judul": forms.TextInput(
                attrs={
                    "class": "form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2",
                    "placeholder": "Masukkan Judul Kegiatan",
                    "required": True,
                }
            ),
            "deskripsi": forms.Textarea(
                attrs={
                    "class": "form-textarea mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2",
                    "placeholder": "Deskripsi singkat agenda",
                    "rows": 4,
                    "required": True,
                }
            ),
            "konten": CKEditor5Widget(config_name="default"),
            "tanggal_mulai": forms.DateTimeInput(
                attrs={
                    "class": "form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2",
                    "type": "datetime-local",
                    "required": True,
                }
            ),
            "tanggal_selesai": forms.DateTimeInput(
                attrs={
                    "class": "form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2",
                    "type": "datetime-local",
                    "required": True,
                }
            ),
            "tempat": forms.TextInput(
                attrs={
                    "class": "form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2",
                    "placeholder": "Tempat kegiatan",
                    "required": True,
                }
            ),
            "jenis_kegiatan": forms.Select(
                attrs={
                    "class": "form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2",
                    "required": True,
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": "form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2",
                    "required": True,
                }
            ),
            "gambar": forms.ClearableFileInput(
                attrs={
                    "class": "file-input mt-1 block w-full text-gray-700 border border-gray-300 rounded-md shadow-sm focus:ring focus:ring-blue-200 py-2",
                }
            ),
            "kontak_person": forms.TextInput(
                attrs={
                    "class": "form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2",
                    "placeholder": "Kontak person (opsional)",
                }
            ),
            "email_kontak": forms.EmailInput(
                attrs={
                    "class": "form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2",
                    "placeholder": "Email kontak (opsional)",
                }
            ),
            "telepon_kontak": forms.TextInput(
                attrs={
                    "class": "form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2",
                    "placeholder": "Telepon kontak (opsional)",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fname in ["tanggal_mulai", "tanggal_selesai"]:
            if fname in self.fields:
                self.fields[fname].input_formats = [
                    "%Y-%m-%dT%H:%M",
                    "%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%d %H:%M",
                ]

    def clean(self):
        cleaned = super().clean()
        mulai = cleaned.get("tanggal_mulai")
        selesai = cleaned.get("tanggal_selesai")
        if mulai and selesai and selesai < mulai:
            self.add_error("tanggal_selesai", "Tanggal selesai harus setelah tanggal mulai")
        return cleaned


##### INI BAGIAN LAYANAN


class LayananForm(forms.ModelForm):
    class Meta:
        model = Layanan
        fields = ["nama", "isi"]
        widgets = {
            "nama": forms.TextInput(
                attrs={
                    "class": "form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2",
                    "placeholder": "Masukkan Judul Layanan",
                    "required": True,
                }
            ),
            "isi": CKEditor5Widget(config_name="default"),
        }


##### INI BAGIAN KONTAK
class KontakForm(forms.ModelForm):
    class Meta:
        model = Kontak
        fields = ["alamat", "no_1", "no_2", "email", "hari", "jam"]
        widgets = {
            "alamat": forms.TextInput(
                attrs={
                    "class": "form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2",
                    "placeholder": "Masukkan Alamat",
                    "required": True,
                }
            ),
            "no_1": forms.TextInput(
                attrs={
                    "class": "form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2",
                    "placeholder": "Masukkan No 1",
                    "required": True,
                }
            ),
            "no_2": forms.TextInput(
                attrs={
                    "class": "form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2",
                    "placeholder": "Masukkan No 2",
                    "required": True,
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2",
                    "placeholder": "Masukkan Email",
                    "required": True,
                }
            ),
            "hari": forms.TextInput(
                attrs={
                    "class": "form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2",
                    "placeholder": "Masukkan Hari Operasional",
                    "required": True,
                }
            ),
            "jam": forms.TextInput(
                attrs={
                    "class": "form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2",
                    "placeholder": "Masukkan Jam Operasional",
                    "required": True,
                }
            ),
        }


##### INI BAGIAN SLIDE
class SlideForm(forms.ModelForm):
    class Meta:
        model = Slide
        fields = ["nama", "teks_awal", "teks_dua", "gambar_slide"]
        widgets = {
            "nama": forms.TextInput(
                attrs={
                    "class": "form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2",
                    "placeholder": "Masukkan Judul Slide",
                    "required": True,
                }
            ),
            "teks_awal": forms.TextInput(
                attrs={
                    "class": "form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2",
                    "placeholder": "Masukkan Isi Slide",
                    "required": True,
                }
            ),
            "gambar_slide": forms.ClearableFileInput(
                attrs={
                    "class": "file-input mt-1 block w-full text-gray-700 border border-gray-300 rounded-md shadow-sm focus:ring focus:ring-blue-200 py-2",
                }
            ),
        }


##### INI BAGIAN BAGROUND
class BagroundForm(forms.ModelForm):
    class Meta:
        model = Baground
        fields = ["nama_baground", "gambar_baground"]
        widgets = {
            "nama_baground": CKEditor5Widget(config_name="default"),
            "gambar_baground": forms.ClearableFileInput(
                attrs={
                    "class": "file-input mt-1 block w-full text-gray-700 border border-gray-300 rounded-md shadow-sm focus:ring focus:ring-blue-200 py-2",
                }
            ),
        }


# Forms untuk field terpisah
class VisiForm(forms.ModelForm):
    class Meta:
        model = VisiMisi
        fields = ["visi"]
        widgets = {
            "visi": CKEditor5Widget(config_name="default"),
        }


class MisiForm(forms.ModelForm):
    class Meta:
        model = VisiMisi
        fields = ["misi"]
        widgets = {
            "misi": CKEditor5Widget(config_name="default"),
        }


class SasaranForm(forms.ModelForm):
    class Meta:
        model = VisiMisi
        fields = ["sasaran"]
        widgets = {
            "sasaran": CKEditor5Widget(config_name="default"),
        }


class TujuanForm(forms.ModelForm):
    class Meta:
        model = VisiMisi
        fields = ["tujuan"]
        widgets = {
            "tujuan": CKEditor5Widget(config_name="default"),
        }


# Tetap pertahankan form lengkap jika diperlukan
class VisiMisiForm(forms.ModelForm):
    class Meta:
        model = VisiMisi
        fields = ["visi", "misi", "sasaran", "tujuan"]
        widgets = {
            "visi": CKEditor5Widget(config_name="default"),
            "misi": CKEditor5Widget(config_name="default"),
            "sasaran": CKEditor5Widget(config_name="default"),
            "tujuan": CKEditor5Widget(config_name="default"),
        }


##### INI BAGIAN TEAM
class TeamForm(forms.ModelForm):
    facebook = forms.URLField(required=False)
    twitter = forms.URLField(required=False)
    instagram = forms.URLField(required=False)

    class Meta:
        model = Team
        fields = ["gambar", "nama", "jabatan", "facebook", "twitter", "instagram"]
        widgets = {
            "gambar": forms.ClearableFileInput(
                attrs={
                    "class": "file-input mt-1 block w-full text-gray-700 border border-gray-300 rounded-md shadow-sm focus:ring focus:ring-blue-200 py-2",
                }
            ),
            "nama": forms.TextInput(
                attrs={
                    "class": "form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2",
                    "placeholder": "Masukkan Judul Kontak",
                    "required": True,
                }
            ),
            "jabatan": forms.TextInput(
                attrs={
                    "class": "form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2",
                    "placeholder": "Masukkan Isi Kontak",
                    "required": True,
                }
            ),
            "facebook": forms.URLInput(
                attrs={
                    "class": "form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2",
                    "placeholder": "Masukkan Link Facebook",
                    "required": False,
                }
            ),
            "twitter": forms.URLInput(
                attrs={
                    "class": "form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2",
                    "placeholder": "Masukkan link Twitter",
                    "required": False,
                }
            ),
            "instagram": forms.URLInput(
                attrs={
                    "class": "form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2",
                    "placeholder": "Masukkan Link Instagram",
                    "required": False,
                }
            ),
        }


##### INI BAGIAN MODELINKUBASI
class ModelInkubasiForm(forms.ModelForm):
    class Meta:
        model = ModelInkubasi
        fields = ["nama", "gambar", "deskripsi"]
        widgets = {
            "gambar": forms.ClearableFileInput(
                attrs={
                    "class": "file-input mt-1 block w-full text-gray-700 border border-gray-300 rounded-md shadow-sm focus:ring focus:ring-blue-200 py-2",
                }
            ),
            "nama": forms.TextInput(
                attrs={
                    "class": "form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2",
                    "placeholder": "Masukkan Judul Kontak",
                    "required": True,
                }
            ),
            "deskripsi": forms.TextInput(
                attrs={
                    "class": "form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2",
                    "placeholder": "Masukkan Isi Kontak",
                    "required": True,
                }
            ),
        }


##### INI BAGIAN TESTIMONI


# --- Telegram Recipient Form ---
class TelegramRecipientForm(forms.ModelForm):
    class Meta:
        model = TelegramRecipient
        fields = ["nama", "bot_token", "chat_id", "aktif", "catatan"]
        widgets = {
            "nama": forms.TextInput(
                attrs={
                    "class": "form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2",
                    "placeholder": "Nama penerima/bot (opsional)",
                }
            ),
            "bot_token": forms.TextInput(
                attrs={
                    "class": "form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2",
                    "placeholder": "Masukkan Bot Token dari @BotFather",
                    "autocomplete": "off",
                }
            ),
            "chat_id": forms.TextInput(
                attrs={
                    "class": "form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2",
                    "placeholder": "Masukkan Chat ID (contoh: 123456789 atau -100xxxxxxxxxx)",
                    "autocomplete": "off",
                }
            ),
            "aktif": forms.CheckboxInput(
                attrs={
                    "class": "form-checkbox h-5 w-5 text-blue-600 focus:ring focus:ring-blue-200",
                }
            ),
            "catatan": forms.Textarea(
                attrs={
                    "class": "form-textarea mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2",
                    "rows": 3,
                    "placeholder": "Catatan opsional untuk penerima ini",
                }
            ),
        }

    def clean_bot_token(self):
        token = (self.cleaned_data.get("bot_token") or "").strip()
        if not token.startswith(""):
            # no prefix rule, but basic length check
            pass
        if len(token) < 20:
            raise forms.ValidationError("Bot token terlalu pendek.")
        return token

    def clean_chat_id(self):
        chat_id = (self.cleaned_data.get("chat_id") or "").strip()
        # chat id bisa angka positif atau channel id negatif (-100...)
        import re

        if not re.match(r"^-?\d{5,}$", chat_id):
            raise forms.ValidationError(
                "Format Chat ID tidak valid. Gunakan angka saja, contoh 123456789 atau -1001234567890."
            )
        return chat_id


class TestimoniForm(forms.ModelForm):
    class Meta:
        model = Testimoni
        fields = ["deskripsi", "gambar", "nama", "jabatan"]
        widgets = {
            "deskripsi": CKEditor5Widget(config_name="default"),
            "gambar": forms.ClearableFileInput(
                attrs={
                    "class": "file-input mt-1 block w-full text-gray-700 border border-gray-300 rounded-md shadow-sm focus:ring focus:ring-blue-200 py-2",
                }
            ),
            "nama": forms.TextInput(
                attrs={
                    "class": "form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2",
                    "placeholder": "Masukkan Nama Pengirim",
                    "required": True,
                }
            ),
            "jabatan": forms.TextInput(
                attrs={
                    "class": "form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2",
                    "placeholder": "Masukkan Jabatan Pengirim",
                    "required": True,
                }
            ),
        }


##### INI BAGIAN Profil
class ProfilForm(forms.ModelForm):
    class Meta:
        model = Profil
        fields = ["judul", "deskripsi", "gambar", "gambar_2"]
        widgets = {
            "judul": forms.TextInput(
                attrs={
                    "class": "form-input mt-1 block w-full rounded-md border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 py-2",
                    "placeholder": "Masukkan Judul Profil",
                    "required": True,
                }
            ),
            "deskripsi": CKEditor5Widget(config_name="default"),
            "gambar": forms.ClearableFileInput(
                attrs={
                    "class": "file-input mt-1 block w-full text-gray-700 border border-gray-300 rounded-md shadow-sm focus:ring focus:ring-blue-200 py-2",
                }
            ),
            "gambar_2": forms.ClearableFileInput(
                attrs={
                    "class": "file-input mt-1 block w-full text-gray-700 border border-gray-300 rounded-md shadow-sm focus:ring focus:ring-blue-200 py-2",
                }
            ),
        }


##### INI BAGIAN PESAN
class PesanForm(forms.ModelForm):
    class Meta:
        model = Pesan
        fields = ["nama", "email", "pesan"]
        widgets = {
            "nama": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nama Anda"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "Email Anda"}
            ),
            "pesan": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Tulis pesan Anda di sini",
                    "rows": 5,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Wajib diisi walau model mengizinkan blank
        self.fields["nama"].required = True
        self.fields["email"].required = True
        self.fields["pesan"].required = True

    def clean_nama(self):
        nama = (self.cleaned_data.get("nama") or "").strip()
        if not nama:
            raise forms.ValidationError("Nama wajib diisi.")
        return nama

    def clean_pesan(self):
        pesan = (self.cleaned_data.get("pesan") or "").strip()
        if not pesan:
            raise forms.ValidationError("Pesan tidak boleh kosong.")
        if len(pesan) < 5:
            raise forms.ValidationError("Pesan terlalu pendek (min. 5 karakter).")
        return pesan

    def clean(self):
        cleaned = super().clean()
        # Email field sudah memiliki validasi format dari EmailField; cukup pastikan ada nilainya
        email = (cleaned.get("email") or "").strip()
        if not email:
            self.add_error("email", "Email wajib diisi.")
        return cleaned


##### INI BAGIAN DAFTAR TENANT
class DaftarTenantForm(forms.ModelForm):
    class Meta:
        model = DaftarTenant
        fields = [
            "nama",
            "email",
            "telepon",
            "namausaha",
            "jenisusaha",
            "deskripsi",
            "form_upload",
        ]
        # Tambahkan field lainnya jika ada

        # Tambahkan widget untuk styling form
        widgets = {
            "nama": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Masukkan Nama Lengkap"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "contoh@email.com"}
            ),
            "telepon": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nomor Telepon/WhatsApp"}
            ),
            "namausaha": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nama Usaha Anda"}
            ),
            "jenisusaha": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Jenis Usaha"}
            ),
            "deskripsi": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Deskripsi usaha",
                    "rows": 4,
                }
            ),
            "form_upload": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".pdf,.doc,.docx,.jpg,.jpeg,.png",
                }
            ),
        }

    # Validasi untuk email
    def clean_email(self):
        # Pastikan self.cleaned_data sudah ada sebelum mencoba mengakses
        if hasattr(self, "cleaned_data"):
            email = self.cleaned_data.get("email")
            if email:  # Pastikan email tidak None
                # Cek apakah email sudah ada di database
                if DaftarTenant.objects.filter(email=email).exists():
                    raise forms.ValidationError(
                        "Email ini sudah terdaftar dalam sistem."
                    )
                return email
        return None  # Jika tidak ada data, kembalikan None


class DaftarLayananForm(forms.ModelForm):
    """Form untuk pengguna mengisi permintaan layanan"""

    class Meta:
        model = DaftarLayanan
        fields = [
            "nama",
            "email",
            "alamat",
            "telepon",
            "jenislayanan",
            "tanggal",
            "pesan",
        ]
        widgets = {
            "nama": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Masukkan nama lengkap"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "Masukkan email"}
            ),
            "alamat": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Masukkan alamat lengkap",
                    "rows": 3,
                }
            ),
            "telepon": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Masukkan nomor telepon"}
            ),
            "jenislayanan": forms.Select(attrs={"class": "form-select"}),
            "tanggal": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "pesan": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Masukkan pesan atau keterangan tambahan",
                    "rows": 4,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default tanggal to tomorrow
        if not self.initial.get("tanggal"):
            self.initial["tanggal"] = (
                timezone.now() + timezone.timedelta(days=1)
            ).date()

        # Add required attribute
        for field_name in ["nama", "email", "telepon", "jenislayanan", "tanggal"]:
            self.fields[field_name].required = True

        # Add help text
        self.fields["tanggal"].help_text = "Pilih tanggal yang diinginkan untuk layanan"
        self.fields["telepon"].help_text = "Masukkan nomor telepon yang aktif"

        # Gunakan daftar layanan dari model Layanan secara terurut
        try:
            from .models import Layanan

            self.fields["jenislayanan"].queryset = Layanan.objects.all().order_by(
                "nama"
            )
            self.fields["jenislayanan"].empty_label = "Pilih jenis layanan"
            self.fields["jenislayanan"].label_from_instance = (
                lambda obj: obj.nama or "Layanan"
            )
        except Exception:
            # Jika migrasi belum dijalankan, biarkan Django menangani default-nya
            pass
