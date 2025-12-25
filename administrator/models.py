from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from django.template.defaultfilters import slugify
import uuid
import datetime
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User, Group, Permission
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

# Model Admin Panel User (memperluas User bawaan)
class AdminRole(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Nama Role"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Deskripsi"))
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        verbose_name=_("Izin"),
        help_text=_("Pilih izin untuk role ini"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Admin Role"
        verbose_name_plural = "Admin Roles"
        ordering = ['name']


class AdminPanelUser(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="admin_panel_profile"
    )
    is_superadmin = models.BooleanField(default=False, verbose_name=_("Super Admin"))
    is_active = models.BooleanField(default=True, verbose_name=_("Aktif"))
    foto_profil = models.ImageField(
        upload_to='gambar/admin/',
        blank=True,
        null=True,
        verbose_name=_("Foto Profil"),
        help_text=_("Unggah foto profil admin")
    )
    role = models.ForeignKey(
        AdminRole,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Role"),
        related_name="users"
    )

    def __str__(self):
        if self.is_superadmin:
            return f"{self.user.username} - Superadmin"
        return f"{self.user.username} - {self.role.name if self.role else 'No Role'}"

    class Meta:
        verbose_name = "Admin Panel User"
        verbose_name_plural = "Admin Panel Users"

    def sync_user_permissions(self):
        if not self.user_id:
            return
        user = self.user
        if user.is_superuser or self.is_superadmin:
            user.user_permissions.clear()
            user.save(update_fields=["last_login"])
            return
        if self.role:
            perms = self.role.permissions.all()
            user.user_permissions.set(perms)
        else:
            user.user_permissions.clear()
        user.save(update_fields=["last_login"])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.sync_user_permissions()


class Kategori(models.Model):
    nama = models.CharField(max_length=200, blank=True, null=True)
    aktif = models.BooleanField(default=True)
    token_kategori = models.CharField(max_length=300, blank=True, null=True)
    slug = models.SlugField(max_length=200, null=True, blank=True, unique=True)

    class Meta:
        verbose_name_plural = "Data Kategori"

    def __str__(self):
        return self.nama

    def save(self, *args, **kwargs):  # new
        if not self.slug:
            self.slug = slugify(self.nama)
        return super().save(*args, **kwargs)


class Berita(models.Model):
    kategori = models.ForeignKey(
        Kategori, on_delete=models.CASCADE
    )  # Pakai ForeignKey ke Kategori
    judul = models.CharField(max_length=300)
    tanggal = models.DateField(
        blank=True, null=True, help_text="Tanggal berita yang ditentukan oleh user."
    )
    gambar = models.ImageField(upload_to="gambar/berita/", blank=True, null=True)
    gambar_1 = models.ImageField(upload_to="gambar/berita/", blank=True, null=True)
    gambar_2 = models.ImageField(upload_to="gambar/berita/", blank=True, null=True)
    gambar_3 = models.ImageField(upload_to="gambar/berita/", blank=True, null=True)
    # Opsi unggah video tambahan (opsional)
    video = models.FileField(
        upload_to="video/berita/",
        blank=True,
        null=True,
        help_text="Opsional. Unggah video pendukung (mp4/avi/mov).",
    )
    deskripsi = CKEditor5Field(blank=True, null=True, config_name="default")
    isi_berita = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True)
    token_berita = models.CharField(max_length=300, blank=True, null=True)
    tanggal_upload = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Pilih tanggal berita. Jika dikosongkan, akan otomatis sesuai waktu upload.",
    )

    class Meta:
        verbose_name_plural = "Data Berita"
        ordering = ["-tanggal_upload"]  # Mengurutkan dari yang terbaru

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.judul)
        super().save(*args, **kwargs)


