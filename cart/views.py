from django.shortcuts import render, get_object_or_404, redirect
from django.utils.html import strip_tags
from .models import SlidePenjualan, Pemesanan, Jasa, KategoriPenjualan, Produk
from .forms import SlidePenjualanForm, PemesananForm, JasaForm, KategoriPenjualanForm, ProdukForm
import uuid
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.db.models import Q

# View untuk form tambah slide penjualan
@login_required(login_url='login')
def formslidepenjualanadmin(request):
    if request.method == "POST":
        token_slidepenjualan = str(uuid.uuid4())
        form = SlidePenjualanForm(request.POST, request.FILES)
        if form.is_valid():
            slidepenjualan = form.save(commit=False)
            slidepenjualan.token_slidepenjualan = token_slidepenjualan
            slidepenjualan.save()
            return redirect('slidepenjualanadmin')
    else:
        form = SlidePenjualanForm()
    context = {
        "judul": "Form SlidePenjualan",
        "menu": "slidepenjualan",
        "form": form
    }
    return render(request, 'formslidepenjualanadmin.html', context)


# View untuk edit slide penjualan
@login_required(login_url='login')
def editslidepenjualanadmin(request, token):
    slidepenjualan = get_object_or_404(SlidePenjualan, token_slidepenjualan=token)
    if request.method == "POST":
        form = SlidePenjualanForm(request.POST, request.FILES, instance=slidepenjualan)
        if form.is_valid():
            form.save()
            return redirect('slidepenjualanadmin')
    else:
        form = SlidePenjualanForm(instance=slidepenjualan)
    context = {
        "judul": "Form Edit SlidePenjualan",
        "menu": "slidepenjualan",
        "form": form,
        'slidepenjualan': slidepenjualan
    }
    return render(request, 'formslidepenjualanadmin.html', context)

# View untuk hapus slide penjualan
@login_required(login_url='login')
def deleteslidepenjualanadmin(request, token):
    slidepenjualan = get_object_or_404(SlidePenjualan, token_slidepenjualan=token)
    if request.method == 'POST':
        slidepenjualan.delete()
        return redirect('slidepenjualanadmin')
    return redirect('slidepenjualanadmin')
# View untuk admin slide penjualan
@login_required(login_url='login')
def slidepenjualanadmin(request):
    slidepenjualan = SlidePenjualan.objects.order_by('-id')
    context = {
        "judul": "Data SlidePenjualan",
        "menu": "penjualan",
        "submenu": "slidepenjualanadmin",
        "slidepenjualan_list": slidepenjualan
    }
    return render(request, 'slidepenjualanadmin.html', context)




@login_required(login_url='login')
def berandapenjualan(request):
    slidepenjualan = SlidePenjualan.objects.filter(aktif=True).count()
    produk_qs = Produk.objects.filter(aktif=True)
    produk = produk_qs.count()
    jasa = Jasa.objects.filter(aktif=True).count()
    kategoripenjualan = KategoriPenjualan.objects.filter(aktif=True).count()
    pesan_qs = Pemesanan.objects.filter(aktif=True).filter(
        Q(pilihan='ingin_membeli')
        | Q(pilihan='pesan')
        | Q(pilihan='tertarik')
        | Q(pilihan='ingin_bertanya')
    )
    pesan = pesan_qs.count()
    like_qs = Pemesanan.objects.filter(aktif=True, pilihan='like')
    like = like_qs.count()

    # KPI tambahan
    low_stock_count = produk_qs.filter(stok__lte=5).count()
    terbaru_produk = produk_qs.order_by('-tanggal_upload')[:6]
    terbaru_pesanan = pesan_qs.order_by('-tanggal_upload')[:6]

    isi = {
        "judul": "Administrator Cart",
        'menu': 'penjualan',
        'slidepenjualan': slidepenjualan,
        'pesan': pesan,
        'like': like,
        'jasa': jasa,
        'kategoripenjualan': kategoripenjualan,
        'produk': produk,
        'low_stock_count': low_stock_count,
        'terbaru_produk': terbaru_produk,
        'terbaru_pesanan': terbaru_pesanan,
    }
    return render(request, 'berandapenjualan.html', isi)


