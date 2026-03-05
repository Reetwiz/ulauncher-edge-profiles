import os
import subprocess
import json
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction

def scan_edge_folder(edge_config_folder):
    profiles = {}
    local_state_path = os.path.join(edge_config_folder, 'Local State')
    
    if not os.path.exists(local_state_path):
        return profiles

    try:
        with open(local_state_path, 'r', encoding='utf-8') as f:
            local_state = json.load(f)
            cache = local_state.get('profile', {}).get('info_cache', {})
            for folder, profile_data in cache.items():
                display_name = profile_data.get('given_name') or \
                               profile_data.get('name') or \
                               folder
                
                profiles[folder] = {
                    'name': display_name,
                    'email': profile_data.get('user_name', '')
                }
    except Exception:
        pass

    for folder in list(profiles.keys()):
        if not os.path.isdir(os.path.join(edge_config_folder, folder)):
            profiles.pop(folder)

    return profiles

class EdgeProfileExtension(Extension):
    def __init__(self):
        super(EdgeProfileExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())

class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        edge_config_folder = os.path.expanduser(extension.preferences['edge_folder'])
        profiles = scan_edge_folder(edge_config_folder)

        query = event.get_argument()
        if query:
            query = query.strip().lower()
            for folder in list(profiles.keys()):
                name = profiles[folder]['name'].lower()
                email = profiles[folder]['email'].lower()
                if query not in name and query not in email:
                    profiles.pop(folder)

        entries = []
        for folder in sorted(profiles.keys()):
            icon_path = os.path.join(edge_config_folder, folder, 'Edge Profile.png')
            if not os.path.exists(icon_path):
                icon_path = 'images/icon.png'

            entries.append(ExtensionResultItem(
                icon=icon_path,
                name=profiles[folder]['name'],
                description=f"{profiles[folder]['email']} (Folder: {folder})",
                on_enter=ExtensionCustomAction({
                    'edge_cmd': extension.preferences['edge_cmd'],
                    'opt': ['--profile-directory={0}'.format(folder)],
                    'profile_name': profiles[folder]['name']
                }, keep_app_open=False)
            ))
        
        return RenderResultListAction(entries)

class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        data = event.get_data()
        edge_path = data['edge_cmd']
        opt = data['opt']
        profile_name = data.get('profile_name', '')

        activated = False
        try:
            # Get list of all open windows via wmctrl
            output = subprocess.check_output(['wmctrl', '-l'], text=True)
            
            for line in output.splitlines():
                # Partial match: look for Profile Name AND "Edge" in the same title
                # This bypasses the hidden character Edge inserts between "Microsoft" and "Edge"
                if profile_name.lower() in line.lower() and "edge" in line.lower():
                    window_id = line.split()[0]
                    # Activate window using its unique Hex ID
                    subprocess.call(['wmctrl', '-ia', window_id])
                    activated = True
                    break
        except Exception:
            # Fallback if wmctrl is missing or fails
            pass

        if not activated:
            # If no existing window was found/focused, launch a new one
            subprocess.Popen([edge_path] + opt)

if __name__ == '__main__':
    EdgeProfileExtension().run()
