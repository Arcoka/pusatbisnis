from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.contrib.auth.models import Group, Permission, User
from django.contrib import messages
from django.db import transaction, DatabaseError
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.translation import gettext_lazy as _
from .export_utils import export_model_to_excel
from openpyxl import load_workbook
from django.db.models import Count
from django.db.models.functions import TruncMonth, TruncDay
from django.contrib.sessions.models import Session
import logging
import datetime
import json

# Konfigurasi logger
logger = logging.getLogger('admin_actions')
logger.setLevel(logging.DEBUG)

# Buat handler untuk menulis ke file
file_handler = logging.FileHandler('admin_actions.log')
file_handler.setLevel(logging.DEBUG)

# Format log
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Tambahkan handler ke logger
if not logger.handlers:
    logger.addHandler(file_handler)
from .models import (
    Berita,
    Agenda,
    Slide,
    Kategori,
    Layanan,
    Kontak,
    Baground,
    User,
    VisiMisi,
    Team,
    ModelInkubasi,
    Testimoni,
    Profil,
    Pesan,
    DaftarTenant,
    DaftarLayanan,
    ProfilImage,
    TelegramRecipient,
    LogAktivitas,
    AdminRole,
)
from .role_forms import AdminRoleForm
from .forms import (
    KategoriForm,
    BeritaForm,
    AgendaForm,
    LayananForm,
    KontakForm,
    SlideForm,
    BagroundForm,
    VisiMisiForm,
    TeamForm,
    ModelInkubasiForm,
    TestimoniForm,
    ProfilForm,
    VisiForm,
    MisiForm,
    SasaranForm,
    TujuanForm,
    TelegramRecipientForm,
)
import uuid
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.utils.timezone import now
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import PesanForm
from .models import AdminPanelUser


def check_superadmin_access(user):
    """
    Cek apakah user adalah superadmin
    """
    if not user.is_authenticated:
        return False
    if hasattr(user, 'admin_panel_profile'):
        return user.admin_panel_profile.is_superadmin
    return user.is_superuser

def check_admin_access(user):
    """
    Cek apakah user adalah admin (termasuk superadmin)
    """
    if not user.is_authenticated:
        return False
    if hasattr(user, 'admin_panel_profile'):
        return user.admin_panel_profile.role is not None or user.admin_panel_profile.is_superadmin
    return user.is_superuser


def has_administrator_permissions(user):
    if not user.is_authenticated:
        return False
    return any(
        [
            user.has_perm('administrator.view_pesan'),
            user.has_perm('administrator.view_daftartenant'),
            user.has_perm('administrator.view_daftarlayanan'),
            user.has_perm('administrator.view_kategori'),
            user.has_perm('administrator.view_berita'),
            user.has_perm('administrator.view_visimisi'),
            user.has_perm('administrator.view_team'),
            user.has_perm('administrator.view_testimoni'),
            user.has_perm('administrator.view_slide'),
            user.has_perm('administrator.view_profil'),
            user.has_perm('administrator.view_baground'),
            user.has_perm('administrator.view_layanan'),
            user.has_perm('administrator.view_kontak'),
        ]
    )


def has_cart_permissions(user):
    if not user.is_authenticated:
        return False
    return any(
        [
            user.has_perm('cart.view_kategoripenjualan'),
            user.has_perm('cart.view_produk'),
            user.has_perm('cart.view_pemesanan'),
            user.has_perm('cart.view_slidepenjualan'),
            user.has_perm('cart.view_jasa'),
        ]
    )

# ============================
# Views
# ============================


@login_required
@user_passes_test(check_superadmin_access, login_url='administrator:login')
def role_list(request):
    """
    List semua role yang tersedia
    """
    roles = AdminRole.objects.all().order_by('name')
    return render(request, 'role_list.html', {'roles': roles})

@login_required
@user_passes_test(check_superadmin_access, login_url='administrator:login')
def role_create(request):
    """
    Buat role baru
    """
    if request.method == 'POST':
        form = AdminRoleForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    role = form.save()
                    messages.success(request, 'Role berhasil ditambahkan')
                    logger.info(f"Role {role.name} berhasil ditambahkan oleh {request.user.username}")
                    return redirect('administrator:role_list')
            except Exception as e:
                messages.error(request, f'Terjadi kesalahan: {str(e)}')
                logger.error(f"Gagal menambahkan role: {str(e)}")
        else:
            messages.error(request, 'Mohon periksa form yang Anda isi')
    else:
        form = AdminRoleForm()
    
    return render(request, 'role_form.html', {
        'form': form,
        'title': 'Tambah Role Baru',
        'action': 'Tambah'
    })
@login_required
@user_passes_test(check_superadmin_access, login_url='administrator:login')
def role_edit(request, role_id):
    """
    Edit role yang sudah ada
    """
    role = get_object_or_404(AdminRole, id=role_id)
    
    if request.method == 'POST':
        form = AdminRoleForm(request.POST, instance=role)
        if form.is_valid():
            try:
                with transaction.atomic():
                    role = form.save()
                    messages.success(request, f"Perubahan pada role '{role.name}' berhasil disimpan.")
                    logger.info(f"Role {role.name} berhasil diupdate oleh {request.user.username}")
                    return redirect('administrator:role_list')
            except Exception as e:
                messages.error(request, f'Terjadi kesalahan: {str(e)}')
                logger.error(f"Gagal mengupdate role: {str(e)}")
        else:
            messages.error(request, 'Mohon periksa form yang Anda isi')
    else:
        form = AdminRoleForm(instance=role)
    
    return render(request, 'role_form.html', {
        'form': form,
        'title': f'Edit Role: {role.name}',
        'submit_text': 'Simpan Perubahan',
    })

@login_required
def role_delete(request, role_id):
    """
    Hapus role
    """
    if not check_superadmin_access(request.user):
        messages.error(request, "Anda tidak memiliki izin untuk melakukan aksi ini.")
        return redirect("administrator:role_list")
    
    role = get_object_or_404(AdminRole, id=role_id)
    
    if request.method == 'POST':
        role_name = role.name
        role.delete()
        messages.success(request, f"Role '{role_name}' berhasil dihapus.")
        return redirect("administrator:role_list")
    
    return render(request, 'role_confirm_delete.html', {'role': role})

@login_required
def active_users(request):
    """
    List semua user yang terdaftar di Admin Panel
    """
    if not check_admin_access(request.user):
        messages.error(request, "Anda tidak memiliki akses ke halaman ini.")
        return redirect("administrator:berandaadmin")

    admin_panel_users = AdminPanelUser.objects.select_related("user", "role").all()
    context = {
        "users": [profile.user for profile in admin_panel_users],
        "admin_profiles": admin_panel_users,
        "is_superadmin": check_superadmin_access(request.user),
    }
    return render(request, "user_list.html", context)


@login_required
def add_admin_user(request):
    """
    Tambah user baru (hanya superadmin)
    """
    if not check_superadmin_access(request.user):
        messages.error(request, "Anda tidak memiliki izin untuk menambahkan user admin.")
        return redirect('administrator:active_users')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        is_superadmin = request.POST.get('is_superadmin') == 'on'
        role_id = request.POST.get('role')

        # Validasi input
        if not all([username, password, password2]):
            messages.error(request, "Semua field yang wajib diisi harus diisi!")
            return redirect('administrator:add_admin_user')

        if password != password2:
            messages.error(request, "Password tidak cocok!")
            return redirect('administrator:add_admin_user')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username sudah digunakan!")
            return redirect('administrator:add_admin_user')

        try:
            # Buat user baru
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password,
                is_staff=True
            )
            
            # Set user sebagai superuser jika dipilih
            if is_superadmin:
                user.is_superuser = True
                user.save()
            
            # Buat profil admin
            admin_profile = AdminPanelUser.objects.create(
                user=user, 
                is_superadmin=is_superadmin,
                role=None
            )
            
            # Set role jika dipilih dan bukan superadmin
            if not is_superadmin and role_id and role_id != '':
                try:
                    role = AdminRole.objects.get(id=role_id)
                    admin_profile.role = role
                    admin_profile.save()
                except AdminRole.DoesNotExist:
                    messages.warning(request, "Role yang dipilih tidak ditemukan. User dibuat tanpa role.")
            
            messages.success(request, f"User {username} berhasil ditambahkan!")
            return redirect('administrator:active_users')
        
        except Exception as e:
            messages.error(request, f"Terjadi kesalahan: {str(e)}")
            return redirect('administrator:add_admin_user')
    
    # Ambil daftar role untuk ditampilkan di form
    roles = AdminRole.objects.all()
    return render(request, 'add_user.html', {
        'roles': roles, 
        'can_edit_superadmin': True
    })