@login_required(login_url='login')
def pesanadmin(request):
    if not request.user.has_perm('cart.view_pemesanan'):
        raise Http404()

    qs = Pemesanan.objects.filter(aktif=True).filter(
        Q(pilihan='ingin_membeli')
        | Q(pilihan='pesan')
        | Q(pilihan='tertarik')
        | Q(pilihan='ingin_bertanya')
    ).order_by('-tanggal_upload', '-id')

    count_tertarik = qs.filter(pilihan='tertarik').count()
    count_ingin_membeli = qs.filter(pilihan='ingin_membeli').count()
    count_ingin_bertanya = qs.filter(pilihan='ingin_bertanya').count()

    q = (request.GET.get('q') or '').strip()
    if q:
        qs = qs.filter(
            Q(nama__icontains=q)
            | Q(email__icontains=q)
            | Q(no_telepon__icontains=q)
            | Q(produk__nama__icontains=q)
            | Q(alamat__icontains=q)
        )

    context = {
        'judul': 'Pesan Produk',
        'menu': 'penjualan',
        'submenu': 'pesan',
        'pemesanan_list': qs,
        'q': q,
        'total': qs.count(),
        'count_tertarik': count_tertarik,
        'count_ingin_membeli': count_ingin_membeli,
        'count_ingin_bertanya': count_ingin_bertanya,
    }
    return render(request, 'pemesananadmin.html', context)


@login_required(login_url='login')
def delete_pesanadmin(request, token: str):
    if not request.user.has_perm('cart.delete_pemesanan'):
        raise Http404()
    item = get_object_or_404(Pemesanan, token_pemesanan=token)
    if request.method == 'POST':
        item.delete()
    return redirect('pesanadmin')


@login_required(login_url='login')
def likeadmin(request):
    if not request.user.has_perm('cart.view_pemesanan'):
        raise Http404()

    qs = Pemesanan.objects.filter(aktif=True, pilihan='like').order_by('-tanggal_upload', '-id')

    q = (request.GET.get('q') or '').strip()
    if q:
        qs = qs.filter(Q(produk__nama__icontains=q) | Q(nama__icontains=q) | Q(email__icontains=q))

    context = {
        'judul': 'Like Produk',
        'menu': 'penjualan',
        'submenu': 'like',
        'items': qs,
        'q': q,
        'total': qs.count(),
    }
    return render(request, 'likeadmin.html', context)


@login_required(login_url='login')
def delete_likeadmin(request, token: str):
    if not request.user.has_perm('cart.delete_pemesanan'):
        raise Http404()
    item = get_object_or_404(Pemesanan, token_pemesanan=token)
    if request.method == 'POST':
        item.delete()
    return redirect('likeadmin')



@login_required(login_url='login')
def deleteslidepenjualanadmin(request, token):
    slidepenjualan = get_object_or_404(SlidePenjualan, token_slidepenjualan=token)
    if request.method == 'POST':
        slidepenjualan.delete()
        return redirect('slidepenjualanadmin')  
    return redirect('slidepenjualanadmin')

##### INI BAGIAN PEMESANAN
@login_required(login_url='login')
def pemesananadmin(request):
    qs = Pemesanan.objects.order_by('-id')

    # Pencarian sederhana
    q = (request.GET.get('q') or '').strip()
    if q:
        qs = qs.filter(
            Q(no_pemesanan__icontains=q)
            | Q(nama_pemesanan__icontains=q)
            | Q(nama__icontains=q)
            | Q(email__icontains=q)
            | Q(no_telepon__icontains=q)
            | Q(alamat__icontains=q)
            | Q(produk__nama__icontains=q)
        )

    # Ringkasan
    total = Pemesanan.objects.count()
    count_tertarik = Pemesanan.objects.filter(pilihan='tertarik').count()
    count_ingin_membeli = Pemesanan.objects.filter(pilihan='ingin_membeli').count()
    count_ingin_bertanya = Pemesanan.objects.filter(pilihan='ingin_bertanya').count()
    last_updated = Pemesanan.objects.order_by('-tanggal_upload').values_list('tanggal_upload', flat=True).first()

    context = {
        "judul": "Data Pemesanan",
        "menu": "penjualan",
        "submenu": "pemesanan",
        "pemesanan_list": qs,
        "q": q,
        "total": total,
        "count_tertarik": count_tertarik,
        "count_ingin_membeli": count_ingin_membeli,
        "count_ingin_bertanya": count_ingin_bertanya,
        "last_updated": last_updated,
    }
    return render(request, 'pemesananadmin.html', context)