class Agenda(models.Model):
    JENIS_KEGIATAN_CHOICES = [
        ("internal", "Kegiatan Internal"),
        ("eksternal", "Kegiatan Eksternal"),
        ("pelatihan", "Pelatihan"),
        ("seminar", "Seminar"),
        ("workshop", "Workshop"),
        ("lainnya", "Lainnya"),
    ]

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]

    judul = models.CharField(max_length=300, verbose_name="Judul Kegiatan")
    deskripsi = models.TextField(verbose_name="Deskripsi Singkat")
    konten = CKEditor5Field(verbose_name="Konten Lengkap")
    tanggal_mulai = models.DateTimeField(verbose_name="Tanggal & Waktu Mulai")
    tanggal_selesai = models.DateTimeField(verbose_name="Tanggal & Waktu Selesai")
    tempat = models.CharField(max_length=200, verbose_name="Tempat Kegiatan")
    jenis_kegiatan = models.CharField(
        max_length=20,
        choices=JENIS_KEGIATAN_CHOICES,
        default="internal",
        verbose_name="Jenis Kegiatan",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name="Status",
    )
    gambar = models.ImageField(
        upload_to="gambar/agenda/",
        blank=True,
        null=True,
        verbose_name="Gambar Poster",
    )
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True)
    tanggal_upload = models.DateTimeField(auto_now_add=True)
    tanggal_update = models.DateTimeField(auto_now=True)
    kontak_person = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Kontak Person"
    )
    email_kontak = models.EmailField(
        blank=True, null=True, verbose_name="Email Kontak"
    )
    telepon_kontak = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="Telepon Kontak"
    )

    class Meta:
        verbose_name = "Agenda"
        verbose_name_plural = "Agenda"
        ordering = ["-tanggal_mulai"]

    def __str__(self):
        return self.judul

    def save(self, *args, **kwargs):
        if not self.slug and self.judul:
            base_slug = slugify(self.judul)
            slug = base_slug
            counter = 1
            while (
                type(self)
                .objects.filter(slug=slug)
                .exclude(pk=self.pk)
                .exists()
            ):
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        return super().save(*args, **kwargs)


class Slide(models.Model):
    nama = models.CharField(max_length=200, blank=True, null=True)
    teks_awal = models.CharField(max_length=200, blank=True, null=True)
    teks_dua = models.CharField(max_length=200, blank=True, null=True)
    # teks_tiga = models.CharField(max_length=200, blank=True, null=True)
    gambar_slide = models.ImageField(upload_to="gambar/slide", blank=False, null=True)
    aktif = models.BooleanField(default=True)
    token_slide = models.CharField(max_length=300, blank=True, null=True)
    tanggal_upload = models.DateTimeField(auto_now_add=True, null=True)
    slug = models.SlugField(max_length=200, null=True, blank=True, unique=True)

    class Meta:
        verbose_name_plural = "Data Slide"


class Baground(models.Model):
    nama_baground = CKEditor5Field(blank=True, null=True, config_name="default")
    gambar_baground = models.ImageField(
        upload_to="gambar/baground", blank=False, null=True
    )
    aktif = models.BooleanField(default=True)
    token_baground = models.CharField(max_length=300, blank=True, null=True)
    tanggal_upload = models.DateTimeField(auto_now_add=True, null=True)
    slug = models.SlugField(max_length=200, null=True, blank=True, unique=True)

    class Meta:
        verbose_name_plural = "Data Baground"

    def save(self, *args, **kwargs):  # new
        if not self.slug:
            self.slug = slugify(self.nama_baground)
        return super().save(*args, **kwargs)


class VisiMisi(models.Model):
    visi = CKEditor5Field(blank=True, null=True, config_name="default")
    misi = CKEditor5Field(blank=True, null=True, config_name="default")
    sasaran = CKEditor5Field(blank=True, null=True, config_name="default")
    tujuan = CKEditor5Field(blank=True, null=True, config_name="default")
    aktif = models.BooleanField(default=True)
    token_visimisi = models.CharField(max_length=300, blank=True, null=True)
    tanggal_upload = models.DateTimeField(auto_now_add=True, null=True)
    slug = models.SlugField(max_length=200, null=True, blank=True, unique=True)

    class Meta:
        verbose_name_plural = "Data VisiMisi"

    def save(self, *args, **kwargs):
        if not self.slug:
            # Coba buat slug dari field yang ada (visi, misi, sasaran, tujuan)
            base_text = None

            # Prioritas: visi -> misi -> sasaran -> tujuan -> fallback
            if self.visi:
                base_text = self.visi
            elif self.misi:
                base_text = self.misi
            elif self.sasaran:
                base_text = self.sasaran
            elif self.tujuan:
                base_text = self.tujuan

            if base_text:
                # Bersihkan HTML tags dan ambil 50 karakter pertama
                import re

                clean_text = re.sub(r"<[^>]*>", "", str(base_text))
                base_slug = slugify(clean_text[:50])
            else:
                # Fallback jika semua field kosong
                base_slug = f"visimisi-{uuid.uuid4().hex[:8]}"

            # Pastikan slug unik
            slug = base_slug
            counter = 1

            while VisiMisi.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        return super().save(*args, **kwargs)


