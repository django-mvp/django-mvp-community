# django-mvp-community

<!--
  The vocabulary of this package: the words to use in issues, commit messages,
  test names, docstrings and documentation.

  It is worth writing because this package sits between other people's
  libraries, and they use the same English words for different things. Once two
  meanings of one word are both in circulation, a bug report stops being
  readable and nobody notices, because everyone understands their own reading
  of it.

  Write an entry when a term is genuinely ambiguous or genuinely this
  package's own. Do not restate the language of Django or Python — a glossary
  that defines "view" teaches nobody anything and buries the three entries that
  matter.

  Entry format, one blank line between entries:

    **Term**:
    What it is, in one or two sentences, in the present tense. Then, where it
    helps, what it is *not* — the boundary is usually the useful half.
    _Avoid_: the synonyms that should not be used for it, and where a word is
    already taken by something else, say by what.

  The closing section is for words deliberately kept out of circulation. It is
  the most useful part of the file and the part most often skipped: a word
  nobody has ruled out arrives in an issue title eventually, and by then it has
  a meaning.

  Replace everything below.
-->

Domain vocabulary for django-mvp-community — Notifications, mail and activity pages for django-mvp projects, built on established Django packages

The terms below are the ones to use in issues, commits and tests.

## Core concepts

**Host project**:
The Django project that installs this package. It owns the theme, the base
template, the data, and the URLs. This package renders into it and decides none
of those.
_Avoid_: consumer, client, downstream, user (a user is a person using the host
project, not the project itself).

**Component**:
A Cotton template this package ships, placed on a page with a tag. The tag name
is the file path, so renaming the file changes the public API.
_Avoid_: widget, partial, include, block.

<!--
  Add the terms that are actually this package's own. Three to eight entries is
  usually right. Twenty means the file has become documentation.
-->

## Terms deliberately not used

<!--
  Each entry names the word and says what using it would imply that is not
  true. "Backend" implying a swappable one. "Data source" implying this fetches
  something. The reason matters more than the ruling — without it, someone will
  reasonably re-introduce the word in six months.
-->
