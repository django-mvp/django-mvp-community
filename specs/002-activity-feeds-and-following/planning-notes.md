# Planning notes

The feature depends only on django-activity-stream. Sam, 2026-11-05: "This particular depends only on django-activity-stream I believe."

The project feature document that proposed this extra builds it on django-activity-stream "after a trial install on Django 6". This package supports Django 5.2, 6.0 and 6.1.

Sam, 2026-11-05, approving the specification: "Keep in mind that we are providing UI and templates for existing code. We AVOID writing custom code where possible. This follows Django-mvp philosophy and what happened in the notifications feature spec where custom code was rejected. If absolutely necessary, template tags are allowed but from memory Django-activity-feed already provides its own."