@login_required
@user_passes_test(lambda u: u.is_superuser or hasattr(u, 'admin_panel_profile') and u.admin_panel_profile.is_superadmin)
def edit_public_user(request, user_id):
    """Edit user biasa (bukan admin)"""
    user_to_edit = get_object_or_404(User, id=user_id)
    
    # Pastikan ini bukan admin user
    if hasattr(user_to_edit, 'admin_panel_profile'):
        messages.error(request, "User ini adalah admin user. Gunakan halaman edit admin user.")
        return redirect('administrator:edit_admin_user', user_id=user_id)
    
    if request.method == "POST":
        try:
            with transaction.atomic():
                # Validasi username unik
                new_username = request.POST.get("username", "").strip()
                if not new_username:
                    error_msg = "Username tidak boleh kosong"
                    logger.error(f"Gagal update user {user_to_edit.id}: {error_msg}")
                    messages.error(request, error_msg)
                    raise ValueError(error_msg)
                    
                if User.objects.filter(username=new_username).exclude(id=user_to_edit.id).exists():
                    error_msg = f"Username '{new_username}' sudah digunakan"
                    logger.warning(f"Gagal update user {user_to_edit.id}: {error_msg}")
                    messages.error(request, f"{error_msg}. Silakan gunakan username lain.")
                    raise ValueError("Username already exists")
                
                # Update user data dengan validasi
                try:
                    user_to_edit.username = new_username
                    
                    email = request.POST.get("email", "").strip()
                    if email and User.objects.filter(email=email).exclude(id=user_to_edit.id).exists():
                        error_msg = f"Email '{email}' sudah digunakan"
                        logger.warning(f"Gagal update user {user_to_edit.id}: {error_msg}")
                        messages.error(request, f"{error_msg}. Silakan gunakan email lain.")
                        raise ValueError("Email already exists")
                    
                    user_to_edit.email = email
                    user_to_edit.first_name = request.POST.get("first_name", "").strip()
                    user_to_edit.last_name = request.POST.get("last_name", "").strip()
                    
                    # Update status aktif
                    is_active = request.POST.get("is_active") == "on"
                    user_to_edit.is_active = is_active
                    
                    # Update status staff
                    is_staff = request.POST.get("is_staff") == "on"
                    user_to_edit.is_staff = is_staff
                    
                except Exception as e:
                    logger.error(f"Error validasi data user {user_to_edit.id}: {str(e)}")
                    messages.error(request, f"Kesalahan validasi data: {str(e)}")
                    raise
                
                # Update password jika diisi
                password = request.POST.get("password", "").strip()
                if password:
                    if len(password) < 8:
                        error_msg = "Password harus terdiri dari minimal 8 karakter"
                        logger.warning(f"Gagal update password user {user_to_edit.id}: {error_msg}")
                        messages.error(request, error_msg)
                        raise ValueError("Password too short")
                    try:
                        user_to_edit.set_password(password)
                        logger.info(f"Password user {user_to_edit.id} berhasil diupdate")
                    except Exception as e:
                        logger.error(f"Gagal mengupdate password user {user_to_edit.id}: {str(e)}")
                        messages.error(request, "Terjadi kesalahan saat mengupdate password.")
                        raise
                
                try:
                    user_to_edit.save()
                    
                    # Log aktivitas
                    try:
                        LogAktivitas.objects.create(
                            user=request.user,
                            aksi='Mengedit data user biasa',
                            keterangan=f'User {request.user.username} mengedit data user biasa {user_to_edit.username} (ID: {user_to_edit.id})',
                            tipe_aksi='update',
                            status_aksi='berhasil',
                            data_sebelum={
                                'username': user_to_edit.username,
                                'email': user_to_edit.email,
                                'is_active': user_to_edit.is_active,
                                'is_staff': user_to_edit.is_staff
                            }
                        )
                        logger.info(f"Berhasil update data user biasa {user_to_edit.id} oleh {request.user.username}")
                    except Exception as log_error:
                        logger.error(f"Gagal mencatat log aktivitas: {str(log_error)}")
                    
                    messages.success(request, f"User {user_to_edit.username} berhasil diperbarui!")
                    return redirect("administrator:daftar_user")
                    
                except DatabaseError as db_error:
                    error_msg = f"Kesalahan database: {str(db_error)}"
                    logger.error(f"Database error saat update user {user_to_edit.id}: {error_msg}", exc_info=True)
                    messages.error(request, "Terjadi kesalahan pada database. Silakan coba beberapa saat lagi.")
                    
                except Exception as save_error:
                    error_msg = f"Gagal menyimpan perubahan: {str(save_error)}"
                    logger.error(f"Error saat menyimpan perubahan user {user_to_edit.id}: {error_msg}", exc_info=True)
                    messages.error(request, "Gagal menyimpan perubahan. Silakan coba lagi.")
                    
        except ValueError as ve:
            logger.warning(f"Validation error saat edit user {user_to_edit.id}: {str(ve)}")
            
        except Exception as e:
            error_msg = f"Terjadi kesalahan tak terduga: {str(e)}"
            logger.error(f"Error tak terduga saat edit user {user_to_edit.id}: {error_msg}", exc_info=True)
            messages.error(request, "Terjadi kesalahan tak terduga. Silakan coba lagi.")
    
    # Render halaman edit
    return render(request, "edit_public_user.html", {
        "user": user_to_edit,
        "is_public_user": True
    })


@login_required
def edit_admin_user(request, user_id):
    # Dapatkan user yang akan diedit
    user_to_edit = get_object_or_404(User, id=user_id)
    
    # Hanya superadmin yang bisa mengedit user lain
    if not request.user.is_superuser and (not hasattr(request.user, 'admin_panel_profile') or not request.user.admin_panel_profile.is_superadmin):
        messages.error(request, "Anda tidak memiliki izin untuk mengedit user ini.")
        return redirect('administrator:active_users')

    # Get admin profile jika ada
    admin_profile_to_edit = None
    if hasattr(user_to_edit, 'admin_panel_profile'):
        admin_profile_to_edit = user_to_edit.admin_panel_profile

    if request.method == "POST":
        try:
            with transaction.atomic():
                # Validasi username unik
                new_username = request.POST.get("username", "").strip()
                if not new_username:
                    error_msg = "Username tidak boleh kosong"
                    logger.error(f"Gagal update user {user_to_edit.id}: {error_msg}")
                    messages.error(request, error_msg)
                    raise ValueError(error_msg)
                    
                if User.objects.filter(username=new_username).exclude(id=user_to_edit.id).exists():
                    error_msg = f"Username '{new_username}' sudah digunakan"
                    logger.warning(f"Gagal update user {user_to_edit.id}: {error_msg}")
                    messages.error(request, f"{error_msg}. Silakan gunakan username lain.")
                    raise ValueError("Username already exists")
                
                # Update user data dengan validasi
                try:
                    user_to_edit.username = new_username
                    email = request.POST.get("email", "").strip()
                    if not email:
                        raise ValueError("Email tidak boleh kosong")
                    
                    user_to_edit.email = email
                    user_to_edit.first_name = request.POST.get("first_name", "").strip()
                    user_to_edit.last_name = request.POST.get("last_name", "").strip()
                    
                except Exception as e:
                    logger.error(f"Error validasi data user {user_to_edit.id}: {str(e)}")
                    messages.error(request, f"Kesalahan validasi data: {str(e)}")
                    raise
                
                # Update status superadmin hanya jika user memiliki admin profile
                if admin_profile_to_edit:
                    is_superadmin = request.POST.get("is_superadmin") == "on"
                    admin_profile_to_edit.is_superadmin = is_superadmin
                    
                    # Update role jika bukan superadmin
                    if not is_superadmin:
                        role_id = request.POST.get("role")
                        if role_id and role_id != '':
                            try:
                                role = AdminRole.objects.get(id=role_id)
                                admin_profile_to_edit.role = role
                            except AdminRole.DoesNotExist:
                                admin_profile_to_edit.role = None
                                messages.warning(request, "Role yang dipilih tidak valid. User tidak memiliki role.")
                        else:
                            admin_profile_to_edit.role = None
                    else:
                        # Jika dijadikan superadmin, hapus role-nya
                        admin_profile_to_edit.role = None
                    
                    # Handle foto profil
                    if 'foto_profil' in request.FILES:
                        # Hapus foto lama jika ada
                        if admin_profile_to_edit.foto_profil:
                            admin_profile_to_edit.foto_profil.delete(save=False)
                        # Simpan foto baru
                        admin_profile_to_edit.foto_profil = request.FILES['foto_profil']
                    # Hapus foto jika dicentang
                    elif 'foto_profil-clear' in request.POST and request.POST['foto_profil-clear'] == '1':
                        if admin_profile_to_edit.foto_profil:
                            admin_profile_to_edit.foto_profil.delete(save=False)
                            admin_profile_to_edit.foto_profil = None
                
                # Update password jika diisi (untuk semua user)
                password = request.POST.get("password", "").strip()
                if password:
                    if len(password) < 8:
                        error_msg = "Password harus terdiri dari minimal 8 karakter"
                        logger.warning(f"Gagal update password user {user_to_edit.id}: {error_msg}")
                        messages.error(request, error_msg)
                        raise ValueError("Password too short")
                    try:
                        user_to_edit.set_password(password)
                        logger.info(f"Password user {user_to_edit.id} berhasil diupdate")
                    except Exception as e:
                        logger.error(f"Gagal mengupdate password user {user_to_edit.id}: {str(e)}")
                        messages.error(request, "Terjadi kesalahan saat mengupdate password.")
                        raise
                
                try:
                    user_to_edit.save()
                    if admin_profile_to_edit:
                        admin_profile_to_edit.save()
                    
                    # Log aktivitas
                    try:
                        LogAktivitas.objects.create(
                            user=request.user,
                            aksi='Mengedit data user',
                            keterangan=f'User {request.user.username} mengedit data user {user_to_edit.username} (ID: {user_to_edit.id})',
                            tipe_aksi='update',
                            status_aksi='berhasil',
                            data_sebelum={
                                'username': user_to_edit.username,
                                'email': user_to_edit.email,
                                'is_superadmin': admin_profile_to_edit.is_superadmin if admin_profile_to_edit else False,
                                'role': str(admin_profile_to_edit.role) if admin_profile_to_edit and admin_profile_to_edit.role else None
                            }
                        )
                        logger.info(f"Berhasil update data user {user_to_edit.id} oleh {request.user.username}")
                    except Exception as log_error:
                        logger.error(f"Gagal mencatat log aktivitas: {str(log_error)}")
                    
                    messages.success(request, f"Profil {user_to_edit.username} berhasil diperbarui!")
                    return redirect("administrator:active_users")
                    
                except DatabaseError as db_error:
                    error_msg = f"Kesalahan database: {str(db_error)}"
                    logger.error(f"Database error saat update user {user_to_edit.id}: {error_msg}", exc_info=True)
                    messages.error(request, "Terjadi kesalahan pada database. Silakan coba beberapa saat lagi.")
                    
                except Exception as save_error:
                    error_msg = f"Gagal menyimpan perubahan: {str(save_error)}"
                    logger.error(f"Error saat menyimpan perubahan user {user_to_edit.id}: {error_msg}", exc_info=True)
                    messages.error(request, "Gagal menyimpan perubahan. Silakan coba lagi.")
                    
        except ValueError as ve:
            # Pesan error untuk validasi sudah ditangani di atas
            logger.debug(f"Validasi gagal untuk user {user_to_edit.id}: {str(ve)}")
            
        except Exception as e:
            error_msg = f"Terjadi kesalahan tak terduga: {str(e)}"
            logger.critical(f"Error tak terduga saat update user {user_to_edit.id}: {error_msg}", exc_info=True)
            messages.error(request, "Terjadi kesalahan sistem. Silakan hubungi administrator.")
    
    # Ambil semua role untuk dropdown
    roles = AdminRole.objects.all()
    return render(request, "edit_user.html", {
        "user": user_to_edit,  # Mengubah dari user_edit ke user untuk konsistensi template
        "admin_profile": admin_profile_to_edit,
        "roles": roles,
        "can_edit_superadmin": True
    })


