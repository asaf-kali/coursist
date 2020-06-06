$(document).ready(function () {
    $('#course_input').keypress(function (e) {
        if (e.keyCode === 13) {
            e.preventDefault();
            $('#search_btn').click();
        }
    });
});

class ScheduleLogic {
    constructor() {
        this.courses = {};
    }

    addCourse(course, groups) {
        this.courses[course['course_number']] = {
            'course': course,
            'groups': groups
        };
    }

    hasCourse(course) {
        return course['course_number'] in this.courses;
    }

    getCourseNameByNumber(courseNumber) {
        return this.courses[courseNumber]['course']['name'];
    }

    getCourseGroupsByNumber(courseNumber) {
        return this.courses[courseNumber]['groups'];
    }

    /**
     * Returns an array of the class types of the given course.
     * @param course_number The number of the course.
     * @returns {[]|undefined} Array containing all the distinct class types.
     */
    getClassTypes(course_number) {
        let class_types = [];
        if (!course_number in this.courses) {
            return undefined;
        }

        let groups = this.courses[course_number]['groups'];
        for (let i = 0; i < groups.length; i++) {
            let cur_type = groups[i]['class_type'];
            if (!class_types.includes(cur_type)) {
                class_types.push(cur_type);
            }
        }

        return class_types;
    }

    classTypeToName(class_type) {
        let types = {
            '1': 'שיעור',
            '2': 'תרגול',
            '3': 'סמינר',
            '4': 'מעבדה',
            '5': 'סדנה',
            '6': 'מטלה',
            '7': 'שיעור קליני',
            '8': 'סיור',
            '9': 'מכינה',
            '10': 'הדרכה',
            '11': 'שיעור ומעבדה',
            '12': 'שיעור ותרגיל',
            '13': 'עבודה מעשית',
            '14': 'שיעור וסדנה',
            '15': 'שיעור והדרכה',
            '16': 'שיעור וסמינר',
            '17': 'מחנה',
        };

        if (class_type in types) {
            return types[class_type];
        }

        return 'Unknown class type';
    }

    semesterToName(semester) {
        let semesters = {
            '1': 'סמסטר א',
            '2': 'סמסטר ב',
            '3': 'סמסטר ג',
            '4': 'סמסטר קיץ',
            '5': 'שנתי',
        };

        if (semester in semesters) {
            return semesters[semester];
        }

        return 'Unknown semester';
    }

    getGroupTeachers(group) {
        let teachers = "";
        if (group['classes'].length > 0) {
            for (let i = 0; i < group['classes'].length; i++) {
                teachers += group['classes'][i]['teacher'] + ', ';
            }

            teachers = teachers.substring(0, teachers.length - 2);
        }

        return teachers;
    }

    removeCourse(course_number) {
        let course_groups = this.courses[course_number]['groups'];
        for (let i = 0; i < course_groups.length; i++) {
            let group_id = course_groups[i]['id'];
            $('[data-group=class_item_' + group_id + ']').remove();
        }
        delete this.courses[course_number];
    }
}

let schedule = new ScheduleLogic();

/**
 * Autocompletes the user search.
 */
function courses_autocomplete(search_val, csrf) {
    let container = $('#search_results');

    if (search_val.length < 2) {
        container.html('');
        return;
    }

    container.html(
        '<div class="text-center">' +
        '<div class="spinner-grow text-primary" role="status"></div>' +
        '</div>'
    );

    ajax({'search_val': search_val},
        (response) => {
            if (response.status !== 'success') {
                container.html('Error, try again.');
                return;
            }

            container.html('<ul></ul>');
            let courses = response.courses;
            if (courses.length === 0) {
                container.html();
                return;
            }

            // display the results
            let list = container.find('ul');
            $.each(courses, function (index, value) {
                if (!schedule.hasCourse(value)) {
                    const item_html = hb_templates['schedule-course-autocomplete-item']({'course': value});
                    list.append(item_html);
                    $('#add_course_' + value['course_number']).click(function (e) {
                        e.preventDefault();
                        addCourse(value, csrf);
                        list.html('');
                        $('#course_input').val('');
                    });
                }
            });
        }, () => {
            container.html('Error, try again.');
        });
}

