"""
AI Timetable Scheduling Engine using CSP (Constraint Satisfaction Problem) with Google OR-Tools
Template for school scheduling: assigns teachers to classes/periods/days, respecting constraints.
"""
from ortools.sat.python import cp_model
from collections import defaultdict

def generate_timetable(classes, teachers, subjects, availabilities, period_controls, config=None):
    """
    Generates a timetable using CSP/OR-Tools.
    Args:
        classes: list of class dicts
        teachers: list of teacher dicts
        subjects: list of subject dicts
        availabilities: list of availability dicts
        period_controls: list of period control dicts
        config: optional config dict
    Returns:
        assignments: dict of timetable assignments
    """
    # === CONFIGURATION ===
    DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    PERIODS = ["1st_period", "2nd_period", "3rd_period", "4th_period"]

    # Map for quick lookup
    teacher_id_map = {t['user_id']: t for t in teachers}
    class_id_map = {c['class_id']: c for c in classes}
    subject_id_map = {s['subject_id']: s for s in subjects}
    availability_map = {a['user_id']: a['availabilities'] for a in availabilities}

    # Map teacher string IDs to integer IDs for CSP
    teacher_str_to_int = {t['user_id']: i for i, t in enumerate(teachers)}
    teacher_int_to_str = {i: t['user_id'] for i, t in enumerate(teachers)}

    # For each class, determine the relevant subject(s) and eligible teachers
    class_subject_teachers = defaultdict(list)  # class_id -> list of (subject_id, teacher_id)
    for subject in subjects:
        for teacher in subject.get('teachers', []):
            for c in classes:
                # Match class/subject by section, level, field_of_study
                if (subject['section'] == c['section'] and
                    subject['level'] == c['level'] and
                    (c['level'] != 3 or subject.get('field_of_study') == c.get('field_of_study'))):
                    class_subject_teachers[c['class_id']].append((subject['subject_id'], teacher['teacherId']))

    model = cp_model.CpModel()
    # === VARIABLE DEFINITION ===
    # assign[class_id][day][period] = teacher_id
    assign = {}
    for c in classes:
        class_id = c['class_id']
        assign[class_id] = {}
        for day in DAYS:
            assign[class_id][day] = {}
            for period in PERIODS:
                eligible_teachers = [teacher_str_to_int[t] for (s, t) in class_subject_teachers[class_id] if t in teacher_str_to_int]
                # Decision variable: which teacher is assigned (or -1 for no teacher)
                if eligible_teachers:
                    assign[class_id][day][period] = model.NewIntVarFromDomain(
                        cp_model.Domain.FromValues(eligible_teachers + [-1]),
                        f"assign_{class_id}_{day}_{period}"
                    )
                else:
                    assign[class_id][day][period] = model.NewConstant(-1)

    # === CONSTRAINTS ===
    # 1. Teacher cannot be double-booked in the same period
    for day in DAYS:
        for period in PERIODS:
            for teacher in teachers:
                teacher_id_int = teacher_str_to_int[teacher['user_id']]
                # For all classes, teacher can only appear once per period
                indicators = []
                for c in classes:
                    class_id = c['class_id']
                    indicator = model.NewBoolVar(f"is_{teacher_id_int}_assigned_{class_id}_{day}_{period}")
                    model.Add(assign[class_id][day][period] == teacher_id_int).OnlyEnforceIf(indicator)
                    model.Add(assign[class_id][day][period] != teacher_id_int).OnlyEnforceIf(indicator.Not())
                    indicators.append(indicator)
                model.Add(sum(indicators) <= 1)

    # 2. Teacher must be available
    for c in classes:
        class_id = c['class_id']
        for day in DAYS:
            for period_idx, period in enumerate(PERIODS):
                for (subject_id, teacher_id) in class_subject_teachers[class_id]:
                    if teacher_id not in teacher_str_to_int:
                        continue
                    teacher_id_int = teacher_str_to_int[teacher_id]
                    # If assigned, must be available
                    avail = availability_map.get(teacher_id, [])
                    available = False
                    for a in avail:
                        if a.get('dayOfWeek') == day and a.get('periods', [False]*len(PERIODS))[period_idx]:
                            available = True
                    if not available:
                        # Teacher cannot be assigned if not available
                        model.Add(assign[class_id][day][period] != teacher_id_int)

    # 3. Period control (class/section/field_of_study restrictions)
    for c in classes:
        class_id = c['class_id']
        section = c['section']
        level = c['level']
        field_of_study = c.get('field_of_study')
        for day in DAYS:
            for period in PERIODS:
                allowed = True
                for control in period_controls:
                    if (control['level'] == level and control['section'] == section and
                        (level != 3 or control.get('field_of_study') == field_of_study)):
                        day_control = next((d for d in control['days'] if d['day'] == day), None)
                        if day_control and not day_control['periods'].get(period, True):
                            allowed = False
                if not allowed:
                    model.Add(assign[class_id][day][period] == -1)

    # 4. (Optional) Teacher load, contract status, priorities, fairness, etc.
    # TODO: Add constraints/objectives for load balancing, priorities, etc.

    # === OBJECTIVE ===
    # Maximize total assignments (minimize unassigned slots)
    assigned_indicators = []
    for c in classes:
        class_id = c['class_id']
        for day in DAYS:
            for period in PERIODS:
                indicator = model.NewBoolVar(f"assigned_{class_id}_{day}_{period}")
                model.Add(assign[class_id][day][period] != -1).OnlyEnforceIf(indicator)
                model.Add(assign[class_id][day][period] == -1).OnlyEnforceIf(indicator.Not())
                assigned_indicators.append(indicator)
    model.Maximize(sum(assigned_indicators))

    # === SOLVE ===
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # === EXTRACT SOLUTION ===
    timetable = defaultdict(lambda: defaultdict(list))  # day -> period -> list of assignments
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        # Build reverse lookup for subject by class and teacher
        class_subject_teacher_to_subject = {}
        for subject in subjects:
            for teacher in subject.get('teachers', []):
                for c in classes:
                    if (subject['section'] == c['section'] and
                        subject['level'] == c['level'] and
                        (c['level'] != 3 or subject.get('field_of_study') == c.get('field_of_study'))):
                        class_subject_teacher_to_subject[(c['class_id'], teacher['teacherId'])] = subject
        for c in classes:
            class_id = c['class_id']
            class_label = c.get('label', class_id)
            for day in DAYS:
                for period in PERIODS:
                    teacher_id_int = solver.Value(assign[class_id][day][period])
                    if teacher_id_int != -1:
                        teacher_id = teacher_int_to_str[teacher_id_int]
                        # Format teacher name as 'Mr./Ms. LastName' if gender is available, else 'FirstName LastName'
                        teacher_obj = teacher_id_map[teacher_id]
                        gender = teacher_obj.get('gender', '').lower() if teacher_obj.get('gender') else ''
                        if gender == 'male':
                            teacher_name = f"Mr. {teacher_obj.get('last_name', '')}"
                        elif gender == 'female':
                            teacher_name = f"Ms. {teacher_obj.get('last_name', '')}"
                        else:
                            teacher_name = f"{teacher_obj.get('first_name', '')} {teacher_obj.get('last_name', '')}"
                        # Find the subject for this class and teacher
                        subject = class_subject_teacher_to_subject.get((class_id, teacher_id), None)
                        subject_name = subject['name'] if subject else ''
                        timetable[day][period].append({
                            'class_id': class_id,
                            'class_label': class_label,
                            'teacher_id': teacher_id,
                            'teacher_name': teacher_name,
                            'subject_id': subject['subject_id'] if subject else '',
                            'subject_name': subject_name,
                        })
    else:
        # No feasible solution
        return {'status': 'no_solution', 'timetable': {}}

    return {'status': 'ok', 'timetable': timetable}