@login_required
def delete_admin_user(request, user_id):
    user_to_delete = get_object_or_404(User, id=user_id)

    if user_to_delete == request.user:
        messages.error(request, "Anda tidak dapat menghapus akun Anda sendiri.")
        return redirect("administrator:active_users")

    if request.method == "POST":
        try:
            username = user_to_delete.username
            if hasattr(user_to_delete, "admin_panel_profile"):
                user_to_delete.admin_panel_profile.delete()
            user_to_delete.delete()
            messages.success(request, f"User {username} berhasil dihapus.")
            return redirect("administrator:active_users")
        except Exception as e:
            messages.error(request, f"Gagal menghapus user: {str(e)}")
            return redirect("administrator:active_users")

    return render(
        request, "delete_user_confirm.html", {"user_to_delete": user_to_delete}
    )


def error_page(request):
    return render(request, "error.html", status=403)


@login_required
def berandaadmin(request):
    if not (check_superadmin_access(request.user) or has_administrator_permissions(request.user)):
        if has_cart_permissions(request.user):
            return redirect('berandapenjualan')
        return render(request, "error.html", status=403)

    berita = Berita.objects.count()
    slide = Slide.objects.filter(aktif=True).count()
    kategori = Kategori.objects.filter(aktif=True).count()
    kontak = Kontak.objects.filter(aktif=True).count()
    profil = Profil.objects.filter(aktif=True).count()
    visimisi = VisiMisi.objects.filter(aktif=True).count()
    pesan = Pesan.objects.filter(aktif=True).count()
    baground = Baground.objects.filter(aktif=True).count()
    # user = User.objects.filter(aktif=True).count()
    daftartenant = DaftarTenant.objects.filter(aktif=True).count()
    daftarlayanan = DaftarLayanan.objects.filter(aktif=True).count()
    layanan = Layanan.objects.count()

    # Filter statistik berdasarkan bulan dan tahun
    now_dt = now()
    selected_year = request.GET.get("tahun")
    selected_month = request.GET.get("bulan")

    try:
        selected_year_int = int(selected_year) if selected_year else now_dt.year
    except ValueError:
        selected_year_int = now_dt.year

    try:
        selected_month_int = int(selected_month) if selected_month else None
    except ValueError:
        selected_month_int = None

    tenant_qs = DaftarTenant.objects.filter(
        aktif=True, tanggal_upload__year=selected_year_int
    )
    layanan_qs = DaftarLayanan.objects.filter(
        aktif=True, tanggal_upload__year=selected_year_int
    )

    if selected_month_int:
        tenant_qs = tenant_qs.filter(tanggal_upload__month=selected_month_int)
        layanan_qs = layanan_qs.filter(tanggal_upload__month=selected_month_int)

        tenant_agg = (
            tenant_qs.annotate(period=TruncDay("tanggal_upload"))
            .values("period")
            .annotate(total=Count("id"))
            .order_by("period")
        )
        layanan_agg = (
            layanan_qs.annotate(period=TruncDay("tanggal_upload"))
            .values("period")
            .annotate(total=Count("id"))
            .order_by("period")
        )
        date_format = "%d %b"
    else:
        tenant_agg = (
            tenant_qs.annotate(period=TruncMonth("tanggal_upload"))
            .values("period")
            .annotate(total=Count("id"))
            .order_by("period")
        )
        layanan_agg = (
            layanan_qs.annotate(period=TruncMonth("tanggal_upload"))
            .values("period")
            .annotate(total=Count("id"))
            .order_by("period")
        )
        date_format = "%b %Y"

    tenant_labels = [item["period"].strftime(date_format) for item in tenant_agg]
    tenant_values = [item["total"] for item in tenant_agg]
    layanan_labels = [item["period"].strftime(date_format) for item in layanan_agg]
    layanan_values = [item["total"] for item in layanan_agg]

    # Daftar tahun yang tersedia dari data tenant dan layanan
    tenant_years = DaftarTenant.objects.dates("tanggal_upload", "year")
    layanan_years = DaftarLayanan.objects.dates("tanggal_upload", "year")
    year_set = {d.year for d in tenant_years} | {d.year for d in layanan_years}
    if not year_set:
        year_set = {now_dt.year}
    year_choices = sorted(year_set)

    # Tambahkan unread messages count untuk sidebar
    unread_messages_count = Pesan.objects.filter(aktif=True, is_read=False).count()

    isi = {
        "judul": "Halaman Administrator",
        "berita": berita,
        "slide": slide,
        "profil": profil,
        "kontak": kontak,
        "pesan": pesan,
        "baground": baground,
        "kategori": kategori,
        "daftartenant": daftartenant,
        "daftarlayanan": daftarlayanan,
        "visimisi": visimisi,
        "menu": "beranda",
        "layanan": layanan,
        "unread_messages_count": unread_messages_count,
        "year_choices": year_choices,
        "selected_year": selected_year_int,
        "selected_month": selected_month_int,
        "chart_tenant_labels": json.dumps(tenant_labels),
        "chart_tenant_values": json.dumps(tenant_values),
        "chart_layanan_labels": json.dumps(layanan_labels),
        "chart_layanan_values": json.dumps(layanan_values),
    }
    return render(request, "berandaadmin.html", isi)


# ============================
# Audit: Log Aktivitas (Superadmin Only)
# ============================
@login_required
def log_aktivitas_list(request):
    if not check_superadmin_access(request.user):
        messages.error(request, "Hanya superadmin yang dapat mengakses log aktivitas.")
        return redirect("administrator:berandaadmin")

    qs = LogAktivitas.objects.all().order_by("-started_at", "-id")

    # Filter sederhana
    q = request.GET.get("q", "").strip()
    method = request.GET.get("method", "").strip().upper()
    status = request.GET.get("status", "").strip()
    action = request.GET.get("action", "").strip().upper()

    if q:
        from django.db.models import Q

        qs = qs.filter(
            Q(path__icontains=q)
            | Q(user__username__icontains=q)
            | Q(ip_address__icontains=q)
            | Q(user_agent__icontains=q)
        )
    if method:
        qs = qs.filter(method=method[:10])
    if status:
        try:
            qs = qs.filter(status_code=int(status))
        except ValueError:
            pass
    if action:
        qs = qs.filter(action_type=action[:10])

    # Pagination sederhana
    page = int(request.GET.get("page", "1") or 1)
    page_size = 20
    start = (page - 1) * page_size
    end = start + page_size
    total = qs.count()
    items = qs[start:end]
    total_pages = (total + page_size - 1) // page_size

    context = {
        "judul": "Log Aktivitas",
        "menu": "audit",
        "items": items,
        "q": q,
        "method": method,
        "status": status,
        "action": action,
        "page": page,
        "total_pages": total_pages,
        "total": total,
    }
    return render(request, "log_aktivitas_list.html", context)