/**
 * Adds a course to the course list.
 */
function addCourse(course, csrf) {
    console.log(course);
    if (schedule.hasCourse(course)) {
        return;
    }

    $.ajax({
        method: 'POST',
        url: './',
        data: {
            csrfmiddlewaretoken: csrf,
            'course_number': course['course_number']
        },
        success: function (response) {
            const groups = response.groups;
            if (groups.length === 0) {
                // TODO show to the user error message?
                return;
            }
            schedule.addCourse(course, groups);
            let course_number = course['course_number'];
            let course_list_container = $('#my_courses_list');
            let item_html = hb_templates['schedule-course-item']({'course': course});
            course_list_container.append(item_html);

            // collapse functionality
            $('#course_item_' + course_number).find('.course_name').click(function () {
                toggleCourseItem($(this));
            });

            // delete functionality
            $('#del_btn_' + course_number).click(function () {
                schedule.removeCourse(course_number);
                $('#course_item_' + course_number).remove();
            });

            let groupsContainer = $('#course_groups_' + course_number);
            displayCourseGroups(groupsContainer, course_number, groups);
        },
        error: function () {
            alert('failed');
        }
    });
}

function displayGroup(group, cur_class_type, passed_first, courseNumber, group_list) {
    if (group['class_type'] === cur_class_type) {
        let css_class = (passed_first === false) ? 'active' : '';

        let group_item = hb_templates['schedule-course-item-group-item']({
            'css_class': css_class,
            'course_number': courseNumber,
            'group_id': group['id'],
            'mark': group['mark'],
            'teachers': schedule.getGroupTeachers(group)
        });
        group_list.append(group_item);

        // Add click functionality
        $('#list_group_' + courseNumber + '_' + group['id']).click(function (e) {
            if (!$(this).hasClass('active')) {
                $(this).siblings().removeClass('active');
                $(this).addClass('active');
                updateScheduleDisplay(courseNumber, group);
                ajax({"group_choice": group["id"]}, () => {
                    console.log(`Successfully added group ${group["id"]} to schedule`);
                });
            }
        });

        // Display first of each class type in the schedule
        if (passed_first === false) {
            updateScheduleDisplay(courseNumber, group);
        }
        return true;
    }
}

/**
 * Displays the groups of the given course.
 */
function displayCourseGroups(container, courseNumber, groups) {
    let class_types = schedule.getClassTypes(courseNumber);
    for (let i = 0; i < class_types.length; i++) {
        let cur_class_type = class_types[i];
        let group_header = hb_templates['schedule-course-item-group-header']({
            'class_type': cur_class_type,
            'class_type_name': schedule.classTypeToName(cur_class_type)
        });
        container.append(group_header);

        let group_list = container.find('.course_group_' + cur_class_type);
        let passed_first = false;
        groups.forEach((group) => {
            passed_first = displayGroup(group, cur_class_type, passed_first, courseNumber, group_list);
        });
    }
}

// time table UI
let scheduleTemplate = document.getElementsByClassName('js-cd-schedule'),
    scheduleTemplateArray = [],
    resizing = false;

if (scheduleTemplate.length > 0) { // init ScheduleTemplate objects
    for (let i = 0; i < scheduleTemplate.length; i++) {
        (function (i) {
            scheduleTemplateArray.push(new ScheduleTemplate(scheduleTemplate[i]));
        })(i);
    }

    window.addEventListener('resize', function (event) {
        // on resize - update events position and modal position (if open)
        if (!resizing) {
            resizing = true;
            (!window.requestAnimationFrame) ? setTimeout(checkResize, 250) : window.requestAnimationFrame(checkResize);
        }
    });

    window.addEventListener('keyup', function (event) {
        // close event modal when pressing escape key
        if (event.keyCode && event.keyCode === 27 || event.key && event.key.toLowerCase() === 'escape') {
            for (let i = 0; i < scheduleTemplateArray.length; i++) {
                scheduleTemplateArray[i].closeModal();
            }
        }
    });

    function checkResize() {
        for (let i = 0; i < scheduleTemplateArray.length; i++) {
            scheduleTemplateArray[i].scheduleReset();
        }
        resizing = false;
    }
}

