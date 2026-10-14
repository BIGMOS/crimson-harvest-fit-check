# Changelog

## 14 October 2026

### Added
- **C1 and C2 wormhole sites**: Perimeter Ambush Point, Perimeter Camp, Phase Catalyst Node, The Line (C1); Perimeter Checkpoint, Perimeter Hangar, The Ruins of Enclave Cohort 27, Sleeper Data Sanctuary (C2). C1 and C2 tick boxes were added for Correct my fit and Cost effective.
- **More Crimson Harvest sites**: Crimson Harvest Sanctuary (Level 5 escalation) and Criterion of Fitness (solo Triglavian site).
- **Future events**: event sites now come from `event-data.js`, built by `tools/build_events.py`. A new event is added by listing its NPCs and wave layouts there.
- Event sites can carry a short note, shown above the site table.

### Changed
- Title changed to **Event, Wormhole Site & PvP Fit Check**.

## 13 October 2026

### Added
- **I am an Alpha pilot** button, for pilots without an Omega account. The fit is calculated with the highest skill levels an Alpha clone can train instead of all skills at V, and anything an Alpha cannot use is flagged.
- In Alpha mode, "Correct my fit" swaps items an Alpha cannot use for ones it can, removes modules that have no Alpha version, and only suggests modules an Alpha can fit.
- PvP "Correct my fit" now aims for the best win rate instead of having to beat every opponent. It can also upgrade drones, weapons and damage modules, and stops at faction modules.
- Alpha skill limits in `alpha-data.js`, rebuilt with `python tools/build_alpha.py`.

### Changed
- A fit that cannot be flown as pasted now says so at the top, with the reason, instead of "Not a good PvP fit".
- PvP correction results show matchups won before and after, and remind you to press "Load into checker" to see the corrected fit's full result.
- "Correct my fit" and "Cost effective" now respect the module boxes you ticked or unticked.
- "Correct my fit" stops after 60 seconds and shows the best fit found so far.
- The C3 to C6 tick boxes are greyed out in PvP, where they do not apply.

### Fixed
- PvP data mix-up: switching PvP area or pasting a new hull while data was still loading could leave another hull's opponents in place, giving a wrong win count.
- Alpha mode with a hull an Alpha cannot fly: the corrector searched anyway and returned an unusable fit. It now stops with a clear message.
- Alpha mode: a module with no Alpha version stayed in the corrected fit.
- After a paste that failed to load, the previous fit's result stayed on screen.
- The progress text next to the buttons could get stuck after an error.
- The correction heading and the verdict card could disagree on whether a fit was "good".
- The Alpha button did nothing, silently, when `alpha-data.js` was missing; it is now disabled with an explanation.

## 9 to 13 October 2026

### Added
- C3 to C6 wormhole combat anomalies, with a Wave dropdown.
- PvP check using zKillboard data: the hulls that most often kill your hull, each in its typical fit.
- "Cost effective" button: swaps modules for cheaper ones of the same kind while the fit still passes.
- C3 to C6 tick boxes so "Correct my fit" and "Cost effective" can cover whole wormhole classes at once.
- A note under the title: the fit must be checked for each site.

### Changed
- "Correct my fit" works on any pasted fit, against every wave of the chosen site, trying Tech II, then faction, then deadspace.

### Fixed
- The Bastion Module was counted as switched off, so Marauders were judged without it.
- Plated armor fits with no repairer were treated as shield fits.