@login_required
def log_aktivitas_detail(request, pk: int):
    if not check_superadmin_access(request.user):
        messages.error(request, "Hanya superadmin yang dapat mengakses log aktivitas.")
        return redirect("administrator:berandaadmin")

    item = get_object_or_404(LogAktivitas, pk=pk)
    return render(
        request,
        "log_aktivitas_detail.html",
        {
            "judul": "Detail Log Aktivitas",
            "menu": "audit",
            "item": item,
        },
    )


# ============================
# Telegram Recipients (custom admin pages)
# ============================


@login_required
def telegram_list(request):
    if not check_admin_access(request.user):
        messages.error(request, "Anda tidak memiliki akses ke halaman ini.")
        return redirect("administrator:berandaadmin")
    items = TelegramRecipient.objects.all().order_by("-dibuat", "-id")
    return render(
        request,
        "telegram_list.html",
        {
            "items": items,
            "judul": "Penerima Telegram",
            "menu": "telegram",
        },
    )


@login_required
def telegram_create(request):
    if not check_superadmin_access(request.user):
        messages.error(request, "Hanya superadmin yang dapat menambah penerima.")
        return redirect("administrator:telegram_list")
    if request.method == "POST":
        form = TelegramRecipientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Penerima Telegram berhasil ditambahkan.")
            return redirect("administrator:telegram_list")
    else:
        form = TelegramRecipientForm()
    return render(
        request,
        "telegram_form.html",
        {
            "form": form,
            "judul": "Tambah Penerima Telegram",
            "menu": "telegram",
            "mode": "create",
        },
    )


@login_required
def telegram_edit(request, pk: int):
    if not check_superadmin_access(request.user):
        messages.error(request, "Hanya superadmin yang dapat mengedit penerima.")
        return redirect("administrator:telegram_list")
    item = get_object_or_404(TelegramRecipient, pk=pk)
    if request.method == "POST":
        form = TelegramRecipientForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "Penerima Telegram berhasil diperbarui.")
            return redirect("administrator:telegram_list")
    else:
        form = TelegramRecipientForm(instance=item)
    return render(
        request,
        "telegram_form.html",
        {
            "form": form,
            "judul": "Edit Penerima Telegram",
            "menu": "telegram",
            "mode": "edit",
            "item": item,
        },
    )


@login_required
def telegram_delete(request, pk: int):
    if not check_superadmin_access(request.user):
        messages.error(request, "Hanya superadmin yang dapat menghapus penerima.")
        return redirect("administrator:telegram_list")
    item = get_object_or_404(TelegramRecipient, pk=pk)
    if request.method == "POST":
        item.delete()
        messages.success(request, "Penerima Telegram berhasil dihapus.")
        return redirect("administrator:telegram_list")
    return render(
        request,
        "telegram_confirm_delete.html",
        {
            "item": item,
            "judul": "Hapus Penerima Telegram",
            "menu": "telegram",
        },
    )


####### INI BAGIAN KATEGORI
@login_required(login_url="login")
def kategoriadmin(request):
    kategori = Kategori.objects.order_by("-id")
    context = {"judul": "Data Kategori", "menu": "kategori", "kategori_list": kategori}
    return render(request, "kategori/kategoriadmin.html", context)


@login_required(login_url="login")
def formkategoriadmin(request):
    if request.method == "POST":
        token_kategori = str(uuid.uuid4())
        datadeskripsi = request.POST.get("deskripsi")
        form = KategoriForm(request.POST, request.FILES)  # Ambil data dari request
        if form.is_valid():  # Validasi form
            kategori = form.save(commit=False)
            kategori.token_kategori = token_kategori
            kategori.deskripsi = datadeskripsi
            kategori.save()
            return redirect(
                "administrator:kategoriadmin"
            )  # Redirect ke halaman kategori setelah menyimpan
    else:
        form = KategoriForm()  # Tampilkan form kosong jika GET request
    context = {"judul": "Form Kategori", "menu": "kategori", "form": form}
    return render(request, "kategori/formkategoriadmin.html", context)


@login_required(login_url="login")
def editkategoriadmin(request, token):
    kategori = get_object_or_404(
        Kategori, token_kategori=token
    )  # memanggil satu data yang kategorinya sama maka satu yang lainnya tidak akan tertampil
    if request.method == "POST":
        datadeskripsi = request.POST.get("deskripsi")
        form = KategoriForm(request.POST, request.FILES, instance=kategori)
        if form.is_valid():
            kategoriedit = form.save(commit=False)
            kategoriedit.deskripsi = datadeskripsi
            kategoriedit.save()
            return redirect("administrator:kategoriadmin")  # Redirect ke halaman daftar kategori
    else:
        form = KategoriForm(instance=kategori)
    context = {
        "judul": "Form Edit Kategori",
        "menu": "kategori",
        "form": form,
        "kategori": kategori,
    }
    return render(request, "kategori/formkategoriadmin.html", context)


@login_required(login_url="login")
def deletekategoriadmin(request, token):
    kategori = get_object_or_404(Kategori, token_kategori=token)
    if request.method == "POST":
        kategori.delete()
        return redirect("administrator:kategoriadmin")
    return redirect("administrator:kategoriadmin")


########  INI BAGIAN BERITA


@login_required(login_url="login")
def beritaadmin(request):
    # Urutkan berdasarkan tanggal publikasi terbaru, fallback ke tanggal_upload jika diperlukan
    berita = Berita.objects.order_by("-tanggal", "-tanggal_upload")
    context = {"judul": "Data Berita", "menu": "berita", "berita_list": berita}
    return render(request, "berita/beritaadmin.html", context)


@login_required(login_url="login")
def formberitaadmin(request):
    if request.method == "POST":
        token_berita = str(uuid.uuid4())
        datadeskripsi = request.POST.get("deskripsi")

        form = BeritaForm(request.POST, request.FILES)  # Ambil data dari request
        if form.is_valid():  # Validasi form
            berita = form.save(commit=False)
            berita.token_berita = token_berita
            berita.deskripsi = datadeskripsi
            berita.save()
            return redirect(
                "administrator:beritaadmin"
            )  # Redirect ke halaman berita setelah menyimpan
    else:
        form = BeritaForm()  # Tampilkan form kosong jika GET request
    context = {"judul": "Form Berita", "menu": "berita", "form": form}
    return render(request, "berita/formberitaadmin.html", context)


@login_required(login_url="login")
def editberitaadmin(request, token):
    berita = get_object_or_404(
        Berita, token_berita=token
    )  # memanggil satu data yang beritanya sama maka satu yang lainnya tidak akan tertampil
    if request.method == "POST":
        # datadeskripsi = request.POST.get('deskripsi')
        form = BeritaForm(request.POST, request.FILES, instance=berita)
        if form.is_valid():
            form.save()
            # beritaedit.deskripsi = datadeskripsi
            # beritaedit.save()
            return redirect("administrator:beritaadmin")  # Redirect ke halaman daftar berita
    else:
        form = BeritaForm(instance=berita)
    context = {
        "judul": "Form Edit Berita",
        "menu": "berita",
        "form": form,
        "berita": berita,
    }
    return render(request, "berita/formberitaadmin.html", context)


@login_required(login_url="login")
def deleteberitaadmin(request, token):
    berita = get_object_or_404(Berita, token_berita=token)
    if request.method == "POST":
        berita.delete()
        return redirect("administrator:beritaadmin")
    return redirect("administrator:beritaadmin")


@login_required(login_url="login")
def agendaadmin(request):
    agenda = Agenda.objects.order_by("-tanggal_mulai")
    context = {"judul": "Data Agenda", "menu": "agenda", "agenda_list": agenda}
    return render(request, "agenda/agendaadmin.html", context)


@login_required(login_url="login")
def formagendaadmin(request):
    if request.method == "POST":
        form = AgendaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("administrator:agendaadmin")
    else:
        form = AgendaForm()
    context = {"judul": "Form Agenda", "menu": "agenda", "form": form}
    return render(request, "agenda/formagendaadmin.html", context)


@login_required(login_url="login")
def editagendaadmin(request, slug):
    agenda = get_object_or_404(Agenda, slug=slug)
    if request.method == "POST":
        form = AgendaForm(request.POST, request.FILES, instance=agenda)
        if form.is_valid():
            form.save()
            return redirect("administrator:agendaadmin")
    else:
        form = AgendaForm(instance=agenda)
    context = {
        "judul": "Form Edit Agenda",
        "menu": "agenda",
        "form": form,
        "agenda": agenda,
    }
    return render(request, "agenda/formagendaadmin.html", context)


@login_required(login_url="login")
def deleteagendaadmin(request, slug):
    agenda = get_object_or_404(Agenda, slug=slug)
    if request.method == "POST":
        agenda.delete()
        return redirect("administrator:agendaadmin")
    return redirect("administrator:agendaadmin")


