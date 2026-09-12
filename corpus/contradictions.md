# Deliberate Contradictions in the Corpus

This document exists for evaluation and demonstration purposes. It records the three
intentional, logically incompatible rule pairs planted in the corpus. The QA system itself
must detect these at query time from the underlying source documents — it must not read
this file as a shortcut.

---

# Contradiction 1

Topic:
Attendance eligibility for the semester examination when a student has an approved
medical certificate.

Source A:
attendance_policy.md
Section 3.1
Exact text:
"Students must maintain at least 75% attendance in each registered course to be eligible
to appear for the semester examination in that course. ... Under no circumstances shall a
student whose attendance in a course falls below 75% be permitted to appear for the
semester examination in that course, and no departmental waiver of this specific threshold
may be granted at the department level."

Source B:
academic_regulations.pdf, Page 2
Section 8.2
Exact text:
"Notwithstanding the general attendance requirement, a student who has completed all
internal assessment components in a course and who has an approved medical certificate on
file for the period of absence may appear for the semester examination in that course with
an attendance record as low as 60%, provided the certificate is submitted within seven days
of the student resuming classes after the medical absence."

Why contradictory:
For a student with attendance between 60% and 75% and a valid medical certificate, Source A
states categorically that appearing for the examination is not permitted below 75%, with no
exception. Source B states that the same student is explicitly permitted to appear. Both
provisions purport to govern the same concrete situation and produce opposite eligibility
outcomes; neither text defers to, cross-references, or is subordinate to the other.

Expected behavior:
CONTRADICTION

--------------------------------

# Contradiction 2

Topic:
Deadline for payment of the semester tuition fee and the consequence of late payment.

Source A:
fee_deadlines.md
Section 13.2
Exact text:
"The semester tuition fee must be paid on or before 15 July for the Odd Semester ... Fees
paid after this date will not be accepted through the standard fee portal, and the student's
semester registration shall be liable to cancellation for non-payment."

Source B:
rulebook.md
Section 2.2
Exact text:
"A student who fails to register within the standard registration window may complete late
registration, including payment of the semester fee, at any time up to 31 July for the Odd
Semester ... upon payment of a late registration fee of ₹500. Registration completed within
this late window shall be treated as valid and shall not be cancelled solely on account of
its lateness."

Why contradictory:
Source A states the tuition fee will not be accepted, and registration is liable to
cancellation, for any payment after 15 July. Source B states the same fee may validly be
paid as late as 31 July without cancellation, merely attracting a ₹500 late fee. For a
student paying on, say, 20 July, Source A implies rejection/cancellation risk while Source B
explicitly guarantees validity. The two provisions cannot both be the operative rule for
that payment date.

Expected behavior:
CONTRADICTION

--------------------------------

# Contradiction 3

Topic:
Whether a scholarship already awarded to a student is continued or suspended when the
student is placed on Academic Probation.

Source A:
scholarship_policy.md
Section 15.3
Exact text:
"A student placed on academic probation shall be ineligible to hold or receive any
scholarship for the duration of the probation period. Any scholarship held by the student at
the time academic probation is imposed is suspended with immediate effect and no
disbursement shall be made for the semester in which probation is imposed or for any
subsequent semester in which the student remains on probation."

Source B:
academic_regulations.pdf, Page 6
Section 12.3
Exact text:
"A student placed on Academic Probation retains any scholarship already awarded and
disbursed for the current academic year for the remainder of that academic year;
imposition of Academic Probation affects only new scholarship applications, which are
suspended for the duration of the probation period, and does not affect an existing award
already in payment."

Why contradictory:
Source A says an existing scholarship is suspended immediately, with no further
disbursement, once probation is imposed. Source B says an existing scholarship already in
payment is retained and continues for the rest of the academic year, and that probation
affects only new applications. For the same fact pattern — a student with an active,
already-disbursed scholarship who is placed on probation mid-year — the two provisions
dictate opposite outcomes for the next scheduled disbursement.

Expected behavior:
CONTRADICTION
