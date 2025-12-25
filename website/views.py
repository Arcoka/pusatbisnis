from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.http import url_has_allowed_host_and_scheme
from django.core.paginator import Paginator
from django.conf import settings
from administrator.models import Slide, Berita, Kategori, Team, Testimoni, Profil, Kontak, VisiMisi, DaftarTenant, Baground, DaftarLayanan, Layanan, JenisLayanan, ModelInkubasi, Seleksi, TenantInkubator, Agenda
from cart.models import SlidePenjualan, Jasa, KategoriPenjualan, Produk
from django.utils.text import slugify
from administrator.forms import PesanForm, DaftarTenantForm, DaftarLayananForm
import uuid
from django.contrib import messages
from django.urls import reverse
import logging
from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from .utils.telegram import send_telegram_message

logger = logging.getLogger(__name__)


# from .models import Berita  # Pastikan model diimport

def login_view(request):
    context = {}
    
    # Tambahkan reCAPTCHA site key ke context jika ada
    if hasattr(settings, 'RECAPTCHA_SITE_KEY') and settings.RECAPTCHA_SITE_KEY:
        context['recaptcha_site_key'] = settings.RECAPTCHA_SITE_KEY
        logger.info(f"reCAPTCHA Site Key loaded: {settings.RECAPTCHA_SITE_KEY}")
    else:
        logger.warning("reCAPTCHA Site Key not found or empty in settings")
    
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        # Validasi reCAPTCHA jika diaktifkan
        if hasattr(settings, 'RECAPTCHA_SECRET_KEY') and settings.RECAPTCHA_SECRET_KEY:
            from urllib.parse import urlencode
            from urllib.request import urlopen
            import json
            
            recaptcha_response = request.POST.get('g-recaptcha-response')
            if not recaptcha_response:
                context['error'] = "Harap lengkapi validasi CAPTCHA"
                return render(request, "login.html", context)
                
            data = {
                'secret': settings.RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            
            try:
                # Verifikasi reCAPTCHA
                result = urlopen('https://www.google.com/recaptcha/api/siteverify', 
                              urlencode(data).encode()).read()
                result_json = json.loads(result)
                
                if not result_json.get('success'):
                    context['error'] = "Validasi CAPTCHA gagal. Silakan coba lagi."
                    return render(request, "login.html", context)
                    
            except Exception as e:
                # Jika terjadi error saat verifikasi, lanjutkan tanpa CAPTCHA (untuk development)
                if settings.DEBUG:
                    print(f"Error verifying reCAPTCHA: {e}")
                else:
                    context['error'] = "Terjadi kesalahan saat memverifikasi CAPTCHA. Silakan coba lagi nanti."
                    return render(request, "login.html", context)
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Debug: Print user information
            print(f"DEBUG: User {user.username} logged in")
            print(f"DEBUG: is_superuser: {user.is_superuser}")
            print(f"DEBUG: is_staff: {user.is_staff}")
            print(f"DEBUG: is_active: {user.is_active}")

            # Cek apakah user adalah superuser, jika ya langsung ke admin
            if user.is_superuser:
                print("DEBUG: Redirecting to administrator:berandaadmin (superuser)")
                return redirect("administrator:berandaadmin")

            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url and url_has_allowed_host_and_scheme(
                url=next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                print(f"DEBUG: Redirecting to next_url: {next_url}")
                return redirect(next_url)

            # Cek apakah user memiliki akses admin panel
            try:
                admin_profile = user.admin_panel_profile
                print("DEBUG: Redirecting to administrator:berandaadmin (admin profile)")
                return redirect("administrator:berandaadmin")
            except Exception as e:
                print(f"DEBUG: No admin profile found: {e}")
                # Jika bukan admin panel, cek apakah user adalah tenant (memiliki produk)
                from cart.models import Produk

                has_tenant_products = Produk.objects.filter(user=user).exists()
                if has_tenant_products:
                    print("DEBUG: Redirecting to penjualan (tenant)")
                    return redirect("penjualan")

                # Default: redirect ke beranda umum
                print("DEBUG: Redirecting to home (default)")
                return redirect("home")
        else:
            context['error'] = "Username atau password salah!"
            return render(request, "login.html", context)

    return render(request, "login.html", context)

def logout_view(request):
    logout(request)
    return redirect("login")  # Arahkan kembali ke halaman login setelah logout

def user_login(request):
    """Login khusus untuk user publik (bukan admin)"""
    context = {}

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            context['error'] = "Username dan password harus diisi!"
            return render(request, "user_login.html", context)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Debug: Print user information
            print(f"DEBUG: User {user.username} logged in")
            print(f"DEBUG: is_superuser: {user.is_superuser}")
            print(f"DEBUG: is_staff: {user.is_staff}")
            print(f"DEBUG: is_active: {user.is_active}")

            # Cek apakah user adalah superuser, jika ya langsung ke admin
            if user.is_superuser:
                print("DEBUG: Redirecting to administrator:berandaadmin (superuser)")
                return redirect("administrator:berandaadmin")
            
            # Cek apakah user adalah admin panel, jika ya tetap ke admin
            try:
                admin_profile = user.admin_panel_profile
                print("DEBUG: Redirecting to administrator:berandaadmin (admin profile)")
                return redirect("administrator:berandaadmin")
            except Exception as e:
                print(f"DEBUG: No admin profile found: {e}")
                # Bukan admin -> arahkan ke next atau home
                next_url = request.GET.get('next') or request.POST.get('next')
                if next_url and url_has_allowed_host_and_scheme(
                    url=next_url,
                    allowed_hosts={request.get_host()},
                    require_https=request.is_secure(),
                ):
                    print(f"DEBUG: Redirecting to next_url: {next_url}")
                    return redirect(next_url)
                print("DEBUG: Redirecting to home")
                return redirect("home")
        else:
            context['error'] = "Username atau password salah!"
            return render(request, "user_login.html", context)

    return render(request, "user_login.html", context)


def user_logout(request):
    logout(request)
    return redirect("home")

def user_register(request):
    """Pendaftaran user baru"""
    context = {}
    
    if request.method == "POST":
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validasi input
        if not email or not username or not password or not confirm_password:
            context['error'] = "Semua field harus diisi!"
            return render(request, "user_login.html", context)
        
        if password != confirm_password:
            context['error'] = "Password dan konfirmasi password tidak cocok!"
            return render(request, "user_login.html", context)
        
        if len(password) < 6:
            context['error'] = "Password minimal 6 karakter!"
            return render(request, "user_login.html", context)
        
        # Cek apakah username atau email sudah ada
        if User.objects.filter(username=username).exists():
            context['error'] = "Username sudah digunakan!"
            return render(request, "user_login.html", context)
        
        if User.objects.filter(email=email).exists():
            context['error'] = "Email sudah digunakan!"
            return render(request, "user_login.html", context)
        
        # Buat user baru
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            # Login otomatis setelah pendaftaran
            login(request, user)
            
            # Kirim notifikasi Telegram
            try:
                text_lines = [
                    "User Baru Terdaftar 🎉",
                    f"Username : {username}",
                    f"Email    : {email}",
                    f"Tanggal  : {user.date_joined.strftime('%d/%m/%Y %H:%M')}",
                ]
                send_telegram_message(text="\n".join(text_lines))
            except Exception as te:
                logger.warning(f"Gagal kirim Telegram (user register): {te}")
            
            context['success'] = f"Selamat! Akun dengan username {username} berhasil dibuat."
            return render(request, "user_login.html", context)
            
        except Exception as e:
            context['error'] = "Terjadi kesalahan saat membuat akun. Silakan coba lagi."
            logger.error(f"Error saat membuat user: {e}")
            return render(request, "user_login.html", context)
    
    return render(request, "user_login.html", context)

def beranda(request):
    query_slide = Slide.objects.filter(aktif=True).order_by('-id')
    query_team = Team.objects.filter(aktif=True).order_by('-id')
    query_testimoni = Testimoni.objects.filter(aktif=True).order_by('-id')
    query_profil = Profil.objects.filter(aktif=True).order_by('-id')
    query_kontak = Kontak.objects.filter(aktif=True).order_by('-id')
    berita_terbaru = Berita.objects.order_by('-tanggal', '-tanggal_upload', '-id')[:3]
    # Ambil agenda terbaru yang published, prioritaskan yang punya gambar
    agenda_with_image = Agenda.objects.filter(status='published').exclude(gambar='').exclude(gambar__isnull=True).order_by('-tanggal_mulai').first()
    agenda_terbaru = agenda_with_image if agenda_with_image else Agenda.objects.filter(status='published').order_by('-tanggal_mulai').first()
    query_baground = Baground.objects.filter(aktif=True).order_by('-id')
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Anda belum terdaftar sebagai user, silakan login terlebih dahulu untuk melanjutkan proses pengiriman pesan ini.')
            next_url = request.get_full_path()
            return redirect(f"{reverse('user_login')}?next={next_url}")
        form = PesanForm(request.POST)
        if form.is_valid():
            pesan = form.save(commit=False) # Get unsaved object
            pesan.save()  # Save the object to the database

            # Kirim notifikasi Telegram ringkasan pesan yang masuk
            try:
                text_lines = [
                    "Pesan Masuk (Beranda) ✉️",
                    f"Nama   : {getattr(pesan, 'nama', '-')}",
                    f"Email  : {getattr(pesan, 'email', '-')}",
                    f"Subjek : {getattr(pesan, 'subjek', getattr(pesan, 'subject', '-'))}",
                    f"Token  : {getattr(pesan, 'token_pesan', '-')}",
                ]
                send_telegram_message(text="\n".join(text_lines))
            except Exception as te:
                logger.warning(f"Gagal kirim Telegram (beranda pesan): {te}")

            messages.success(request, 'Pesan Anda telah berhasil dikirim!')
            return redirect('home')
    else:
        form = PesanForm()
    
    isi = {
        "judul": "Halaman Beranda",
        "slide": query_slide,
        "baground": query_baground,
        "team": query_team,
        "testimoni": query_testimoni,
        "profil": query_profil,
        "kontak": query_kontak,
        "berita": berita_terbaru,
        "agenda_terbaru": agenda_terbaru,
        "form": form,  # Form sudah ditambahkan ke dalam context
    }
    return render(request, 'beranda.html', isi)

def berita_detail(request, slug): 
    berita = get_object_or_404(Berita, slug=slug)  # Ambil berita berdasarkan slug
    

    context = {
        "judul": berita.judul, 
        "berita": berita,
    # Form sudah ditambahkan ke dalam context
    }
    return render(request, 'berita.html', context)

def berita_list(request):
    query_slide = Slide.objects.filter(aktif=True).order_by('-id')
    # Urutkan berdasarkan tanggal publikasi terbaru, fallback tanggal_upload, lalu id
    berita_list = Berita.objects.all().order_by('-tanggal', '-tanggal_upload', '-id')
    paginator = Paginator(berita_list, 12)  # 12 berita per halaman
    page_number = request.GET.get('page')  # Ambil nomor halaman dari query string
    berita_page = paginator.get_page(page_number)  # Ambil objek berita berdasarkan halaman
    query_kategori = Kategori.objects.filter(aktif=True).order_by('-id')
    
    context = { 
        "kategori": query_kategori,
        "slide": query_slide
        
    }
    return render(request, 'beritalist.html', {'berita_list': berita_page})

def profil(request): 
    query_slide = Slide.objects.filter(aktif=True).order_by('-id')
    query_profil = Profil.objects.filter(aktif=True).order_by('-id')
    isi = {
        "judul": "Halaman Profil", 
        "profil": query_profil,
        "slide": query_slide
    } 
    return render(request, 'profil.html', isi)

def team(request): 
    query_team = Team.objects.filter(aktif=True).order_by('-id')
    isi = {
        "judul": "Halaman Team", 
        "team": query_team  # Ubah dari "profil" menjadi "team" agar sesuai dengan template
    } 
    return render(request, 'team.html', isi)  # Gunakan template khusus team

def visimisi(request): 
    query_slide = Slide.objects.filter(aktif=True).order_by('-id')
    
    # Ambil data visi, misi, sasaran, dan tujuan secara terpisah
    visi_list = VisiMisi.objects.filter(visi__isnull=False, aktif=True).order_by('-id')
    misi_list = VisiMisi.objects.filter(misi__isnull=False, aktif=True).order_by('-id')
    sasaran_list = VisiMisi.objects.filter(sasaran__isnull=False, aktif=True).order_by('-id')
    tujuan_list = VisiMisi.objects.filter(tujuan__isnull=False, aktif=True).order_by('-id')
    
    isi = {
        "judul": "Halaman Profil", 
        "visi_list": visi_list,
        "misi_list": misi_list,
        "sasaran_list": sasaran_list,
        "tujuan_list": tujuan_list,
        "slide": query_slide
    } 
    return render(request, 'visimisi.html', isi)

def kontak(request):
    query_kontak = Kontak.objects.filter(aktif=True).order_by('-id')
    query_slide = Slide.objects.filter(aktif=True).order_by('-id')
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Anda belum terdaftar sebagai user, silakan login terlebih dahulu untuk melanjutkan proses pengiriman pesan ini.')
            next_url = request.get_full_path()
            return redirect(f"{reverse('user_login')}?next={next_url}")
        form = PesanForm(request.POST)
        if form.is_valid():
            pesan = form.save(commit=False) # Get unsaved object
            pesan.save()  # Save the object to the database

            # Telegram notify
            try:
                text_lines = [
                    "Pesan Masuk (Kontak) ✉️",
                    f"Nama   : {getattr(pesan, 'nama', '-')}",
                    f"Email  : {getattr(pesan, 'email', '-')}",
                    f"Subjek : {getattr(pesan, 'subjek', getattr(pesan, 'subject', '-'))}",
                    f"Token  : {getattr(pesan, 'token_pesan', '-')}",
                ]
                send_telegram_message(text="\n".join(text_lines))
            except Exception as te:
                logger.warning(f"Gagal kirim Telegram (kontak pesan): {te}")

            messages.success(request, 'Pesan Anda telah berhasil dikirim!')
            return redirect('kontak')
    else:
        form = PesanForm()
    isi = {
        "judul": "Informasi Kontak",
        "kontak": query_kontak,
        "slide": query_slide,
        "form": form,
    }
    return render(request, 'kontak.html', isi)

def hubungi_kami(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, 'Anda belum terdaftar sebagai user, silakan login terlebih dahulu untuk melanjutkan proses pengiriman pesan ini.')
            next_url = request.get_full_path()
            return redirect(f"{reverse('user_login')}?next={next_url}")
        form = PesanForm(request.POST)
        if form.is_valid():
            try:
                pesan = form.save(commit=False)
                pesan.token_pesan = str(uuid.uuid4())
                pesan.slug = slugify(pesan.nama) if getattr(pesan, 'nama', None) else str(uuid.uuid4())
                pesan.save()

                # Telegram notify
                try:
                    text_lines = [
                        "Pesan Masuk (Hubungi Kami) ✉️",
                        f"Nama   : {getattr(pesan, 'nama', '-')}",
                        f"Email  : {getattr(pesan, 'email', '-')}",
                        f"Subjek : {getattr(pesan, 'subjek', getattr(pesan, 'subject', '-'))}",
                        f"Token  : {getattr(pesan, 'token_pesan', '-')}",
                    ]
                    send_telegram_message(text="\n".join(text_lines))
                except Exception as te:
                    logger.warning(f"Gagal kirim Telegram (hubungi kami): {te}")

                messages.success(request, 'Pesan terkirim!')
                return redirect('hubungi_kami')
            except Exception as e:
                print("Error saving:", e)  # Debugging
                messages.error(request, 'Terjadi kesalahan sistem')
        else:
            print("Form errors:", form.errors)  # Debugging
            messages.error(request, 'Isi form dengan benar')
    else:
        form = PesanForm()
    
    return render(request, 'hubungikami.html', {'form': form})

def daftar_tenant(request):
    # Mengambil slide yang aktif, diurutkan berdasarkan ID terbaru
    query_slide = Slide.objects.filter(aktif=True).order_by('-id')

    # Cek apakah request adalah POST untuk menghandle form
    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, 'Anda belum terdaftar sebagai user, silakan login terlebih dahulu untuk melanjutkan proses pendaftaran tenant ini.')
            next_url = request.get_full_path()
            return redirect(f"{reverse('user_login')}?next={next_url}")
        # Perbaikan 1: Tambahkan request.FILES untuk menangani upload file
        form = DaftarTenantForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Menyimpan data tenant yang telah diisi
                daftartenant = form.save(commit=False)
                
                # Membuat token unik menggunakan uuid
                daftartenant.token_daftartenant = str(uuid.uuid4())
                
                # Membuat slug menggunakan nama, atau uuid jika nama tidak ada
                nama_slug = daftartenant.nama if daftartenant.nama else str(uuid.uuid4())
                base_slug = slugify(nama_slug)
                
                # Pastikan slug unik dengan menambahkan random string jika diperlukan
                if DaftarTenant.objects.filter(slug=base_slug).exists():
                    daftartenant.slug = f"{base_slug}-{str(uuid.uuid4())[:8]}"
                else:
                    daftartenant.slug = base_slug
                
                # Perbaikan 2: Cek integritas data sebelum menyimpan
                daftartenant.clean()  # Ini akan memvalidasi model-level constraints
                
                # Simpan data tenant ke database
                daftartenant.save()
                
                # Perbaikan 3: Tambahkan log untuk berhasil
                logger.info(f"Tenant berhasil terdaftar: {daftartenant.nama} ({daftartenant.email})")

                # Kirim notifikasi Telegram berisi data lengkap pendaftar tenant (teks),
                # dan jika ada file upload, kirim juga dokumen sebagai notifikasi terpisah
                try:
                    text_lines = [
                        "Pendaftaran Tenant Baru ✅",
                        f"Nama        : {daftartenant.nama or '-'}",
                        f"Email       : {daftartenant.email or '-'}",
                        f"Telepon     : {daftartenant.telepon or '-'}",
                        f"Nama Usaha  : {daftartenant.namausaha or '-'}",
                        f"Jenis Usaha : {daftartenant.jenisusaha or '-'}",
                        f"Form Upload : {'Ada' if daftartenant.form_upload else 'Kosong'}",
                        f"Token       : {daftartenant.token_daftartenant}",
                        f"Tanggal     : {daftartenant.tanggal_upload.strftime('%d/%m/%Y %H:%M') if daftartenant.tanggal_upload else '-'}",
                    ]
                    telegram_text = "\n".join(text_lines)

                    # Selalu kirim teks ringkasan
                    tg_result = send_telegram_message(text=telegram_text)
                    if not tg_result.get('success'):
                        logger.warning(f"Telegram notify gagal: {tg_result}")

                    # Jika ada file, kirim dokumen sebagai notifikasi kedua
                    if daftartenant.form_upload:
                        from .utils.telegram import send_telegram_document
                        try:
                            doc_result = send_telegram_document(
                                daftartenant.form_upload.path,
                                caption=f"Form Tenant: {daftartenant.nama or ''}"
                            )
                            if not doc_result.get('success'):
                                logger.warning(f"Kirim dokumen Telegram gagal: {doc_result}")
                        except Exception as de:
                            logger.error(f"Exception kirim dokumen Telegram: {de}")
                except Exception as te:
                    logger.error(f"Gagal kirim Telegram: {te}")
                
                # Kirim email token dinonaktifkan: cukup tampilkan pesan sukses sederhana
                messages.success(request, 'Pendaftaran tenant berhasil dikirim! Tim kami akan segera menghubungi Anda.')
                
                # Perbaikan 4: Redirect dengan parameter untuk konfirmasi
                return redirect('daftar_tenant')
            except ValidationError as ve:
                # Perbaikan 5: Tangani error validasi model secara spesifik
                messages.error(request, f'Validasi gagal: {ve}')
                logger.warning(f"Validasi tenant gagal: {ve}")
            except IntegrityError as ie:
                # Perbaikan 6: Tangani error integritas database (seperti duplikat)
                messages.error(request, 'Data yang Anda masukkan mungkin sudah terdaftar.')
                logger.warning(f"Integrity error: {ie}")
            except Exception as e:
                # Menampilkan pesan error jika ada masalah saat menyimpan data
                messages.error(request, 'Terjadi kesalahan sistem. Coba lagi.')
                # Perbaikan 7: Log error lebih detail
                logger.error(f"Error saat menyimpan tenant: {e}", exc_info=True)
        else:
            # Menampilkan form error jika form tidak valid
            logger.warning(f"Form errors: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    # Perbaikan 8: Tampilkan error per field untuk user
                    messages.error(request, f'Error pada {field}: {error}')
    else:
        form = DaftarTenantForm()  # Menampilkan form kosong jika request bukan POST

    # Menyusun konteks untuk mengirimkan data ke template
    context = {
        "slide": query_slide,  # Data slide untuk tampilan
        "form": form,  # Form untuk pendaftaran tenant
        "page_title": "Pendaftaran Tenant Inkubator Bisnis",  # Perbaikan 9: Tambahkan judul halaman
    }
    
    # Render halaman dengan data yang dikirimkan
    return render(request, 'daftartenantinkubator.html', context)

def toggle_aktif(request, id):
    # Ambil objek tenant berdasarkan ID, jika tidak ada akan tampil 404
    tenant = get_object_or_404(DaftarTenant, id=id)

    # Ubah nilai aktif (jika True jadi False, jika False jadi True)
    tenant.aktif = not tenant.aktif
    tenant.save()

    # Beri pesan sukses (opsional)
    if tenant.aktif:
        messages.success(request, f"Tenant '{tenant.nama}' telah diaktifkan.")
    else:
        messages.warning(request, f"Tenant '{tenant.nama}' telah dinonaktifkan.")

    # Redirect kembali ke halaman daftar tenant (admin namespace)
    return redirect('administrator:daftartenant_list')

def kategori(request): 
    query_kategori = Kategori.objects.filter(aktif=True).order_by('-id')
    isi = {
        "judul": "Halaman Kategori", 
        "kategori": query_kategori
    } 
    return render(request, 'berita.html', isi)

def baground(request): 
    query_baground = baground.objects.filter(aktif=True).order_by('-id')
    isi = {
        "judul": "Halaman Slide", 
        "baground": query_baground
    } 
    return render(request, 'beranda.html', isi)

def layanan(request): 
    query_layanan = Layanan.objects.order_by('-id')
    isi = { 
        "layanan": query_layanan
    } 
    return render(request, 'layanan.html', isi)

def submit_layanan(request):
    """View untuk user mengisi form layanan"""
    from django.utils import timezone
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Anda belum terdaftar sebagai user, silakan login terlebih dahulu untuk melanjutkan proses permintaan layanan ini.')
            next_url = request.get_full_path()
            return redirect(f"{reverse('user_login')}?next={next_url}")
        form = DaftarLayananForm(request.POST)
        query_slide = Slide.objects.filter(aktif=True).order_by('-id')
        query_layanan = Layanan.objects.order_by('-id')
        
        if form.is_valid():
            layanan = form.save()

            # Telegram notify ringkasan layanan (lebih lengkap)
            try:
                tanggal_str = getattr(layanan, 'tanggal', None)
                tanggal_str = tanggal_str.strftime('%d/%m/%Y') if tanggal_str else '-'
                waktu_str = getattr(layanan, 'waktu', None)
                waktu_str = waktu_str.strftime('%H:%M') if waktu_str else '-'
                dibuat_str = getattr(layanan, 'tanggal_upload', None)
                dibuat_str = dibuat_str.strftime('%d/%m/%Y %H:%M') if dibuat_str else '-'

                text_lines = [
                    "Permintaan Layanan Baru 🧾",
                    f"Nama        : {getattr(layanan, 'nama', '-')}",
                    f"Email       : {getattr(layanan, 'email', '-')}",
                    f"Telepon     : {getattr(layanan, 'telepon', getattr(layanan, 'no_telepon', '-'))}",
                    f"Alamat      : {getattr(layanan, 'alamat', '-')}",
                    f"Jenis Layanan: {getattr(layanan, 'jenislayanan', '-')}",
                    f"Jenis Produk : {getattr(layanan, 'jenisproduk', '-')}",
                    f"Jadwal       : {tanggal_str} • {waktu_str}",
                    f"Pesan        : {getattr(layanan, 'pesan', '-') or '-'}",
                    f"Kode Status  : {getattr(layanan, 'kode_status', '-')}",
                    f"Token        : {getattr(layanan, 'token_daftarlayanan', getattr(layanan, 'token', '-'))}",
                    f"Dibuat       : {dibuat_str}",
                ]
                send_telegram_message(text="\n".join(text_lines))
            except Exception as te:
                logger.warning(f"Gagal kirim Telegram (submit_layanan): {te}")

            messages.success(request, 'Data sudah masuk! Kami akan mengirimkan notifikasi di email Anda setelah admin memproses permintaan layanan.')
            return redirect('submit_layanan')
    else:
        form = DaftarLayananForm()
        query_slide = Slide.objects.filter(aktif=True).order_by('-id')
        query_layanan = Layanan.objects.order_by('-id')
    
    return render(request, 'form_layanan.html', {
        'form': form,
        "slide": query_slide,
        "layanan": query_layanan,
        'title': 'Form Permintaan Layanan',
        'today': timezone.now().date()
    })

def konfirmasi_layanan(request, slug):
    """View konfirmasi setelah submit layanan"""
    try:
        layanan = get_object_or_404(DaftarLayanan, slug=slug)
        return render(request, 'konfirmasi_layanan', {
            'layanan': layanan,
            'title': 'Konfirmasi Permintaan Layanan'
        })
    except:
        raise Http404("Halaman tidak ditemukan")

def modelinkubasi(request): 
    query_modelinkubasi = ModelInkubasi.objects.filter(aktif=True).order_by('-id')
    query_slide = Slide.objects.filter(aktif=True).order_by('-id')
    isi = {
        "judul": "Halaman Model Inkubasi", 
        "modelinkubasi": query_modelinkubasi,
        "slide": query_slide,
    } 
    return render(request, 'modelinkubasi.html', isi)

def tenantinkubator(request): 
    query_tenantinkubator = TenantInkubator.objects.filter(aktif=True).order_by('-id')
    
    isi = {
        "judul": "Halaman Model Inkubasi", 
        "tenantinkubator": query_tenantinkubator,
       
    } 
    return render(request, 'tenantinkubator.html', isi)
def testimoni(request): 
    query_testimoni = Testimoni.objects.filter(aktif=True).order_by('-id')
    isi = {
        "judul": "Halaman Testimoni", 
        "testimoni": query_testimoni  # Ubah dari "profil" menjadi "team" agar sesuai dengan template
    } 
    return render(request, 'beranda.html', isi)  # Gunakan template khusus team

def seleksi(request): 
    query_slide = Slide.objects.filter(aktif=True).order_by('-id')
    query_seleksi = Seleksi.objects.filter(aktif=True).order_by('-id')
    isi = {
        "judul": "Halaman Seleksi",
        "slide": query_slide,
        "seleksi": query_seleksi,
    }
    return render(request, 'seleksi.html', isi)

def faq(request):
    """View untuk halaman FAQ"""
    query_slide = Slide.objects.filter(aktif=True).order_by('-id')
    isi = {
        "judul": "FAQ - Pertanyaan yang Sering Diajukan",
        "slide": query_slide,
    }
    return render(request, 'faq.html', isi)

def jenislayanan(request):
    """View untuk menampilkan daftar jenis layanan"""
    query_jenislayanan = JenisLayanan.objects.filter(aktif=True).order_by('-id')
    query_slide = Slide.objects.filter(aktif=True).order_by('-id')
    isi = {
        "judul": "Jenis Layanan",
        "jenislayanan": query_jenislayanan,
        "slide": query_slide,  # Menambahkan data slide untuk header
    }
    return render(request, 'jenislayanan.html', isi)

#####-------bagian PENJUALAN

def berandapenjualan(request):
    query_slidepenjualan = SlidePenjualan.objects.filter(aktif=True).order_by('-id')
    query_jasa = Jasa.objects.filter(aktif=True).order_by('-id')
    query_kategoripenjualan = KategoriPenjualan.objects.filter(aktif=True).order_by('-id')
    # Menampilkan semua produk dari role manapun
    query_produk = Produk.objects.filter(aktif=True).order_by('-id')
    
    isi = {
        "judul": "Halaman Beranda",
        "slidepenjualan": query_slidepenjualan,
        "jasa": query_jasa,
        "kategoripenjualan": query_kategoripenjualan,
        "produk": query_produk,
    }
    return render(request, 'penjualan.html', isi)

def produk_detail(request, slug): 
    produk = get_object_or_404(Produk, slug=slug)  # Ambil produk berdasarkan slug

    context = {
        "nama": produk.nama, 
        "produk": produk,
    }
    return render(request, 'produk_detail.html', context)


# --- Telegram test endpoint ---
def telegram_test(request):
    """Send a test Telegram message.

    Query params:
    - token: optional, overrides settings.TELEGRAM_BOT_TOKEN
    - chat_id: optional, overrides settings.TELEGRAM_CHAT_ID
    - text: optional message text (default: 'Test dari website')
    """
    token = request.GET.get('token')
    chat_id = request.GET.get('chat_id')
    text = request.GET.get('text', 'Test dari website')
    result = send_telegram_message(text=text, token=token, chat_id=chat_id)
    return JsonResponse(result)




# -----------------------------
# Custom error handlers
# -----------------------------
def custom_404(request, exception):
    """Render a friendly 404 page."""
    context = {
        'title': 'Halaman Tidak Ditemukan',
        'path': request.path,
    }
    return render(request, 'errors/404.html', context, status=404)


def custom_500(request):
    """Render a friendly 500 page."""
    context = {
        'title': 'Terjadi Kesalahan Server',
    }
    return render(request, 'errors/500.html', context, status=500)
