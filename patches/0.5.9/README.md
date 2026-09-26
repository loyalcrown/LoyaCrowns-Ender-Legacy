# 0.5.9 Inventory Panel JEI Search Sync parity

This patch is applied on top of the validated 0.5.8 source snapshot.

It restores the classic Inventory Panel JEI search synchronization control while keeping JEI optional:

- persists the panel's JEI-sync setting in block NBT;
- adds the right-side JEI sync toggle and disables it when JEI is unavailable;
- gives a remembered Inventory Panel search priority when the GUI opens;
- otherwise adopts a non-empty JEI search while sync is enabled;
- sends Inventory Panel-entered text to JEI, including clearing the search;
- does not let an empty JEI search erase the Inventory Panel search;
- treats JEI-sourced search text as temporary, so it filters the live network without overwriting the panel's remembered text;
- uses JEI's compile-only API and a small runtime bridge, so JEI is not required to load Ender Legacy.

Runtime hotfix included after in-game crash validation:

- removes redundant `.stacksTo(1)` calls from the damageable Dark Steel Crook and Dark Steel Treetap registrations. Minecraft 1.20.1 rejects an explicit stack-size setter after durability has been assigned.

The reconstructed source version is `0.5.9-alpha`.