@login_required(login_url='login')
def formpemesananadmin(request):
    if request.method == "POST":
        token_pemesanan = str(uuid.uuid4())
        #datadeskripsi = request.POST.get('deskripsi')
        form = PemesananForm(request.POST, request.FILES)  # Ambil data dari request
        if form.is_valid():  # Validasi form
            pemesanan = form.save(commit=False)  
            pemesanan.token_pemesanan = token_pemesanan
            #pemesanan.deskripsi = datadeskripsi
            pemesanan.save()
            return redirect('pemesananadmin')  # Redirect ke halaman pemesanan setelah menyimpan
    else:
        form = PemesananForm()  # Tampilkan form kosong jika GET request
    context = {
        "judul": "Form Pemesanan",
        "menu": "pemesanan",
        "form": form
    }
    return render(request, 'formspemesananadmin.html', context)
    
@login_required(login_url='login')
def editpemesananadmin(request, token):
    pemesanan = get_object_or_404(Pemesanan, token_pemesanan=token) #memanggil satu data yang pemesanannya sama maka satu yang lainnya tidak akan tertampil
    if request.method == "POST":
        form = PemesananForm(request.POST, request.FILES, instance=pemesanan)
        if form.is_valid():
            form.save()
            #pemesananedit.deskripsi = datadeskripsi
            #pemesananedit.save()
            return redirect('pemesananadmin')  # Redirect ke halaman daftar pemesanan
    else:
        form = PemesananForm(instance=pemesanan)
    context = {
        "judul": "Form Edit Pemesanan",
        "menu": "pemesanan",
        "form": form,
        'pemesanan': pemesanan
    }
    return render(request, 'formspemesananadmin.html', context)

@login_required(login_url='login')
def deletepemesananadmin(request, token):
    pemesanan = get_object_or_404(Pemesanan, token_pemesanan=token)
    if request.method == 'POST':
        pemesanan.delete()
        return redirect('pemesananadmin')  
    return redirect('pemesananadmin')


##### INI BAGIAN PRODUK POPULER
@login_required(login_url='login')
def jasaadmin(request):
    jasa = Jasa.objects.order_by('-id')
    context = {
            "judul": "Data Jasa",
            "menu": "penjualan",
            "submenu": "jasa",
            "jasa_list" : jasa
        }
    return render(request, 'jasaadmin.html', context)

@login_required(login_url='login')
def formjasaadmin(request):
    if request.method == "POST":
        token_jasa = str(uuid.uuid4())
        #datadeskripsi = request.POST.get('deskripsi')
        form = JasaForm(request.POST, request.FILES)  # Ambil data dari request
        if form.is_valid():  # Validasi form
            jasa = form.save(commit=False)  
            jasa.token_jasa = token_jasa
            #jasa.deskripsi = datadeskripsi
            jasa.save()
            return redirect('jasaadmin')  # Redirect ke halaman jasa setelah menyimpan
    else:
        form = JasaForm()  # Tampilkan form kosong jika GET request
    context = {
        "judul": "Form Jasa",
        "menu": "jasa",
        "form": form
    }
    return render(request, 'formjasaadmin.html', context)

@login_required(login_url='login')
def editjasaadmin(request, token):
    jasa = get_object_or_404(Jasa, token_jasa=token) #memanggil satu data yang jasanya sama maka satu yang lainnya tidak akan tertampil
    if request.method == "POST":
        form = JasaForm(request.POST, request.FILES, instance=jasa)
        if form.is_valid():
            form.save()
            #jasaedit.deskripsi = datadeskripsi
            #jasaedit.save()
            return redirect('jasaadmin')  # Redirect ke halaman daftar jasa
    else:
        form = JasaForm(instance=jasa)
    context = {
        "judul": "Form Edit Jasa",
        "menu": "jasa",
        "form": form,
        'jasa': jasa
    }
    return render(request, 'formjasaadmin.html', context)

