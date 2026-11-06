# Planning notes

Sam, 2026-11-06, on the specification's reading: "considering this touches on every package that send emails, I'm wondering whether a large portion of it should be placed in Django-mvp core?" Agreed answer: the feature stays here. django-post-office plugs in as the project's email backend, so no package that sends email needs it as a dependency, and django-mvp core keeps only the email layout it already has. django-mvp's email page gains one paragraph saying that queueing and a delivery log come with this package's mail extra.

The project feature document that proposed this extra lists django-post-office, django-anymail (Scaleway) and mjml-python. django-mvp's email layout now does the job mjml-python was listed for.

Sam, 2026-11-06, approving the removal of provider delivery reports: "Ignore scaleway. This is the provider I have chosen for my projects but if they don't provide that, that's my problem. It's okay that Django post office doesn't provide per user bounce stats. If people want this they can use dedicated email marketing services like Mailchimp. We are not trying to build a fully featured mail chimp alternative."
