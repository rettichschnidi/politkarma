import os.path
import re
import tempfile
import urllib.request
from timeit import default_timer as timer
from urllib.error import HTTPError
from zipfile import ZipFile

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'updating vote db using xml files from parlament.ch'
    base_url = 'http://www.parlament.ch/d/wahlen-abstimmungen/abstimmungen-im-parlament/Documents/xml/'
    language_codes = ['d', 'f', 'i']
    default_language_code = 'd'
    files = ['4801-2007-wintersession-d.zip',
             '4802-2008-fruehjahrssession-d.zip',
             '4804-2008-sommersession-d.zip',
             '4805-2008-herbstsession-d.zip',
             '4806-2008-wintersession-d.zip',
             '4807-2009-fruehjahrssession-d.zip',
             '4808-2009-sondersession-april-d.zip',
             '4809-2009-sommersession-d.zip',
             '4811-2009-herbstsession-d.zip',
             '4812-2009-wintersession-d.zip',
             '4813-2010-fruehjahrssession-d.zip',
             '4814-2010-sommersession-d.zip',
             '4815-2010-herbstsession-d.zip',
             '4816-2010-wintersession-d.zip',
             '4817-2011-fruehjahrssession-d.zip',
             '4818-2011-sondersession-april-d.zip',
             '4819-2011-sommersession-d.zip',
             '4820-2011-herbstsession-d.zip',
             '4901-2011-wintersession-d.zip',
             '4902-2012-fruehjahrssession-d.zip',
             '4903-2012-sondersession-mai-d.zip',
             '4904-2012-sommersession-d.zip',
             '4905-2012-herbstsession-d.zip',
             '4906-2012-wintersession-d.zip',
             '4907-2013-fruehjahrssession-d.zip',
             '4908-2013-sondersession-april-d.zip',
             '4909-2013-sommersession-d.zip',
             '4910-2013-herbstsession-d.zip',
             '4911-2013-wintersession-d.zip',
             '4912-2014-fruehjahrssession-d.zip',
             '4913-2014-sondersession-mai-d.zip',
             '4914-2014-sommersession-d.zip',
             '4915-2014-herbstsession-d.zip',
             '4916-2014-wintersession-d.zip',
             '4917-2015-fruehjahrssession-d.zip',
             '4918-2015-sondersession-mai-d.zip',
             '4919-2015-sommersession-d.zip',
             '4920-2015-herbstsession-d.zip',
             '5001-2015-wintersession-d.zip']

    @staticmethod
    def build_file_name(language_code, base_file_name):
        """
        Return the localized file name.
        :param language_code: language code
        :param base_file_name: base file name using default language code
        :return localized file name
        """
        expression = '-' + Command.default_language_code + '\.'
        replacement = '-' + language_code + '.'
        return re.sub(expression, replacement, base_file_name)

    @staticmethod
    def build_localized_base_url(language_code):
        """
        :param language_code: language code to be used
        :return: base url for the given language
        """
        expression = '/' + Command.default_language_code + '/'
        replacement = '/' + language_code + '/'
        return re.sub(expression, replacement, Command.base_url)

    @staticmethod
    def build_url(language_code, base_file_name):
        """
        :param language_code: language code
        :param base_file_name: base file name
        :return: generated download url
        """
        return Command.build_localized_base_url(language_code) + Command.build_file_name(language_code, base_file_name)

    @staticmethod
    def rotate_file_name(file_name):
        result = re.search('(\d+)-(\d+)-(\S+)-(\S+)-(\S)\.zip', file_name, re.IGNORECASE)
        if not result:
            raise ValueError('File name rotation not supported for file name ' + file_name)
        return (result.group(1) + '-' +
                result.group(2) + '-' +
                result.group(4) + '-' +
                result.group(3) + '-' +
                result.group(5) + '.zip')

    @staticmethod
    def download_file(work_dir, file, language_code):
        """
        downloads a file to the work dir
        :param work_dir: working directory
        :param file: file to be downloaded
        :param language_code: language code to be used
        :return: file name of downloaded file
        """
        url = Command.build_url(language_code, file)
        file_name = os.path.join(work_dir.name, Command.build_file_name(language_code, file))

        try:
            print('downloading ' + url + ', saving result in ' + file_name)
            urllib.request.urlretrieve(url, file_name)
            return file_name
        except HTTPError as e:
            # note: order of parts in file names is not always the same in different language
            # e.g. 4808-2009-april-sondersession-d.zip in french is 4808-2009-sondersession-april-f.zip
            # => change order of session name parts and try again
            print("download for{0} failed: {1}, going to try again with modified name...".format(url, e))
            modified_name = Command.rotate_file_name(file)
            url = Command.build_url(language_code, modified_name)
            file_name = os.path.join(work_dir.name, Command.build_file_name(language_code, modified_name))
            print('downloading ' + url + ', saving result in ' + file_name)
            urllib.request.urlretrieve(url, file_name)
            return file_name

    @staticmethod
    def extract_xml(file, work_dir):
        """
        :param file: path to zip file
        :param work_dir working directory
        :return: name of extracted file
        """
        zip_file = ZipFile(file)
        name_list = list(filter(lambda name: name.endswith('xml'), zip_file.namelist()))
        if name_list.__len__() != 1:
            raise ValueError(
                    'zip file must contain a single file. file {0} contains {1}'.format(file, name_list.__len__()))
        zip_file_name = name_list[0]
        print('extracting file {0} form zip file {1}...'.format(zip_file_name, file))
        zip_file.extract(zip_file_name, work_dir.name)

        fq_extracted_file = os.path.join(work_dir.name, zip_file_name)
        print('file extracted. size: {0}'.format(os.path.getsize(fq_extracted_file)))
        return fq_extracted_file

    @staticmethod
    def import_xml(file):
        """
        :param file: xml file to be imported
        :return: number of records loaded
        """
        # TODO: write import logic
        return 123

    def handle(self, *args, **options):
        try:
            start = timer()
            work_dir = tempfile.TemporaryDirectory(prefix='curia_vista_vote_db_import')
            for language_code in Command.language_codes:
                print('downloads for language {0}'.format(language_code))
                for file in Command.files:
                    # download and extract
                    zip_file_name = Command.download_file(work_dir, file, language_code)
                    unzipped_xml = Command.extract_xml(zip_file_name, work_dir)
                    os.remove(zip_file_name)

                    # import data
                    num_records = Command.import_xml(unzipped_xml)
                    print('xml file {0} imported, {1} records generated'.format(unzipped_xml, num_records))
                    os.remove(unzipped_xml)
                print('data for language {0} loaded'.format(language_code))
            end = timer()
            print('data imported, operation took {0}s'.format(end - start))
        finally:
            if work_dir is not None:
                work_dir.cleanup()