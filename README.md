# Edge Profiles for Ulauncher

Launch Microsoft Edge with different user profiles directly from Ulauncher.

## Features

- Automatically discovers all Edge profiles from your local configuration
- Shows profile names and associated email addresses
- Uses profile pictures if available
- Filter profiles by typing
- Supports both stable and dev versions of Edge

## Installation

### From GitHub

1. Open Ulauncher Preferences
2. Go to Extensions tab
3. Click "Add extension"
4. Paste this repository's GitHub URL
5. Click "Add"

If the extension doesn't appear, restart Ulauncher:
```bash
killall ulauncher && ulauncher
```

## Configuration

The extension provides three configurable options:

1. **Keyword** (default: `edge`): The keyword to trigger the extension
2. **Edge Configuration Folder** (default: `~/.config/microsoft-edge`): 
   - For stable: `~/.config/microsoft-edge`
   - For dev: `~/.config/microsoft-edge-dev`
3. **Edge Executable** (default: `microsoft-edge-stable`):
   - For stable: `microsoft-edge-stable` or `microsoft-edge`
   - For dev: `microsoft-edge-dev`

## Usage

1. Open Ulauncher (usually `Ctrl+Space`)
2. Type `edge` (or your configured keyword)
3. Start typing to filter profiles
4. Select a profile to launch Edge with that profile

## How It Works

The extension reads your Edge's `Local State` file to discover all configured profiles, then launches Edge with the `--profile-directory` flag to open the selected profile.

## Requirements

- Ulauncher 5.0+
- Microsoft Edge (stable or dev) installed on Linux
- Python 3

## License

MIT License - See LICENSE file for details
