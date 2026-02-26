# Book Event Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a "Book Seat" modal with a guest booking form to every event card and the event detail page, storing bookings in a new `EventBooking` model managed via Django admin.

**Architecture:** New `EventBooking` model (FK to Event) → `POST /events/<slug>/book/` view returns JSON → shared modal in templates activated by JS `data-` attributes on "Book Seat" buttons.

**Tech Stack:** Django 5, SQLite, vanilla JS (fetch + CSRF), existing CSS utility classes (nixa-btn, thm-btn, nixa-form-group)

---

### Task 1: Add `EventBooking` model to `core/models.py`

**Files:**
- Modify: `core/models.py` (append after `Event` class, around line 383)

**Step 1: Add the model**

Append this class after the `Event` model (after line 383, before the `Consultation` class):

```python
class EventBooking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='bookings')
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    seats = models.PositiveIntegerField(default=1)
    message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Event Booking'
        verbose_name_plural = 'Event Bookings'

    def __str__(self):
        return f"{self.name} — {self.event.title} ({self.seats} seat{'s' if self.seats != 1 else ''})"
```

**Step 2: Create and run migration**

```bash
cd /Users/abdullahalmamun/Developer/Personal/projects/nixa
python manage.py makemigrations core --name add_event_booking
python manage.py migrate
```

Expected output: `Applying core.0020_add_event_booking... OK`

**Step 3: Commit**

```bash
git add core/models.py core/migrations/0020_add_event_booking.py
git commit -m "feat: add EventBooking model"
```

---

### Task 2: Register `EventBooking` in Django admin (`core/admin.py`)

**Files:**
- Modify: `core/admin.py` (append after the `EventAdmin` block, around line 119)

**Step 1: Add admin class**

Append after the `@admin.register(Event)` block (after line 119):

```python
@admin.register(EventBooking)
class EventBookingAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'event', 'seats', 'status', 'created_at')
    list_filter = ('status', 'event', 'created_at')
    list_editable = ('status',)
    search_fields = ('name', 'email', 'phone')
    readonly_fields = ('created_at',)
    list_display_links = ('name', 'email')
```

**Step 2: Verify admin works**

```bash
python manage.py check
```

Expected: `System check identified no issues (0 silenced).`

**Step 3: Commit**

```bash
git add core/admin.py
git commit -m "feat: register EventBooking in admin"
```

---

### Task 3: Add `event_book` view to `core/views.py`

**Files:**
- Modify: `core/views.py`
  - Add `EventBooking` to the import on line 15
  - Add `event_book` view function after `event_detail` (after line 456)
  - Add `import json` at the top (line 2 area)

**Step 1: Add `EventBooking` to imports**

Current import line 15-19:
```python
from .models import (
    Account, Application, Blog, ContactMessage, Consultation, Destination,
    Event, FAQ, GalleryImage, NewsletterSubscriber, Program, Scholarship, Subject,
    Testimonial, University, Video, Offer,
)
```

Change to:
```python
from .models import (
    Account, Application, Blog, ContactMessage, Consultation, Destination,
    Event, EventBooking, FAQ, GalleryImage, NewsletterSubscriber, Program,
    Scholarship, Subject, Testimonial, University, Video, Offer,
)
```

**Step 2: Add `import json` near the top**

After `import logging` on line 1, add:
```python
import json
```

**Step 3: Add the view after `event_detail` (after line 456)**

```python
@require_http_methods(["POST"])
def event_book(request, slug):
    """AJAX endpoint to book a seat for an event. Returns JSON."""
    event = get_object_or_404(Event, slug=slug, is_active=True)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        data = request.POST

    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip()
    phone = (data.get('phone') or '').strip()
    message = (data.get('message') or '').strip()

    try:
        seats = int(data.get('seats') or 1)
        if seats < 1:
            seats = 1
    except (ValueError, TypeError):
        seats = 1

    if not (name and email and phone):
        return JsonResponse({'error': 'Please fill in your name, email, and phone number.'}, status=400)

    EventBooking.objects.create(
        event=event,
        name=name,
        email=email,
        phone=phone,
        seats=seats,
        message=message or None,
    )
    return JsonResponse({'success': True, 'message': f'Your seat{"s have" if seats > 1 else " has"} been booked for {event.title}!'})
```

**Step 4: Verify no syntax errors**

```bash
python manage.py check
```

Expected: `System check identified no issues (0 silenced).`

**Step 5: Commit**

```bash
git add core/views.py
git commit -m "feat: add event_book AJAX view"
```

---

### Task 4: Add URL for `event_book` in `core/urls.py`

**Files:**
- Modify: `core/urls.py`

**Step 1: Add URL pattern**

After line 35 (`path('events/<slug:slug>/', views.event_detail, name='event-detail'),`), add:

