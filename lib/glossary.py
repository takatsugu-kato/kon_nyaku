"""
This modules is related to translator
"""
import os
import csv
import pytz
from django.conf import settings

from background_task import background
from translate.models import Glossary
from google.cloud import storage
from google.cloud import translate
from google.api_core.exceptions import AlreadyExists

def upload_glossary_on_google():
    bucket_name = os.getenv('GLOSSARY_BACKET_NAME')

    glossaries = Glossary.objects.filter(status=300)

    temp_csv_path = settings.MEDIA_ROOT + "/media/glossary/temp.csv"
    for glossary in glossaries:
        glos_path = str(glossary.document)
        glos_path = os.path.join(settings.MEDIA_ROOT, glos_path)

        print("Uploading {0}".format(glos_path))
        try:

            insert_lang_code_with_1st_line(glos_path, temp_csv_path, glossary.source_lang, glossary.target_lang)
            storage_client = storage.Client()
            bucket = storage_client.bucket(bucket_name)
            destination_blob_name = os.path.basename(glos_path)
            blob = bucket.blob(destination_blob_name)

            blob.upload_from_filename(temp_csv_path)

            glossary.status = 301
        except Exception as e:
            print(e)
            glossary.status = 303
        os.remove(temp_csv_path)
        glossary.save()

def delete_glossary_fron_google(glossary_id):
    project_id = os.getenv('GOOGLE_PROJECT_ID')
    location = os.getenv('GOOGLE_LOCATION')

    client = translate.TranslationServiceClient()

    glossary_id = 'kon-nyaku_' + str(glossary_id)

    parent = client.glossary_path(
        project_id,
        location,
        glossary_id)

    try:
        operation = client.delete_glossary(parent)
        result = operation.result(timeout=90)
        print('Deleted: {}'.format(result.name))
        return True
    except Exception as e:
        return False

def delete_glossary_file_from_google(blob_name):
    """Deletes a blob from the bucket."""

    bucket_name = os.getenv('GLOSSARY_BACKET_NAME')

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.delete()

    print("Blob {} deleted.".format(blob_name))

def set_glossary_status(glossary_id, status):
    glossary = Glossary.objects.get(pk=glossary_id)
    glossary.status = status
    glossary.save()

def delete_glossary_file(glossary):
    os.remove(str(glossary.document))
    glossary.delete()
    return os.path.basename(str(glossary.document))

def insert_lang_code_with_1st_line(csv_path, temp_csv_path, source_lang_code, target_lang_code):
    with open(csv_path, mode="r", encoding="utf-8") as rf:
        reader = csv.reader(rf)
        with open(temp_csv_path, mode="w", encoding="utf-8", newline="") as wf:
            writer = csv.writer(wf)
            writer.writerow([source_lang_code, target_lang_code])
            for line in reader:
                writer.writerow([line[0], line[1]])

def create_glossary_on_google():
    project_id = os.getenv('GOOGLE_PROJECT_ID')
    bucket_name = os.getenv('GLOSSARY_BACKET_NAME')
    location = os.getenv('GOOGLE_LOCATION')

    glossaries = Glossary.objects.filter(status=301)
    for glossary in glossaries:
        csv_basename = os.path.basename(str(glossary.document))
        glossary_id = "kon-nyaku_" + str(glossary.id)
        print("Creating {0}".format(csv_basename))

        try:
            client = translate.TranslationServiceClient()
            name = client.glossary_path(
                project_id,
                location,
                glossary_id)

            language_codes_set = translate.types.Glossary.LanguageCodesSet(
                language_codes=[glossary.source_lang, glossary.target_lang])

            gcs_source = translate.types.GcsSource(
                input_uri='gs://{0}/{1}'.format(bucket_name, csv_basename))

            input_config = translate.types.GlossaryInputConfig(
                gcs_source=gcs_source)

            gcp_glossary = translate.types.Glossary(
                name=name,
                language_codes_set=language_codes_set,
                input_config=input_config)

            parent = client.location_path(project_id, location)

            operation = client.create_glossary(parent=parent, glossary=gcp_glossary)

            result = operation.result(timeout=90)
            print('Created: {}'.format(result.name))
            print('Input Uri: {}'.format(result.input_config.gcs_source.input_uri))
            glossary.terms = result.entry_count
            glossary.status = 302
        except AlreadyExists:
            glossary.status = 302
        except Exception as e:
            glossary.status = 304
        glossary.save()

def create_glossary_for_trans_tbody_html(request, source_lang="en", target_lang="ja"):
    glossaries = Glossary.objects.filter(
        source_lang=source_lang,
        target_lang=target_lang)
    html_string = ""
    for glossary in glossaries:

        download_html = '<a href="/media/{0}">{1}</a>'.format(glossary.document, glossary.name)

        html_string = html_string + '        <tr>\n'\
            '          <td class="text-center"><input name="glossary_id" type="radio" value="' + str(glossary.id) +'"></td>\n'\
            '          <td>' + str(glossary.id) + '</td>\n'\
            '          <td>' + download_html + '</td>\n'\
            '          <td>' + glossary.source_lang + '</td>\n'\
            '          <td>' + glossary.target_lang + '</td>\n'\
            '          <td>' + str(glossary.terms) + '</td>\n'\
            '        </tr>\n'
    return_json = {"html": html_string}
    return return_json

def create_glossary_list_tbody_html(request, status_cons):
    """Create glossary list as html

    Args:
        request (obj): http request
        STATUS (cons): status cons

    Returns:
        json: html
    """
    jst = pytz.timezone('Asia/Tokyo')

    glossaries = Glossary.objects.all().order_by('id').reverse()
    html_string = ""
    for glossary in glossaries:
        created_date = glossary.created_date.astimezone(jst)
        created_date_str = created_date.strftime('%Y-%m-%d %H:%M')

        delete_button_html = (
            '<span data-toggle="tooltip" data-placement="top" title="Delete">'
            '<a href="" class="btn btn-danger btn-mergen-sm del_confirm" data-toggle="modal"'
            ' data-target="#deleteModal" data-pk="' + str(glossary.id) + '">'
            '<i class="fas fa-trash-alt"></i></a></span>\n'
            )

        download_html = '<a href="/media/{0}">{1}</a>'.format(glossary.document, glossary.name)

        html_string = html_string + '        <tr>\n'\
            '          <th scope="row">' + str(glossary.id) + '</th>\n'\
            '          <td>' + download_html + '</td>\n'\
            '          <td>' + glossary.source_lang + '</td>\n'\
            '          <td>' + glossary.target_lang + '</td>\n'\
            '          <td>' + status_cons[glossary.status] + '</td>\n'\
            '          <td>' + str(glossary.terms) + '</td>\n'\
            '          <td>' + created_date_str + '</td>\n'\
            '          <td class="text-center">' + delete_button_html + '</td>\n'\
            '        </tr>\n'
    return_json = {"html": html_string}
    return return_json
