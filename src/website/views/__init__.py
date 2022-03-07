from flask import render_template, flash


def render_default(page, flash_message, _form):
    """ Renders 'default' version of page, i.e. no response """
    flash(flash_message, 'error')
    return render_template(page, grade_results=[], form=_form)