class Kontak(models.Model):
    alamat = models.CharField(max_length=100, blank=True, null=True)
    no_1 = models.CharField(max_length=20, null=True)
    no_2 = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    hari = models.CharField(max_length=100)  # contoh: "Sabtu - Kamis"
    jam = models.CharField(max_length=100)  # contoh: "09:00AM - 04:00PM"
    token_kontak = models.CharField(max_length=300, blank=True, null=True)
    tanggal_upload = models.DateTimeField(auto_now_add=True, null=True)
    slug = models.SlugField(max_length=200, null=True, blank=True, unique=True)
    aktif = models.BooleanField(default=True)

    def save(self, *args, **kwargs):  # new
        if not self.slug:
            self.slug = slugify(self.email)
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Informasi Kontak"


class Pesan(models.Model):
    nama = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    pesan = models.TextField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    token_pesan = models.CharField(max_length=300, blank=True, null=True)
    tanggal_upload = models.DateTimeField(auto_now_add=True, null=True)
    slug = models.SlugField(max_length=200, null=True, blank=True, unique=True)
    aktif = models.BooleanField(default=True)

    tampil_di_website = models.BooleanField(
        default=False, verbose_name="Tampilkan di Website"
    )

    def __str__(self):
        return f"Pesan dari {self.nama} ({self.tanggal_upload.strftime('%Y-%m-%d')})"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.nama)
            timestamp = timezone.now().strftime("%Y%m%d%H%M%S%f")
            unique_id = str(uuid.uuid4())[:8]
            self.slug = f"{base_slug}-{timestamp}-{unique_id}"

            # Ensure slug is unique
            original_slug = self.slug
            num = 1
            while Pesan.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{num}"
                num += 1

        if not self.token_pesan:
            self.token_pesan = str(uuid.uuid4())
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Pesan"
        verbose_name_plural = "Pesan"


class DaftarTenant(models.Model):
    nama = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    deskripsi = CKEditor5Field(blank=True, null=True, config_name="default")
    telepon = models.CharField(
        max_length=20, blank=True, null=True
    )  # Fixed: Changed from EmailField to CharField
    namausaha = models.CharField(
        max_length=200, blank=True, null=True
    )  # Fixed: Changed from TextField for consistency
    jenisusaha = models.CharField(
        max_length=200, blank=True, null=True
    )  # Fixed: Changed from TextField for consistency
    form_upload = models.FileField(
        upload_to="forms/tenant/", blank=True, null=True, verbose_name="Upload Form"
    )
    is_read = models.BooleanField(default=False)
    token_daftartenant = models.CharField(max_length=300, blank=True, null=True)
    tanggal_upload = models.DateTimeField(auto_now_add=True, null=True)
    slug = models.SlugField(max_length=200, null=True, blank=True, unique=True)
    aktif = models.BooleanField(default=True)

    def __str__(self):
        return (
            f"{self.nama} - {self.namausaha}"
            if self.nama and self.namausaha
            else "Tenant"
        )

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.nama) if self.nama else "tenant"
            slug = base_slug
            counter = 1

            # Check if slug exists
            while DaftarTenant.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        if not self.token_daftartenant:
            self.token_daftartenant = str(uuid.uuid4())

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Daftar Tenant"
        verbose_name_plural = "Daftar Tenant"


class DaftarLayanan(models.Model):
    nama = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Nama Lengkap"
    )
    email = models.EmailField(
        max_length=100, blank=True, null=True, verbose_name="Email"
    )
    alamat = models.TextField(blank=True, null=True, verbose_name="Alamat")
    telepon = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="Nomor Telepon"
    )
    # Ubah menjadi relasi ke tabel Layanan agar pilihan dinamis sesuai data slide
    jenislayanan = models.ForeignKey(
        "Layanan",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Jenis Layanan",
    )
    tanggal = models.DateField(
        default=datetime.date.today, verbose_name="Tanggal Layanan"
    )
    waktu = models.TimeField(default=datetime.time(0, 0), verbose_name="Waktu Layanan")
    pesan = models.TextField(blank=True, null=True, verbose_name="Pesan")
    is_read = models.BooleanField(default=False, verbose_name="Sudah Dibaca")
    token_daftarlayanan = models.CharField(
        max_length=300, blank=True, null=True, editable=False
    )
    kode_status = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="Kode Status"
    )
    status_email_token = models.CharField(
        max_length=20,
        choices=[
            ("belum_kirim", "Belum Kirim"),
            ("terkirim", "Terkirim"),
            ("email_invalid", "Email Tidak Valid"),
            ("gagal", "Gagal Kirim"),
        ],
        default="belum_kirim",
        verbose_name="Status Email Token",
    )
    tanggal_upload = models.DateTimeField(
        auto_now_add=True, null=True, verbose_name="Tanggal Permintaan"
    )
    slug = models.SlugField(max_length=200, null=True, blank=True, unique=True)
    aktif = models.BooleanField(default=True, verbose_name="Aktif")

    class Meta:
        verbose_name = "Daftar Layanan"
        verbose_name_plural = "Daftar Layanan"

    def save(self, *args, **kwargs):
        if not self.token_daftarlayanan:
            self.token_daftarlayanan = str(uuid.uuid4())

        if not self.kode_status:
            import random
            import string

            self.kode_status = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=8)
            )

        if not self.slug:
            base_slug = slugify(self.nama) if self.nama else "layanan"
            slug = base_slug
            counter = 1

            # Check if slug exists
            while DaftarLayanan.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nama}" if self.nama else "Layanan Tanpa Nama"


