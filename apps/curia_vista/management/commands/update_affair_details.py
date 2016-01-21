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
    task_queue_size = 100

    def add_arguments(self, parser):
        parser.add_argument('--parallel', choices=range(1, 25), default=12,
                            help="Maximal number threads/connections", type=int)

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
            raise CommandError("Could not fetch file from {}".format(url, e))
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
        """

        :param element: <deposit> element
        :param council_index: council index (key=id, value=council)
        :return:
        """
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

    @staticmethod
    def get_handling(element, lp_index, session_index):
        """

        :param element: <handling> element
        :param lp_index: legislative period index (key=id, value=legislative period)
        :param session_index: session index (key=code, value=session)
        :return: AffairHandling object
        """
        if element is None:
            return None
        date = element.find('date').text
        # Legislative period has both id and code, the values appear to be the same for both columns.
        # I assume it's the id because it is the primary key. No idea if this is correct...
        e_legislative_period = element.find('legislativePeriod')
        legislative_period = None if e_legislative_period is None else lp_index[int(e_legislative_period.text)]
        # One affair's session code is 5002, the greatest session code is 5001.
        # Looks like the session list is not up-to-date.
        session_id = int(element.find('session').text)
        session = None
        if session_id in session_index:
            session = session_index[session_id]
        return AffairHandling.objects.create(date=date, legislative_period=legislative_period, session=session)

    @staticmethod
    def get_roles(element, councillor_index, faction_index):
        """

        :param element: <roles> element
        :param councillor_index: councillor index (key=id, value=councillor)
        :param faction_index: faction index (key=id, value=faction)
        :return:
        """
        affair_roles = AffairRole.objects
        roles = []
        for role in element:
            role_type = role.find('type').text

            e_councillor = role.find('councillor')
            councillor = None
            if e_councillor is not None:
                councillor_id = int(e_councillor.find('id').text)
                councillor = councillor_index[councillor_id]

            e_faction = role.find('faction')
            faction = None
            if e_faction is not None:
                faction_id = int(e_faction.find('id').text)
                if faction_id in faction_index:
                    faction = faction_index[faction_id]
                    # TODO: many factions appear to be missing...
            affair_role = affair_roles.create(role_type=role_type, councillor=councillor, faction=faction)
            roles.append(affair_role)
        return roles

    @staticmethod
    def handle_priority_councils(element, council_index):
        """
        :param element: <priorityCouncil> element
        :param council_index: council index (key=id, value=council)
        :return:
        """
        priority_councils = []
        if element is None:
            return priority_councils
        apcs = AffairPriorityCouncil.objects
        for e_priority_council in element:
            council_id = int(e_priority_council.find('id').text)
            council = None
            if council_id in council_index:
                council = council_index[council_id]
            else:
                # TODO: yes, this really happens. no idea what council with id 4 is...
                print("Council with id {0} does not exist".format(council_id))
            priority = e_priority_council.find('priority').text
            priority_council = apcs.create(council=council, priority=priority)
            priority_councils.append(priority_council)
        return priority_councils

    @staticmethod
    def handle_texts(element):
        """

        :param element: <texts> element
        :return:
        """
        affair_texts = []
        if element is None:
            return affair_texts
        ats = AffairText.objects
        for e_text in element:
            value = e_text.find('value').text
            affair_text_type = Command.handle_affair_text_type(e_text.find('type'))
            text = ats.create(value=value, type=affair_text_type)
            affair_texts.append(text)
        return affair_texts

    @staticmethod
    def handle_affair_text_type(element):
        """

        :param element: <type> element
        :return:
        """
        text_type_id = element.find('id').text
        name = element.find('name').text
        text_type, created = AffairTextType.objects.update_or_create(id=text_type_id, defaults={'name': name})
        return text_type

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
        self.stdout.write("preparing indices...")
        affair_type_index = {x.id: x for x in AffairType.objects.all()}
        councillor_index = {x.id: x for x in Councillor.objects.all()}
        council_index = {x.id: x for x in Council.objects.all()}
        faction_index = {x.id: x for x in Faction.objects.all()}
        state_index = {x.id: x for x in AffairState.objects.all()}
        session_index = {x.code: x for x in Session.objects.all()}
        lp_index = {x.id: x for x in LegislativePeriod.objects.all()}
        self.stdout.write("indices ready, going to process data from queue")

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
            affair = affairs.get(id=affair_id)
            e_sequential_number = xml.find('sequentialNumber')
            affair.sequential_number = None if e_sequential_number is None else e_sequential_number.text
            affair_type_id = xml.find('affairType').find('id').text
            affair.affair_type = affair_type_index[int(affair_type_id)]
            affair.author = Command.get_author(xml.find('author'), councillor_index, faction_index)
            affair.deposit = Command.get_deposit(xml.find('deposit'), council_index)
            # TODO: implement descriptors
            # TODO: implement drafts
            previous_handling = affair.handling
            affair.handling = Command.get_handling(xml.find('handling'), lp_index, session_index)
            previous_priority_councils = affair.priority_councils
            affair.priority_councils = Command.handle_priority_councils(xml.find('priorityCouncils'), council_index)
            # TODO: implement relatedAffairs
            previous_roles = affair.roles
            affair.roles = Command.get_roles(xml.find('roles'), councillor_index, faction_index)
            e_sequential_number = xml.find('sequentialNumber')
            affair.sequential_number = None if e_sequential_number is None else e_sequential_number.text
            affair.title = xml.find('title').text
            e_state = xml.find('state')
            affair.state = state_index[int(e_state.find('id').text)]
            affair.done_key = e_state.find('doneKey').text
            affair.new_key = e_state.find('newKey').text
            previous_texts = affair.texts
            affair.texts = Command.handle_texts(xml.find('texts'))

            affair.save()
            # delete unreferenced objects
            if previous_handling is not None:
                previous_handling.delete()
            if previous_roles is not None:
                for previous_role in previous_roles.all():
                    previous_role.delete()
            if previous_priority_councils is not None:
                for previous_priority_council in previous_priority_councils.all():
                    previous_priority_council.delete()
            if previous_texts is not None:
                for previous_text in previous_texts.all():
                    previous_text.delete()
            xml_queue.task_done()

    def handle(self, *args, **options):
        is_main = True
        resource_url = 'http://ws.parlament.ch/affairs'
        affair_ids = set({x.id for x in Affair.objects.all()})

        self.stdout.write("Starting {} threads".format(options['parallel']))

        is_first_language = True
        for lang in [x[0] for x in settings.LANGUAGES]:
            # if not is_first_language:
            #    break
            self.stdout.write('language: {0}'.format(lang))
            with concurrent.futures.ThreadPoolExecutor(max_workers=options['parallel']) as executor:
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
