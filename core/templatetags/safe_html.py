"""Template filter to sanitize HTML and reduce XSS risk when rendering rich content."""
import bleach
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

# Allow common formatting and structure tags used in CKEditor/rich content
ALLOWED_TAGS = [
    'p', 'br', 'strong', 'b', 'em', 'i', 'u', 's', 'sub', 'sup',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li', 'blockquote',
    'a', 'img', 'span', 'div',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
]
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'target', 'rel'],
    'img': ['src', 'alt', 'title', 'width', 'height'],
    '*': ['class', 'id'],
}


@register.filter(name='sanitize_html')
def sanitize_html(value):
    """Sanitize HTML string: allow safe tags/attributes, strip scripts and event handlers."""
    if value is None or value == '':
        return ''
    if not isinstance(value, str):
        value = str(value)
    cleaned = bleach.clean(
        value,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True,
    )
    return mark_safe(cleaned)