```python
path('events/<slug:slug>/book/', views.event_book, name='event-book'),
```

**Step 2: Verify**

```bash
python manage.py check
```

Expected: `System check identified no issues (0 silenced).`

**Step 3: Commit**

```bash
git add core/urls.py
git commit -m "feat: add event-book URL"
```

---

### Task 5: Add "Book Seat" buttons to event cards in `templates/root/events.html`

**Files:**
- Modify: `templates/root/events.html`

**Step 1: Replace the card body section**

Current card body (lines 48-56):
```html
                    <div class="nixa-event-card__body">
                        <h3 class="nixa-event-card__title">{{ event.title }}</h3>
                        {% if event.venue %}
                        <p class="nixa-event-card__venue"><i class="far fa-map-marker-alt"></i> {{ event.venue }}</p>
                        {% endif %}
                        <p class="nixa-event-card__excerpt">{{ event.description|striptags|truncatewords:18 }}</p>
                        <span class="nixa-event-card__cta">View details <i class="far fa-arrow-right"></i></span>
                    </div>
```

Replace with:
```html
                    <div class="nixa-event-card__body">
                        <h3 class="nixa-event-card__title">{{ event.title }}</h3>
                        {% if event.venue %}
                        <p class="nixa-event-card__venue"><i class="far fa-map-marker-alt"></i> {{ event.venue }}</p>
                        {% endif %}
                        <p class="nixa-event-card__excerpt">{{ event.description|striptags|truncatewords:18 }}</p>
                        <div class="nixa-event-card__actions">
                            <span class="nixa-event-card__cta">View details <i class="far fa-arrow-right"></i></span>
                            <button type="button" class="nixa-event-book-btn"
                                data-event-slug="{{ event.slug }}"
                                data-event-title="{{ event.title|escape }}">
                                <i class="far fa-ticket-alt"></i> Book Seat
                            </button>
                        </div>
                    </div>
```

Note: The `<button>` must be **outside** the `<a>` tag. Currently the whole card is wrapped in an `<a>` tag (line 32). Move the `<a>` to wrap only the image and title, and keep the button separate. The full restructured card should look like:

```html
            <article class="nixa-event-card">
                <a href="{% url 'core:event-detail' event.slug %}" class="nixa-event-card__link">
                    <div class="nixa-event-card__img-wrap">
                        {% if event.image %}
                        <img src="{{ event.image.url }}" alt="{{ event.title }}" class="nixa-event-card__img">
                        {% else %}
                        <div class="nixa-event-card__placeholder">
                            <i class="far fa-calendar-alt"></i>
                            <span>Event</span>
                        </div>
                        {% endif %}
                        <span class="nixa-event-card__type">{{ event.get_event_type_display }}</span>
                        <div class="nixa-event-card__date-badge">
                            <span class="nixa-event-card__date-day">{{ event.event_date|date:"d" }}</span>
                            <span class="nixa-event-card__date-month">{{ event.event_date|date:"M" }}</span>
                        </div>
                    </div>
                    <div class="nixa-event-card__body">
                        <h3 class="nixa-event-card__title">{{ event.title }}</h3>
                        {% if event.venue %}
                        <p class="nixa-event-card__venue"><i class="far fa-map-marker-alt"></i> {{ event.venue }}</p>
                        {% endif %}
                        <p class="nixa-event-card__excerpt">{{ event.description|striptags|truncatewords:18 }}</p>
                        <span class="nixa-event-card__cta">View details <i class="far fa-arrow-right"></i></span>
                    </div>
                </a>
                <div class="nixa-event-card__footer">
                    <button type="button" class="nixa-event-book-btn"
                        data-event-slug="{{ event.slug }}"
                        data-event-title="{{ event.title|escapejs }}">
                        <i class="far fa-ticket-alt"></i> Book Seat
                    </button>
                </div>
            </article>
```

**Step 2: Commit**

```bash
git add templates/root/events.html
git commit -m "feat: add Book Seat button to event cards"
```

---

### Task 6: Update `templates/root/event-detail.html` with "Book Seat" button

**Files:**
- Modify: `templates/root/event-detail.html`

**Step 1: Replace the existing button line**

Current line 38:
```html
                <a href="{% url 'core:consultation' %}" class="thm-btn mt-30">Book a Consultation</a>
```

Replace with:
```html
                <button type="button" class="thm-btn mt-30 nixa-event-book-btn"
                    data-event-slug="{{ event.slug }}"
                    data-event-title="{{ event.title|escapejs }}">
                    <i class="far fa-ticket-alt"></i> Book Seat
                </button>
                <a href="{% url 'core:events' %}" class="thm-btn thm-btn--outline mt-30 ml-2">Back to Events</a>
```

