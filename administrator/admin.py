from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.utils.timezone import now
from django.utils.safestring import mark_safe
import json
from django.http import HttpResponse
from .export_utils import export_model_to_excel
from .models import (
    Kategori,
    Berita,
    Kontak,
    Pesan,
    Profil,
    Slide,
    Layanan,
    Baground,
    VisiMisi,
    Team,
    ModelInkubasi,
    Testimoni,
    DaftarTenant,
    DaftarLayanan,
    ProfilImage,
    TelegramRecipient,
    LogAktivitas,
)
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import  AdminPanelUser
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from .forms import BeritaForm


# Admin untuk AdminPanelUser
class AdminPanelUserInline(admin.StackedInline):
    model = AdminPanelUser
    can_delete = False
    verbose_name_plural = "Admin Panel Profile"
    fields = ('foto_profil', 'is_superadmin', 'role')
    readonly_fields = ('foto_preview',)
    
    def foto_preview(self, obj):
        if obj.foto_profil:
            return mark_safe(f'<img src="{obj.foto_profil.url}" style="max-height: 100px; max-width: 100px;" />')
        return "(Tidak ada gambar)"
    foto_preview.short_description = 'Pratinjau Foto'


# Ubah admin User bawaan untuk menampilkan AdminPanelUser
class CustomUserAdmin(BaseUserAdmin):
    inlines = [AdminPanelUserInline]
    list_display = [
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_admin_panel_superadmin",
    ]

    def is_admin_panel_superadmin(self, obj):
        try:
            return obj.admin_panel_profile.is_superadmin
        except AdminPanelUser.DoesNotExist:
            return False

    is_admin_panel_superadmin.short_description = "Superadmin"
    is_admin_panel_superadmin.boolean = True


# Unregister User bawaan dan register dengan CustomUserAdmin


@admin.register(Kategori)
class KategoriAdmin(admin.ModelAdmin):
    list_display = ("id", "nama", "aktif")
    prepopulated_fields = {"slug": ("nama",)}  # membuat slug otomatis
    actions = ["export_to_excel"]
    
    def export_to_excel(self, request, queryset):
        return export_model_to_excel(self, request, queryset)
    export_to_excel.short_description = "Ekspor ke Excel"

@admin.register(Berita)
class BeritaAdmin(admin.ModelAdmin):
    form = BeritaForm
    list_display = (
        "id",
        "judul",
        "kategori",
        "tanggal",
    )
    prepopulated_fields = {"slug": ("judul",)}
    list_filter = ("kategori", "tanggal_upload")
    readonly_fields = ()
    actions = ["export_to_excel"]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "kategori",
                    "judul",
                    "gambar",
                    "gambar_1",
                    "gambar_2",
                    "gambar_3",
                    "video",
                    "isi_berita",
                    "deskripsi",
                    "tanggal_upload",
                )
            },
        ),
    )
    
    def export_to_excel(self, request, queryset):
        return export_model_to_excel(self, request, queryset)
    export_to_excel.short_description = "Ekspor ke Excel"

@admin.register(Kontak)
class KontakAdmin(admin.ModelAdmin):
    list_display = ("id", "alamat", "no_1", "no_2", "email", "hari", "jam")
    prepopulated_fields = {"slug": ("email",)}
    actions = ["export_to_excel"]
    
    def export_to_excel(self, request, queryset):
        return export_model_to_excel(self, request, queryset)
    export_to_excel.short_description = "Ekspor ke Excel"

@admin.register(Pesan)
class PesanAdmin(admin.ModelAdmin):
    list_display = ("nama", "email", "tanggal_upload", "is_read", "aktif")
    list_filter = ("is_read", "aktif", "tanggal_upload")
    search_fields = ("nama", "email", "pesan")
    readonly_fields = ("tanggal_upload", "token_pesan", "slug")
    date_hierarchy = "tanggal_upload"
    actions = ["mark_as_read", "mark_as_unread", "export_to_excel"]
    
    def export_to_excel(self, request, queryset):
        return export_model_to_excel(self, request, queryset)
    export_to_excel.short_description = "Ekspor ke Excel"

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)

    mark_as_read.short_description = "Tandai pesan terpilih sebagai sudah dibaca"

    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)

    mark_as_unread.short_description = "Tandai pesan terpilih sebagai belum dibaca"


try:
    admin.site.register(Pesan, PesanAdmin)
except admin.sites.AlreadyRegistered:
    pass


