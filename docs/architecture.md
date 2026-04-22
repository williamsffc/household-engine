# Household Engine — Architecture / Blueprint

## Core vision

A 100% local, privacy-first household financial platform with a Hub-and-Spoke architecture.

The Hub owns shared infrastructure:

* local server
* database
* document intake
* processing lifecycle
* audit logging
* review queue
* app shell / navigation
* shared analytics views
* shared UI shell / theming foundation

The Spokes own domain logic:

* Expenses
* Payroll
* later Portfolio
* much later, optional non-financial modules

The system is designed to answer:

* what came in
* what went out
* what is pending review
* what is recurring
* what is changing over time
* how much liquid surplus is actually available

## Product model: household-first, member-aware

The product is primarily a **household command center**, not a set of unrelated personal tools.

However, payroll is inherently person-specific.

So the intended model is:

* the household is the main top-level unit of analysis
* each payroll document/paystub belongs to exactly one household member
* approved payroll remains tied to that member
* household payroll analytics are the rollup of approved payroll across members

This supports the real use case of uploading payroll for multiple household members while still operating one combined household finance system.

### Practical consequence

The system should support both:

* household-combined payroll analytics
* per-member payroll analytics

Later UI should be able to express views such as:

* Household
* Person-M
* Person-W

without breaking the shared household model.

## UI shell / design-system direction

The shared UI shell should behave like product infrastructure, not page-specific decoration.

That means the shell should provide:

* consistent navigation
* consistent page framing
* theme support
* responsive behavior across screen sizes
* reusable surface/card/status styling
* a foundation future pages can inherit without redesign

### Shell design principles

The product should feel:

* calm
* trustworthy
* private
* understandable
* usable every week

The visual system should avoid both:

* overly dark “terminal/admin” heaviness
* overly bright / flat / structureless dashboards

### Theme direction

The shell should support both:

* light mode
* dark mode

Preferred product default:

* light mode

Theme styling should use semantic tokens/variables rather than scattered hardcoded colors.

### Responsive shell direction

Navigation should never disappear completely.

Preferred shell behavior:

* large screens: full sidebar with labels
* medium screens: collapsed rail / compact sidebar
* small screens: compact accessible nav pattern such as top bar + drawer

## Architectural rule for payroll canonicalization

Payroll review and payroll analytics should follow this rule:

* extracted payroll enters the system as draft / in_review
* approval moves that payroll into canonical approved state
* rejection keeps it out of canonical analytics
* only approved payroll affects downstream household and per-member analytics

This rule should remain explicit in both data model and UI semantics.

## Final V1 goal

V1 is a local financial command center with two working modules:

* Expenses
* Payroll

And one shared cross-module outcome:

* Household cashflow overview

V1 is not trying to be perfect document forensics, enterprise workflow software, or a life dashboard.

It is trying to be:

* private
* reliable
* understandable
* reviewable
* modular
* usable every week

## Near-term development order

Near-term product work should follow this sequence:

1. stabilize shared shell/theming foundation
2. stabilize responsive navigation
3. move upload interactions into the UI
4. refresh current page UX under the improved shell
5. add payroll approve/reject + canonical approval flow
6. then add dedicated Payroll page / paystub examination UI
7. then improve member-selection UX and household-vs-person payroll exploration

Reason:

The Payroll page should sit on top of:
* a stable shell
* a clear payroll lifecycle
* a member-aware payroll model

not arrive before those foundations exist.

## Remaining architecture guidance

All other long-term architectural guidance remains unchanged:

* shared platform logic lives in `core/`, `services/`, `api/`
* expense domain logic lives in `expenses/`
* payroll domain logic lives in `payroll/`
* dashboards should read stable views rather than raw ingestion tables
* only approved payroll should affect analytics
* portfolio remains downstream of trustworthy expenses + approved payroll