from django.urls import path
from . import views
from .views import (
    active_users, 
    edit_admin_user,
    edit_public_user,
    delete_admin_user,
    log_aktivitas_list, 
    log_aktivitas_detail,
    role_list,
    role_create,
    role_edit,
    role_delete,
)

app_name = "administrator"

urlpatterns = [
    path("", views.berandaadmin, name="berandaadmin"),
    # Removed proxy admin routes to simplify and avoid conflicts
    path("error/", views.error_page, name="error_page"),
    # User Management URLs
    path("users/", views.active_users, name="active_users"),
    path("users/add/", views.add_admin_user, name="add_admin_user"),
    path("users/<int:user_id>/edit/", views.edit_admin_user, name="edit_admin_user"),
    path("users/<int:user_id>/edit-public/", views.edit_public_user, name="edit_public_user"),
    path(
        "users/<int:user_id>/delete/", views.delete_admin_user, name="delete_admin_user"
    ),
    path("users/login/", views.user_login_list, name="user_login_list"),
    path("users/daftar/", views.daftar_user, name="daftar_user"),
    path("users/<int:user_id>/detail/", views.detail_user, name="detail_user"),
    # Role Management URLs
    path("roles/", views.role_list, name="role_list"),
    path("roles/add/", views.role_create, name="role_create"),
    path("roles/<int:role_id>/edit/", views.role_edit, name="role_edit"),
    path("roles/<int:role_id>/delete/", views.role_delete, name="role_delete"),
    path("kategori/", views.kategoriadmin, name="kategoriadmin"),
    path("form-kategori/", views.formkategoriadmin, name="formkategoriadmin"),
    path(
        "edit-kategori/<str:token>", views.editkategoriadmin, name="editkategoriadmin"
    ),
    path(
        "delete-kategori/<str:token>",
        views.deletekategoriadmin,
        name="deletekategoriadmin",
    ),
    path("berita/", views.beritaadmin, name="beritaadmin"),
    path("form-berita/", views.formberitaadmin, name="formberitaadmin"),
    path("edit-berita/<str:token>", views.editberitaadmin, name="editberitaadmin"),
    path(
        "delete-berita/<str:token>", views.deleteberitaadmin, name="deleteberitaadmin"
    ),
    path("agenda/", views.agendaadmin, name="agendaadmin"),
    path("form-agenda/", views.formagendaadmin, name="formagendaadmin"),
    path("edit-agenda/<slug:slug>/", views.editagendaadmin, name="editagendaadmin"),
    path(
        "delete-agenda/<slug:slug>/",
        views.deleteagendaadmin,
        name="deleteagendaadmin",
    ),
    path("layanan/", views.layananadmin, name="layananadmin"),
    path("form-layanan/", views.formlayananadmin, name="formlayananadmin"),
    path("edit-layanan/<str:token>", views.editlayananadmin, name="editlayananadmin"),
    path(
        "delete-layanan/<str:token>",
        views.deletelayananadmin,
        name="deletelayananadmin",
    ),
    path("kontak/", views.kontakadmin, name="kontakadmin"),
    path("form-kontak/", views.formkontakadmin, name="formkontakadmin"),
    path("edit-kontak/<str:token>", views.editkontakadmin, name="editkontakadmin"),
    path(
        "delete-kontak/<str:token>", views.deletekontakadmin, name="deletekontakadmin"
    ),
    path("slide/", views.slideadmin, name="slideadmin"),
    path("form-slide/", views.formslideadmin, name="formslideadmin"),
    path("edit-slide/<str:token>", views.editslideadmin, name="editslideadmin"),
    path("delete-slide/<str:token>", views.deleteslideadmin, name="deleteslideadmin"),
    path("baground/", views.bagroundadmin, name="bagroundadmin"),
    path(
        "berandapenjualan/form-baground/",
        views.formbagroundadmin,
        name="formbagroundadmin",
    ),
    path(
        "berandapenjualan/edit-baground/<str:token>/",
        views.editbagroundadmin,
        name="editbagroundadmin",
    ),
    path(
        "berandapenjualan/delete-baground/<str:token>/",
        views.deletebagroundadmin,
        name="deletebagroundadmin",
    ),
    path("visimisi/", views.visimisiadmin, name="visimisiadmin"),
    path("form-visimisi/", views.formvisimisiadmin, name="formvisimisiadmin"),
    path(
        "edit-visimisi/<str:token>", views.editvisimisiadmin, name="editvisimisiadmin"
    ),
    path(
        "delete-visimisi/<str:token>",
        views.deletevisimisiadmin,
        name="deletevisimisiadmin",
    ),
    path("team/", views.teamadmin, name="teamadmin"),
    path("form-team/", views.formteamadmin, name="formteamadmin"),
    path("edit-team/<str:token>", views.editteamadmin, name="editteamadmin"),
    path("delete-team/<str:token>", views.deleteteamadmin, name="deleteteamadmin"),
    path("modelinkubasi/", views.modelinkubasiadmin, name="modelinkubasiadmin"),
    path(
        "form-modelinkubasi/",
        views.formmodelinkubasiadmin,
        name="formmodelinkubasiadmin",
    ),
    path(
        "edit-modelinkubasi/<str:token>",
        views.editmodelinkubasiadmin,
        name="editmodelinkubasiadmin",
    ),
    path(
        "delete-modelinkubasi/<str:token>",
        views.deletemodelinkubasiadmin,
        name="deletemodelinkubasiadmin",
    ),
    path("testimoni/", views.testimoniadmin, name="testimoniadmin"),
    path("form-testimoni/", views.formtestimoniadmin, name="formtestimoniadmin"),
    path(
        "edit-testimoni/<str:token>",
        views.edittestimoniadmin,
        name="edittestimoniadmin",
    ),
    path(
        "delete-testimoni/<str:token>",
        views.deletetestimoniadmin,
        name="deletetestimoniadmin",
    ),
    path("profil/", views.profiladmin, name="profiladmin"),
    path("form-profil/", views.formprofiladmin, name="formprofiladmin"),
    path("edit-profil/<str:token>", views.editprofiladmin, name="editprofiladmin"),
    path(
        "delete-profil/<str:token>", views.deleteprofiladmin, name="deleteprofiladmin"
    ),
    path(
        "delete-profil-image/<str:token>/<int:image_id>/",
        views.delete_profil_image,
        name="delete_profil_image",
    ),
    # Telegram Recipients (custom admin pages)
    path("telegram/", views.telegram_list, name="telegram_list"),
    path("telegram/add/", views.telegram_create, name="telegram_create"),
    path("telegram/<int:pk>/edit/", views.telegram_edit, name="telegram_edit"),
    path("telegram/<int:pk>/delete/", views.telegram_delete, name="telegram_delete"),
    path("pesan/", views.pesan_list, name="pesan_list"),
    path("pesan/<slug:slug>/", views.pesan_detail, name="pesan_detail"),
    path("pesan/<slug:slug>/delete/", views.pesan_delete, name="pesan_delete"),
    path(
        "pesan/<slug:slug>/toggle-tampil/",
        views.toggle_tampil_di_website,
        name="toggle_tampil_di_website",
    ),
    path("daftartenant/", views.daftartenant_list, name="daftartenant_list"),
    path(
        "daftartenant/import/",
        views.daftartenant_import,
        name="daftartenant_import",
    ),
    path(
        "daftartenant/<slug:slug>/",
        views.daftartenant_detail,
        name="daftartenant_detail",
    ),
    path(
        "daftartenant/<int:tenant_id>/toggle-aktif/",
        views.toggle_aktif,
        name="toggle_aktif",
    ),
    path(
        "daftartenant/<slug:slug>/delete/",
        views.daftartenant_delete,
        name="daftartenant_delete",
    ),
    path(
        "daftartenant/<slug:slug>/toggle-tampil/",
        views.toggle_tampil_di_website,
        name="toggle_tampil_di_website",
    ),
    path("daftarlayanan/", views.admin_daftar_layanan, name="admin_daftar_layanan"),
    path(
        "daftarlayanan/<slug:slug>/",
        views.admin_detail_layanan,
        name="admin_detail_layanan",
    ),
    path(
        "daftarlayanan/<slug:slug>/update-status/",
        views.admin_update_status,
        name="admin_update_status",
    ),
    # Audit: Log Aktivitas (Superadmin Only)
    path("audit/log-aktivitas/", log_aktivitas_list, name="log_aktivitas_list"),
    path(
        "audit/log-aktivitas/<int:pk>/",
        log_aktivitas_detail,
        name="log_aktivitas_detail",
    ),
    ######------BAAGIAN PENJUALAN
]
