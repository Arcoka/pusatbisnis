from django.db import migrations


def create_agenda_table(apps, schema_editor):
    Agenda = apps.get_model("administrator", "Agenda")
    table_name = Agenda._meta.db_table

    existing_tables = schema_editor.connection.introspection.table_names()
    if table_name in existing_tables:
        return

    schema_editor.create_model(Agenda)


def drop_agenda_table(apps, schema_editor):
    Agenda = apps.get_model("administrator", "Agenda")
    table_name = Agenda._meta.db_table

    existing_tables = schema_editor.connection.introspection.table_names()
    if table_name not in existing_tables:
        return

    schema_editor.delete_model(Agenda)


class Migration(migrations.Migration):

    atomic = False

    dependencies = [
        ("administrator", "0080_agenda_remove_adminpaneluser_created_at"),
    ]

    operations = [
        migrations.RunPython(create_agenda_table, reverse_code=drop_agenda_table),
    ]
