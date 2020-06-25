// Schedule Template - by CodyHouse.co
// License: https://codyhouse.co/mit
function ScheduleTemplate(element) {
    this.element = element;
    this.timelineItems = this.element.getElementsByClassName('cd-schedule__timeline')[0].getElementsByTagName('li');
    this.timelineStart = getScheduleTimestamp(this.timelineItems[0].textContent);
    this.timelineUnitDuration = getScheduleTimestamp(this.timelineItems[1].textContent) - getScheduleTimestamp(this.timelineItems[0].textContent);

    this.topInfoElement = this.element.getElementsByClassName('cd-schedule__top-info')[0];
    this.singleEvents = this.element.getElementsByClassName('cd-schedule__event');

    this.modal = this.element.getElementsByClassName('cd-schedule-modal')[0];
    this.modalHeader = this.element.getElementsByClassName('cd-schedule-modal__header')[0];
    this.modalHeaderBg = this.element.getElementsByClassName('cd-schedule-modal__header-bg')[0];
    this.modalBody = this.element.getElementsByClassName('cd-schedule-modal__body')[0];
    this.modalBodyBg = this.element.getElementsByClassName('cd-schedule-modal__body-bg')[0];
    this.modalClose = this.modal.getElementsByClassName('cd-schedule-modal__close')[0];
    this.modalDate = this.modal.getElementsByClassName('cd-schedule-modal__date')[0];
    this.modalEventName = this.modal.getElementsByClassName('cd-schedule-modal__name')[0];
    this.coverLayer = this.element.getElementsByClassName('cd-schedule__cover-layer')[0];

    this.modalMaxWidth = 800;
    this.modalMaxHeight = 480;

    this.animating = false;
    this.supportAnimation = Util.cssSupports('transition');

    this.initSchedule();
};

ScheduleTemplate.prototype.initSchedule = function () {
    this.scheduleReset();
    this.initEvents();
};

ScheduleTemplate.prototype.scheduleReset = function () {
    // according to the mq value, init the style of the template
    let mq = this.mq(),
        loaded = Util.hasClass(this.element, 'js-schedule-loaded'),
        modalOpen = Util.hasClass(this.modal, 'cd-schedule-modal--open');
    if (mq === 'desktop' && !loaded) {
        Util.addClass(this.element, 'js-schedule-loaded');
        this.placeEvents();
        modalOpen && this.checkEventModal(modalOpen);
    } else if (mq === 'mobile' && loaded) {
        //in this case you are on a mobile version (first load or resize from desktop)
        Util.removeClass(this.element, 'cd-schedule--loading js-schedule-loaded');
        this.resetEventsStyle();
        modalOpen && this.checkEventModal();
    } else if (mq === 'desktop' && modalOpen) {
        //on a mobile version with modal open - need to resize/move modal window
        this.checkEventModal(modalOpen);
        Util.removeClass(this.element, 'cd-schedule--loading');
    } else {
        Util.removeClass(this.element, 'cd-schedule--loading');
    }
};

ScheduleTemplate.prototype.resetEventsStyle = function () {
    // remove js style applied to the single events
    for (let i = 0; i < this.singleEvents.length; i++) {
        this.singleEvents[i].removeAttribute('style');
    }
};

/**
 * Sets the position of the events overlapping the given event (including the
 * given event).
 */
ScheduleTemplate.prototype.setEventPosition = function (cur_event, width) {
    let parent = cur_event.parentNode;
    let children = parent.children;
    let num_overlaps = 0;

    let start = $(cur_event).children('a').data('start').replace(':', '');
    let end = $(cur_event).children('a').data('end').replace(':', '');

    for (let i = 0; i < children.length; i++) {
        let cur_start = $(children[i]).find('a').attr('data-start').replace(':', '');
        let cur_end = $(children[i]).find('a').attr('data-end').replace(':', '');

        // if ends in the middle of another class
        // if start in the middle of another class
        // if in bweteen another class
        // if containing another class
        if (
            (cur_end > start && cur_end <= end) ||
            (cur_start >= start && cur_start < end) ||
            (cur_start >= start && cur_end <= end) ||
            (cur_start <= start && cur_end >= end)
        ) {
            $(children[i]).css('left', (num_overlaps * width) + '%');
            $(children[i]).css('width', width + '%');
            $(children[i]).addClass('adjusted');
            num_overlaps++;
        }
    }
};

/**
 * Returns the number of events overlapping the given event.
 */
