import os
import json

PROFILE_DIR = os.path.join("app", "storage", "profiles")

class Profile:
    def __init__(self, name):
        self.name = name

        # list of Macro objects (runtime)
        self.macros = []

        # list of macro filenames (persistent)
        self.macro_files = []

    def __repr__(self):
        return f"<Profile {self.name}>"

class ProfileStore:
    def __init__(self):
        os.makedirs(PROFILE_DIR, exist_ok=True)

    # ---------------------------------------------------------
    # CREATE PROFILE
    # ---------------------------------------------------------
    def create_profile(self, name):
        profile = Profile(name)
        self.save_profile(profile)
        return profile

    # ---------------------------------------------------------
    # SAVE PROFILE
    # ---------------------------------------------------------
    def save_profile(self, profile):
        path = os.path.join(PROFILE_DIR, f"{profile.name}.json")
        data = {
            "name": profile.name,
            "macro_files": profile.macro_files
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=4)

    # ---------------------------------------------------------
    # LOAD ALL PROFILES
    # ---------------------------------------------------------
    def load_profiles(self):
        profiles = []

        for filename in os.listdir(PROFILE_DIR):
            if not filename.endswith(".json"):
                continue

            path = os.path.join(PROFILE_DIR, filename)
            with open(path, "r") as f:
                data = json.load(f)

            profile = Profile(data["name"])
            profile.macro_files = data.get("macro_files", [])
            profiles.append(profile)

        return profiles

    # ---------------------------------------------------------
    # DELETE PROFILE
    # ---------------------------------------------------------
    def delete_profile(self, profile):
        path = os.path.join(PROFILE_DIR, f"{profile.name}.json")
        if os.path.exists(path):
            os.remove(path)

    # ---------------------------------------------------------
    # RENAME PROFILE
    # ---------------------------------------------------------
    def rename_profile(self, profile, new_name):
        old_path = os.path.join(PROFILE_DIR, f"{profile.name}.json")
        new_path = os.path.join(PROFILE_DIR, f"{new_name}.json")

        profile.name = new_name

        # Save under new name
        self.save_profile(profile)

        # Delete old file
        if os.path.exists(old_path):
            os.remove(old_path)

    # ---------------------------------------------------------
    # ADD MACRO TO PROFILE
    # ---------------------------------------------------------
    def add_macro_to_profile(self, profile, macro):
        filename = f"{macro.name}.json"
        if filename not in profile.macro_files:
            profile.macro_files.append(filename)
            self.save_profile(profile)