##### INI BAGIAN LAYANAN
@login_required(login_url="login")
def layananadmin(request):
    layanan = Layanan.objects.order_by("-id")  # Menampilkan semua layanan dari role manapun
    context = {"judul": "Data Layanan", "menu": "layanan", "layanan_list": layanan}
    return render(request, "layanan/layananadmin.html", context)


@login_required(login_url="login")
def formlayananadmin(request):
    if request.method == "POST":
        token_layanan = str(uuid.uuid4())
        # datadeskripsi = request.POST.get('deskripsi')
        form = LayananForm(request.POST, request.FILES)  # Ambil data dari request
        if form.is_valid():  # Validasi form
            layanan = form.save(commit=False)
            layanan.token_layanan = token_layanan
            # layanan.deskripsi = datadeskripsi
            layanan.save()
            return redirect(
                "administrator:layananadmin"
            )  # Redirect ke halaman layanan setelah menyimpan
    else:
        form = LayananForm()  # Tampilkan form kosong jika GET request
    context = {"judul": "Form Layanan", "menu": "layanan", "form": form}
    return render(request, "layanan/formlayananadmin.html", context)


@login_required(login_url="login")
def editlayananadmin(request, token):
    layanan = get_object_or_404(
        Layanan, token_layanan=token
    )  # memanggil satu data yang layanannya sama maka satu yang lainnya tidak akan tertampil
    if request.method == "POST":
        # datadeskripsi = request.POST.get('deskripsi')
        form = LayananForm(request.POST, request.FILES, instance=layanan)
        if form.is_valid():
            form.save()
            # layananedit.deskripsi = datadeskripsi
            # layananedit.save()
            return redirect("administrator:layananadmin")  # Redirect ke halaman daftar layanan
    else:
        form = LayananForm(instance=layanan)
    context = {"judul": "Form Edit Layanan", "form": form, "layanan": layanan}
    return render(request, "layanan/formlayananadmin.html", context)


@login_required(login_url="login")
def deletelayananadmin(request, token):
    layanan = get_object_or_404(Layanan, token_layanan=token)
    if request.method == "POST":
        layanan.delete()
        return redirect("administrator:layananadmin")
    return redirect("administrator:layananadmin")


# BAGIAN KONTAK
@login_required(login_url="login")
def kontakadmin(request):
    kontak = Kontak.objects.order_by("-id")
    context = {"judul": "Data Kontak", "menu": "kontak", "kontak_list": kontak}
    return render(request, "kontakadmin.html", context)


@login_required(login_url="login")
def formkontakadmin(request):
    if request.method == "POST":
        token_kontak = str(uuid.uuid4())
        form = KontakForm(request.POST, request.FILES)
        if form.is_valid():
            kontak = form.save(commit=False)
            kontak.token_kontak = token_kontak
            kontak.save()
            return redirect("administrator:kontakadmin")
    else:
        form = KontakForm()
    context = {"judul": "Form Kontak", "menu": "kontak", "form": form}
    return render(request, "formkontakadmin.html", context)


@login_required(login_url="login")
def editkontakadmin(request, token):
    kontak = get_object_or_404(Kontak, token_kontak=token)
    if request.method == "POST":
        form = KontakForm(request.POST, request.FILES, instance=kontak)
        if form.is_valid():
            form.save()
            return redirect("administrator:kontakadmin")
    else:
        form = KontakForm(instance=kontak)
    context = {
        "judul": "Form Edit Kontak",
        "menu": "kontak",
        "form": form,
        "kontak": kontak,
    }
    return render(request, "formkontakadmin.html", context)


@login_required(login_url="login")
def deletekontakadmin(request, token):
    kontak = get_object_or_404(Kontak, token_kontak=token)
    if request.method == "POST":
        kontak.delete()
        return redirect("kontakadmin")
    return redirect("kontakadmin")


