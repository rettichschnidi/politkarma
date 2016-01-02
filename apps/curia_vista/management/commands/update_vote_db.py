import os.path
import re
import tempfile
import urllib.request
from timeit import default_timer as timer
from urllib.error import HTTPError
from xml.etree import ElementTree
from zipfile import ZipFile

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.curia_vista.models import *


class Command(BaseCommand):
    help = 'updating vote db using xml files from parlament.ch'
    base_url = 'http://www.parlament.ch/d/wahlen-abstimmungen/abstimmungen-im-parlament/Documents/xml/'
    language_codes = ['d']  # , 'f', 'i']
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

    def download_file(self, work_dir, file, language_code):
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
            self.stdout.write('downloading ' + url + ', saving result in ' + file_name)
            urllib.request.urlretrieve(url, file_name)
            return file_name
        except HTTPError as e:
            # note: order of parts in file names is not always the same in different language
            # e.g. 4808-2009-april-sondersession-d.zip in french is 4808-2009-sondersession-april-f.zip
            # => change order of session name parts and try again
            self.stdout.write("download for{0} failed: {1}, going to try again with modified name...".format(url, e))
            modified_name = Command.rotate_file_name(file)
            url = Command.build_url(language_code, modified_name)
            file_name = os.path.join(work_dir.name, Command.build_file_name(language_code, modified_name))
            self.stdout.write('downloading ' + url + ', saving result in ' + file_name)
            urllib.request.urlretrieve(url, file_name)
            return file_name

    def extract_xml(self, file, work_dir):
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
        self.stdout.write('extracting file {0} form zip file {1}...'.format(zip_file_name, file))
        zip_file.extract(zip_file_name, work_dir.name)

        fq_extracted_file = os.path.join(work_dir.name, zip_file_name)
        self.stdout.write('file extracted. size: {0}'.format(os.path.getsize(fq_extracted_file)))
        return fq_extracted_file

    @transaction.atomic
    def import_xml(self, file, councillor_index, affair_index, registered_cv_ids):
        """
        :param file: xml file to be imported
        :param councillor_index
        :param affair_index
        :param registered_cv_ids
        :return: number of records loaded
        """
        total_records_loaded = 0

        with open(file) as fh:
            model = ElementTree.fromstring(fh.read())
            if not model:
                raise ValueError("Not a valid XML file: {}".format(file))

            with transaction.atomic():
                # model contains affairs
                for affair in model:
                    # load affair from db
                    affair_id = affair.find('id').text
                    affair_model = affair_index[int(affair_id)]
                    if affair_model is None:
                        raise ValueError('unknown affair (id={0})'.format(affair_id))

                    for affair_vote in affair.find('affairVotes'):
                        start = timer()
                        av_id = affair_vote.find('id').text
                        av_date = affair_vote.find('date').text
                        av_division_text = affair_vote.find('divisionText').text
                        av_registration_number = affair_vote.find('registrationNumber').text
                        av_meaning_no = affair_vote.find('meaningNo').text
                        av_meaning_yes = affair_vote.find('meaningYes').text
                        av_submission_text = affair_vote.find('submissionText').text

                        av_model, created = AffairVote.objects.update_or_create(id=av_id,
                                                                                defaults={'date': av_date,
                                                                                          'division_text': av_division_text,
                                                                                          'registration_number': av_registration_number,
                                                                                          'meaning_no': av_meaning_no,
                                                                                          'meaning_yes': av_meaning_yes,
                                                                                          'submission_text': av_submission_text,
                                                                                          'affair': affair_model})
                        total_records_loaded += 1
                        av_model.full_clean()
                        av_model.save()

                        total_records_loaded += Command.load_totals(av_model, affair_vote.find('totalVotes'),
                                                                    affair_vote.find('filteredTotalVotes'))

                        records_loaded = Command.load_councillor_votes(affair_vote.find('councillorVotes'), av_model,
                                                                       councillor_index, registered_cv_ids)
                        total_records_loaded += records_loaded
                        self.stdout.write('affair vote {0}: {1} records loaded in {2}s'.format(av_id, records_loaded,
                                                                                               timer() - start))

        return total_records_loaded

    @staticmethod
    def load_totals(affair_vote, totals, filtered_totals):
        """
        :param affair_vote: affair vote reference
        :param totals: xml node containing totals
        :param filtered_totals: xml note containing filtered totals
        :return: number of records loaded
        """
        records_loaded = 0
        for total in totals:
            total_type = total.find('type').text
            total_count = total.find('count').text
            total_model, created = AffairVoteTotal.objects.update_or_create(type=total_type, affair_vote=affair_vote,
                                                                            defaults={'count': total_count})
            total_model.full_clean()
            total_model.save()
            records_loaded += 1

        for filtered_total in filtered_totals:
            filtered_total_type = filtered_total.find('type').text
            filtered_total_count = filtered_total.find('count').text
            filtered_total_model, created = FilteredAffairVoteTotal.objects.update_or_create(type=filtered_total_type,
                                                                                             affair_vote=affair_vote,
                                                                                             defaults={
                                                                                                 'count': filtered_total_count})
            filtered_total_model.full_clean()
            filtered_total_model.save()
            records_loaded += 1
        return records_loaded

    @staticmethod
    def load_councillor_votes(councillor_votes, affair_vote, councillor_index, registered_cv_ids):
        """
        :param councillor_votes: votes to be processed
        :param affair_vote: current affair vote object
        :param councillor_index: councillor index (map with id as key and councillor as value)
        :return: number of records loaded
        """
        cv_objects = CouncillorVote.objects
        records_loaded = 0
        for councillor_vote in councillor_votes:
            records_loaded += 1
            cv_id = councillor_vote.find('id').text
            cv_decision = councillor_vote.find('decision').text
            cv_number = councillor_vote.find('bioId').text

            # load councillor from db
            councillor = councillor_index[int(cv_number)]
            if councillor is None:
                raise ValueError('unknown councillor (id={0})'.format(cv_number))
            if int(cv_id) in registered_cv_ids:
                cv = cv_objects.get(id=cv_id)
                cv.decision = cv_decision
                cv.councillor = councillor
                cv.affair_vote = affair_vote
                cv.save()
            else:
                cv = cv_objects.create(id=cv_id, decision=cv_decision, councillor=councillor, affair_vote=affair_vote)
                cv.save()
                registered_cv_ids.add(int(cv_id))
                """"
                cv_model, cv_created = cv_objects.update_or_create(id=cv_id,
                                                               defaults={
                                                                   'decision': cv_decision,
                                                                   'councillor': councillor,
                                                                   'affair_vote': affair_vote})
                cv_model.full_clean()
                cv_model.save()
                """
        return records_loaded

    def handle(self, *args, **options):
        try:
            start = timer()
            work_dir = tempfile.TemporaryDirectory(prefix='curia_vista_vote_db_import')
            councillor_index = {x.id: x for x in Councillor.objects.all()}
            affair_index = {x.id: x for x in Affair.objects.all()}
            registered_cv_ids = set({x.id for x in CouncillorVote.objects.all()})

            for language_code in Command.language_codes:
                self.stdout.write('downloads for language {0}'.format(language_code))
                for file in Command.files:
                    # download and extract
                    zip_file_name = self.download_file(work_dir, file, language_code)
                    unzipped_xml = self.extract_xml(zip_file_name, work_dir)
                    os.remove(zip_file_name)

                    # import data
                    num_records = self.import_xml(unzipped_xml, councillor_index, affair_index, registered_cv_ids)
                    self.stdout.write('xml file {0} imported, {1} records generated'.format(unzipped_xml, num_records))
                    """"
                    with open("/tmp/foo.json", "w") as text_file:
                        text_file.write(str(connection.queries))
                    break
                    """""
                    os.remove(unzipped_xml)
                self.stdout.write('data for language {0} loaded'.format(language_code))
            self.stdout.write('data imported, operation took {0}s'.format(timer() - start))
        finally:
            if work_dir is not None:
                work_dir.cleanup()