class Profil(models.Model):
    judul = models.CharField(max_length=200, blank=False, null=True)
    deskripsi = CKEditor5Field(blank=True, null=True, config_name="default")
    gambar = models.ImageField(
        upload_to="gambar",
        blank=False,
        null=True,
        verbose_name="Gambar (1920 x 1200 pixel)",
    )
    gambar_2 = models.ImageField(
        upload_to="gambar",
        blank=False,
        null=True,
        verbose_name="Gambar (1920 x 1200 pixel)",
    )
    tanggal_upload = models.DateTimeField(auto_now_add=True, null=True)
    aktif = models.BooleanField(default=True)
    slug = models.SlugField(max_length=200, null=True, blank=True, unique=True)
    token_profil = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Data Profil"

    def save(self, *args, **kwargs):  # new
        if not self.slug:
            self.slug = slugify(self.judul)
        return super().save(*args, **kwargs)


class ProfilImage(models.Model):
    profil = models.ForeignKey(Profil, on_delete=models.CASCADE, related_name="images")
    gambar = models.ImageField(
        upload_to="gambar",
        blank=False,
        null=True,
        verbose_name="Gambar (1920 x 1200 pixel)",
    )
    keterangan = models.CharField(max_length=255, blank=True, null=True)
    urutan = models.PositiveIntegerField(default=0)
    tanggal_upload = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        verbose_name = "Gambar Profil"
        verbose_name_plural = "Gambar Profil"
        ordering = ["urutan", "id"]

    def __str__(self):
        return f"{self.profil.judul or 'Profil'} - Gambar #{self.id}"

class Layanan(models.Model):
    nama = models.CharField(max_length=200, blank=True, null=True)
    isi = CKEditor5Field(
        blank=True, null=True, config_name="default"
    )  # CKEditor5 rich text editor
    slug = models.SlugField(max_length=200, null=True, blank=True, unique=True)
    token_layanan = models.CharField(max_length=300, blank=True, null=True)
    tanggal_upload = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        verbose_name_plural = "Data Layanan"

    def save(self, *args, **kwargs):  # new
        if not self.slug:
            self.slug = slugify(self.nama)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.nama or "Layanan"


