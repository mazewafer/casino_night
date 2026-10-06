# The SE 101 Term Project

Your team will devise, design, build, test and demonstrate a working piece of software,
using Scrum, in GitLab, over four sprints.

## What you can build

1. **A web-accessible To-Do application.** Evolve the warm-up from Lab 5 into something
   genuinely usable by someone who is not you.
2. **An Android To-Do application.** It can be built and tested entirely on the Android
   emulator; a phone helps for the demo but is not required. See the handbook, §2.6.
3. **Something you propose.** It must be comparable in scope, and it must be approved
   through your charter before you start. Ambitious proposals are welcome; the failure mode
   is over-reach, so be honest about scope.

Options 1 and 2 are not lesser choices. A well-built To-Do application beats an ambitious
half-finished anything.

## Scope, honestly

SE 101 is a **0.25-unit course**. Across the project you have roughly two hours per person
per week outside class, plus the Thursday lab. For a team of five over five weeks that is
on the order of fifty to sixty person-hours **in total**, including everything you write
down.

Scope accordingly. The single most common way this project fails is a team planning as if
they had a term-long capstone and then delivering nothing. **A small thing that works,
is tested, and is demonstrated beats a large thing that does not.** Your charter should
describe something you could finish in half the time available, because you will not have
half the time you think you do.

## Deliverables and marks

The project is worth **45% of the course**. The course outline assesses it as three
components. The marks below are given in **course percentage points**, not as percentages of
the project, so they add to 45 and you can check them directly against the outline.

| Course % | Component | Where |
|---|---|---|
| 5 | **Charter and backlogs** | docs/charter.md, GitLab issue boards |
| 10 | **Presentation and review sessions** — three rounds, marked per member | live, in the lab slot |
| 30 | **Software, tests and documentation** | src/, tests/, docs/, tagged `v1.0` |
| **45** | | |

Inside the 30, expect the weight to fall roughly like this: **source code and build 12**,
**tests and test report 10**, **documentation 4**, and **progress and git hygiene 4** —
commits, issues, boards, role rotation. That is guidance on where to spend your effort, not a
second rubric; the marking rubric issued later in the term is what a TA will actually use.

Two things to notice. The charter and backlogs are worth 5 points, not because they do not
matter — they set up everything else — but because they are cheap to produce well and the
marks are in the software. And the review sessions are marked **per member**, so 10 of your
45 depend on your own answers about your own work, not on your team's.

Note what is **not** on this list, deliberately: there is no separate user manual (put setup
and usage in your README), no presentation deck (the live review is the presentation), and
no per-sprint retrospective document (one issue comment per sprint is enough). The time
that would have gone into those should go into working software.

### A note on the sprint review mark
It is recorded **per member, not per team**. Each of you is asked questions directly, and
answers for your own contribution. A team where one person can answer everything and four
cannot is a team with a problem, and the marks will say so.

## Working rules

**Role rotation.** For each substantial piece of work: one member implements, a *different*
member writes the tests, a *third* reviews the merge request. This is checked mechanically
against GitLab metadata across the whole project, not just the warm-up.

**Labels.** Every issue carries type::, priority::, severity::, and once sprints begin,
sprint::. The board is expected to be *live* — reflecting what is actually happening, not
reconstructed the night before a review.

**Definition of done.** Agree one, write it in the charter, and hold to it. "Merged with
tests passing and reviewed by someone who did not write it" is a reasonable starting point.

**Tag your release** when you are finished:

    git tag v1.0
    git push origin v1.0

## Sprint reviews

Three rounds. Ten minutes at the interim rounds, longer at the final one:

- **Demo working software.** Not slides, not a walkthrough of code. Something running.
- **Answer questions**, individually, about what you personally did.

For the final round, your recorded demo video is submitted in advance so that the live time
is spent on questions rather than on watching. Put it in docs/.

If a review arrives and there is nothing running, say so plainly at the start. It is a bad
outcome but a recoverable one, and it is much better than fifteen minutes of explaining why
the thing that does not work would have worked.

## Getting help

The clinic in the Friday seminar slot exists for this. So do the TAs. A team that is stuck
and says nothing until December is the one failure mode we cannot help with.

## Deadlines

All dates are in **Part 3 of the SE 101 Course Handbook** on Learn.
