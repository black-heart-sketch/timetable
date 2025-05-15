"""
Seed script for populating MongoDB with test data for SchoolAI timetable scheduler.
Run with: python manage.py shell < scheduler/seed.py
"""
from scheduler.models import Teacher, Class, Subject, Availability, PeriodControl

# Clear old data
def clear_all():
    Teacher.drop_collection()
    Class.drop_collection()
    Subject.drop_collection()
    Availability.drop_collection()
    PeriodControl.drop_collection()

clear_all()

# Seed Teachers (10)
teachers_data = [
    ('t1', 'Alice', 'Smith', 'Internal'),
    ('t2', 'Bob', 'Brown', 'Consultant'),
    ('t3', 'Carol', 'Jones', 'External'),
    ('t4', 'David', 'Wilson', 'Internal'),
    ('t5', 'Eva', 'Miller', 'Consultant'),
    ('t6', 'Frank', 'Moore', 'External'),
    ('t7', 'Grace', 'Taylor', 'Internal'),
    ('t8', 'Henry', 'Anderson', 'Consultant'),
    ('t9', 'Ivy', 'Thomas', 'External'),
    ('t10', 'Jack', 'Jackson', 'Internal'),
]
teachers = [
    Teacher(user_id=tid, first_name=fn, last_name=ln, contract_status=cs, assigned_classes=[], role='THR').save()
    for tid, fn, ln, cs in teachers_data
]

# Seed Classes (10)
classes_data = [
    ('c1', 'A', 1, 'Science'),
    ('c2', 'A', 1, 'Math'),
    ('c3', 'B', 2, 'Literature'),
    ('c4', 'B', 2, 'Economics'),
    ('c5', 'C', 3, 'Science'),
    ('c6', 'C', 3, 'Math'),
    ('c7', 'D', 1, 'History'),
    ('c8', 'D', 2, 'Geography'),
    ('c9', 'E', 3, 'Philosophy'),
    ('c10', 'E', 1, 'ICT'),
]
classes = [
    Class(class_id=cid, section=sec, level=lev, field_of_study=fos).save()
    for cid, sec, lev, fos in classes_data
]

# Seed Subjects (12+)
subjects_data = [
    ('s1', 'Biology', 1, 'A', 'Science', ['t1', 't2']),
    ('s2', 'Mathematics', 1, 'A', 'Math', ['t3', 't4']),
    ('s3', 'Physics', 3, 'C', 'Science', ['t2', 't5']),
    ('s4', 'Literature', 2, 'B', 'Literature', ['t6', 't7']),
    ('s5', 'Economics', 2, 'B', 'Economics', ['t8']),
    ('s6', 'Chemistry', 3, 'C', 'Math', ['t9']),
    ('s7', 'History', 1, 'D', 'History', ['t10', 't1']),
    ('s8', 'Geography', 2, 'D', 'Geography', ['t3', 't4']),
    ('s9', 'Philosophy', 3, 'E', 'Philosophy', ['t5', 't6']),
    ('s10', 'ICT', 1, 'E', 'ICT', ['t7', 't8']),
    ('s11', 'English', 2, 'B', 'Literature', ['t9', 't2']),
    ('s12', 'French', 1, 'A', 'Science', ['t10', 't3']),
]
subjects = [
    Subject(subject_id=sid, name=sname, status='active', priority='medium', level=lev, section=sec, field_of_study=fos, teachers=[{'teacherId': t} for t in tids]).save()
    for sid, sname, lev, sec, fos, tids in subjects_data
]

# Seed Availabilities for each teacher (spread out)
avails = [
    ('t1', [('Mon', [True, True, False, False]), ('Tue', [True, True, True, False]), ('Wed', [False, True, True, True])]),
    ('t2', [('Mon', [True, False, True, True]), ('Wed', [True, True, False, False]), ('Thu', [True, True, True, False])]),
    ('t3', [('Tue', [True, True, True, True]), ('Thu', [False, True, True, True]), ('Fri', [True, False, True, False])]),
    ('t4', [('Mon', [True, True, False, True]), ('Fri', [True, True, True, True])]),
    ('t5', [('Tue', [False, True, True, True]), ('Wed', [True, True, True, False])]),
    ('t6', [('Wed', [True, False, True, True]), ('Thu', [True, True, False, True])]),
    ('t7', [('Mon', [True, True, True, False]), ('Sat', [True, True, False, True])]),
    ('t8', [('Tue', [True, False, True, True]), ('Fri', [True, True, True, False])]),
    ('t9', [('Wed', [True, True, False, True]), ('Sat', [True, False, True, True])]),
    ('t10', [('Thu', [True, True, True, True]), ('Fri', [False, True, True, True])]),
]
for tid, days in avails:
    Availability(user_id=tid, availabilities=[{'dayOfWeek': d, 'periods': p} for d, p in days]).save()

# Seed PeriodControls (for each class)
for cid, sec, lev, fos in classes_data:
    PeriodControl(level=lev, section=sec, field_of_study=fos, days=[
        {'day': 'Mon', 'periods': {'1st_period': True, '2nd_period': True, '3rd_period': True, '4th_period': True}},
        {'day': 'Tue', 'periods': {'1st_period': True, '2nd_period': True, '3rd_period': True, '4th_period': True}},
        {'day': 'Wed', 'periods': {'1st_period': True, '2nd_period': True, '3rd_period': True, '4th_period': True}},
        {'day': 'Thu', 'periods': {'1st_period': True, '2nd_period': True, '3rd_period': True, '4th_period': True}},
        {'day': 'Fri', 'periods': {'1st_period': True, '2nd_period': True, '3rd_period': True, '4th_period': True}},
        {'day': 'Sat', 'periods': {'1st_period': True, '2nd_period': True, '3rd_period': True, '4th_period': True}},
    ]).save()

print('Seeded test data with 10 classes, 10 teachers, and realistic subjects.')