ScheduleTemplate.prototype.getNumOverlaps = function (cur_event) {
    let parent = cur_event.parentNode;
    let children = parent.children;
    let num_overlaps = 0;

    let start = $(cur_event).children('a').data('start').replace(':', '');
    let end = $(cur_event).children('a').data('end').replace(':', '');

    for (let i = 0; i < children.length; i++) {
        let cur_start = $(children[i]).find('a').attr('data-start').replace(':', '');
        let cur_end = $(children[i]).find('a').attr('data-end').replace(':', '');

        // if ends in the middle of another class
        // if start in the middle of another class
        // if in bweteen another class
        // if containing another class
        if (
            (cur_end > start && cur_end <= end) ||
            (cur_start >= start && cur_start < end) ||
            (cur_start >= start && cur_end <= end) ||
            (cur_start <= start && cur_end >= end)
        ) {
            num_overlaps++;
        }
    }

    return num_overlaps;
};

ScheduleTemplate.prototype.placeEvents = function () {
    // on big devices - place events in the template according to their time/day
    let self = this,
        slotHeight = this.topInfoElement.offsetHeight;
    for (let i = 0; i < this.singleEvents.length; i++) {
        let anchor = this.singleEvents[i].getElementsByTagName('a')[0];
        let start = getScheduleTimestamp(anchor.getAttribute('data-start')),
            duration = getScheduleTimestamp(anchor.getAttribute('data-end')) - start;

        let eventTop = slotHeight * (start - self.timelineStart) / self.timelineUnitDuration,
            eventHeight = slotHeight * duration / self.timelineUnitDuration;

        this.singleEvents[i].setAttribute('style', 'top: ' + (eventTop - 1) + 'px; height: ' + (eventHeight + 1) + 'px');
        let numOverlaps = this.getNumOverlaps(this.singleEvents[i]);
        this.setEventPosition(this.singleEvents[i], 100 / numOverlaps);
    }

    Util.removeClass(this.element, 'cd-schedule--loading');
};

ScheduleTemplate.prototype.initEvents = function () {
    let self = this;
    for (let i = 0; i < this.singleEvents.length; i++) {
        // open modal when user selects an event
        this.singleEvents[i].addEventListener('click', function (event) {
            event.preventDefault();
            if (!self.animating) self.openModal(this.getElementsByTagName('a')[0]);
        });
    }
    //close modal window
    this.modalClose.addEventListener('click', function (event) {
        event.preventDefault();
        if (!self.animating) self.closeModal();
    });
    this.coverLayer.addEventListener('click', function (event) {
        event.preventDefault();
        if (!self.animating) self.closeModal();
    });
};

ScheduleTemplate.prototype.refreshSchedule = function () {
    this.singleEvents = this.element.getElementsByClassName('cd-schedule__event');
    this.placeEvents();
    this.initEvents();
};

ScheduleTemplate.prototype.openModal = function (target) {
    let self = this;
    let mq = self.mq();
    this.animating = true;

    //update event name and time
    this.modalEventName.textContent = target.getElementsByTagName('em')[0].textContent;
    this.modalDate.textContent = target.getAttribute('data-start') + ' - ' + target.getAttribute('data-end');
    this.modal.setAttribute('data-event', target.getAttribute('data-event'));

    //update event content
    this.loadEventContent(target.getAttribute('data-content'));

    Util.addClass(this.modal, 'cd-schedule-modal--open');

    setTimeout(function () {
        //fixes a flash when an event is selected - desktop version only
        Util.addClass(target.closest('li'), 'cd-schedule__event--selected');
    }, 10);

    if (mq === 'mobile') {
        self.modal.addEventListener('transitionend', function cb() {
            self.animating = false;
            self.modal.removeEventListener('transitionend', cb);
        });
    } else {
        let eventPosition = target.getBoundingClientRect(),
            eventTop = eventPosition.top,
            eventLeft = eventPosition.left,
            eventHeight = target.offsetHeight,
            eventWidth = target.offsetWidth;

        let windowWidth = window.innerWidth,
            windowHeight = window.innerHeight;

        let modalWidth = (windowWidth * .8 > self.modalMaxWidth) ? self.modalMaxWidth : windowWidth * .8,
            modalHeight = (windowHeight * .8 > self.modalMaxHeight) ? self.modalMaxHeight : windowHeight * .8;

        let modalTranslateX = parseInt((windowWidth - modalWidth) / 2 - eventLeft),
            modalTranslateY = parseInt((windowHeight - modalHeight) / 2 - eventTop);

        let HeaderBgScaleY = modalHeight / eventHeight,
            BodyBgScaleX = (modalWidth - eventWidth);

        //change modal height/width and translate it
        self.modal.setAttribute('style', 'top:' + eventTop + 'px;left:' + eventLeft + 'px;height:' + modalHeight + 'px;width:' + modalWidth + 'px;transform: translateY(' + modalTranslateY + 'px) translateX(' + modalTranslateX + 'px)');
        //set modalHeader width
        self.modalHeader.setAttribute('style', 'width:' + eventWidth + 'px');
        //set modalBody left margin
        self.modalBody.setAttribute('style', 'margin-left:' + eventWidth + 'px');
        //change modalBodyBg height/width ans scale it
        self.modalBodyBg.setAttribute('style', 'height:' + eventHeight + 'px; width: 1px; transform: scaleY(' + HeaderBgScaleY + ') scaleX(' + BodyBgScaleX + ')');
        //change modal modalHeaderBg height/width and scale it
        self.modalHeaderBg.setAttribute('style', 'height: ' + eventHeight + 'px; width: ' + eventWidth + 'px; transform: scaleY(' + HeaderBgScaleY + ')');

        self.modalHeaderBg.addEventListener('transitionend', function cb() {
            //wait for the  end of the modalHeaderBg transformation and show the modal content
            self.animating = false;
            Util.addClass(self.modal, 'cd-schedule-modal--animation-completed');
            self.modalHeaderBg.removeEventListener('transitionend', cb);
        });
    }

    //if browser do not support transitions -> no need to wait for the end of it
    this.animationFallback();
};