# BAGIAN PESAN KONTAK
@login_required
def pesan_list(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    pesan_list = Pesan.objects.all().order_by('-tanggal_upload')
    
    # Handle export to Excel
    if 'export' in request.GET and request.GET.get('export') == 'excel':
        from .admin import PesanAdmin
        pesan_admin = PesanAdmin(Pesan, None)
        return pesan_admin.export_to_excel(request, pesan_list)
    
    belum_dibaca = pesan_list.filter(is_read=False).count()
    unread_messages_count = belum_dibaca  # Untuk sidebar badge
    context = {
        'pesan_list': pesan_list,
        'belum_dibaca': belum_dibaca,
        'unread_messages_count': unread_messages_count,
        "menu": "pesan",  # Menandai menu "Pesan" aktif
    }
    return render(request, "pesan_list.html", context)


@login_required
def pesan_detail(request, slug):
    pesan = get_object_or_404(Pesan, slug=slug)

    # Menandai pesan sebagai telah dibaca saat dibuka
    if not pesan.is_read:
        pesan.is_read = True
        pesan.save()

    return render(request, "pesan_detail.html", {"pesan": pesan})


@login_required
def pesan_delete(request, slug):
    pesan = get_object_or_404(Pesan, slug=slug)

    if request.method == "POST":
        # Soft delete - mengubah status aktif menjadi False
        pesan.aktif = False
        pesan.save()
        messages.success(request, "Pesan berhasil dihapus")
        return redirect("administrator:pesan_list")

    # Jika bukan POST, tampilkan halaman konfirmasi
    return render(request, "pesan_confirm_delete.html", {"pesan": pesan})


# Fungsi baru untuk toggle status tampil di website
@login_required
def toggle_tampil_di_website(request, slug):
    pesan = get_object_or_404(Pesan, slug=slug)

    if request.method == "POST":
        # Toggle status tampil_di_website
        pesan.tampil_di_website = not pesan.tampil_di_website
        pesan.save()

        status = (
            "ditampilkan di website"
            if pesan.tampil_di_website
            else "disembunyikan dari website"
        )
        messages.success(request, f"Pesan berhasil {status}")

        # Kembali ke halaman yang sama (detail atau list)
        redirect_url = request.POST.get("next", "administrator:pesan_list")
        return redirect(redirect_url)

    # Redirect ke halaman list jika bukan POST
    return redirect("administrator:pesan_list")


# BAGIAN DAFTAR TENANT
@login_required
def daftartenant_list(request):
    """Halaman daftar tenant untuk admin panel"""
    # Cek akses admin
    if not check_admin_access(request.user):
        messages.error(request, "Anda tidak memiliki akses ke halaman ini.")
        return redirect("administrator:berandaadmin")

    daftartenant_list = DaftarTenant.objects.filter(aktif=True).order_by(
        "-tanggal_upload"
    )
    
    # Handle export to Excel
    if 'export' in request.GET and request.GET.get('export') == 'excel':
        from .admin import DaftarTenantAdmin
        tenant_admin = DaftarTenantAdmin(DaftarTenant, None)
        return tenant_admin.export_to_excel(request, daftartenant_list)
    
    belum_dibaca = daftartenant_list.filter(is_read=False).count()
    context = {
        "daftartenant_list": daftartenant_list,
        "belum_dibaca": belum_dibaca,
        "menu": "daftartenant",  # Menandai menu "DaftarTenant" aktif
    }
    return render(request, "daftar_tenant/daftartenant_list.html", context)


@login_required
def daftartenant_import(request):
    """Import data DaftarTenant dari file Excel (.xlsx).

    Format kolom yang diharapkan (baris pertama sebagai header, baris kedua dst data):
      1. Nama
      2. Email
      3. Telepon
      4. Nama Usaha
      5. Jenis Usaha
      6. Deskripsi (opsional)
    """
    # Cek akses admin panel
    if not check_admin_access(request.user):
        messages.error(request, "Anda tidak memiliki akses ke halaman ini.")
        return redirect("administrator:berandaadmin")

    # Wajib punya permission tambah DaftarTenant
    if not request.user.has_perm("administrator.add_daftartenant"):
        messages.error(request, "Anda tidak memiliki izin untuk mengimport data tenant.")
        return redirect("administrator:daftartenant_list")

    if request.method != "POST":
        messages.error(request, "Metode request tidak valid.")
        return redirect("administrator:daftartenant_list")

    upload = request.FILES.get("file")
    if not upload:
        messages.error(request, "Silakan pilih file Excel terlebih dahulu.")
        return redirect("administrator:daftartenant_list")

    # Hanya izinkan .xlsx
    if not (upload.name.lower().endswith(".xlsx")):
        messages.error(request, "Format file tidak didukung. Gunakan file Excel (.xlsx).")
        return redirect("administrator:daftartenant_list")

    try:
        wb = load_workbook(upload, data_only=True)
        ws = wb.active

        created = 0
        skipped = 0

        # Mulai dari baris ke-2 (baris pertama dianggap header)
        for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            if not row or not any(row):
                continue  # lewati baris kosong

            # Pastikan kita punya minimal 5 kolom pertama
            nama = (row[0] or "").strip() if len(row) > 0 and row[0] else ""
            email = (row[1] or "").strip() if len(row) > 1 and row[1] else ""
            telepon = (row[2] or "").strip() if len(row) > 2 and row[2] else ""
            namausaha = (row[3] or "").strip() if len(row) > 3 and row[3] else ""
            jenisusaha = (row[4] or "").strip() if len(row) > 4 and row[4] else ""
            deskripsi = (row[5] or "").strip() if len(row) > 5 and row[5] else ""

            # Minimal nama atau email harus terisi, kalau tidak skip
            if not nama and not email:
                skipped += 1
                continue

            DaftarTenant.objects.create(
                nama=nama,
                email=email or None,
                telepon=telepon or None,
                namausaha=namausaha or None,
                jenisusaha=jenisusaha or None,
                deskripsi=deskripsi or None,
                aktif=True,
            )
            created += 1

        if created:
            messages.success(
                request,
                f"Berhasil mengimport {created} tenant dari Excel. {skipped} baris dilewati.",
            )
        else:
            messages.warning(
                request,
                "Tidak ada data tenant yang berhasil diimport. Periksa isi file Excel Anda.",
            )

    except Exception as e:
        messages.error(request, f"Terjadi kesalahan saat membaca file Excel: {e}")

    return redirect("administrator:daftartenant_list")


@login_required
def daftartenant_detail(request, slug):
    """Detail satu tenant untuk admin panel"""
    # Cek akses admin
    if not check_admin_access(request.user):
        messages.error(request, "Anda tidak memiliki akses ke halaman ini.")
        return redirect("administrator:berandaadmin")

    daftartenant = get_object_or_404(DaftarTenant, slug=slug)

    # Menandai daftartenant sebagai telah dibaca saat dibuka
    if not daftartenant.is_read:
        daftartenant.is_read = True
        daftartenant.save()

    return render(request, "daftar_tenant/daftartenant_detail.html", {"daftartenant": daftartenant})


@login_required
def daftartenant_delete(request, slug):
    # Cek akses superadmin untuk delete
    if not check_superadmin_access(request.user):
        messages.error(request, "Anda tidak memiliki akses untuk menghapus data.")
        return redirect("administrator:daftartenant_list")

    daftartenant = get_object_or_404(DaftarTenant, slug=slug)

    if request.method == "POST":
        # Soft delete - mengubah status aktif menjadi False
        daftartenant.aktif = False
        daftartenant.save()
        messages.success(
            request, "DaftarTenant berhasil dihapus", extra_tags="admin-only"
        )
        return redirect("administrator:daftartenant_list")

    # Jika bukan POST, tampilkan halaman konfirmasi
    return render(
        request, "daftartenant_confirm_delete.html", {"daftartenant": daftartenant}
    )


@login_required
def toggle_aktif(request, tenant_id):
    """Toggle status aktif/nonaktif tenant"""
    daftartenant = get_object_or_404(DaftarTenant, id=tenant_id)
    
    if request.method == "POST":
        # Toggle status aktif
        daftartenant.aktif = not daftartenant.aktif
        daftartenant.save()
        
        status = "diaktifkan" if daftartenant.aktif else "dinonaktifkan"
        messages.success(request, f"Tenant '{daftartenant.nama}' berhasil {status}")
        
        # Kembali ke halaman yang sama
        redirect_url = request.POST.get("next", "administrator:daftartenant_list")
        return redirect(redirect_url)
    
    # Redirect ke halaman list jika bukan POST
    return redirect("administrator:daftartenant_list")


###untuk Daftar layanan


@login_required
def admin_daftar_layanan(request):
    """View admin untuk melihat semua layanan"""
    layanan_list = DaftarLayanan.objects.all().order_by("-tanggal_upload")
    return render(
        request,
        "daftar_layanan/daftar_layanan.html",
        {"layanan_list": layanan_list, "title": "Daftar Permintaan Layanan"},
    )


@login_required
def admin_detail_layanan(request, slug):
    """View admin untuk melihat detail layanan"""
    layanan = get_object_or_404(DaftarLayanan, slug=slug)

    # Mark as read when viewed
    if not layanan.is_read:
        layanan.is_read = True
        layanan.save()

    return render(
        request,
        "daftar_layanan/detail_layanan.html",
        {"layanan": layanan, "title": f"Detail Layanan - {layanan.nama}"},
    )


@login_required
def admin_update_status(request, slug):
    """View admin untuk mengubah status aktif/nonaktif layanan"""
    layanan = get_object_or_404(DaftarLayanan, slug=slug)

    if request.method == "POST":
        status = request.POST.get("status", None)
        if status is not None:
            layanan.aktif = status == "aktif"
            layanan.save()
            messages.success(
                request, f"Status layanan dari {layanan.nama} berhasil diperbarui"
            )

    return redirect(reverse("administrator:admin_detail_layanan", kwargs={"slug": layanan.slug}))


##### INI BAGIAN SLIDE
@login_required(login_url="login")
def slideadmin(request):
    slide = Slide.objects.order_by("-id")
    context = {"judul": "Data Slide", "menu": "slide", "slide_list": slide}
    return render(request, "slideadmin.html", context)


@login_required(login_url="login")
def formslideadmin(request):
    if request.method == "POST":
        token_slide = str(uuid.uuid4())
        # datadeskripsi = request.POST.get('deskripsi')
        form = SlideForm(request.POST, request.FILES)  # Ambil data dari request
        if form.is_valid():  # Validasi form
            slide = form.save(commit=False)
            slide.token_slide = token_slide
            # slide.deskripsi = datadeskripsi
            slide.save()
            return redirect("administrator:slideadmin")  # Redirect ke halaman slide setelah menyimpan
    else:
        form = SlideForm()  # Tampilkan form kosong jika GET request
    context = {"judul": "Form Slide", "menu": "slide", "form": form}
    return render(request, "formslideadmin.html", context)


@login_required(login_url="login")
def editslideadmin(request, token):
    slide = get_object_or_404(
        Slide, token_slide=token
    )  # memanggil satu data yang slidenya sama maka satu yang lainnya tidak akan tertampil
    if request.method == "POST":
        form = SlideForm(request.POST, request.FILES, instance=slide)
        if form.is_valid():
            form.save()
            return redirect("administrator:slideadmin")  # Redirect ke halaman daftar slide
    else:
        form = SlideForm(instance=slide)
    context = {
        "judul": "Form Edit Slide",
        "menu": "slide",
        "form": form,
        "slide": slide,
    }
    return render(request, "formslideadmin.html", context)


@login_required(login_url="login")
def deleteslideadmin(request, token):
    slide = get_object_or_404(Slide, token_slide=token)
    if request.method == "POST":
        slide.delete()
        return redirect("administrator:slideadmin")
    return redirect("administrator:slideadmin")


##### INI BAGIAN BAGROUND
@login_required(login_url="login")
def bagroundadmin(request):
    baground = Baground.objects.order_by("-id")
    context = {"judul": "Data Baground", "menu": "baground", "baground_list": baground}
    return render(request, "bagroundadmin.html", context)


@login_required(login_url="login")
def formbagroundadmin(request):
    if request.method == "POST":
        token_baground = str(uuid.uuid4())
        # datadeskripsi = request.POST.get('deskripsi')
        form = BagroundForm(request.POST, request.FILES)  # Ambil data dari request
        if form.is_valid():  # Validasi form
            baground = form.save(commit=False)
            baground.token_baground = token_baground
            # baground.deskripsi = datadeskripsi
            baground.save()
            return redirect(
                "administrator:bagroundadmin"
            )  # Redirect ke halaman baground setelah menyimpan
    else:
        form = BagroundForm()  # Tampilkan form kosong jika GET request
    context = {"judul": "Form Baground", "menu": "baground", "form": form}
    return render(request, "formbagroundadmin.html", context)


@login_required(login_url="login")
def editbagroundadmin(request, token):
    baground = get_object_or_404(
        Baground, token_baground=token
    )  # memanggil satu data yang bagroundnya sama maka satu yang lainnya tidak akan tertampil
    if request.method == "POST":
        form = BagroundForm(request.POST, request.FILES, instance=baground)
        if form.is_valid():
            form.save()
            return redirect("administrator:bagroundadmin")  # Redirect ke halaman daftar baground
    else:
        form = BagroundForm(instance=baground)
    context = {
        "judul": "Form Edit Baground",
        "menu": "baground",
        "form": form,
        "baground": baground,
    }
    return render(request, "formbagroundadmin.html", context)


@login_required(login_url="login")
def deletebagroundadmin(request, token):
    baground = get_object_or_404(Baground, token_baground=token)
    if request.method == "POST":
        baground.delete()
        return redirect("administrator:bagroundadmin")
    return redirect("administrator:bagroundadmin")


@login_required(login_url="login")
def visimisiadmin(request):
    visimisi = VisiMisi.objects.order_by("-id")
    context = {"judul": "Data VisiMisi", "menu": "visimisi", "visimisi_list": visimisi}
    return render(request, "visi_misi/visimisiadmin.html", context)


@login_required(login_url="login")
def formvisimisiadmin(request):
    jenis = request.GET.get("jenis", "lengkap")
    form_class = None

    # Pilih form berdasarkan jenis
    if jenis == "visi":
        form_class = VisiForm
        judul = "Tambah Visi"
    elif jenis == "misi":
        form_class = MisiForm
        judul = "Tambah Misi"
    elif jenis == "sasaran":
        form_class = SasaranForm
        judul = "Tambah Sasaran"
    elif jenis == "tujuan":
        form_class = TujuanForm
        judul = "Tambah Tujuan"
    else:
        form_class = VisiMisiForm
        judul = "Form VisiMisi"

    # PENTING: Inisialisasi form DI SINI
    form = form_class()

    if request.method == "POST":
        token_visimisi = str(uuid.uuid4())
        form = form_class(request.POST, request.FILES)

        if form.is_valid():
            visimisi = form.save(commit=False)
            visimisi.token_visimisi = token_visimisi

            # Set field yang tidak digunakan jadi None
            if jenis == "tujuan":
                visimisi.visi = None
                visimisi.misi = None
                visimisi.sasaran = None

            visimisi.save()
            return redirect("administrator:visimisiadmin")

    context = {"judul": judul, "menu": "visimisi", "form": form, "jenis": jenis}

    return render(request, f"visi_misi/form_{jenis}_admin.html", context)


@login_required(login_url="login")
def editvisimisiadmin(request, token):
    visimisi = get_object_or_404(VisiMisi, token_visimisi=token)
    jenis = request.GET.get("jenis", "lengkap")
    form_class = None

    # Tentukan jenis form berdasarkan data yang diedit
    if jenis == "visi" or (
        visimisi.visi
        and not visimisi.misi
        and not visimisi.sasaran
        and not visimisi.tujuan
    ):
        form_class = VisiForm
        judul = "Edit Visi"
    elif jenis == "misi" or (
        not visimisi.visi
        and visimisi.misi
        and not visimisi.sasaran
        and not visimisi.tujuan
    ):
        form_class = MisiForm
        judul = "Edit Misi"
    elif jenis == "sasaran" or (
        not visimisi.visi
        and not visimisi.misi
        and visimisi.sasaran
        and not visimisi.tujuan
    ):
        form_class = SasaranForm
        judul = "Edit Sasaran"
    elif jenis == "tujuan" or (
        not visimisi.visi
        and not visimisi.misi
        and not visimisi.sasaran
        and visimisi.tujuan
    ):
        form_class = TujuanForm
        judul = "Edit Tujuan"
    else:
        form_class = VisiMisiForm
        judul = "Edit VisiMisi"

    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=visimisi)
        if form.is_valid():
            form.save()
            return redirect("administrator:visimisiadmin")
    else:
        form = form_class(instance=visimisi)

    context = {
        "judul": judul,
        "menu": "visimisi",
        "form": form,
        "visimisi": visimisi,
        "jenis": jenis,
    }

    # Gunakan template sesuai jenis
    if jenis in ["visi", "misi", "sasaran", "tujuan"]:
        return render(request, f"visi_misi/form_{jenis}_admin.html", context)
    return render(request, "visi_misi/formvisimisiadmin.html", context)


