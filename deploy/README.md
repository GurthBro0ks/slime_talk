# Feasibility deployment — NUC2 preparation, NOT ENABLED

The owner approved NUC2 and temporary public Funnel exposure for Phase-0 testing.
As of 2026-09-28, the controller is **not deployed**: the required LiveKit and APNs
credentials are absent from the expected private NUC2 paths, and the deployment
account cannot perform the required root-owned installation. Node 22+ is required.
No packages or paid services are needed. Existing free LiveKit carries audio.

Transfer the already authorized server credentials privately into the host's secret files;
GitHub Actions secrets cannot be read back. Never paste keys into chat, Git, logs,
command-line arguments, or downloadable artifacts.

Prepared layout:

- Controller source: `/opt/slime-talk-feasibility/controller`
- Dedicated system user/group: `slime-talk`
- Environment: `/etc/slime-talk-feasibility/controller.env`, root-owned mode 0600
- APNs P8 and devices JSON: root:slime-talk mode 0640, parent mode 0750
- Unit: `/etc/systemd/system/slime-talk-feasibility.service`

Pairing material was generated on NUC2 in
`/home/slimy/.local/share/slime-talk-feasibility/devices.json` (private directory
0700, file 0600). Preserve these credentials and install that file at the prepared
path when privileged installation is possible. On another host with no existing
pairing file, create pairing material locally with:

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

NUC2 already serves an unrelated public Funnel on HTTPS port 443, proxying to
`127.0.0.1:8080`. Preserve that mapping. After the dedicated service starts and
the real local authentication smoke tests pass, use a separate HTTPS port:

```sh
tailscale funnel --bg --https=8443 http://127.0.0.1:8787
```

The intended origin is `https://slimy-nuc2.tailf64507.ts.net:8443`. Confirm the
8443 mapping with `tailscale funnel status --json` before sharing it with clients.
Funnel must terminate public TLS and proxy only to the local authenticated controller.
Enter that HTTPS origin on both phones. Do not expose LiveKit/APNs keys or an admin
API. Public authentication failures return only numeric status codes; there is no
public health/debug/log endpoint. Check current Tailscale tailnet permissions before
activation; any new ACL/account decision is outside this deployment scope.

For rollback, remove only the controller's HTTPS port mapping, then stop only its
service. Do not use `tailscale funnel reset`, which would erase the unrelated 443
mapping:

```sh
tailscale funnel --https=8443 off
sudo systemctl stop slime-talk-feasibility.service
```
