class ScheduleLogic {
    COOKIE_NAME = 'schedule';

    constructor() {
        this.courses = {};
        this.savedGroups = [];
    }

    /**
     * Retrieves from the server a list of courses matching to the searched
     * value.
     * @param searchVal Value to search (course number or name).
     * @param successCallback Callback to call on success.
     * @param errorCallback Callback to call on error.
     */
    getCoursesFromServer(searchVal, successCallback, errorCallback) {
        ajax({'search_val': searchVal},
        (response) => {
            successCallback(response);
        }, () => {
            errorCallback();
        });
    }

    /**
     * Retrieves from server the groups of the given course and adds the
     * course to the list of added courses.
     * @param course The course to add.
     * @param successCallback Callback to call on success.
     * @param errorCallback Callback to call on error.
     * @param autoLoaded Whether this course was auto loaded, or manually loaded.
     */
    addCourse(course, successCallback, errorCallback, autoLoaded) {
        ajax({'course_number': course['course_number']},
        (response) => {
            let groups = response.groups;
            this.courses[course['course_number']] = {
                'course': course,
                'groups': groups
            };
            response['course'] = course;
            response['auto_loaded'] = autoLoaded;
            successCallback(response);
        }, () => {
            errorCallback();
        });
    }

    cookieStoreGroup(groupId) {
        if (LOGGED_IN) {
            return;
        }

        let storedGroups = {'groups': []};

        if (!Cookies.get(this.COOKIE_NAME)) {
            Cookies.set(this.COOKIE_NAME, JSON.stringify(storedGroups));
            console.log('Created new cookie ' + this.COOKIE_NAME);
        }

        storedGroups = JSON.parse(Cookies.get(this.COOKIE_NAME));
        if (storedGroups['groups'].includes(groupId)) {
            console.log('Tried to add group ' + groupId + ' which is already stored.');
            return;
        }

        storedGroups['groups'].push(groupId);
        Cookies.set(this.COOKIE_NAME, JSON.stringify(storedGroups));
        console.log('Added group ' + groupId + '. New value is: ' + JSON.stringify(storedGroups));
    }

    cookieDeleteGroup(groupId) {
        if (LOGGED_IN) {
            return;
        }

        if (!Cookies.get(this.COOKIE_NAME)) {
            return;
        }

        let storedGroups = JSON.parse(Cookies.get(this.COOKIE_NAME));
        if (storedGroups['groups'].includes(groupId)) {
            let idx = storedGroups['groups'].indexOf(groupId);
            storedGroups['groups'].splice(idx, 1);
            Cookies.set(this.COOKIE_NAME, JSON.stringify(storedGroups));
            console.log('Deleted ' + groupId + '. New value is: ' + storedGroups['groups']);
        }
    }

    cookieHasGroup(groupId) {
        if (!Cookies.get(this.COOKIE_NAME)) {
            return;
        }

        let storedGroup = JSON.parse(Cookies.get(this.COOKIE_NAME));
        return storedGroup['groups'].includes(groupId);
    }

    choicesHasGroup(groupId) {
        return this.savedGroups.includes(groupId);
    }

    userStoreGroup(groupId) {
        ajax({"group_choice": groupId}, () => {
            console.log(`Successfully added group ${groupId} to schedule`);
        });
    }

    loadSavedCourses(choices) {
        const parsed_choices = JSON.parse(choices);
        this.savedGroups = parsed_choices["group_ids"];

        parsed_choices["courses"].forEach(function (course) {
            schedule.addCourse(course, addCourseSuccessCb, addCourseErrorCb, true);
        });
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
        let group_ids = {"group_ids": []};
        for (let i = 0; i < course_groups.length; i++) {
            let group_id = course_groups[i]['id'];
            group_ids["group_ids"].push(group_id);
            $('[data-group=class_item_' + group_id + ']').remove();
            if (this.cookieHasGroup(group_id)) {
                this.cookieDeleteGroup(group_id);
            }
        }

        ajax({"groups_to_del": JSON.stringify(group_ids)}, () => {
            console.log(`Successfully deleted group ${group_ids["group_ids"]} from schedule`);
        });
        delete this.courses[course_number];
    }
}

let schedule = new ScheduleLogic();