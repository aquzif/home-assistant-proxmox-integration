# home-assistant-proxmox-integration

Podstawowa custom integration do Home Assistanta, która pobiera status maszyn z Proxmox API i tworzy encje typu `binary_sensor` dla:
- LXC (`/api2/json/nodes/<node>/lxc`)
- QEMU/KVM (`/api2/json/nodes/<node>/qemu`)

## Co robi integracja

- Odczytuje listę kontenerów i maszyn wirtualnych z wskazanego noda Proxmox.
- Dla każdej pozycji tworzy encję `binary_sensor`.
- `on` oznacza `status == running`, a `off` oznacza np. `stopped`.
- Autoryzacja jest realizowana nagłówkiem `Authorization`.

## Instalacja

1. Skopiuj folder `custom_components/proxmox_status` do:
   - `<config>/custom_components/proxmox_status`
2. Zrestartuj Home Assistanta.
3. Dodaj konfigurację do `configuration.yaml` (patrz niżej).

## Konfiguracja

Przykład jest w pliku `configuration.example.yaml`.

```yaml
proxmox_status:
  host: "https://proxmox.arpa.home"
  node: "proxmox"
  token: "PVEAPIToken=user@pam!token-name=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
  scan_interval: 30
```

### Parametry

- `host` (wymagane): URL do Proxmox, np. `https://proxmox.arpa.home`
- `node` (wymagane): nazwa noda, np. `proxmox`
- `token` (wymagane): wartość nagłówka `Authorization`
- `scan_interval` (opcjonalne): odświeżanie w sekundach, domyślnie `30`

## Przykładowe encje

- `binary_sensor.proxmox_main_linux_status`
- `binary_sensor.proxmox_nginxproxymanager_status`

Każda encja zawiera dodatkowe atrybuty, m.in. `vmid`, `type`, `status`, `uptime`, `cpu`, `mem`.
