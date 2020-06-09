def get_model():
    from course_comments.models import CourseComment

    return CourseComment


def get_form():
    from course_comments.forms import CourseCommentForm

    return CourseCommentForm
