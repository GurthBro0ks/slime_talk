# Feasibility deployment — NOT ENABLED

No NUC has been selected/accessed for this deployment and **no public Funnel is
approved or enabled**. This directory only prepares deployment. Node 22+ is required.
No packages or paid services are needed. Existing free LiveKit carries audio.

Before activation, the owner/Canonical PM must identify the NUC and approve public
Funnel exposure. Transfer server credentials privately into the host's secret files;
GitHub Actions secrets cannot be read back. Never paste keys into chat, Git, logs,
command-line arguments, or downloadable artifacts.

Prepared layout:

- Controller source: `/opt/slime-talk-feasibility/controller`
- Dedicated system user/group: `slime-talk`
- Environment: `/etc/slime-talk-feasibility/controller.env`, root-owned mode 0600
- APNs P8 and devices JSON: root:slime-talk mode 0640, parent mode 0750
- Unit: `/etc/systemd/system/slime-talk-feasibility.service`

Create pairing material locally with:

```sh
node deploy/generate-device-keys.mjs /PRIVATE/PATH/devices.json
```

Copy only the Pixel device key into the Pixel enrollment form and only the iPhone
key into its form; these are per-device credentials, not server/API secrets.
Clients require HTTPS and store pairing material using Android Keystore encryption
or iOS Keychain. Revoke a device by replacing its private host key and restarting
(the controller clears room participants before accepting requests).

Once the private service is configured, its only listener is `127.0.0.1:8787`.
The systemd unit does not enable itself. Approved host activation commands are:

```sh
sudo systemctl daemon-reload
sudo systemctl enable --now slime-talk-feasibility
```

**Prepared Funnel command — DO NOT RUN without explicit public-exposure approval:**

```sh
tailscale funnel --bg 8787
```

Funnel must terminate public TLS and proxy only to the local authenticated controller.
Enter that HTTPS origin on both phones. Do not expose LiveKit/APNs keys or an admin
API. Public authentication failures return only numeric status codes; there is no
public health/debug/log endpoint. Check current Tailscale tailnet permissions before
the approved activation; an ACL/account decision must be relayed to the owner.

For rollback: disable Funnel using the tailnet's supported reset command and stop
this dedicated systemd service. Do not affect other NUC services or Funnels.
