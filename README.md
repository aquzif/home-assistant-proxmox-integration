# Home Assistant Proxmox VE Integration

A custom Home Assistant integration for monitoring and managing Proxmox VE servers.

## Installation

### HACS (Recommended)

1. Add this repository as a custom repository in HACS
2. Search for "Proxmox VE" in HACS
3. Click "Install"
4. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/proxmox` directory to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Proxmox VE"
4. Enter your Proxmox VE server details:
   - Host: Your Proxmox VE server IP or hostname
   - Port: API port (default: 8006)
   - Username: Your Proxmox VE username (e.g., `root@pam`)
   - Password: Your Proxmox VE password
   - Verify SSL: Whether to verify SSL certificates

## Features

This integration provides basic setup and configuration flow for Proxmox VE integration.

## Development

This is a basic boilerplate for the Proxmox VE integration. Additional features and platforms will be added in future updates.

## License

This project is open source.