ScheduleTemplate.prototype.closeModal = function () {
    let self = this;
    let mq = self.mq();

    let item = self.element.getElementsByClassName('cd-schedule__event--selected')[0],
        target = item.getElementsByTagName('a')[0];

    this.animating = true;

    if (mq === 'mobile') {
        Util.removeClass(this.modal, 'cd-schedule-modal--open');
        self.modal.addEventListener('transitionend', function cb() {
            Util.removeClass(self.modal, 'cd-schedule-modal--content-loaded');
            Util.removeClass(item, 'cd-schedule__event--selected');
            self.animating = false;
            self.modal.removeEventListener('transitionend', cb);
        });
    } else {
        let eventPosition = target.getBoundingClientRect(),
            eventTop = eventPosition.top,
            eventLeft = eventPosition.left,
            eventHeight = target.offsetHeight,
            eventWidth = target.offsetWidth;

        let modalStyle = window.getComputedStyle(self.modal),
            modalTop = Number(modalStyle.getPropertyValue('top').replace('px', '')),
            modalLeft = Number(modalStyle.getPropertyValue('left').replace('px', ''));

        let modalTranslateX = eventLeft - modalLeft,
            modalTranslateY = eventTop - modalTop;

        Util.removeClass(this.modal, 'cd-schedule-modal--open cd-schedule-modal--animation-completed');

        //change modal width/height and translate it
        self.modal.style.width = eventWidth + 'px';
        self.modal.style.height = eventHeight + 'px';
        self.modal.style.transform = 'translateX(' + modalTranslateX + 'px) translateY(' + modalTranslateY + 'px)';
        //scale down modalBodyBg element
        self.modalBodyBg.style.transform = 'scaleX(0) scaleY(1)';
        //scale down modalHeaderBg element
        // self.modalHeaderBg.setAttribute('style', 'transform: scaleY(1)');
        self.modalHeaderBg.style.transform = 'scaleY(1)';

        self.modalHeaderBg.addEventListener('transitionend', function cb() {
            //wait for the  end of the modalHeaderBg transformation and reset modal style
            Util.addClass(self.modal, 'cd-schedule-modal--no-transition');
            setTimeout(function () {
                self.modal.removeAttribute('style');
                self.modalBody.removeAttribute('style');
                self.modalHeader.removeAttribute('style');
                self.modalHeaderBg.removeAttribute('style');
                self.modalBodyBg.removeAttribute('style');
            }, 10);
            setTimeout(function () {
                Util.removeClass(self.modal, 'cd-schedule-modal--no-transition');
            }, 20);
            self.animating = false;
            Util.removeClass(self.modal, 'cd-schedule-modal--content-loaded');
            Util.removeClass(item, 'cd-schedule__event--selected');
            self.modalHeaderBg.removeEventListener('transitionend', cb);
        });
    }

    //if browser do not support transitions -> no need to wait for the end of it
    this.animationFallback();
};