@login_required(login_url='login')
def deletejasaadmin(request, token):
    jasa = get_object_or_404(Jasa, token_jasa=token)
    if request.method == 'POST':
        jasa.delete()
        return redirect('jasaadmin')  
    return redirect('jasaadmin')


####### INI BAGIAN KATEGORIPENJUALAN
@login_required(login_url='login')
def kategoripenjualanadmin(request):
    kategoripenjualan = KategoriPenjualan.objects.order_by('-id')
    context = {
            "judul": "Data KategoriPenjualan",
            "menu": "penjualan",
            "submenu": "kategoripenjualanadmin",
            "kategoripenjualan_list" : kategoripenjualan
        }
    return render(request, 'kategoripenjualanadmin.html', context)

@login_required(login_url='login')
def formkategoripenjualanadmin(request):
    if request.method == "POST":
        token_kategoripenjualan = str(uuid.uuid4())
        datadeskripsi = request.POST.get('deskripsi')
        form = KategoriPenjualanForm(request.POST, request.FILES)  # Ambil data dari request
        if form.is_valid():  # Validasi form
            kategoripenjualan = form.save(commit=False)  
            kategoripenjualan.token_kategoripenjualan = token_kategoripenjualan
            kategoripenjualan.deskripsi = datadeskripsi
            kategoripenjualan.save()
            return redirect('kategoripenjualanadmin')  # Redirect ke halaman kategoripenjualan setelah menyimpan
    else:
        form = KategoriPenjualanForm()  # Tampilkan form kosong jika GET request
    context = {
        "judul": "Form KategoriPenjualan",
        "menu": "kategoripenjualan",
        "form": form
    }
    return render(request, 'formkategoripenjualanadmin.html', context)

@login_required(login_url='login')
def editkategoripenjualanadmin(request, token):
    kategoripenjualan = get_object_or_404(KategoriPenjualan, token_kategoripenjualan=token) #memanggil satu data yang kategoripenjualannya sama maka satu yang lainnya tidak akan tertampil
    if request.method == "POST":
        datadeskripsi = request.POST.get('deskripsi')
        form = KategoriPenjualanForm(request.POST, request.FILES, instance=kategoripenjualan)
        if form.is_valid():
            kategoripenjualanedit = form.save(commit=False)
            kategoripenjualanedit.deskripsi = datadeskripsi
            kategoripenjualanedit.save()
            return redirect('kategoripenjualanadmin')  # Redirect ke halaman daftar kategoripenjualan
    else:
        form = KategoriPenjualanForm(instance=kategoripenjualan)
    context = {
        "judul": "Form Edit KategoriPenjualan",
        "menu": "kategoripenjualan",
        "form": form,
        'kategoripenjualan': kategoripenjualan
    }
    return render(request, 'formkategoripenjualanadmin.html', context)

@login_required(login_url='login')
def deletekategoripenjualanadmin(request, token):
    kategoripenjualan = get_object_or_404(KategoriPenjualan, token_kategoripenjualan=token)
    if request.method == 'POST':
        kategoripenjualan.delete()
        return redirect('kategoripenjualanadmin')  
    return redirect('kategoripenjualanadmin')

########  INI BAGIAN PRODUK

# @login_required(login_url='login')
# def produkadmin(request):
#     produk = Produk.objects.order_by('-id')
#     context = {
#             "judul": "Data Produk",
#             "menu":"produk",
#             "produk_list" : produk
#         }
#     return render(request, 'produkadmin.html', context)

