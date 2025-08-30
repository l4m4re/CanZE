# CanZE

You have to read and agree to the informal warning and the formal disclaimer at the end of this readme.md file!

CanZE is an Android App that allows you to read out some useful information out of your Renault ZE car (actually Zoe,
Kangoo & Fluence) that you cannot access using the on-board computer or display.

The website can be found at http://canze.fisch.lu


# Issues and language

We strongly urge you to report bugs, issues and requests here on github using the issue system. You have to have a github account for that, but it offloads the team from an awful lot of administrative tasks, wasting valuable time that would better be spent on more productive work. You can report in English (preferred, and really, we don't mind language errors, NONE of the team members are native speakers!), German, French, Portuguese, Dutch and Danish, as long as you don't mind us answering in English, to keep things coordinated.


# Informal warning

Before you download and use this software consider the following:
you are interfering with your car and doing that with hardware and software beyond your control (and frankly, for
a large part beyond ours), created by a loose team of interested amateurs in this field. Any car is a possibly
lethal piece of machinery and you might hurt or kill yourself or others using it, or even paying attention to
the displays instead of watching the road. Be extremely prudent!

By even downloading this software, or the source code provided on github, you agree to have completely understand this.

# Formal disclaimer

CANZE (“THE SOFTWARE”) IS PROVIDED AS IS. USE THE SOFTWARE AT YOUR OWN RISK. THE AUTHORS MAKE NO WARRANTIES AS TO
PERFORMANCE OR FITNESS FOR A PARTICULAR PURPOSE, OR ANY OTHER WARRANTIES WHETHER EXPRESSED OR IMPLIED. NO ORAL OR
WRITTEN COMMUNICATION FROM OR INFORMATION PROVIDED BY THE AUTHORS SHALL CREATE A WARRANTY. UNDER NO CIRCUMSTANCES
SHALL THE AUTHORS BE LIABLE FOR DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES RESULTING FROM THE
USE, MISUSE, OR INABILITY TO USE THE SOFTWARE, EVEN IF THE AUTHOR HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH
DAMAGES. THESE EXCLUSIONS AND LIMITATIONS MAY NOT APPLY IN ALL JURISDICTIONS. YOU MAY HAVE ADDITIONAL RIGHTS AND
SOME OF THESE LIMITATIONS MAY NOT APPLY TO YOU. THIS SOFTWARE IS ONLY INTENDED FOR SCIENTIFIC USAGE.

## PyCanZE (Python tools) roadmap

This repository also contains a Python toolkit under `PyCanZE/` used for command‑line polling and experiments (MQTT, HA integration, etc.). See `PyCanZE/AGENTS.md` for a living roadmap, Codex analysis plan, and next goals including a 5‑minute MQTT poller (SoC/SOH/HV/odometer) and optional battery diagnostics snapshots.

### Known limitations (PyCanZE tools)

These apply to the Python command‑line tools under `PyCanZE/` and do not affect the Android app:

- No free‑frame capture yet: the tools do not use `ATMA` to sniff broadcast frames. They focus on on‑demand UDS reads (0x21/0x22). This mainly impacts “live dashboard” use cases that rely on high‑rate broadcast messages. It does not affect the planned Home Assistant integration or periodic snapshots (EVC‑based SoC/SOH/HV/odometer are supported).
- 11‑bit CAN only: extended (29‑bit) ISO‑TP addressing (`ATSP7` + `ATCP`) isn’t implemented yet. Legacy ZOE and Twingo 3 Ph2 battery ECUs use 11‑bit and are supported. ZOE Ph2 battery ECUs (e.g., LBC/LBC2 with 29‑bit IDs) are not yet reachable from the Python tools.

These gaps are intentional for now. Primary goal is HA integration and basic diagnostics; there’s no intent to build a live driving dashboard. If needed later, both features can be added behind flags with per‑ECU selection from the CSV database.