class Team(models.Model):
    gambar = models.ImageField(upload_to="gambar", blank=False, null=True)
    nama = models.CharField(max_length=200, blank=True, null=True)
    jabatan = models.CharField(max_length=200, blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    slug = models.SlugField(max_length=200, null=True, blank=True, unique=True)
    token_team = models.CharField(max_length=300, blank=True, null=True)
    tanggal_upload = models.DateTimeField(auto_now_add=True, null=True)
    aktif = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Data Team"

    def save(self, *args, **kwargs):  # new
        if not self.slug:
            self.slug = slugify(self.nama)
        return super().save(*args, **kwargs)


class ModelInkubasi(models.Model):
    nama = models.CharField(max_length=200, blank=True, null=True)
    gambar = models.ImageField(upload_to="gambar", blank=False, null=True)
    deskripsi = models.CharField(max_length=200, blank=True, null=True)
    slug = models.SlugField(max_length=200, null=True, blank=True, unique=True)
    token_modelinkubasi = models.CharField(max_length=300, blank=True, null=True)
    tanggal_upload = models.DateTimeField(auto_now_add=True, null=True)
    aktif = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Data Model Inkubasi"

    def save(self, *args, **kwargs):  # new
        if not self.slug:
            self.slug = slugify(self.nama)
        return super().save(*args, **kwargs)


class Testimoni(models.Model):
    deskripsi = CKEditor5Field(blank=True, null=True, config_name="default")
    gambar = models.ImageField(upload_to="gambar", blank=False, null=True)
    nama = models.CharField(max_length=200, blank=True, null=True)
    jabatan = models.CharField(max_length=200, blank=True, null=True)
    slug = models.SlugField(max_length=200, null=True, blank=True, unique=True)
    token_testimoni = models.CharField(max_length=300, blank=True, null=True)
    tanggal_upload = models.DateTimeField(auto_now_add=True, null=True)
    aktif = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Data Testimoni"

    def save(self, *args, **kwargs):  # new
        if not self.slug:
            self.slug = slugify(self.nama)
        return super().save(*args, **kwargs)


class JenisLayanan(models.Model):
    judul = models.CharField(max_length=1000, blank=True, null=True)
    slug = models.SlugField(max_length=200, null=True, blank=True, unique=True)
    token_faq = models.CharField(max_length=300, blank=True, null=True)
    tanggal_upload = models.DateTimeField(auto_now_add=True, null=True)
    aktif = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Data Faq"

    def save(self, *args, **kwargs):  # new
        if not self.slug:
            self.slug = slugify(self.noslug)
        return super().save(*args, **kwargs)


class Seleksi(models.Model):
    judul = models.CharField(max_length=1000, blank=True, null=True)
    slug = models.SlugField(max_length=200, null=True, blank=True, unique=True)
    token_faq = models.CharField(max_length=300, blank=True, null=True)
    tanggal_upload = models.DateTimeField(auto_now_add=True, null=True)
    aktif = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Data Faq"

    def save(self, *args, **kwargs):  # new
        if not self.slug:
            self.slug = slugify(self.noslug)
        return super().save(*args, **kwargs)


class TenantInkubator(models.Model):
    judul = models.CharField(max_length=1000, blank=True, null=True)
    slug = models.SlugField(max_length=200, null=True, blank=True, unique=True)
    token_faq = models.CharField(max_length=300, blank=True, null=True)
    tanggal_upload = models.DateTimeField(auto_now_add=True, null=True)
    aktif = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Data Faq"

    def save(self, *args, **kwargs):  # new
        if not self.slug:
            self.slug = slugify(self.noslug)
        return super().save(*args, **kwargs)


##### Bagian Penjualan


# --- Telegram configuration ---
class TelegramRecipient(models.Model):
    nama = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text="Nama pemilik/tujuan (opsional)",
    )
    bot_token = models.CharField(max_length=200, help_text="Bot Token dari @BotFather")
    chat_id = models.CharField(
        max_length=100, help_text="Chat ID atau Channel ID (mis. -100xxxxxxxxxx)"
    )
    aktif = models.BooleanField(default=True)
    catatan = models.TextField(blank=True, null=True)
    dibuat = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Penerima Telegram"
        verbose_name_plural = "Penerima Telegram"
        ordering = ["-dibuat", "-id"]

    def __str__(self):
        label = self.nama or self.chat_id
        status = "Aktif" if self.aktif else "Nonaktif"
        return f"{label} ({status})"


@receiver(m2m_changed, sender=AdminRole.permissions.through)
def adminrole_permissions_changed(sender, instance, action, **kwargs):
    if action not in {"post_add", "post_remove", "post_clear"}:
        return
    for admin_user in instance.users.select_related("user"):
        admin_user.sync_user_permissions()


# -------------------------------------------------------------
# Audit Trail: Log Aktivitas Aplikasi
# -------------------------------------------------------------
class LogAktivitas(models.Model):
    AKSI_CHOICES = (
        ("ACCESS", "Akses"),
        ("CREATE", "Buat"),
        ("UPDATE", "Ubah"),
        ("DELETE", "Hapus"),
        ("OTHER", "Lainnya"),
    )

    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="log_aktivitas",
    )
    path = models.CharField(max_length=500)
    method = models.CharField(max_length=10)
    status_code = models.PositiveIntegerField(default=0)
    ip_address = models.CharField(max_length=64, blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)

    action_type = models.CharField(
        max_length=10, choices=AKSI_CHOICES, default="ACCESS"
    )
    app_label = models.CharField(max_length=100, blank=True, null=True)
    model_name = models.CharField(max_length=100, blank=True, null=True)
    object_id = models.CharField(max_length=100, blank=True, null=True)

    started_at = models.DateTimeField()
    finished_at = models.DateTimeField()
    duration_ms = models.PositiveIntegerField(default=0)

    request_data = models.TextField(blank=True, null=True)
    extra = models.JSONField(blank=True, null=True)

    class Meta:
        verbose_name = "Log Aktivitas"
        verbose_name_plural = "Log Aktivitas"
        indexes = [
            models.Index(fields=["-started_at"]),
            models.Index(fields=["user", "started_at"]),
            models.Index(fields=["action_type", "started_at"]),
        ]
        ordering = ["-started_at", "-id"]

    def __str__(self):
        uname = self.user.username if self.user else "anon"
        return f"{self.action_type} {self.method} {self.path} by {uname} [{self.status_code}]"