ScheduleTemplate.prototype.checkEventModal = function (modalOpen) {
    // this function is used on resize to reset events/modal style
    this.animating = true;
    let self = this;
    let mq = this.mq();
    if (mq === 'mobile') {
        //reset modal style on mobile
        self.modal.removeAttribute('style');
        self.modalBody.removeAttribute('style');
        self.modalHeader.removeAttribute('style');
        self.modalHeaderBg.removeAttribute('style');
        self.modalBodyBg.removeAttribute('style');
        Util.removeClass(self.modal, 'cd-schedule-modal--no-transition');
        self.animating = false;
    } else if (mq === 'desktop' && modalOpen) {
        Util.addClass(self.modal, 'cd-schedule-modal--no-transition cd-schedule-modal--animation-completed');
        let item = self.element.getElementsByClassName('cd-schedule__event--selected')[0],
            target = item.getElementsByTagName('a')[0];

        let eventPosition = target.getBoundingClientRect(),
            eventTop = eventPosition.top,
            eventLeft = eventPosition.left,
            eventHeight = target.offsetHeight,
            eventWidth = target.offsetWidth;

        let windowWidth = window.innerWidth,
            windowHeight = window.innerHeight;

        let modalWidth = (windowWidth * .8 > self.modalMaxWidth) ? self.modalMaxWidth : windowWidth * .8,
            modalHeight = (windowHeight * .8 > self.modalMaxHeight) ? self.modalMaxHeight : windowHeight * .8;

        let HeaderBgScaleY = modalHeight / eventHeight,
            BodyBgScaleX = (modalWidth - eventWidth);


        setTimeout(function () {
            self.modal.setAttribute('style', 'top:' + (windowHeight / 2 - modalHeight / 2) + 'px;left:' + (windowWidth / 2 - modalWidth / 2) + 'px;height:' + modalHeight + 'px;width:' + modalWidth + 'px;transform: translateY(0) translateX(0)');
            //change modal modalBodyBg height/width
            self.modalBodyBg.style.height = modalHeight + 'px';
            self.modalBodyBg.style.transform = 'scaleY(1) scaleX(' + BodyBgScaleX + ')';
            self.modalBodyBg.style.width = '1px';
            //set modalHeader width
            self.modalHeader.setAttribute('style', 'width:' + eventWidth + 'px');
            //set modalBody left margin
            self.modalBody.setAttribute('style', 'margin-left:' + eventWidth + 'px');
            //change modal modalHeaderBg height/width and scale it
            self.modalHeaderBg.setAttribute('style', 'height: ' + eventHeight + 'px;width:' + eventWidth + 'px; transform:scaleY(' + HeaderBgScaleY + ');');
        }, 10);

        setTimeout(function () {
            Util.removeClass(self.modal, 'cd-schedule-modal--no-transition');
            self.animating = false;
        }, 20);

    }
};

ScheduleTemplate.prototype.loadEventContent = function (content) {
    // load the content of an event when user selects it
    let self = this;

    httpRequest = new XMLHttpRequest();
    httpRequest.onreadystatechange = function () {
        if (httpRequest.readyState === XMLHttpRequest.DONE) {
            if (httpRequest.status === 200) {
                self.modal.getElementsByClassName('cd-schedule-modal__event-info')[0].innerHTML = self.getEventContent(httpRequest.responseText);
                Util.addClass(self.modal, 'cd-schedule-modal--content-loaded');
            }
        }
    };
    httpRequest.open('GET', content + '.html');
    httpRequest.send();
};

ScheduleTemplate.prototype.getEventContent = function (string) {
    // reset the loaded event content so that it can be inserted in the modal
    let div = document.createElement('div');
    div.innerHTML = string.trim();
    return div.getElementsByClassName('cd-schedule-modal__event-info')[0].innerHTML;
};

ScheduleTemplate.prototype.animationFallback = function () {
    if (!this.supportAnimation) { // fallback for browsers not supporting transitions
        let event = new CustomEvent('transitionend');
        self.modal.dispatchEvent(event);
        self.modalHeaderBg.dispatchEvent(event);
    }
};

ScheduleTemplate.prototype.mq = function () {
    //get MQ value ('desktop' or 'mobile')
    let self = this;
    return window.getComputedStyle(this.element, '::before').getPropertyValue('content').replace(/'|"/g, "");
};

function getScheduleTimestamp(time) {
    //accepts hh:mm format - convert hh:mm to timestamp
    time = time.replace(/ /g, '');
    let timeArray = time.split(':');
    return parseInt(timeArray[0]) * 60 + parseInt(timeArray[1]);
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

// init general binds
$(document).ready(function () {
    $('#course_input').on("input", function () {
        courses_autocomplete(this.value);
    });

    const item_html = hb_templates['schedule-legend']();
    $('#schedule-legend').popover({
        'content': item_html,
        'placement': 'bottom',
        'html': true,
        'trigger': 'hover',
    });
});

/**
 * Autocompletes the user search.
 */
function courses_autocomplete(search_val) {
    let container = $('#search_results');

    if (search_val.length < 2) {
        container.html('');
        return;
    }

    const loader_html = hb_templates['schedule-loader']();
    container.html(loader_html);

    schedule.getCoursesFromServer(search_val, autocompleteSuccessCb, autocompleteErrorCb);
}

function autocompleteSuccessCb(response) {
    let container = $('#search_results');

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
                addCourse(value);
                list.html('');
                $('#course_input').val('');
            });
        }
    });
}