@admin.register(DaftarTenant)
class DaftarTenantAdmin(admin.ModelAdmin):
    list_display = ("nama", "email", "deskripsi", "tanggal_upload", "is_read", "aktif")
    list_filter = ("is_read", "aktif", "tanggal_upload")
    search_fields = ("nama", "email", "daftartenant")
    readonly_fields = ("tanggal_upload", "token_daftartenant", "slug")
    date_hierarchy = "tanggal_upload"
    actions = ["mark_as_read", "mark_as_unread", "export_to_excel"]
    
    def export_to_excel(self, request, queryset):
        return export_model_to_excel(self, request, queryset)
    export_to_excel.short_description = "Ekspor ke Excel"

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)

    mark_as_read.short_description = "Tandai daftartenant terpilih sebagai sudah dibaca"

    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)

    mark_as_unread.short_description = (
        "Tandai daftartenant terpilih sebagai belum dibaca"
    )


try:
    admin.site.register(DaftarTenant, DaftarTenantAdmin)
except admin.sites.AlreadyRegistered:
    pass


@admin.register(DaftarLayanan)
class DaftarLayananAdmin(admin.ModelAdmin):
    list_display = [
        "nama",
        "email",
        "telepon",
        "jenislayanan",
        "waktu",
        "is_read",
        "tanggal_upload",
        "aktif",
    ]
    list_filter = ["is_read", "aktif", "jenislayanan", ]
    search_fields = ["nama", "email", "telepon"]
    date_hierarchy = "tanggal_upload"
    readonly_fields = ["token_daftarlayanan", "tanggal_upload", "slug"]
    actions = ["export_to_excel"]
    
    def export_to_excel(self, request, queryset):
        return export_model_to_excel(self, request, queryset)
    export_to_excel.short_description = "Ekspor ke Excel"
    fieldsets = (
        ("Informasi Pelanggan", {"fields": ("nama", "email", "alamat", "telepon")}),
        (
            "Detail Layanan",
            {"fields": ("jenislayanan", "waktu", "pesan")},
        ),
        ("Status", {"fields": ("is_read", "aktif")}),
        (
            "Informasi Sistem",
            {
                "fields": ("token_daftarlayanan", "tanggal_upload", "slug"),
                "classes": ("collapse",),
            },
        ),
    )

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)

    mark_as_read.short_description = "Tandai sebagai sudah dibaca"

    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)

    mark_as_unread.short_description = "Tandai sebagai belum dibaca"

    actions = ["mark_as_read", "mark_as_unread"]

    def get_ordering(self, request):
        return ["-tanggal_upload"]


class ProfilImageInline(admin.TabularInline):
    model = ProfilImage
    extra = 3
    min_num = 0
    can_delete = True
    show_change_link = False
    fields = ("preview", "gambar", "keterangan", "urutan")
    readonly_fields = ("preview",)
    ordering = ("urutan", "id")

    def preview(self, obj):
        if obj and obj.gambar:
            return (
                f"<img src='{obj.gambar.url}' style='height:60px;border-radius:6px'/>"
            )
        return "-"

    preview.allow_tags = True
    preview.short_description = "Pratinjau"


@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin):
    list_display = ("id", "judul", "deskripsi", "jumlah_gambar")
    prepopulated_fields = {"slug": ("judul",)}
    inlines = [ProfilImageInline]
    actions = ["export_to_excel"]

    def jumlah_gambar(self, obj):
        return obj.images.count()

    jumlah_gambar.short_description = "Jumlah Gambar Tambahan"
    
    def export_to_excel(self, request, queryset):
        return export_model_to_excel(self, request, queryset)
    export_to_excel.short_description = "Ekspor ke Excel"


@admin.register(Slide)
class SlideAdmin(admin.ModelAdmin):
    list_display = ("id", "nama", "teks_awal", "teks_dua", "gambar_slide")
    prepopulated_fields = {"slug": ("nama",)}
    actions = ["export_to_excel"]
    
    def export_to_excel(self, request, queryset):
        return export_model_to_excel(self, request, queryset)
    export_to_excel.short_description = "Ekspor ke Excel"


@admin.register(Baground)
class BagroundAdmin(admin.ModelAdmin):
    list_display = ("id", "nama_baground", "gambar_baground")
    prepopulated_fields = {"slug": ("nama_baground",)}
    actions = ["export_to_excel"]
    
    def export_to_excel(self, request, queryset):
        return export_model_to_excel(self, request, queryset)
    export_to_excel.short_description = "Ekspor ke Excel"


@admin.register(VisiMisi)
class VisiMisiAdmin(admin.ModelAdmin):
    list_display = ("id", "visi", "misi", "sasaran", "tujuan")
    prepopulated_fields = {"slug": ("visi",)}
    actions = ["export_to_excel"]
    
    def export_to_excel(self, request, queryset):
        return export_model_to_excel(self, request, queryset)
    export_to_excel.short_description = "Ekspor ke Excel"


