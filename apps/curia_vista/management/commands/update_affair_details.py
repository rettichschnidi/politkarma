import concurrent
import concurrent.futures
from queue import Queue
from threading import Thread
from timeit import default_timer as timer
from xml.etree import ElementTree

import requests
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.curia_vista.models import *
from politkarma import settings


class Command(BaseCommand):
    help = 'Import affair details from parlament.ch'
    ws_threads = 24
    task_queue_size = 100

    def update(self, resource_url, lang, affair_id, is_main):
        foo = 1

    @staticmethod
    def download(resource_url, lang, affair_id, is_main, task_queue):
        """
        requests the details for a single affair from the web service and puts it into a queue
        :param resource_url: web service base url
        :param lang: language
        :param affair_id: id of the affair
        :param is_main:
        :param task_queue: queue
        :return: nothing
        """
        from django.utils import translation
        translation.activate(lang)
        url = resource_url + '/' + str(affair_id) + '?format=xml&lang=' + lang

        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla'})
        except Exception as e:
            raise CommandError("Could not fetch file from {}".format(url))
        task_queue.put(response.content)

    @staticmethod
    def get_author(element, councillor_index, faction_index):
        """
        reads an author from the db or creates it
        :param element <author> element
        :param councillor_index
        :param faction_index
        :return: author
        """
        authors = AffairAuthor.objects
        # most values are optional :(
        councillor = None
        faction = None
        if element is not None:
            councillor_element = element.find('councillor')
            if councillor_element is not None:
                councillor_id = int(councillor_element.find('id').text)
                if councillor_id in councillor_index:
                    councillor = councillor_index[councillor_id]

            faction_element = element.find('faction')
            if faction_element is not None:
                faction_id = int(faction_element.find('id').text)
                if faction_id in faction_index:
                    faction = faction_index[faction_id]

        try:
            return authors.get(councillor=councillor, faction=faction)
        except AffairAuthor.DoesNotExist:
            return authors.create(councillor=councillor, faction=faction)

    @staticmethod
    def get_deposit(element, council_index):
        deposits = AffairDeposit.objects
        council = None
        e_council = element.find('council')
        if e_council is not None:
            council_id = e_council.find('id').text
            council = council_index[int(council_id)]
        date = element.find('date').text
        legislative_period = None
        e_legislative_period = element.find('legislativePeriod')
        if e_legislative_period is not None:
            legislative_period = e_legislative_period.text
        session = element.find('session').text

        try:
            return deposits.get(council=council, date=date, legislative_period=legislative_period, session=session)
        except AffairDeposit.DoesNotExist:
            return deposits.create(council=council, date=date, legislative_period=legislative_period, session=session)

    @transaction.atomic
    def update_db(self, xml_queue, is_first_language):
        """
        parses XML objects using data from a queue and updates the db
        :param xml_queue: queue
        :param is_first_language true, if the first language is being processed
        :return: nothing
        """
        counter = 0
        affairs = Affair.objects
        affair_type_index = {x.id: x for x in AffairType.objects.all()}
        councillor_index = {x.id: x for x in Councillor.objects.all()}
        council_index = {x.id: x for x in Council.objects.all()}
        faction_index = {x.id: x for x in Faction.objects.all()}
        start = timer()
        while True:
            content = xml_queue.get()
            if content is None:
                self.stdout.write("Queue returned none")
                break
            xml = ElementTree.fromstring(content)
            if not xml:
                raise CommandError("Not a valid XML {}".format(content))
            counter += 1

            if (counter % 1000) == 0:
                self.stdout.write(
                    "updates: {0} current queue size: {1}, last batch took {2}s".format(counter, xml_queue.qsize(),
                                                                                        timer() - start))
                start = timer()

            affair_id = xml.find('id').text
            e_sequential_number = xml.find('sequentialNumber')
            sequential_number = None if e_sequential_number is None else e_sequential_number.text
            affair_type_id = xml.find('affairType').find('id').text
            affair_type = affair_type_index[int(affair_type_id)]
            author = Command.get_author(xml.find('author'), councillor_index, faction_index)
            deposit = Command.get_deposit(xml.find('deposit'), council_index)

            # TODO: populate all other fields...

            affair_model, created = affairs.update_or_create(id=affair_id,
                                                             defaults={
                                                                 'sequential_number': sequential_number,
                                                                 'affair_type': affair_type,
                                                                 'author': author,
                                                                 'deposit': deposit,
                                                             })
            affair_model.save()
            xml_queue.task_done()

    def handle(self, *args, **options):
        is_main = True
        resource_url = 'http://ws.parlament.ch/affairs'
        affair_ids = set({x.id for x in Affair.objects.all()})

        is_first_language = True
        for lang in [x[0] for x in settings.LANGUAGES]:
            self.stdout.write('language: {0}'.format(lang))
            with concurrent.futures.ThreadPoolExecutor(max_workers=Command.ws_threads) as executor:
                task_queue = Queue(Command.task_queue_size)
                db_thread = Thread(target=Command.update_db, args=(self, task_queue, is_first_language))
                db_thread.start()
                future_to_xml = {
                executor.submit(Command.download, resource_url, lang, affair_id, is_main, task_queue): affair_id for
                affair_id in affair_ids}

                # wait until all downloads finished
                for future in concurrent.futures.as_completed(future_to_xml):
                    try:
                        future.result()
                    except Exception as e:
                        self.stdout.write('download failed {0}'.format(e))
                # wait until all updates have been written to the db
                task_queue.join()
                task_queue.put(None)
                db_thread.join()
            is_first_language = False
            is_main = False