@login_required(login_url="login")
def deletevisimisiadmin(request, token):
    visimisi = get_object_or_404(VisiMisi, token_visimisi=token)

    if request.method == "POST":
        # Cek jenis hapus berdasarkan parameter jenis
        jenis = request.POST.get("jenis", "lengkap")

        if jenis == "lengkap":
            # Hapus seluruh record
            visimisi.delete()
        else:
            # Hapus/kosongkan field tertentu saja
            if jenis == "visi":
                visimisi.visi = None
            elif jenis == "misi":
                visimisi.misi = None
            elif jenis == "sasaran":
                visimisi.sasaran = None
            elif jenis == "tujuan":
                visimisi.tujuan = None

            # Simpan perubahan
            visimisi.save()

        return redirect("administrator:visimisiadmin")

    # Tentukan jenis hapus berdasarkan data yang ada
    jenis = "lengkap"
    judul = "Hapus VisiMisi"

    if (
        visimisi.visi
        and not visimisi.misi
        and not visimisi.sasaran
        and not visimisi.tujuan
    ):
        jenis = "visi"
        judul = "Hapus Visi"
    elif (
        not visimisi.visi
        and visimisi.misi
        and not visimisi.sasaran
        and not visimisi.tujuan
    ):
        jenis = "misi"
        judul = "Hapus Misi"
    elif (
        not visimisi.visi
        and not visimisi.misi
        and visimisi.sasaran
        and not visimisi.tujuan
    ):
        jenis = "sasaran"
        judul = "Hapus Sasaran"
    elif (
        not visimisi.visi
        and not visimisi.misi
        and not visimisi.sasaran
        and visimisi.tujuan
    ):
        jenis = "tujuan"
        judul = "Hapus Tujuan"

    context = {"judul": judul, "menu": "visimisi", "visimisi": visimisi, "jenis": jenis}

    # Bisa juga membuat template konfirmasi hapus sesuai jenis
    if jenis in ["visi", "misi", "sasaran", "tujuan"]:
        return render(request, f"visi_misi/confirm_delete_{jenis}_admin.html", context)
    return render(request, "visi_misi/confirm_delete_visimisi_admin.html", context)


##### INI BAGIAN TEAM
@login_required(login_url="login")
def teamadmin(request):
    team = Team.objects.order_by("-id")
    context = {"judul": "Data Team", "menu": "team", "team_list": team}
    return render(request, "teamadmin.html", context)


@login_required(login_url="login")
def formteamadmin(request):
    if request.method == "POST":
        token_team = str(uuid.uuid4())
        # datadeskripsi = request.POST.get('deskripsi')
        form = TeamForm(request.POST, request.FILES)  # Ambil data dari request
        if form.is_valid():  # Validasi form
            team = form.save(commit=False)
            team.token_team = token_team
            # team.deskripsi = datadeskripsi
            team.save()
            return redirect("administrator:teamadmin")  # Redirect ke halaman team setelah menyimpan
    else:
        form = TeamForm()  # Tampilkan form kosong jika GET request
    context = {"judul": "Form Team", "menu": "team", "form": form}
    return render(request, "formteamadmin.html", context)


@login_required(login_url="login")
def editteamadmin(request, token):
    team = get_object_or_404(
        Team, token_team=token
    )  # memanggil satu data yang teamnya sama maka satu yang lainnya tidak akan tertampil
    if request.method == "POST":
        form = TeamForm(request.POST, request.FILES, instance=team)
        if form.is_valid():
            form.save()
            # teamedit.deskripsi = datadeskripsi
            # teamedit.save()
            return redirect("administrator:teamadmin")  # Redirect ke halaman daftar team
    else:
        form = TeamForm(instance=team)
    context = {"judul": "Form Edit Team", "menu": "team", "form": form, "team": team}
    return render(request, "formteamadmin.html", context)


@login_required(login_url="login")
def deleteteamadmin(request, token):
    team = get_object_or_404(Team, token_team=token)
    if request.method == "POST":
        team.delete()
        return redirect("administrator:teamadmin")
    return redirect("administrator:teamadmin")


##### INI BAGIAN MODEL INKUBASI
@login_required(login_url="login")
def modelinkubasiadmin(request):
    modelinkubasi = ModelInkubasi.objects.order_by("-id")
    context = {
        "judul": "Data ModelInkubasi",
        "menu": "modelinkubasi",
        "modelinkubasi_list": modelinkubasi,
    }
    return render(request, "modelinkubasiadmin.html", context)


@login_required(login_url="login")
def formmodelinkubasiadmin(request):
    if request.method == "POST":
        token_modelinkubasi = str(uuid.uuid4())
        # datadeskripsi = request.POST.get('deskripsi')
        form = ModelInkubasiForm(request.POST, request.FILES)  # Ambil data dari request
        if form.is_valid():  # Validasi form
            modelinkubasi = form.save(commit=False)
            modelinkubasi.token_modelinkubasi = token_modelinkubasi
            # modelinkubasi.deskripsi = datadeskripsi
            modelinkubasi.save()
            return redirect(
                "modelinkubasiadmin"
            )  # Redirect ke halaman modelinkubasi setelah menyimpan
    else:
        form = ModelInkubasiForm()  # Tampilkan form kosong jika GET request
    context = {"judul": "Form ModelInkubasi", "menu": "modelinkubasi", "form": form}
    return render(request, "formmodelinkubasiadmin.html", context)


@login_required(login_url="login")
def editmodelinkubasiadmin(request, token):
    modelinkubasi = get_object_or_404(
        ModelInkubasi, token_modelinkubasi=token
    )  # memanggil satu data yang modelinkubasinya sama maka satu yang lainnya tidak akan tertampil
    if request.method == "POST":
        form = ModelInkubasiForm(request.POST, request.FILES, instance=modelinkubasi)
        if form.is_valid():
            form.save()
            return redirect(
                "modelinkubasiadmin"
            )  # Redirect ke halaman daftar modelinkubasi
    else:
        form = ModelInkubasiForm(instance=modelinkubasi)
    context = {
        "judul": "Form Edit ModelInkubasi",
        "menu": "modelinkubasi",
        "form": form,
        "modelinkubasi": modelinkubasi,
    }
    return render(request, "formmodelinkubasiadmin.html", context)


