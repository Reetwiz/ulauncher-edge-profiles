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

    with open(local_state_path, 'r', encoding='utf-8') as f:
        local_state = json.load(f)
        # Chromium-based browsers store profile info here
        cache = local_state.get('profile', {}).get('info_cache', {})
        for folder, profile_data in cache.items():
            profiles[folder] = {
                'name': profile_data.get('name', folder),
                'email': profile_data.get('user_name', '')
            }

    # Verify folders actually exist on disk
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
                if query not in name:
                    profiles.pop(folder)

        entries = []
        for folder in profiles:
            # Look for a profile picture in the profile folder
            icon_path = os.path.join(edge_config_folder, folder, 'Edge Profile.png')
            if not os.path.exists(icon_path):
                icon_path = 'images/icon.png'

            entries.append(ExtensionResultItem(
                icon=icon_path,
                name=profiles[folder]['name'],
                description=f"{profiles[folder]['email']} (Folder: {folder})",
                on_enter=ExtensionCustomAction({
                    'edge_cmd': extension.preferences['edge_cmd'],
                    'opt': ['--profile-directory={0}'.format(folder)]
                }, keep_app_open=False)
            ))
        
        if not entries:
            entries.append(ExtensionResultItem(
                icon='images/icon.png',
                name='No profiles found',
                description='Check your Edge configuration folder in extension settings',
                on_enter=None
            ))

        return RenderResultListAction(entries)

class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        data = event.get_data()
        edge_path = data['edge_cmd']
        opt = data['opt']
        # Execute the launch command
        subprocess.Popen([edge_path] + opt)

if __name__ == '__main__':
    EdgeProfileExtension().run()
