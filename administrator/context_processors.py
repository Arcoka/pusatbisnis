# context_processors.py
from .models import Pesan, DaftarTenant, DaftarLayanan, AdminPanelUser

def notifications(request):
    """Matikan semua notifikasi di admin panel (selalu 0)."""
    return {
        'belum_dibaca': 0,           # untuk Pesan
        'belum_dilihat': 0,          # untuk Komentar (placeholder)
        'tenant_belum_dibaca': 0,    # untuk DaftarTenant
        'layanan_belum_dibaca': 0,   # untuk DaftarLayanan
        'total_notifications': 0
    }

# Alternatif: Jika ingin fungsi terpisah
def pesan_notifications(request):
    if request.user.is_authenticated:
        try:
            count = Pesan.objects.filter(is_read=False, aktif=True).count()
            return {'pesan_belum_dibaca': count}
        except:
            return {'pesan_belum_dibaca': 0}
    return {'pesan_belum_dibaca': 0}


def tenant_notifications(request):
    if request.user.is_authenticated:
        try:
            # Sesuaikan dengan kondisi "belum dibaca" di model DaftarTenant
            # Jika tidak ada field is_read, mungkin berdasarkan status lain
            count = DaftarTenant.objects.filter(aktif=True).count()
            return {'tenant_belum_dibaca': count}
        except:
            return {'tenant_belum_dibaca': 0}
    return {'tenant_belum_dibaca': 0}

def layanan_notifications(request):
    if request.user.is_authenticated:
        try:
            # Sesuaikan dengan kondisi "belum dibaca" di model DaftarLayanan
            count = DaftarLayanan.objects.filter(aktif=True).count()
            return {'layanan_belum_dibaca': count}
        except:
            return {'layanan_belum_dibaca': 0}
    return {'layanan_belum_dibaca': 0}

def admin_context(request):
    """
    Context processor untuk menyediakan data admin panel dan user permissions
    """
    context = {}

    is_superadmin = False
    is_admin_panel_user = False

    if request.user.is_authenticated:
        try:
            # Cek apakah user memiliki profile admin panel
            admin_profile = request.user.admin_panel_profile
            is_admin_panel_user = True
            is_superadmin = bool(getattr(admin_profile, 'is_superadmin', False))
            context['is_superadmin'] = is_superadmin
            context['is_admin'] = True
        except AdminPanelUser.DoesNotExist:
            context['is_superadmin'] = False
            context['is_admin'] = False
            is_admin_panel_user = False

        # Fallback untuk superuser bawaan Django
        if getattr(request.user, 'is_superuser', False):
            is_admin_panel_user = True
            is_superadmin = True
            context['is_superadmin'] = True
            context['is_admin'] = True

        # Flag akses per-app untuk sidebar
        user = request.user

        if is_admin_panel_user or is_superadmin:
            has_admin_access = is_superadmin or any([
                user.has_perm('administrator.view_pesan'),
                user.has_perm('administrator.view_daftartenant'),
                user.has_perm('administrator.view_daftarlayanan'),
                user.has_perm('administrator.view_kategori'),
                user.has_perm('administrator.view_berita'),
                user.has_perm('administrator.view_agenda'),
                user.has_perm('administrator.view_visimisi'),
                user.has_perm('administrator.view_team'),
                user.has_perm('administrator.view_testimoni'),
                user.has_perm('administrator.view_slide'),
                user.has_perm('administrator.view_profil'),
                user.has_perm('administrator.view_baground'),
                user.has_perm('administrator.view_layanan'),
                user.has_perm('administrator.view_kontak'),
            ])

            has_cart_access = is_superadmin or any([
                user.has_perm('cart.view_kategoripenjualan'),
                user.has_perm('cart.view_produk'),
                user.has_perm('cart.view_pemesanan'),
                user.has_perm('cart.view_slidepenjualan'),
                user.has_perm('cart.view_jasa'),
            ])
        else:
            has_admin_access = False
            has_cart_access = False

        context['has_admin_access'] = has_admin_access
        context['has_cart_access'] = has_cart_access

    else:
        context['is_superadmin'] = False
        context['is_admin'] = False
        context['has_admin_access'] = False
        context['has_cart_access'] = False

    return context