@admin.register(Layanan)
class LayananAdmin(admin.ModelAdmin):
    list_display = ("id", "nama", "isi")
    prepopulated_fields = {"slug": ("nama",)}
    actions = ["export_to_excel"]
    
    def export_to_excel(self, request, queryset):
        return export_model_to_excel(self, request, queryset)
    export_to_excel.short_description = "Ekspor ke Excel"


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "gambar",
        "nama",
        "jabatan",
        "facebook",
        "twitter",
        "instagram",
        "aktif",
    )
    prepopulated_fields = {"slug": ("nama",)}
    actions = ["export_to_excel"]
    
    def export_to_excel(self, request, queryset):
        return export_model_to_excel(self, request, queryset)
    export_to_excel.short_description = "Ekspor ke Excel"


@admin.register(Testimoni)
class TestimoniAdmin(admin.ModelAdmin):
    list_display = ("id", "deskripsi", "gambar", "nama", "jabatan", "aktif")
    prepopulated_fields = {"slug": ("nama",)}
    actions = ["export_to_excel"]
    
    def export_to_excel(self, request, queryset):
        return export_model_to_excel(self, request, queryset)
    export_to_excel.short_description = "Ekspor ke Excel"


@admin.register(ModelInkubasi)
class ModelInkubasiAdmin(admin.ModelAdmin):
    list_display = ("id", "nama", "gambar", "deskripsi", "aktif")
    prepopulated_fields = {"slug": ("nama",)}
    actions = ["export_to_excel"]
    
    def export_to_excel(self, request, queryset):
        return export_model_to_excel(self, request, queryset)
    export_to_excel.short_description = "Ekspor ke Excel"

# --- Telegram configuration admin ---
@admin.register(TelegramRecipient)
class TelegramRecipientAdmin(admin.ModelAdmin):
    from .forms import TelegramRecipientForm

    form = TelegramRecipientForm
    list_display = ("nama", "chat_id", "aktif", "dibuat")
    list_filter = ("aktif", "dibuat")
    search_fields = ("nama", "chat_id", "bot_token")
    readonly_fields = ("dibuat",)
    list_display_links = ("nama", "chat_id")
    ordering = ("-dibuat", "-id")
    list_per_page = 25

    actions = ["kirim_pesan_tes", "export_to_excel"]
    
    def export_to_excel(self, request, queryset):
        return export_model_to_excel(self, request, queryset)
    export_to_excel.short_description = "Ekspor ke Excel"

    def kirim_pesan_tes(self, request, queryset):
        from website.utils.telegram import send_telegram_message

        sukses = 0
        gagal = 0
        for rec in queryset:
            if not rec.bot_token or not rec.chat_id:
                gagal += 1
                continue
            result = send_telegram_message(
                text="Pengujian notifikasi dari Admin Panel",
                token=rec.bot_token,
                chat_id=rec.chat_id,
            )
            if result.get("success"):
                sukses += 1
            else:
                gagal += 1
        self.message_user(
            request, f"Pesan tes terkirim: {sukses} berhasil, {gagal} gagal."
        )

    kirim_pesan_tes.short_description = "Kirim pesan tes ke penerima terpilih"


# --- Audit Log admin (superuser-only) ---
@admin.register(LogAktivitas)
class LogAktivitasAdmin(admin.ModelAdmin):
    list_display = (
        "started_at",
        "user",
        "method",
        "path",
        "status_code",
        "duration_ms",
        "ip_address",
    )
    list_filter = ("method", "status_code", "action_type", "started_at")
    search_fields = ("path", "user__username", "ip_address", "user_agent")
    readonly_fields = (
        "user",
        "path",
        "method",
        "status_code",
        "ip_address",
        "user_agent",
        "action_type",
        "app_label",
        "model_name",
        "object_id",
        "started_at",
        "finished_at",
        "duration_ms",
        "request_data",
        "extra",
    )
    ordering = ("-started_at", "-id")
    actions = ["hapus_terpilih", "export_to_excel"]
    
    def export_to_excel(self, request, queryset):
        return export_model_to_excel(self, request, queryset)
    export_to_excel.short_description = "Ekspor ke Excel"

    def has_module_permission(self, request):
        return bool(request.user and request.user.is_superuser)

    def has_view_permission(self, request, obj=None):
        return bool(request.user and request.user.is_superuser)

    def has_change_permission(self, request, obj=None):
        # Log hanya untuk baca
        return False

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        # Hanya superuser yang boleh menghapus
        return bool(request.user and request.user.is_superuser)

    def hapus_terpilih(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"Berhasil menghapus {count} log.")

    hapus_terpilih.short_description = "Hapus log terpilih"
