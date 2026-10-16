# Renomeia DocAuthor -> Organisation e migra a FK doc_author (1:N) para o
# M2M organisations (N:N), preservando os vínculos existentes.

from django.db import migrations, models


def copy_doc_author_to_organisations(apps, schema_editor):
    """Para cada documento com doc_author definido, adiciona essa organização
    ao novo M2M organisations."""
    Document = apps.get_model('pesquisas', 'Document')
    for document in Document.objects.exclude(doc_author__isnull=True).iterator():
        document.organisations.add(document.doc_author_id)


def copy_organisations_to_doc_author(apps, schema_editor):
    """Rollback: pega a primeira organização de cada documento e grava em
    doc_author (a FK só comporta uma)."""
    Document = apps.get_model('pesquisas', 'Document')
    for document in Document.objects.filter(organisations__isnull=False).distinct().iterator():
        first = document.organisations.first()
        if first is not None:
            document.doc_author_id = first.id
            document.save(update_fields=['doc_author'])


class Migration(migrations.Migration):

    dependencies = [
        ('pesquisas', '0002_document_file_authorship_doi'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='DocAuthor',
            new_name='Organisation',
        ),
        migrations.AlterModelOptions(
            name='organisation',
            options={
                'ordering': ['name'],
                'verbose_name': 'Organização',
                'verbose_name_plural': 'Organizações',
            },
        ),
        migrations.AlterField(
            model_name='organisation',
            name='name',
            field=models.CharField(max_length=255, unique=True, verbose_name='Organização'),
        ),
        migrations.AddField(
            model_name='document',
            name='organisations',
            field=models.ManyToManyField(
                blank=True,
                related_name='documents',
                to='pesquisas.Organisation',
                verbose_name='Organizações',
            ),
        ),
        migrations.RunPython(
            copy_doc_author_to_organisations,
            copy_organisations_to_doc_author,
        ),
        migrations.RemoveField(
            model_name='document',
            name='doc_author',
        ),
    ]