(Remove the existing "Back to Events" line 39 since it's now included above.)

**Step 2: Commit**

```bash
git add templates/root/event-detail.html
git commit -m "feat: add Book Seat button to event detail page"
```

---

### Task 7: Add booking modal + JS to `templates/root/partial/base.html`

**Files:**
- Modify: `templates/root/partial/base.html`

**Step 1: Add modal HTML just before `</body>`**

Find the closing `</body>` tag and insert this block before it:

```html
<!-- Event Booking Modal -->
<div id="nixaEventBookModal" class="nixa-modal" aria-hidden="true" role="dialog" aria-labelledby="nixaBookModalTitle">
    <div class="nixa-modal__overlay" id="nixaBookModalOverlay"></div>
    <div class="nixa-modal__dialog">
        <div class="nixa-modal__header">
            <h3 class="nixa-modal__title" id="nixaBookModalTitle">Book a Seat</h3>
            <button type="button" class="nixa-modal__close" id="nixaBookModalClose" aria-label="Close">&times;</button>
        </div>
        <div class="nixa-modal__body">
            <div id="nixaBookFormWrap">
                <form id="nixaEventBookForm" novalidate>
                    {% csrf_token %}
                    <input type="hidden" id="nixaBookEventSlug" name="event_slug" value="">
                    <div class="nixa-form-group">
                        <label for="nixaBookName">Full Name <span class="required">*</span></label>
                        <input type="text" id="nixaBookName" name="name" placeholder="Your full name" required>
                    </div>
                    <div class="nixa-form-group">
                        <label for="nixaBookEmail">Email <span class="required">*</span></label>
                        <input type="email" id="nixaBookEmail" name="email" placeholder="your@email.com" required>
                    </div>
                    <div class="nixa-form-group">
                        <label for="nixaBookPhone">Phone <span class="required">*</span></label>
                        <input type="tel" id="nixaBookPhone" name="phone" placeholder="+60 123456789" required>
                    </div>
                    <div class="nixa-form-group">
                        <label for="nixaBookSeats">Number of Seats</label>
                        <input type="number" id="nixaBookSeats" name="seats" value="1" min="1" max="10">
                    </div>
                    <div class="nixa-form-group">
                        <label for="nixaBookMessage">Message / Notes</label>
                        <textarea id="nixaBookMessage" name="message" rows="3" placeholder="Any special requirements..."></textarea>
                    </div>
                    <div id="nixaBookError" class="nixa-alert nixa-alert--error" style="display:none;"></div>
                    <div class="nixa-form-actions">
                        <button type="submit" class="nixa-btn nixa-btn--primary" id="nixaBookSubmitBtn">
                            <i class="far fa-ticket-alt"></i> Confirm Booking
                        </button>
                    </div>
                </form>
            </div>
            <div id="nixaBookSuccess" style="display:none;" class="nixa-book-success">
                <div class="nixa-book-success__icon"><i class="far fa-check-circle"></i></div>
                <h4 id="nixaBookSuccessMsg"></h4>
                <p>We'll be in touch with further details. See you at the event!</p>
                <button type="button" class="nixa-btn nixa-btn--outline" id="nixaBookSuccessClose">Close</button>
            </div>
        </div>
    </div>
</div>

<script>
(function () {
    var modal = document.getElementById('nixaEventBookModal');
    var overlay = document.getElementById('nixaBookModalOverlay');
    var closeBtn = document.getElementById('nixaBookModalClose');
    var form = document.getElementById('nixaEventBookForm');
    var slugInput = document.getElementById('nixaBookEventSlug');
    var titleEl = document.getElementById('nixaBookModalTitle');
    var errorEl = document.getElementById('nixaBookError');
    var formWrap = document.getElementById('nixaBookFormWrap');
    var successWrap = document.getElementById('nixaBookSuccess');
    var successMsg = document.getElementById('nixaBookSuccessMsg');
    var successClose = document.getElementById('nixaBookSuccessClose');
    var submitBtn = document.getElementById('nixaBookSubmitBtn');

    function openModal(slug, title) {
        slugInput.value = slug;
        titleEl.textContent = 'Book a Seat — ' + title;
        formWrap.style.display = '';
        successWrap.style.display = 'none';
        errorEl.style.display = 'none';
        form.reset();
        document.getElementById('nixaBookSeats').value = '1';
        modal.setAttribute('aria-hidden', 'false');
        modal.classList.add('is-open');
        document.body.style.overflow = 'hidden';
    }

    function closeModal() {
        modal.setAttribute('aria-hidden', 'true');
        modal.classList.remove('is-open');
        document.body.style.overflow = '';
    }

    document.addEventListener('click', function (e) {
        var btn = e.target.closest('.nixa-event-book-btn');
        if (btn) {
            e.preventDefault();
            openModal(btn.dataset.eventSlug, btn.dataset.eventTitle);
        }
    });

    if (closeBtn) closeBtn.addEventListener('click', closeModal);
    if (overlay) overlay.addEventListener('click', closeModal);
    if (successClose) successClose.addEventListener('click', closeModal);

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && modal.classList.contains('is-open')) closeModal();
    });

    if (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            errorEl.style.display = 'none';
            submitBtn.disabled = true;
            submitBtn.textContent = 'Booking...';

            var slug = slugInput.value;
            var csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value;

            fetch('/events/' + slug + '/book/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify({
                    name: document.getElementById('nixaBookName').value,
                    email: document.getElementById('nixaBookEmail').value,
                    phone: document.getElementById('nixaBookPhone').value,
                    seats: parseInt(document.getElementById('nixaBookSeats').value) || 1,
                    message: document.getElementById('nixaBookMessage').value,
                }),
            })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="far fa-ticket-alt"></i> Confirm Booking';
                if (data.success) {
                    formWrap.style.display = 'none';
                    successMsg.textContent = data.message;
                    successWrap.style.display = '';
                } else {
                    errorEl.textContent = data.error || 'Something went wrong. Please try again.';
                    errorEl.style.display = '';
                }
            })
            .catch(function () {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="far fa-ticket-alt"></i> Confirm Booking';
                errorEl.textContent = 'Network error. Please check your connection and try again.';
                errorEl.style.display = '';
            });
        });
    }
})();
</script>
```

**Step 2: Commit**

```bash
git add templates/root/partial/base.html
git commit -m "feat: add event booking modal and JS"
```

---

### Task 8: Add CSS for the modal and Book Seat button

**Files:**
- Modify: `static/root/assets/css/nixa-consultancy.css` (append at end)

**Step 1: Append modal + button styles**

```css
/* ── Event Booking Modal ────────────────────────────────── */
.nixa-modal {
    display: none;
    position: fixed;
    inset: 0;
    z-index: 9999;
    align-items: center;
    justify-content: center;
}
.nixa-modal.is-open {
    display: flex;
}
.nixa-modal__overlay {
    position: absolute;
    inset: 0;
    background: rgba(0, 0, 0, 0.55);
    cursor: pointer;
}
.nixa-modal__dialog {
    position: relative;
    background: #fff;
    border-radius: 12px;
    width: 100%;
    max-width: 520px;
    max-height: 90vh;
    overflow-y: auto;
    z-index: 1;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.25);
    margin: 16px;
}
.nixa-modal__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 20px 24px 16px;
    border-bottom: 1px solid #f0f0f0;
}
.nixa-modal__title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #1a1a2e;
    margin: 0;
}
.nixa-modal__close {
    background: none;
    border: none;
    font-size: 1.6rem;
    line-height: 1;
    cursor: pointer;
    color: #888;
    padding: 0 4px;
    transition: color 0.2s;
}
.nixa-modal__close:hover { color: #e63946; }
.nixa-modal__body {
    padding: 24px;
}

/* Book Seat button on event cards */
.nixa-event-card__footer {
    padding: 0 16px 16px;
}
.nixa-event-book-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--tg-theme-primary, #e63946);
    color: #fff;
    border: none;
    border-radius: 6px;
    padding: 8px 18px;
    font-size: 0.875rem;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s, transform 0.15s;
    width: 100%;
    justify-content: center;
}
.nixa-event-book-btn:hover {
    background: #c1121f;
    transform: translateY(-1px);
}

/* Success state inside modal */
.nixa-book-success {
    text-align: center;
    padding: 16px 0;
}
.nixa-book-success__icon {
    font-size: 3rem;
    color: #2dc653;
    margin-bottom: 12px;
}
.nixa-book-success h4 {
    font-size: 1.1rem;
    font-weight: 700;
    margin-bottom: 8px;
    color: #1a1a2e;
}
.nixa-book-success p {
    color: #666;
    margin-bottom: 20px;
}
```

**Step 2: Commit**

```bash
git add static/root/assets/css/nixa-consultancy.css
git commit -m "feat: add modal and Book Seat button CSS"
```

---

### Task 9: Manual smoke test

1. Start dev server: `python manage.py runserver`
2. Go to `http://127.0.0.1:8000/events/`
3. Verify each event card shows a "Book Seat" button below the card
4. Click "Book Seat" — modal should open with correct event title
5. Submit with empty fields — error message should appear inside modal
6. Fill in valid Name / Email / Phone, click "Confirm Booking"
7. Verify success state appears inside modal
8. Go to Django admin (`/admin/core/eventbooking/`) — confirm the booking row exists
9. Go to `http://127.0.0.1:8000/events/<any-slug>/` (event detail page)
10. Verify "Book Seat" button is present, modal opens and works the same way
11. Press Escape — modal should close
12. Click overlay — modal should close