# @login_required(login_url='login')
# def formprodukadmin(request):
#     if request.method == "POST":
#         token_produk = str(uuid.uuid4())
#         #datadeskripsi = request.POST.get('deskripsi')
#         form = ProdukForm(request.POST, request.FILES)  # Ambil data dari request
#         if form.is_valid():  # Validasi form
#             produk = form.save(commit=False)  
#             produk.token_produk = token_produk
#             #produk.deskripsi = datadeskripsi
#             produk.save()
#             return redirect('produkadmin')  # Redirect ke halaman produk setelah menyimpan
#     else:
#         form = ProdukForm()  # Tampilkan form kosong jika GET request
#     context = {
#         "judul": "Form Produk",
#         "menu": "produk",
#         "form": form
#     }
#     return render(request, 'formprodukadmin.html', context)

# ---------- Interest form (public) ----------
from website.utils.telegram import send_telegram_message
import uuid
from django.utils import timezone
from django.utils.html import strip_tags
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages

def _gen_no_pemesanan():
    return timezone.now().strftime('PM-%Y%m%d-%H%M%S')

def pesan_produk(request, token: str):
    produk = get_object_or_404(Produk, token_produk=token)
    next_qs = request.GET.get('next') or request.POST.get('next')
    if next_qs:
        redirect_base = next_qs
    else:
        redirect_base = reverse('produk_detail', kwargs={'slug': produk.slug}) if getattr(produk, 'slug', None) else '/penjualan'

    if not request.user.is_authenticated:
        messages.error(request, 'Anda belum terdaftar sebagai user, silakan login terlebih dahulu untuk melanjutkan proses pembelian produk ini.')
        login_url = f"{reverse('user_login')}?next={request.get_full_path()}"
        return HttpResponseRedirect(login_url)

    if request.method == 'POST':
        nama = request.POST.get('nama')
        email = request.POST.get('email')
        no_telepon = request.POST.get('no_telepon')
        jumlah = request.POST.get('jumlah', '1')
        alamat = request.POST.get('alamat')
        pesan = request.POST.get('pesan')

        # Jika user login dan email tidak diisi, gunakan email user
        if request.user.is_authenticated and not email:
            email = request.user.email

        try:
            p = Pemesanan(
                no_pemesanan=_gen_no_pemesanan(),
                nama_pemesanan=f"Pesanan: {produk.nama}",
                token_pemesanan=str(uuid.uuid4()),
                aktif=True,
                produk=produk,
                pilihan='ingin_membeli',
                nama=nama,
                email=email,
                no_telepon=no_telepon,
                alamat=alamat,
            )
            p.save()

            try:
                msg = (
                    f"[Pesanan Produk]\n"
                    f"Produk: {produk.nama}\n"
                    f"Jumlah: {jumlah}\n"
                    f"Nama: {nama}\nEmail: {email}\nTelepon: {no_telepon}\n"
                    f"Alamat: {alamat}\n"
                    f"Pesan: {pesan}"
                )
                send_telegram_message(text=msg)
            except Exception:
                pass

            return HttpResponseRedirect(redirect_base + ('?sent=1' if '?' not in redirect_base else '&sent=1'))
        except Exception:
            return HttpResponseRedirect(redirect_base + ('?sent=0' if '?' not in redirect_base else '&sent=0'))

    return render(request, 'tertarik_form.html', {'produk': produk, 'next': redirect_base})


def pesan_produk_by_id(request, pk: int):
    produk = get_object_or_404(Produk, pk=pk)
    if produk.token_produk:
        return redirect('pesan_produk', token=produk.token_produk)
    return pesan_produk(request, token=_ensure_token(produk))


def like_produk(request, token: str):
    produk = get_object_or_404(Produk, token_produk=token)
    next_qs = request.GET.get('next') or request.POST.get('next')
    if next_qs:
        redirect_base = next_qs
    else:
        redirect_base = reverse('produk_detail', kwargs={'slug': produk.slug}) if getattr(produk, 'slug', None) else '/penjualan'

    if request.method != 'POST':
        return HttpResponseRedirect(redirect_base)

    try:
        nama = getattr(request.user, 'get_full_name', lambda: '')() if getattr(request, 'user', None) and request.user.is_authenticated else None
        email = request.user.email if getattr(request, 'user', None) and request.user.is_authenticated else None
        p = Pemesanan(
            no_pemesanan=_gen_no_pemesanan(),
            nama_pemesanan=f"Like: {produk.nama}",
            token_pemesanan=str(uuid.uuid4()),
            aktif=True,
            produk=produk,
            pilihan='like',
            nama=nama,
            email=email,
        )
        p.save()
        return HttpResponseRedirect(redirect_base + ('?liked=1' if '?' not in redirect_base else '&liked=1'))
    except Exception:
        return HttpResponseRedirect(redirect_base)