@login_required(login_url="login")
def deletemodelinkubasiadmin(request, token):
    modelinkubasi = get_object_or_404(ModelInkubasi, token_modelinkubasi=token)
    if request.method == "POST":
        modelinkubasi.delete()
        return redirect("modelinkubasiadmin")
    return redirect("modelinkubasiadmin")


##### INI BAGIAN TESTIMONI
@login_required(login_url="login")
def testimoniadmin(request):
    testimoni = Testimoni.objects.order_by("-id")
    context = {
        "judul": "Data Testimoni",
        "menu": "testimoni",
        "testimoni_list": testimoni,
    }
    return render(request, "testimoniadmin.html", context)


@login_required(login_url="login")
def formtestimoniadmin(request):
    if request.method == "POST":
        token_testimoni = str(uuid.uuid4())
        # datadeskripsi = request.POST.get('deskripsi')
        form = TestimoniForm(request.POST, request.FILES)  # Ambil data dari request
        if form.is_valid():  # Validasi form
            testimoni = form.save(commit=False)
            testimoni.token_testimoni = token_testimoni
            # testimoni.deskripsi = datadeskripsi
            testimoni.save()
            return redirect(
                "administrator:testimoniadmin"
            )  # Redirect ke halaman testimoni setelah menyimpan
    else:
        form = TestimoniForm()  # Tampilkan form kosong jika GET request
    context = {"judul": "Form Testimoni", "menu": "testimoni", "form": form}
    return render(request, "formtestimoniadmin.html", context)


@login_required(login_url="login")
def edittestimoniadmin(request, token):
    testimoni = get_object_or_404(
        Testimoni, token_testimoni=token
    )  # memanggil satu data yang testimoninya sama maka satu yang lainnya tidak akan tertampil
    if request.method == "POST":
        form = TestimoniForm(request.POST, request.FILES, instance=testimoni)
        if form.is_valid():
            form.save()
            return redirect("administrator:testimoniadmin")  # Redirect ke halaman daftar testimoni
    else:
        form = TestimoniForm(instance=testimoni)
    context = {
        "judul": "Form Edit Testimoni",
        "menu": "testimoni",
        "form": form,
        "testimoni": testimoni,
    }
    return render(request, "formtestimoniadmin.html", context)


@login_required(login_url="login")
def deletetestimoniadmin(request, token):
    testimoni = get_object_or_404(Testimoni, token_testimoni=token)
    if request.method == "POST":
        testimoni.delete()
        return redirect("administrator:testimoniadmin")
    return redirect("administrator:testimoniadmin")


##### INI BAGIAN PROIL
@login_required(login_url="login")
def profiladmin(request):
    profil = Profil.objects.order_by("-id")
    context = {"judul": "Data Profil", "menu": "profil", "profil_list": profil}
    return render(request, "profiladmin.html", context)


@login_required(login_url="login")
def formprofiladmin(request):
    if request.method == "POST":
        token_profil = str(uuid.uuid4())
        form = ProfilForm(request.POST, request.FILES)
        if form.is_valid():
            profil = form.save(commit=False)
            profil.token_profil = token_profil
            profil.save()

            # simpan gambar tambahan (multiple)
            files = request.FILES.getlist("images")
            if files:
                base_order = ProfilImage.objects.filter(profil=profil).count()
                for idx, f in enumerate(files):
                    ProfilImage.objects.create(
                        profil=profil, gambar=f, urutan=base_order + idx
                    )
            messages.success(request, "Profil berhasil disimpan.")
            return redirect("administrator:profiladmin")
    else:
        form = ProfilForm()

    context = {"judul": "Form Profil", "menu": "profil", "form": form}
    if request.method == "POST" and not form.is_valid():
        messages.error(
            request,
            f"Gagal menyimpan profil. Periksa isian Anda. Error: {form.errors.as_text()}",
        )
    return render(request, "formprofiladmin.html", context)


@login_required(login_url="login")
@user_passes_test(lambda u: u.is_superuser or hasattr(u, 'admin_panel_profile') and u.admin_panel_profile.is_superadmin)
def detail_user(request, user_id):
    """Menampilkan detail user"""
    user = get_object_or_404(User, id=user_id)
    
    # Get session info if user is logged in
    from django.utils import timezone
    is_logged_in = False
    session_info = None
    
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    for session in sessions:
        try:
            data = session.get_decoded()
            if data.get('_auth_user_id') == str(user.id):
                is_logged_in = True
                session_info = {
                    'session_key': session.session_key,
                    'expire_date': session.expire_date,
                    'ip_address': data.get('ip_address', 'Unknown'),
                    'user_agent': data.get('user_agent', 'Unknown')[:100] if data.get('user_agent') else 'Unknown'
                }
                break
        except (User.DoesNotExist, KeyError, AttributeError):
            continue
    
    context = {
        'judul': 'Detail User',
        'menu': 'daftar_user',
        'user_detail': user,
        'is_logged_in': is_logged_in,
        'session_info': session_info
    }
    
    return render(request, 'detail_user.html', context)


def daftar_user(request):
    """Menampilkan daftar semua user yang ada di sistem"""
    from django.utils import timezone
    
    # Get all users
    all_users = User.objects.all().order_by('-date_joined')
    
    # Get active sessions to show login status
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    logged_in_user_ids = []
    
    for session in sessions:
        try:
            data = session.get_decoded()
            user_id = data.get('_auth_user_id')
            if user_id:
                logged_in_user_ids.append(int(user_id))
        except (User.DoesNotExist, KeyError, AttributeError):
            continue
    
    context = {
        'judul': 'Daftar User',
        'menu': 'daftar_user',
        'users': all_users,
        'logged_in_user_ids': logged_in_user_ids,
        'total_users': all_users.count(),
        'total_logged_in': len(logged_in_user_ids)
    }
    
    return render(request, 'daftar_user.html', context)


def user_login_list(request):
    """Menampilkan daftar user yang sedang login"""
    from django.utils import timezone
    
    # Get all active sessions
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    
    logged_in_users = []
    for session in sessions:
        try:
            data = session.get_decoded()
            user_id = data.get('_auth_user_id')
            if user_id:
                user = User.objects.get(id=user_id)
                # Get session info
                session_data = {
                    'user': user,
                    'session_key': session.session_key,
                    'expire_date': session.expire_date,
                    'login_time': session.expire_date - timezone.timedelta(seconds=1200),  # Approximate login time
                    'ip_address': data.get('ip_address', 'Unknown'),
                    'user_agent': data.get('user_agent', 'Unknown')[:100] if data.get('user_agent') else 'Unknown'
                }
                logged_in_users.append(session_data)
        except (User.DoesNotExist, KeyError, AttributeError):
            continue
    
    # Sort by login time (most recent first)
    logged_in_users.sort(key=lambda x: x['login_time'], reverse=True)
    
    context = {
        'judul': 'Daftar User Login',
        'menu': 'user_login',
        'logged_in_users': logged_in_users,
        'total_logged_in': len(logged_in_users),
        'total_sessions': sessions.count(),
        'debug_sessions': sessions.count()  # Tambahkan debug info
    }
    
    return render(request, 'user_login_list.html', context)


@login_required(login_url="login")
def editprofiladmin(request, token):
    profil = get_object_or_404(Profil, token_profil=token)
    if request.method == "POST":
        form = ProfilForm(request.POST, request.FILES, instance=profil)
        if form.is_valid():
            form.save()
            files = request.FILES.getlist("images")
            if files:
                base_order = ProfilImage.objects.filter(profil=profil).count()
                for idx, f in enumerate(files):
                    ProfilImage.objects.create(
                        profil=profil, gambar=f, urutan=base_order + idx
                    )
            messages.success(request, "Perubahan profil berhasil disimpan.")
            return redirect("administrator:profiladmin")
    else:
        form = ProfilForm(instance=profil)

    context = {
        "judul": "Form Edit Profil",
        "menu": "profil",
        "form": form,
        "profil": profil,
        "profil_images": ProfilImage.objects.filter(profil=profil).order_by(
            "urutan", "id"
        ),
    }
    if request.method == "POST" and not form.is_valid():
        messages.error(
            request,
            f"Gagal menyimpan perubahan. Periksa isian Anda. Error: {form.errors.as_text()}",
        )
    return render(request, "formprofiladmin.html", context)


@login_required(login_url="login")
def delete_profil_image(request, token, image_id):
    profil = get_object_or_404(Profil, token_profil=token)
    img = get_object_or_404(ProfilImage, id=image_id, profil=profil)
    if request.method == "POST":
        img.delete()
    return redirect("administrator:editprofiladmin", token=token)


@login_required(login_url="login")
def deleteprofiladmin(request, token):
    profil = get_object_or_404(Profil, token_profil=token)
    if request.method == "POST":
        profil.delete()
        return redirect("administrator:profiladmin")
    return redirect("administrator:profiladmin")


@login_required
def kirim_token_layanan(request, slug):
    """
    Mengirim token layanan ke email pendaftar dari admin panel
    """
    from django.http import Http404

    raise Http404("Fitur kirim token dinonaktifkan")


#########--------BAGIAN PENJUALAN
