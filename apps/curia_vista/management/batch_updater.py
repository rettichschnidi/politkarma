from bulk_update.helper import bulk_update
from django.core.management import CommandError


class SimpleBatchUpdater:
    def __init__(self, model_class, pks, update_interval=20, use_bulk_update=False):
        """

        :param model_class: model class
        :param pks: primary keys
        :param update_interval: update/insert interval (in number of records)
        :param use_bulk_update: if set, the extension bulk_update is used for updates.
        :return:
        """
        self.use_bulk_update = use_bulk_update
        self.model_class = model_class
        self.update_interval = update_interval
        self.update_count = 0
        self.pk_fields = pks

        # calling instance method in constructor here..
        self.pk_index = {self.extract_key(x): x for x in model_class.objects.all()}
        self.update_list = []
        self.insert_list = []

    def extract_key(self, obj):
        key_dict = {}
        # TODO: index is currently string based to match the type of the model class attributes
        for key in self.pk_fields:
            key_dict[key] = str(getattr(obj, key))

        return frozenset(key_dict)

    @staticmethod
    def get_pk_from_class(model_class):
        """
        :param model_class:
        :return
        from pprint import pprint
        pprint(vars(model_class._meta))
        """
        pks = []
        for field in model_class._meta.fields:
            if field.primary_key:
                pks.append(field.name)

        if pks.__len__() == 0:
            raise CommandError("Model class {} has no primary key".format(model_class))
        return pks

    @staticmethod
    def get_pk_from_config(config_mapping):
        pks = []
        for tag, mapping in config_mapping.items():
            if mapping.primary:
                pks.append(tag)
        return pks

    def add(self, element):
        element_key = self.extract_key(element)
        if element_key in self.pk_index:
            self.update_list.append(element)
        else:
            self.insert_list.append(element)
            self.pk_index[element_key] = element

        self.update_count += 1
        if self.update_count % self.update_interval == 0:
            self.write_to_db()

    def non_batch_update(self):
        for element in self.update_list:
            element.save()

    def write_to_db(self):
        if self.insert_list.__len__() > 0:
            try:
                self.model_class.objects.bulk_create(self.insert_list)
                self.insert_list.clear()
            except Exception as e:
                print("bulk_create failed {}".format(self.model_class))
                raise e
        if self.update_list.__len__() > 0:
            try:
                if self.use_bulk_update:
                    bulk_update(self.update_list)
                else:
                    self.non_batch_update()
                self.update_list.clear()
            except Exception as e:
                print("bulk_update failed{}".format(self.model_class))
                raise e
