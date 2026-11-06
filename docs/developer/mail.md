# Mail

The mail extra queues every email your project sends, keeps a log of each one, and hands it to your email provider. It is built on [django-post-office](https://github.com/ui/django-post-office), which stores and sends the email, and [django-anymail](https://github.com/anymail/django-anymail), which delivers it through a provider such as Amazon SES, Mailgun or Postmark. Email you write as a stored template extends django-mvp's own email layout, so it looks like the rest of the project's mail. This package adds no Python, no models and no migrations of its own. What it supplies is the configuration below, tested in the demo project, and this page.

Everything the two packages do is described in their own documentation. This page covers what you set up in a project to use them together, and how to send.

## Install mail

Install the extra, apply four settings and create the tables.

1. Install the `mail` extra:

   ```bash
   pip install "django-mvp-community[mail]"
   ```

2. Add `post_office` to `INSTALLED_APPS`. Add `anymail` as well if your provider is one django-anymail has a backend for:

   ```python
   INSTALLED_APPS = [
       # ...
       "post_office",
       "anymail",
   ]
   ```

3. Make django-post-office the backend Django sends through, so every email a library or your own code sends with `send_mail` is queued and logged:

   ```python
   EMAIL_BACKEND = "post_office.EmailBackend"
   ```

   Django 6.1 deprecates `EMAIL_BACKEND` in favour of `MAILERS`, and django-post-office reads either. `EMAIL_BACKEND` works on every Django version this package supports, so it is the form shown here.

4. Name the backend django-post-office hands queued email to, in `POST_OFFICE`. This is where django-anymail comes in. Anymail's backend for Mailgun is shown; use your provider's:

   ```python
   POST_OFFICE = {
       "BACKENDS": {
           "default": "anymail.backends.mailgun.EmailBackend",
       },
   }

   ANYMAIL = {
       "MAILGUN_API_KEY": "...",
       "MAILGUN_SENDER_DOMAIN": "mail.example.com",
   }
   ```

   Keep the key out of your settings file: read it from the environment.

5. Turn off django-post-office's template cache, so a change to a stored template is used straight away:

   ```python
   POST_OFFICE_TEMPLATE_CACHE = False
   ```

6. Create django-post-office's tables:

   ```bash
   python manage.py migrate
   ```

Email sent with `send_mail`, `EmailMessage` or any library that uses Django's email now lands in the queue and the log instead of going straight to the provider. Nothing leaves your server until the queue is sent, which the next section covers.

## Send the queue

Queued email waits until something sends it. Choose one of the three ways.

- **Run `send_queued_mail` on a schedule.** Call it every minute from cron or a systemd timer:

  ```bash
  python manage.py send_queued_mail
  ```

- **Send from Celery.** Set `CELERY_ENABLED` to `True` in `POST_OFFICE` and django-post-office queues a Celery task for each email you send. Its task is `post_office.tasks.send_queued_mail`.
- **Send during the call.** Set `DEFAULT_PRIORITY` to `"now"` in `POST_OFFICE` and each email is handed to the provider as it is sent, and still logged. Nothing needs to run in the background, which suits a small project or development. A slow provider then slows the request that sent the email.

A message that fails is left in the log with the error. It is tried again only when you set `MAX_RETRIES` in `POST_OFFICE` above its default of `0`, and `RETRY_INTERVAL` sets the wait between attempts.

The log keeps each email's full body, so it grows with every email you send. Delete old email on a schedule with `cleanup_mail`:

```bash
python manage.py cleanup_mail --days=30 --delete-attachments
```

## Check what was sent

Every email the project sends is listed in the admin under **Post Office → Emails**, newest first.

1. Search for the recipient's address to list only the emails sent to them.
2. Each row shows the recipients, the subject, when it was last updated and its status: queued, sent or failed.
3. Open an email to see its logs. A failed email has a log entry with the error the provider or the connection gave.

"Sent" means the provider accepted the email. What happened after that, whether it reached the inbox, bounced or was marked as spam, is not recorded. Your provider's own dashboard has that, and a service built for bulk mail has it per recipient.

The log keeps each email's full body, including one-time links such as password resets and sign-in codes. Give the permissions to view django-post-office's Email, Log and Email template models only to staff you trust with those links, and remove old email with `cleanup_mail` as described above.

## Write a stored template

A stored template is written and translated in the admin, under **Post Office → Email templates**, and changed there whenever its wording needs to change. No code change or deploy is needed.

1. Add an email template. Give it a name, the name your code sends it by, and a subject.
2. Write the HTML content on django-mvp's email layout, in plain `h1`, `h2`, `p`, `ul`, `li` and `a`, which the layout styles:

   ```django
   {% extends "mvp/email/base.html" %}
   {% block preheader %}Your account is ready.{% endblock %}
   {% block body %}
     <h1>Welcome, {{ name }}</h1>
     <p>Your account is ready.</p>
   {% endblock %}
   ```

   django-mvp's email components, such as `<c-mvp.email.button>`, do not work in a stored template. django-post-office renders it from the database rather than from a file, and Cotton only compiles templates it loads from files. An email that needs them stays a template file in your project.
3. Write the plain-text content as well, for mail clients that show no HTML.
4. Add a translation for each language below the template: its language, subject and content, written the same way. A translation that should not carry the layout's English footer writes its own `footer` block, as shown below.
5. Save. A template that would not render, such as one with an unclosed tag, is refused with the error, and the saved version keeps being sent.

The next email sent from the template carries the change.

## Send a stored template

A stored template is an email whose subject and body are kept in the database and edited in the admin, with a translation per language. Send one by name with django-post-office's `mail.send`:

```python
from django.utils import translation
from post_office import mail

with translation.override(user.language):
    mail.send(
        user.email,
        template="welcome",
        context={"name": user.first_name},
        language=user.language,
    )
```

Both lines about the language matter, and they do different things.

- `language=` picks the translation to send. If the template has no translation in that language, `mail.send` raises `EmailTemplate.DoesNotExist` and nothing is queued or logged.
- `translation.override` sets the language the email is rendered in. The layout writes `lang` on the root element and its default footer from it, so without the override a German translation still says `lang="en"`.

Leave `language` out to send the template's own language.

## Why a template writes its own footer

A stored template extends `mvp/email/base.html`, django-mvp's email layout, which supplies the page, the header and a default footer. django-mvp ships no German catalogue, so that default footer is English whatever language the email is in. A translation that matters to its readers writes its own `footer` block:

```django
{% extends "mvp/email/base.html" %}
{% block body %}<h1>Willkommen</h1><p>Ihr Konto ist bereit.</p>{% endblock %}
{% block footer %}<p>Gesendet von Beispiel GmbH.</p>{% endblock %}
```

## Why the template cache is off

When a translation is saved, django-post-office clears the cache entry for the template's name, but reads the entry for the name and language together. With the cache on, an edit to a translation is not used for up to five minutes. Turning the cache off costs one query for each stored template sent.