function autocompleteErrorCb() {
    let container = $('#search_results');

    container.html('Error, try again.');
}

/**
 * Adds a course to the course list.
 */
function addCourse(course) {
    if (schedule.hasCourse(course)) {
        return;
    }

    schedule.addCourse(course, addCourseSuccessCb, addCourseErrorCb, false);
}

function addCourseSuccessCb(response) {
    const course = response.course;
    const groups = response.groups;

    if (groups.length === 0) {
        console.log('Error: No groups for course.');
        return;
    }

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
    displayCourseGroups(groupsContainer, course_number, groups, response.auto_loaded);
}

function addCourseErrorCb() {
    console.log('Error in addCourse ajax.');
}

/**
 * Displays the groups of the given course.
 */
function displayCourseGroups(container, courseNumber, groups, autoLoaded) {
    let class_types = schedule.getClassTypes(courseNumber);
    for (let i = 0; i < class_types.length; i++) {
        let cur_class_type = class_types[i];
        let group_header = hb_templates['schedule-course-item-group-header']({
            'class_type': cur_class_type,
            'class_type_name': classTypeToName(cur_class_type)
        });
        container.append(group_header);

        let group_list = container.find('.course_group_' + cur_class_type);
        let passed_first = false;
        groups.forEach((group) => {
            if (group['class_type'] === cur_class_type) {
                passed_first = displayGroup(group, cur_class_type, passed_first, courseNumber, group_list, autoLoaded);
            }
        });
    }
}

function displayGroup(group, cur_class_type, passed_first, courseNumber, group_list, autoLoaded) {
    let css_class = '';

    if (autoLoaded) {
        // check in saved groups if its a selected group
        if (schedule.choicesHasGroup(group['id'])) {
            updateScheduleDisplay(courseNumber, group);
            css_class = 'active';
        }
    } else {
        // Display first of each class type in the schedule
        if (passed_first === false) {
            css_class = 'active';
            schedule.cookieStoreGroup(group["id"]);
            schedule.userStoreGroup(group["id"]);
            updateScheduleDisplay(courseNumber, group);
        }
    }

    let group_item = hb_templates['schedule-course-item-group-item']({
        'css_class': css_class,
        'course_number': courseNumber,
        'group_id': group['id'],
        'mark': group['mark'],
        'semester': semesterToName(group['semester']),
        'teachers': schedule.getGroupTeachers(group)
    });
    group_list.append(group_item);

    // Add click functionality
    $('#list_group_' + courseNumber + '_' + group['id']).click(function (e) {
        if (!$(this).hasClass('active')) {
            $(this).siblings().removeClass('active');
            $(this).addClass('active');
            updateScheduleDisplay(courseNumber, group);
            schedule.cookieStoreGroup(group["id"]);
            schedule.userStoreGroup(group["id"]);
        }
    });

    return true;
}

function getNiceTime(time) {
    const lastIndex = time.lastIndexOf(":");
    return time.substring(0, lastIndex);
}

/**
 * Adds a class to the time table.
 * @param courseNumber The course number.
 * @param courseName The course name.
 * @param group The group object of the course.
 * @param courseClass the course class object.
 */
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

/**
 * Gets all the groups of the specified course, except the given group, that
 * match the class_type of the given group.
 * This function is used to get these groups to (potentially) delete them from
 * the time table when updating it with the given group.
 * @param courseNumber The course number of the group.
 * @param group The group to exclude from returning.
 * @returns {[]} All the groups
 */
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
        schedule.cookieDeleteGroup(groupsToRemove[i]);
        $('[data-group=class_item_' + groupsToRemove[i] + ']').remove();
    }
}

function updateScheduleDisplay(courseNumber, group) {
    const courseName = schedule.getCourseNameByNumber(courseNumber);
    let groupsToRemove = getGroupsToRemove(courseNumber, group);
    removeCourseGroups(groupsToRemove);
    $.each(group['classes'], function (index, courseClass) {
        addClassToDisplay(courseNumber, courseName, group, courseClass);
    });
}

/**
 * Toggles collapse of course groups in course list.
 */
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