# Book Event Feature Design
Date: 2026-02-26

## Overview
Add a "Book Seat" feature to the events section so guest users (no login required) can reserve a seat for any upcoming event via a modal form.

## Data Layer

### New Model: `EventBooking`
| Field | Type | Notes |
|-------|------|-------|
| `event` | ForeignKey(Event) | on_delete=CASCADE |
| `name` | CharField(255) | required |
| `email` | EmailField | required |
| `phone` | CharField(20) | required |
| `seats` | PositiveIntegerField | default=1 |
| `message` | TextField | blank, null |
| `status` | CharField choices | pending / confirmed / cancelled, default=pending |
| `created_at` | DateTimeField | auto_now_add |

Registered in Django admin for staff to manage bookings.

## URLs & Views

- `POST /events/<slug>/book/` → `event_book` view
  - Validates name, email, phone (required); seats (min 1); message (optional)
  - Returns JSON `{"success": true}` or `{"error": "message"}`
  - Uses `@require_http_methods(["POST"])`

## Frontend

### Events List (`/events/`)
- Each event card gets a "Book Seat" button with `data-event-slug` and `data-event-title` attributes
- Button sits alongside the existing "View details" link

### Event Detail (`/events/<slug>/`)
- "Book a Consultation" button replaced with "Book Seat" button
- Same `data-` attributes pattern

### Shared Modal
- One modal in `base.html` (or injected per page) reused for all events
- JS reads `data-event-slug` and `data-event-title` from the clicked button to populate modal title and form action URL
- Form fields: Name, Email, Phone, Seats (number, min=1, default=1), Message (textarea)
- On submit: `fetch` POST with CSRF token, shows success message or error inline inside modal

## Success / Error Handling
- Success: modal body replaced with a thank-you message, form hidden
- Error: inline error shown below the form, modal stays open