def like_produk_by_id(request, pk: int):
    produk = get_object_or_404(Produk, pk=pk)
    if produk.token_produk:
        return redirect('like_produk', token=produk.token_produk)
    return like_produk(request, token=_ensure_token(produk))


def tertarik_produk(request, token:str):
    return pesan_produk(request, token=token)

def tertarik_produk_by_id(request, pk:int):
    produk = get_object_or_404(Produk, pk=pk)
    if produk.token_produk:
        return redirect('tertarik_produk', token=produk.token_produk)
    return pesan_produk(request, token=_ensure_token(produk))

def _ensure_token(produk: Produk) -> str:
    if not produk.token_produk:
        produk.token_produk = str(uuid.uuid4())
        produk.save(update_fields=['token_produk'])
    return produk.token_produk

# @login_required(login_url='login')
# def editprodukadmin(request, token):
    produk = get_object_or_404(Produk, token_produk=token) #memanggil satu data yang produknya sama maka satu yang lainnya tidak akan tertampil
    if request.method == "POST":
        #datadeskripsi = request.POST.get('deskripsi')
        form = ProdukForm(request.POST, request.FILES, instance=produk)
        if form.is_valid():
            form.save()
            #produkedit.deskripsi = datadeskripsi
            #produkedit.save()
            return redirect('produkadmin')  # Redirect ke halaman daftar produk
    else:
        form = ProdukForm(instance=produk)
    context = {
        "judul": "Form Edit Produk",
        "menu": "produk",
        "form": form,
        'produk': produk
    }
    return render(request, 'formprodukadmin.html', context)

# @login_required(login_url='login')
# def deleteprodukadmin(request, token):
#     produk = get_object_or_404(Produk, token_produk=token)
#     if request.method == 'POST':
#         produk.delete()
#         return redirect('produkadmin')  
#     return redirect('produkadmin')


# View untuk menampilkan halaman produk yang bisa difilter
@login_required(login_url='login')
def produkdisplay(request):
    produk = Produk.objects.filter(aktif=True)
    kategoripenjualan = KategoriPenjualan.objects.filter(aktif=True)
    
    context = {
        'produk': produk,
        'kategoripenjualan': kategoripenjualan,
    }
    return render(request, 'produkdisplay.html', context) 

@login_required(login_url='login')
def produkadmin(request):
    if not request.user.has_perm('cart.view_produk'):
        raise Http404()

    qs = Produk.objects.all()
    if not request.user.is_superuser and hasattr(request.user, 'admin_panel_profile') and not request.user.admin_panel_profile.is_superadmin:
        qs = qs.filter(user=request.user)

    for p in qs:
        if not getattr(p, 'token_produk', None):
            try:
                p.token_produk = str(uuid.uuid4())
                p.save(update_fields=['token_produk'])
            except Exception:
                pass

    kategoripenjualan = KategoriPenjualan.objects.filter(aktif=True)
    
    context = {
        'produk': qs,
        'kategoripenjualan': kategoripenjualan,
        'menu': 'penjualan',
        'submenu': 'produk',
    }
    return render(request, 'produkadmin.html', context)

