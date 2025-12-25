from django.core.management.base import BaseCommand
from django.db import transaction
from django.apps import apps
import re


def strip_html(value: str) -> str:
    if value is None:
        return value
    text = re.sub(r"<br\s*/?>", "\n", value, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


class Command(BaseCommand):
    help = "Remove HTML tags (e.g., <p>, <br>) from text fields across important models"

    def add_arguments(self, parser):
        parser.add_argument(
            "--database",
            default="default",
            help="Database alias to operate on (default: 'default')",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would change without saving",
        )

    def handle(self, *args, **options):
        using_db = options["database"]
        dry_run = options["dry_run"]

        # Target models and fields to clean
        ModelFields = [
            ("administrator", "Berita", ["isi_berita", "deskripsi", "judul"]),
            ("administrator", "Kategori", ["nama"]),
            ("administrator", "Layanan", ["deskripsi", "nama"]),
            ("administrator", "Profil", ["deskripsi"]),
            ("administrator", "Slide", ["deskripsi", "judul"]),
            ("administrator", "Faq", ["pertanyaan", "jawaban"]),
            ("administrator", "Testimoni", ["deskripsi", "nama"]),
            ("administrator", "Pesan", ["pesan"]),
            # cart app
            ("cart", "Produk", ["deskripsi", "nama"]),
            ("cart", "SlidePenjualan", ["deskripsi", "judul"]),
            ("cart", "Jasa", ["deskripsi", "nama"]),
            ("cart", "KategoriPenjualan", ["nama", "filter"]),
        ]

        total_updated = 0
        with transaction.atomic(using=using_db):
            for app_label, model_name, fields in ModelFields:
                try:
                    Model = apps.get_model(app_label, model_name)
                except LookupError:
                    continue

                qs = Model.objects.using(using_db).all()
                for obj in qs.iterator():
                    changed = False
                    for field_name in fields:
                        if not hasattr(obj, field_name):
                            continue
                        original = getattr(obj, field_name)
                        if isinstance(original, str) and ("<" in original and ">" in original):
                            cleaned = strip_html(original)
                            if cleaned != original:
                                setattr(obj, field_name, cleaned)
                                changed = True
                    if changed:
                        total_updated += 1
                        if not dry_run:
                            obj.save(using=using_db, update_fields=[f for f in fields if hasattr(obj, f)])

        self.stdout.write(self.style.SUCCESS(f"Cleaned HTML for {total_updated} objects on '{using_db}' database."))