function getClassLecturer(cls) {
    ret = [];

    if (cls['lecturer'].length !== cls['hour'].length) {
        // case where the same lecturer in all classes
        for (let i = 0; i < cls['hour'].length; i++) {
            ret.push(cls['lecturer'][0]);
        }
    } else {
        // case where different lecturer in classes
        for (let i = 0; i < cls['lecturer'].length; i++) {
            ret.push(cls['lecturer'][i]);
        }
    }

    return ret;
}

function getNiceTime(time) {
    const lastIndex = time.lastIndexOf(":");
    return time.substring(0, lastIndex);
}

function addClassToDisplay(courseNumber, courseName, group, courseClass) {
    const class_id = courseClass['id'];
    const group_id = group['id'];
    const class_type = group['class_type'];
    const teacher = courseClass['teacher'];
    const semester = courseClass['semester'];
    const day = courseClass['day'];
    const startTime = getNiceTime(courseClass['start_time']);
    const endTime = getNiceTime(courseClass['end_time']);
    const hall = courseClass['hall'];

    const li_id = 'class_item_' + courseNumber + '_' + class_id;
    const li_data_group = 'class_item_' + group_id;

    let schedule_event = hb_templates['schedule-single-event']({
        'li_id': li_id,
        'li_data_group': li_data_group,
        'class_type': class_type,
        'start_time': startTime,
        'end_time': endTime,
        'course_number': courseNumber,
        'course_name': courseName
    });

    $('#schedule_semester_' + semester).find('#day_' + day + '_a').append(schedule_event);

    scheduleTemplateArray[semester - 1].refreshSchedule();
}

function getGroupsToRemove(courseNumber, group) {
    let allGroups = schedule.getCourseGroupsByNumber(courseNumber);
    let groupsToRemove = [];
    for (let i = 0; i < allGroups.length; i++) {
        if (allGroups[i]['class_type'] === group["class_type"]) {
            if (allGroups[i]['id'] !== group["id"]) {
                groupsToRemove.push(allGroups[i]['id']);
            }
        }
    }
    return groupsToRemove;
}

function removeCourseGroups(groupsToRemove) {
    for (let i = 0; i < groupsToRemove.length; i++) {
        $('[data-group=class_item_' + groupsToRemove[i] + ']').remove();
    }
}

function updateScheduleDisplay(courseNumber, group) {
    // TODO decide to which schedule depending on the semester
    const courseName = schedule.getCourseNameByNumber(courseNumber);
    let groupsToRemove = getGroupsToRemove(courseNumber, group);
    removeCourseGroups(groupsToRemove);
    $.each(group['classes'], function (index, courseClass) {
        addClassToDisplay(courseNumber, courseName, group, courseClass);
    });
}

function toggleCourseItem($title_element) {
    if ($title_element.hasClass('opened')) {
        $title_element.removeClass('opened');
        $title_element.parent().parent().find('.course_groups_wrapper').slideUp();
    } else {
        $title_element.addClass('opened');
        $title_element.parent().parent().find('.course_groups_wrapper').slideDown();
    }
}

/**
 * Refresh the schedule when the tab is shown, to properly display the events.
 */
$('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
    const jq_elem = $(e.target);
    const target = jq_elem.attr('href');
    const schedule_idx = $(target).data('schedule');
    scheduleTemplateArray[schedule_idx].refreshSchedule();
});

function initWithChoices(choices) {
    // TODO: Take it from here
    console.log(choices);
}