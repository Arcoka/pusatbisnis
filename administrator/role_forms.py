from django import forms
from django.contrib.auth.models import Permission
from .models import AdminRole
from collections import OrderedDict

class AdminRoleForm(forms.ModelForm):
    class Meta:
        model = AdminRole
        fields = ['name', 'description', 'permissions']
        widgets = {
            'permissions': forms.CheckboxSelectMultiple(),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Model penjualan utama, kita ingin hanya mengambilnya dari app "cart".
        # Jika di database masih ada ContentType lama di app "administrator",
        # permission-permission itu akan kita sembunyikan agar tidak dobel.
        sales_models = {"produk", "pemesanan", "detailpemesanan"}

        # Hanya tampilkan permission yang relevan (sembunyikan internal Django
        # dan content type penjualan lama milik app "administrator").
        perms_qs = (
            Permission.objects.exclude(
                content_type__app_label__in=[
                    "admin",
                    "sessions",
                    "contenttypes",
                    "logentry",
                ]
            )
            .exclude(
                content_type__app_label="administrator",
                content_type__model__in=sales_models,
            )
            .select_related("content_type")
            .order_by("content_type__app_label", "content_type__model", "codename")
        )

        field = self.fields["permissions"]
        field.queryset = perms_qs

        # Kelompokkan permission berdasarkan app_label lalu model agar rapi di form
        grouped = OrderedDict()  # {app_label_verbose: {model_verbose: [(id, label), ...]}}

        app_labels_verbose = {
            "administrator": "Administrator (Website Admin)",
            "cart": "Penjualan (Cart)",
            "auth": "Authentication & Users",
        }

        for perm in perms_qs:
            ct = perm.content_type
            app_label = ct.app_label

            app_group_label = app_labels_verbose.get(app_label, app_label.title())

            # Nama model yang lebih ramah (misal "Berita" daripada "berita")
            model_label = ct.name or ct.model.replace('_', ' ').title()

            if app_group_label not in grouped:
                grouped[app_group_label] = OrderedDict()
            if model_label not in grouped[app_group_label]:
                grouped[app_group_label][model_label] = []

            # Gunakan perm.name agar label lebih singkat: "Can add berita", dll
            grouped[app_group_label][model_label].append((perm.id, perm.name))

        # Simpan struktur nested di field agar bisa dipakai di template (app -> model -> permissions)
        field.grouped_by_app_and_model = grouped

        # Untuk render default (tanpa template kustom), tetap sediakan choices flat per app
        flat_grouped = []
        for app_group_label, models in grouped.items():
            options = []
            for model_label, perms in models.items():
                options.extend(perms)
            flat_grouped.append((app_group_label, options))

        field.choices = flat_grouped
