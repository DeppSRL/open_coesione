Rationale
=========
*Idioticon* (see http://en.wiktionary.org/wiki/idioticon for the meaning),
is a module that allows to disseminate html templates with clickable question marks (idioticons).

Whenever a user clicks on an idioticon, a popover appears, showing some content.
The content can be easily managed by administrators in the backend.

Prerequisites
=============
django-idioticon is based on bootstrap. Both version 2 and 3 are supported,
although you need to vary the installation.

Bootstrap's CSS and Javascript need to be correctly loaded in the html pages
where the popovers appear.

Installation
============
Install, or upgrade django-tinymce with::

    pip install --upgrade django-tinymce

Install the idioticon module, by downloading it and copying it as a django app, within your project.

Add both ``tinymce`` and ``idioticon`` to the installed apps.

Execute ``syncdb`` or ``python manage.py migrate idioticon`` to generate the table in the db,
where the idioticons' content will be stored.


Usage
=====
Go to the admin interface, in the *Idioticon* section and add some content (name, title, definition).
Idioticons are referenced in the HTMl template by their slugs, which therefore cannot be null or blank.

Choose an HTML template where you want to add an idioticon.
Add this snippet of code::

    {% popover_info 'home' %}

Right where you want the question mark to appear.

The popover_info templatetags library (one template tag, actually), needs to be included
in all the templates where you want idioticons to appear. This can be done with::

    {% load popover_info %}


Load the popover css file, by adding this line in the base html template::

    <link href="{{ STATIC_URL }}css/popover.css" rel="stylesheet">

Check your bootstrap's version and add this lines to the base html template, if using Bootstrap 2::

    <link href="{{ STATIC_URL }}css/popover.css" rel="stylesheet">
    <script type="text/javascript" src="{{ STATIC_URL }}js/bootstrapx-clickover.js"></script>


Enable the popovers, by adding a javascript ``$(document).ready`` section
in your base template javascript::

    !function($){
        $(document).ready(function(){
            // enable popovers (bootstrap 3)
            $('a[rel=info-popover]').popover();

            // enable clickovers (bootstrap 2)
            $('a[rel=info-popover]').clickover();
        });
    }(jQuery);