# View untuk form tambah produk
@login_required(login_url='login')
def formprodukadmin(request):
    if not request.user.has_perm('cart.add_produk'):
        raise Http404()

    if request.method == 'POST':
        nama = request.POST.get('nama')
        deskripsi = request.POST.get('deskripsi')
        deskripsi_clean = strip_tags(deskripsi or '')
        harga = request.POST.get('harga')
        stok = request.POST.get('stok', 0)
        kategori_id = request.POST.get('kategori')
        gambar = request.FILES.get('gambar')
        gambar2 = request.FILES.get('gambar2')
        gambar3 = request.FILES.get('gambar3')
        aktif = request.POST.get('aktif', False) == 'on'  # Checkbox handling

        # Generate token unik
        token = str(uuid.uuid4())

        # Ambil kategori
        kategoripenjualan = get_object_or_404(KategoriPenjualan, id=kategori_id) if kategori_id else None

        # Buat objek produk baru
        produk = Produk(
            nama=nama,
            deskripsi=deskripsi_clean,
            harga=harga,
            stok=int(stok) if stok else 0,
            kategoripenjualan=kategoripenjualan,
            gambar=gambar,
            aktif=aktif,
            token_produk=token,
            user=request.user  # Menyimpan user yang sedang login
        )
        if gambar2:
            produk.gambar2 = gambar2
        if gambar3:
            produk.gambar3 = gambar3
        produk.save()

        return redirect('produkadmin')

    kategoripenjualan = KategoriPenjualan.objects.filter(aktif=True)
    context = {
        'kategoripenjualan': kategoripenjualan,
        'menu': 'penjualan',
        'submenu': 'produk',
        'judul': 'Form Produk',
    }
    return render(request, 'formprodukadmin.html', context)

# View untuk edit produk
@login_required(login_url='login')
def editprodukadmin(request, token):
    if not request.user.has_perm('cart.change_produk'):
        raise Http404()

    produk = get_object_or_404(Produk, token_produk=token)
    if not request.user.is_superuser and hasattr(request.user, 'admin_panel_profile') and not request.user.admin_panel_profile.is_superadmin:
        if produk.user_id != request.user.id:
            raise Http404()
    kategoripenjualan = KategoriPenjualan.objects.filter(aktif=True)
    
    if request.method == 'POST':
        nama = request.POST.get('nama')
        deskripsi = request.POST.get('deskripsi')
        deskripsi_clean = strip_tags(deskripsi or '')
        harga = request.POST.get('harga')
        stok = request.POST.get('stok', 0)
        kategori_id = request.POST.get('kategori')
        gambar = request.FILES.get('gambar')
        gambar2 = request.FILES.get('gambar2')
        gambar3 = request.FILES.get('gambar3')
        aktif = request.POST.get('aktif', False) == 'on'  # Checkbox handling

        # Update data produk
        produk.nama = nama
        produk.deskripsi = deskripsi_clean
        produk.harga = harga
        produk.stok = int(stok) if stok else 0
        produk.aktif = aktif
        if kategori_id:
            produk.kategoripenjualan = get_object_or_404(KategoriPenjualan, id=kategori_id)
        if gambar:
            produk.gambar = gambar
        if gambar2:
            produk.gambar2 = gambar2
        if gambar3:
            produk.gambar3 = gambar3
        produk.save()
        return redirect('produkadmin')

    context = {
        'produk': produk,
        'kategoripenjualan': kategoripenjualan,
        'menu': 'penjualan',
        'submenu': 'produk',
        'judul': 'Edit Produk',
    }
    return render(request, 'formprodukadmin.html', context)

# View untuk menghapus produk
@login_required(login_url='login')
def deleteprodukadmin(request, token):
    if not request.user.has_perm('cart.delete_produk'):
        raise Http404()

    produk = get_object_or_404(Produk, token_produk=token)
    if not request.user.is_superuser and hasattr(request.user, 'admin_panel_profile') and not request.user.admin_panel_profile.is_superadmin:
        if produk.user_id != request.user.id:
            raise Http404()

    produk.delete()
    return redirect('produkadmin')

# ------- Fallback handlers by numeric ID -------
@login_required(login_url='login')
def editprodukadmin_by_id(request, pk:int):
    produk = get_object_or_404(Produk, pk=pk)
    # redirect to token route if token exists or generate one
    if not produk.token_produk:
        produk.token_produk = str(uuid.uuid4())
        produk.save(update_fields=['token_produk'])
    return redirect('editprodukadmin', token=produk.token_produk)

@login_required(login_url='login')
def deleteprodukadmin_by_id(request, pk:int):
    produk = get_object_or_404(Produk, pk=pk)
    if produk.token_produk:
        return redirect('deleteprodukadmin', token=produk.token_produk)
    produk.delete()
    return redirect('produkadmin')


