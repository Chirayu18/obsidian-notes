---
name: home-assistant-setup
description: "HA lighting setup — entity IDs, scenes, scripts, and the ha-mcp server that controls them"
metadata: 
  node_type: memory
  type: project
  originSessionId: 7ca21f69-71ba-4de4-a60c-ac4ca2aeca80
  modified: 2026-07-27T16:45:37.065Z
---

Home Assistant runs containerized (config_dir `/config`) on the laptop, reachable at
`http://192.168.0.214:8123`. Controlled via the **ha-mcp** MCP server (HACS custom
component `ha_mcp_tools`), which exposes 78 tools including `ha_call_service`,
`ha_config_set_script`, `ha_config_set_scene`, and `ha_set_entity`.

**Lights** — three Govee (`govee_light_local`), all in the `bedroom` area:

| Entity ID | Name |
|---|---|
| `light.bedside_left` | Bedside Left |
| `light.bedside_right` | Bedside Right |
| `light.h619a` | Bedroom Strip (entity ID never renamed) |

All three *advertise* the same 12 effects: `none, sunrise, sunset, movie, dating,
romantic, twinkle, candlelight, snowflake, energetic, breathe, crossing`.
Color temp range 2000–9000K. Set effects via `light.turn_on` with `effect:`.

**IMPORTANT — effects only work on the H619A strip.** The two H6008 bedside bulbs
publish the full `effect_list` (it is one shared list for the whole integration) but
their firmware does not implement effects. HA accepts the command, reports the effect
as set, and the bulb ignores it — there is no read-back, so HA never notices.
Confirmed visually on 2026-07-27: `twinkle` on a bulb produced a static light.
Use warm `rgb_color` + low `brightness_pct` on the bulbs instead; keep real effects
for `light.h619a`. Note the H6008 also converts RGB to its nearest color temp, so
the reported `rgb_color` won't match what was sent.

**Saved scenes and scripts** (as of 2026-07-27):
- `scene.bedroom_normal` — all three, 100% brightness, 4000K neutral white
- `scene.bedroom_night` — all three, brightness 13/255 (~5%), 2000K warm
- `script.romantic_mood` — bulbs warm amber `rgb_color: [255,120,40]` @18% with
  `effect: none`; strip `romantic` @25%

**After a laptop/network restart** `govee_light_local` may land in `setup_retry` and
all three lights go `unavailable` (no attributes at all). It has recovered on its own;
`homeassistant.reload_config_entry` with the entry_id is the manual nudge. The bulbs
themselves answer a Govee LAN scan (UDP multicast `239.255.255.250:4001`, replies to
4002) from the host — useful to prove the bulbs are fine and it is HA that cannot see
them. Bulb IPs seen 2026-07-27: `.128` Bedside Left, `.113` Bedside Right, `.240` Strip.
Service calls to `unavailable` entities still return `success: true` — always verify
state afterwards.

Areas defined: Living Room, Kitchen, Bedroom (only Bedroom is populated).

Notes: ha-mcp ships a best-practices skill; gated write tools (`ha_config_set_*`)
require a `BestPracticeKey` read-receipt fetched from `ha_get_skill_guide` — it
rotates hourly, so fetch it fresh rather than reusing a stored value. Use
`color_temp_kelvin`, not `color_temp` (mireds removed in HA 2026.3).

See [[Meta/claude-memory/_history/general/home/home-assistant-security|home-assistant-security]] for the auth posture and its open items.
