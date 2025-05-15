from mongoengine import Document, StringField, IntField, ListField, DictField

class Teacher(Document):
    user_id = StringField(required=True, unique=True)
    first_name = StringField()
    last_name = StringField()
    contract_status = StringField(choices=["Consultant", "External", "Internal"])
    assigned_classes = ListField(DictField())
    role = StringField()

class Class(Document):
    class_id = StringField(required=True, unique=True)
    section = StringField()
    level = IntField()
    field_of_study = StringField()

class Subject(Document):
    subject_id = StringField(required=True, unique=True)
    name = StringField()
    status = StringField()
    priority = StringField(choices=["low", "medium", "high"])
    level = IntField()
    section = StringField()
    field_of_study = StringField()
    teachers = ListField(DictField())

class Availability(Document):
    user_id = StringField(required=True)
    availabilities = ListField(DictField())

class PeriodControl(Document):
    level = IntField()
    section = StringField()
    field_of_study = StringField()
    days = ListField(DictField())
