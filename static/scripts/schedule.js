
// Schedule Template - by CodyHouse.co
function ScheduleTemplate( element ) {
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

ScheduleTemplate.prototype.initSchedule = function() {
	this.scheduleReset();
	this.initEvents();
};

ScheduleTemplate.prototype.scheduleReset = function() {
	// according to the mq value, init the style of the template
	var mq = this.mq(),
		loaded = Util.hasClass(this.element, 'js-schedule-loaded'),
		modalOpen = Util.hasClass(this.modal, 'cd-schedule-modal--open');
	if( mq == 'desktop' && !loaded ) {
		Util.addClass(this.element, 'js-schedule-loaded');
		this.placeEvents();
		modalOpen && this.checkEventModal(modalOpen);
	} else if( mq == 'mobile' && loaded) {
		//in this case you are on a mobile version (first load or resize from desktop)
		Util.removeClass(this.element, 'cd-schedule--loading js-schedule-loaded');
		this.resetEventsStyle();
		modalOpen && this.checkEventModal();
	} else if( mq == 'desktop' && modalOpen ) {
		//on a mobile version with modal open - need to resize/move modal window
		this.checkEventModal(modalOpen);
		Util.removeClass(this.element, 'cd-schedule--loading');
	} else {
		Util.removeClass(this.element, 'cd-schedule--loading');
	}
};

ScheduleTemplate.prototype.resetEventsStyle = function() {
	// remove js style applied to the single events
	for(var i = 0; i < this.singleEvents.length; i++) {
		this.singleEvents[i].removeAttribute('style');
	}
};

/**
 * Sets the position of the events overlapping the given event (including the
 * given event).
 */
ScheduleTemplate.prototype.setEventPosition = function(cur_event, width) {
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
ScheduleTemplate.prototype.getNumOverlaps = function(cur_event) {
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

ScheduleTemplate.prototype.placeEvents = function() {
	// on big devices - place events in the template according to their time/day
	var self = this,
		slotHeight = this.topInfoElement.offsetHeight;
	for(var i = 0; i < this.singleEvents.length; i++) {
		var anchor = this.singleEvents[i].getElementsByTagName('a')[0];
		var start = getScheduleTimestamp(anchor.getAttribute('data-start')),
			duration = getScheduleTimestamp(anchor.getAttribute('data-end')) - start;

		var eventTop = slotHeight*(start - self.timelineStart)/self.timelineUnitDuration,
			eventHeight = slotHeight*duration/self.timelineUnitDuration;

		this.singleEvents[i].setAttribute('style', 'top: '+(eventTop-1)+'px; height: '+(eventHeight +1)+'px');
		if (!$(this.singleEvents[i]).hasClass('adjusted')) {
			let numOverlaps = this.getNumOverlaps(this.singleEvents[i]);
			this.setEventPosition(this.singleEvents[i], 100 / numOverlaps);
		}
	}

	Util.removeClass(this.element, 'cd-schedule--loading');
};

ScheduleTemplate.prototype.initEvents = function() {
	var self = this;
	for(var i = 0; i < this.singleEvents.length; i++) {
		// open modal when user selects an event
		this.singleEvents[i].addEventListener('click', function(event){
			event.preventDefault();
			if(!self.animating) self.openModal(this.getElementsByTagName('a')[0]);
		});
	}
	//close modal window
	this.modalClose.addEventListener('click', function(event){
		event.preventDefault();
		if( !self.animating ) self.closeModal();
	});
	this.coverLayer.addEventListener('click', function(event){
		event.preventDefault();
		if( !self.animating ) self.closeModal();
	});
};

ScheduleTemplate.prototype.addEvent = function() {
	this.singleEvents = this.element.getElementsByClassName('cd-schedule__event');
	this.placeEvents();
	this.initEvents();
};

ScheduleTemplate.prototype.openModal = function(target) {
	var self = this;
	var mq = self.mq();
	this.animating = true;

	//update event name and time
	this.modalEventName.textContent = target.getElementsByTagName('em')[0].textContent;
	this.modalDate.textContent = target.getAttribute('data-start')+' - '+target.getAttribute('data-end');
	this.modal.setAttribute('data-event', target.getAttribute('data-event'));

	//update event content
	this.loadEventContent(target.getAttribute('data-content'));

	Util.addClass(this.modal, 'cd-schedule-modal--open');

	setTimeout(function(){
		//fixes a flash when an event is selected - desktop version only
		Util.addClass(target.closest('li'), 'cd-schedule__event--selected');
	}, 10);

	if( mq == 'mobile' ) {
		self.modal.addEventListener('transitionend', function cb(){
			self.animating = false;
			self.modal.removeEventListener('transitionend', cb);
		});
	} else {
		var eventPosition = target.getBoundingClientRect(),
			eventTop = eventPosition.top,
			eventLeft = eventPosition.left,
			eventHeight = target.offsetHeight,
			eventWidth = target.offsetWidth;

		var windowWidth = window.innerWidth,
			windowHeight = window.innerHeight;

		var modalWidth = ( windowWidth*.8 > self.modalMaxWidth ) ? self.modalMaxWidth : windowWidth*.8,
			modalHeight = ( windowHeight*.8 > self.modalMaxHeight ) ? self.modalMaxHeight : windowHeight*.8;

		var modalTranslateX = parseInt((windowWidth - modalWidth)/2 - eventLeft),
			modalTranslateY = parseInt((windowHeight - modalHeight)/2 - eventTop);

		var HeaderBgScaleY = modalHeight/eventHeight,
			BodyBgScaleX = (modalWidth - eventWidth);

		//change modal height/width and translate it
		self.modal.setAttribute('style', 'top:'+eventTop+'px;left:'+eventLeft+'px;height:'+modalHeight+'px;width:'+modalWidth+'px;transform: translateY('+modalTranslateY+'px) translateX('+modalTranslateX+'px)');
		//set modalHeader width
		self.modalHeader.setAttribute('style', 'width:'+eventWidth+'px');
		//set modalBody left margin
		self.modalBody.setAttribute('style', 'margin-left:'+eventWidth+'px');
		//change modalBodyBg height/width ans scale it
		self.modalBodyBg.setAttribute('style', 'height:'+eventHeight+'px; width: 1px; transform: scaleY('+HeaderBgScaleY+') scaleX('+BodyBgScaleX+')');
		//change modal modalHeaderBg height/width and scale it
		self.modalHeaderBg.setAttribute('style', 'height: '+eventHeight+'px; width: '+eventWidth+'px; transform: scaleY('+HeaderBgScaleY+')');

		self.modalHeaderBg.addEventListener('transitionend', function cb(){
			//wait for the  end of the modalHeaderBg transformation and show the modal content
			self.animating = false;
			Util.addClass(self.modal, 'cd-schedule-modal--animation-completed');
			self.modalHeaderBg.removeEventListener('transitionend', cb);
		});
	}

	//if browser do not support transitions -> no need to wait for the end of it
	this.animationFallback();
};

ScheduleTemplate.prototype.closeModal = function() {
	var self = this;
	var mq = self.mq();

	var item = self.element.getElementsByClassName('cd-schedule__event--selected')[0],
		target = item.getElementsByTagName('a')[0];

	this.animating = true;

	if( mq == 'mobile' ) {
		Util.removeClass(this.modal, 'cd-schedule-modal--open');
		self.modal.addEventListener('transitionend', function cb(){
			Util.removeClass(self.modal, 'cd-schedule-modal--content-loaded');
			Util.removeClass(item, 'cd-schedule__event--selected');
			self.animating = false;
			self.modal.removeEventListener('transitionend', cb);
		});
	} else {
		var eventPosition = target.getBoundingClientRect(),
			eventTop = eventPosition.top,
			eventLeft = eventPosition.left,
			eventHeight = target.offsetHeight,
			eventWidth = target.offsetWidth;

		var modalStyle = window.getComputedStyle(self.modal),
			modalTop = Number(modalStyle.getPropertyValue('top').replace('px', '')),
			modalLeft = Number(modalStyle.getPropertyValue('left').replace('px', ''));

		var modalTranslateX = eventLeft - modalLeft,
			modalTranslateY = eventTop - modalTop;

		Util.removeClass(this.modal, 'cd-schedule-modal--open cd-schedule-modal--animation-completed');

		//change modal width/height and translate it
		self.modal.style.width = eventWidth+'px';self.modal.style.height = eventHeight+'px';self.modal.style.transform = 'translateX('+modalTranslateX+'px) translateY('+modalTranslateY+'px)';
		//scale down modalBodyBg element
		self.modalBodyBg.style.transform = 'scaleX(0) scaleY(1)';
		//scale down modalHeaderBg element
		// self.modalHeaderBg.setAttribute('style', 'transform: scaleY(1)');
		self.modalHeaderBg.style.transform = 'scaleY(1)';

		self.modalHeaderBg.addEventListener('transitionend', function cb(){
			//wait for the  end of the modalHeaderBg transformation and reset modal style
			Util.addClass(self.modal, 'cd-schedule-modal--no-transition');
			setTimeout(function(){
				self.modal.removeAttribute('style');
				self.modalBody.removeAttribute('style');
				self.modalHeader.removeAttribute('style');
				self.modalHeaderBg.removeAttribute('style');
				self.modalBodyBg.removeAttribute('style');
			}, 10);
			setTimeout(function(){
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

ScheduleTemplate.prototype.checkEventModal = function(modalOpen) {
	// this function is used on resize to reset events/modal style
	this.animating = true;
	var self = this;
	var mq = this.mq();
	if( mq == 'mobile' ) {
		//reset modal style on mobile
		self.modal.removeAttribute('style');
		self.modalBody.removeAttribute('style');
		self.modalHeader.removeAttribute('style');
		self.modalHeaderBg.removeAttribute('style');
		self.modalBodyBg.removeAttribute('style');
		Util.removeClass(self.modal, 'cd-schedule-modal--no-transition');
		self.animating = false;
	} else if( mq == 'desktop' && modalOpen) {
		Util.addClass(self.modal, 'cd-schedule-modal--no-transition cd-schedule-modal--animation-completed');
		var item = self.element.getElementsByClassName('cd-schedule__event--selected')[0],
			target = item.getElementsByTagName('a')[0];

		var eventPosition = target.getBoundingClientRect(),
			eventTop = eventPosition.top,
			eventLeft = eventPosition.left,
			eventHeight = target.offsetHeight,
			eventWidth = target.offsetWidth;

		var windowWidth = window.innerWidth,
			windowHeight = window.innerHeight;

		var modalWidth = ( windowWidth*.8 > self.modalMaxWidth ) ? self.modalMaxWidth : windowWidth*.8,
			modalHeight = ( windowHeight*.8 > self.modalMaxHeight ) ? self.modalMaxHeight : windowHeight*.8;

		var HeaderBgScaleY = modalHeight/eventHeight,
			BodyBgScaleX = (modalWidth - eventWidth);


		setTimeout(function(){
			self.modal.setAttribute('style', 'top:'+(windowHeight/2 - modalHeight/2)+'px;left:'+(windowWidth/2 - modalWidth/2)+'px;height:'+modalHeight+'px;width:'+modalWidth+'px;transform: translateY(0) translateX(0)');
			//change modal modalBodyBg height/width
			self.modalBodyBg.style.height = modalHeight+'px';self.modalBodyBg.style.transform = 'scaleY(1) scaleX('+BodyBgScaleX+')';self.modalBodyBg.style.width = '1px';
			//set modalHeader width
			self.modalHeader.setAttribute('style', 'width:'+eventWidth+'px');
			//set modalBody left margin
			self.modalBody.setAttribute('style', 'margin-left:'+eventWidth+'px');
			//change modal modalHeaderBg height/width and scale it
			self.modalHeaderBg.setAttribute('style', 'height: '+eventHeight+'px;width:'+eventWidth+'px; transform:scaleY('+HeaderBgScaleY+');');
		}, 10);

		setTimeout(function(){
			Util.removeClass(self.modal, 'cd-schedule-modal--no-transition');
			self.animating = false;
		}, 20);

	}
};

ScheduleTemplate.prototype.loadEventContent = function(content) {
	// load the content of an event when user selects it
	var self = this;

	httpRequest = new XMLHttpRequest();
	httpRequest.onreadystatechange = function() {
		if (httpRequest.readyState === XMLHttpRequest.DONE) {
	  if (httpRequest.status === 200) {
		self.modal.getElementsByClassName('cd-schedule-modal__event-info')[0].innerHTML = self.getEventContent(httpRequest.responseText);
		Util.addClass(self.modal, 'cd-schedule-modal--content-loaded');
	  }
	}
	};
	httpRequest.open('GET', content+'.html');
httpRequest.send();
};

ScheduleTemplate.prototype.getEventContent = function(string) {
	// reset the loaded event content so that it can be inserted in the modal
	var div = document.createElement('div');
	div.innerHTML = string.trim();
	return div.getElementsByClassName('cd-schedule-modal__event-info')[0].innerHTML;
};

ScheduleTemplate.prototype.animationFallback = function() {
	if( !this.supportAnimation ) { // fallback for browsers not supporting transitions
		var event = new CustomEvent('transitionend');
		self.modal.dispatchEvent(event);
		self.modalHeaderBg.dispatchEvent(event);
	}
};

ScheduleTemplate.prototype.mq = function(){
	//get MQ value ('desktop' or 'mobile')
	var self = this;
	return window.getComputedStyle(this.element, '::before').getPropertyValue('content').replace(/'|"/g, "");
};

function getScheduleTimestamp(time) {
	//accepts hh:mm format - convert hh:mm to timestamp
	time = time.replace(/ /g,'');
	var timeArray = time.split(':');
	var timeStamp = parseInt(timeArray[0])*60 + parseInt(timeArray[1]);
	return timeStamp;
};





$(document).ready(function(){
    $('#course_input').keypress(function(e) {
        if(e.keyCode==13) {
            e.preventDefault();
            $('#search_btn').click();
        }
    });
});

class Schedule {
    constructor() {
        this.courses = {};
    }

    addCourse(course, classes) {
        let course_tuple = {
            'course': course,
            'classes': classes
        };
        this.courses[course['course_number']] = course_tuple;
    }

    hasCourse(course) {
        return course['course_number'] in this.courses;
    }

    getCourseHeNameByNumber(course_number) {
        return this.courses[course_number]['course']['name_he'];
    }

    getCourseClassesByNumber(course_number) {
        return this.courses[course_number]['classes'];
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

        let classes = this.courses[course_number]['classes'];
        for (let i = 0; i < classes.length; i++) {
            let cur_type = classes[i]['class_type'];
            if (!class_types.includes(cur_type)) {
                class_types.push(cur_type);
            }
        }

        return class_types;
    }

    removeCourse(course_number) {
        let course_classes = this.courses[course_number]['classes'];
        for (let i = 0; i < course_classes.length; i++) {
            let serial = course_classes[i]['serial_number'];
            $('[data-group=class_item_' + course_number + '_' + serial + ']').remove();
        }
        delete this.courses[course_number];
    }
}
let schedule = new Schedule();

/**
 * Converts the courses returned from server to convenient objects.
 */
function toCourseObj(courses) {
    let ret = [];
    for (let i = 0; i < courses.length; i++) {
        ret[i] = {
            course_number: courses[i]['fields']['course_number'],
            name_he: courses[i]['fields']['name_he'],
            name_en: courses[i]['fields']['name_en'],
            year: courses[i]['fields']['year'],
            semester: courses[i]['fields']['semester'],
            nz: courses[i]['fields']['nz']
        };
    }

    return ret;
}

/**
 * Converts the classes returned from server to convenient objects.
 */
function toClassObj(classes) {
    let delim = ';';
    let ret = [];
    for (let i = 0; i < classes.length; i++) {
        let lecturers = classes[i]['fields']['lecturer'].split(delim);
        let semesters = classes[i]['fields']['semester'].split(delim);
        let days = classes[i]['fields']['day'].split(delim);
        let hours = classes[i]['fields']['hour'].split(delim);
        let halls = classes[i]['fields']['hall'].split(delim);

        ret[i] = {
            course_id: classes[i]['fields']['course_id'],
            course_number: classes[i]['fields']['course_number'],
            serial_number: classes[i]['fields']['serial_number'],
            lecturer: lecturers,
            class_type: classes[i]['fields']['class_type'],
            group: classes[i]['fields']['group'],
            semester: semesters,
            day: days,
            hour: hours,
            hall: halls
        };
    }

    return ret;
}

/**
 * Displays the results of course search.
 */
function display_course_results(list, course, csrf) {
    let course_number = course['course_number'];
    let course_name_he = course['name_he'];
    list.append(
        '<li>' +
            '<a href="#" id="add_course_' + course_number + '">' + course_number +
            ' - ' + course_name_he + '</a>' +
        '</li>'
    );
    $('#add_course_' + course_number).click(function (e) {
        e.preventDefault();
        add_course(course, csrf);
        list.html('');
        $('#course_input').val('');
    });
}

/**
 * Autocompletes the user search.
 */
function courses_autocomplete(search_val, csrf) {
    let container = $('#search_results');

    if (search_val.length < 2) {
        container.html('');
        return;
    }

    $.ajax({
        method: 'POST',
        url: './',
        data: {
            'csrfmiddlewaretoken': csrf,
            'search_val': search_val
        },
        success: function (response) {
            if (response.status !== 'success') {
                container.html('Error, try again.');
                return;
            }

            container.html('<ul></ul>');
            let courses = JSON.parse(response.course);
            if (courses.length === 0) {
                container.html();
                return;
            }

            courses = toCourseObj(courses);
            $.each(courses, function(index, value) {
                if (!schedule.hasCourse(value)) {
                    display_course_results(container.children('ul'), value, csrf);
                }
            });
        },
        error: function () {
            container.html('Error, try again.');
        }
    });
}

/**
 * Search for a specific course number.
 */
function search_course(csrf) {
    let search_val = $('#course_input').val();
    let container = $('#search_results');

    if (search_val.length < 2) {
        return;
    }

    container.html(
        '<div class="text-center">' +
            '<div class="spinner-grow text-primary" role="status"></div>' +
        '</div>'
    );
    $.ajax({
        method: 'POST',
        url: './search',
        data: {
            csrfmiddlewaretoken: csrf,
            'search_val': search_val
        },
        success: function (response) {
            container.html('<ul></ul>');
            if (response.status === 'error') {
                if (response.msg === 'Course not found') {
                    container.html('לא נמצאו קורסים');
                    return;
                }
            }

            let courses = JSON.parse(response.course);
            courses = toCourseObj(courses);
            display_course_results(container.children('ul'), courses[0], csrf);
        },
        error: function () {
            container.html('Error, try again.');
        }
    });
}

/**
 * Adds a course to the course list.
 */
function add_course(course, csrf) {
    if (schedule.hasCourse(course)) {
        return;
    }

    $.ajax({
        method: 'POST',
        url: './fetch_classes',
        data: {
            csrfmiddlewaretoken: csrf,
            'search_val': course['course_number']
        },
        success: function (response) {
            let classes = JSON.parse(response.classes);
            if (classes.length === 0) {
                // TODO show to the user error message?
                return;
            }

            classes = toClassObj(classes);
            schedule.addCourse(course, classes);
            let course_number = course['course_number'];
            let course_name_he = course['name_he'];
            let course_list_container = $('#my_courses_list');
            course_list_container.append(
                '<li id="course_item_' + course_number + '">' +
                    '<div class="title_wrapper clear">' +
                        '<div class="course_name">' + course_name_he + '</div>' +
                        '<div class="remove_button" id="del_btn_' + course_number + '">' +
                            '<svg class="bi bi-trash" width="1em" height="1em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">\n' +
                            '  <path d="M5.5 5.5A.5.5 0 016 6v6a.5.5 0 01-1 0V6a.5.5 0 01.5-.5zm2.5 0a.5.5 0 01.5.5v6a.5.5 0 01-1 0V6a.5.5 0 01.5-.5zm3 .5a.5.5 0 00-1 0v6a.5.5 0 001 0V6z"/>\n' +
                            '  <path fill-rule="evenodd" d="M14.5 3a1 1 0 01-1 1H13v9a2 2 0 01-2 2H5a2 2 0 01-2-2V4h-.5a1 1 0 01-1-1V2a1 1 0 011-1H6a1 1 0 011-1h2a1 1 0 011 1h3.5a1 1 0 011 1v1zM4.118 4L4 4.059V13a1 1 0 001 1h6a1 1 0 001-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z" clip-rule="evenodd"/>\n' +
                            '</svg>' +
                        '</div>' +
                    '</div>' +
                    '<div id="course_classes_' + course_number + '" class="course_classes_wrapper"></div>' +
                '</li>'
            );
            $('#del_btn_' + course_number).click(function () {
                schedule.removeCourse(course_number);
                $('#course_item_' + course_number).remove();
            });

            let classes_container = $('#course_classes_' + course_number);
            display_course_classes(classes_container, course_number, classes);


        },
        error: function () {
            alert('failed');
        }
    });
}

/**
 * Displays the classes of the given course.
 */
function display_course_classes(container, course_number, classes) {
    let class_types = schedule.getClassTypes(course_number);
    // TODO map class types to strings
    for (let i = 0; i < class_types.length; i++) {
        let cur_class_type = class_types[i];
        container.append(
            '<ul class="course_class_' + i + '">' +
                '<li class="course_class_title">' + cur_class_type + '</li>' +
            '</ul>'
        );
        let class_list = container.find('.course_class_' + i);
        let passed_first = false;
        for (let j = 0; j < classes.length; j++) {
            if (classes[j]['class_type'] === cur_class_type) {
                let cur_class = classes[j];
                let css_class = (passed_first === false) ? 'active' : '';
                class_list.append(
                    '<li class="' + css_class + '" id="list_class_' + classes[j]['course_number'] + '_' + classes[j]['serial_number'] + '">' +
                        cur_class['group'] + ' - ' + cur_class['lecturer'] +
                    '</li>'
                );
                $('#list_class_' + classes[j]['course_number'] + '_' + classes[j]['serial_number']).click(function (e) {
                    if (!$(this).hasClass('active')) {
                        $(this).siblings().removeClass('active');
                        $(this).addClass('active');
                        updateScheduleDisplay(classes[j]);
                    }
                });
                if (passed_first === false) {
                    updateScheduleDisplay(classes[j]);
                }
                passed_first = true;
            }
        }
    }
}

// time table UI
var scheduleTemplate = document.getElementsByClassName('js-cd-schedule'),
    scheduleTemplateArray = [],
    resizing = false;
if( scheduleTemplate.length > 0 ) { // init ScheduleTemplate objects
    for( var i = 0; i < scheduleTemplate.length; i++) {
        (function(i){
            scheduleTemplateArray.push(new ScheduleTemplate(scheduleTemplate[i]));
        })(i);
    }

    window.addEventListener('resize', function(event) {
        // on resize - update events position and modal position (if open)
        if( !resizing ) {
            resizing = true;
            (!window.requestAnimationFrame) ? setTimeout(checkResize, 250) : window.requestAnimationFrame(checkResize);
        }
    });

    window.addEventListener('keyup', function(event){
        // close event modal when pressing escape key
        if( event.keyCode && event.keyCode == 27 || event.key && event.key.toLowerCase() == 'escape' ) {
            for(var i = 0; i < scheduleTemplateArray.length; i++) {
                scheduleTemplateArray[i].closeModal();
            }
        }
    });

    function checkResize(){
        for(var i = 0; i < scheduleTemplateArray.length; i++) {
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

function getClassSemester(cls) {
    ret = [];

    for (let i = 0; i < cls['semester'].length; i++) {
        ret.push(cls['semester'][i]);
    }

    return ret;
}

function getClassDay(cls) {
    ret = [];

    for (let i = 0; i < cls['day'].length; i++) {
        let day;
        switch (cls['day'][i]) {
            case "יום א'":
                day = 1;
                break;
            case "יום ב'":
                day = 2;
                break;
            case "יום ג'":
                day = 3;
                break;
            case "יום ד'":
                day = 4;
                break;
            case "יום ה'":
                day = 5;
                break;
            default:
                day = 1; // TODO maybe return error
        }
        ret.push(day);
    }

    return ret;
}

function getClassHour(cls) {
    ret = [];

    for (let i = 0; i < cls['hour'].length; i++) {
        ret.push(cls['hour'][i]);
    }

    return ret;
}

function getClassHall(cls) {
    ret = [];

    for (let i = 0; i < cls['hall'].length; i++) {
        ret.push(cls['hall'][i]);
    }

    return ret;
}

function updateScheduleDisplay(add_class) {
    // TODO decide to which schedule depending on the semester

    let course_number = add_class['course_number'];
    let course_mame_he = schedule.getCourseHeNameByNumber(course_number);
    let serial_number = add_class['serial_number'];
    let lecturer = getClassLecturer(add_class);
    let semester = getClassSemester(add_class);
    let day = getClassDay(add_class);
    let hour = getClassHour(add_class);
    let hall = getClassHall(add_class);

    // gather classes to remove
    let all_classes = schedule.getCourseClassesByNumber(course_number);
    let to_remove = []; // classes of same group that we potentially need to remove
    for (let i = 0; i < all_classes.length; i++) {
        if (all_classes[i]['class_type'] === add_class['class_type']) {
            if (all_classes[i]['serial_number'] !== add_class['serial_number']) {
                to_remove.push(all_classes[i]['serial_number']);
            }
        }
    }

    // remove gathered classes
    for (let i = 0; i < to_remove.length; i++) {
        $('[data-group=class_item_' + course_number + '_' + to_remove[i] + ']').remove();
    }

    for (let i = 0; i < hour.length; i++) {
        let li_id = 'class_item_' + course_number + '_' + serial_number + '_' + i;
        let li_data_group = 'class_item_' + course_number + '_' + serial_number;
        let start_end_hour = hour[i].split('-');
        $('#day_' + day[i] + '_a').append(
            '<li class="cd-schedule__event" id="' + li_id + '" data-group="' + li_data_group + '">' +
            '   <a data-start="' + start_end_hour[1] + '" data-end="' + start_end_hour[0] +
                '"  data-content="event-rowing-workout" data-event="event-4" href="#0">' +
            '       <em class="cd-schedule__name">' + course_number + ' - ' + course_mame_he + '</em>' +
            '   </a>' +
            '</li>'
        );
    }

    for(let i = 0; i < scheduleTemplateArray.length; i++) {
        scheduleTemplateArray[i].addEvent();
    }
}