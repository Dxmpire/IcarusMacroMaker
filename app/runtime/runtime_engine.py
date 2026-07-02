import os
import time
import threading
from pynput import keyboard, mouse

from app.storage.profile_store import ProfileStore, Profile


class RuntimeEngine:
    def __init__(self, store=None):
        # MacroStore (optional, but needed for saving macros)
        self.store = store

        # ---------------------------------------------------------
        # PROFILE SYSTEM
        # ---------------------------------------------------------
        self.profile_store = ProfileStore()

        profiles = self.profile_store.load_profiles()
        if not profiles:
            default = self.profile_store.create_profile("Default")
            profiles = [default]

        self.profiles = profiles
        self.active_profile = profiles[0]

        # Macros list always mirrors active profile
        # (MainWindow will populate this)
        self.macros = self.active_profile.macros
        
        # ---------------------------------------------------------
        # RUNTIME STATE
        # ---------------------------------------------------------
        self.key_states = set()
        self.mouse_states = set()

        self.toggles = {}
        self.macro_state = {}
        self.action_running = {}

        self.toggle_latch = {}
        self.mouse_toggle_latch = {}
        self.action_from_key_latch = {}

        self.running = True

        self.keyboard_ctrl = keyboard.Controller()
        self.mouse_ctrl = mouse.Controller()

        # Start listeners
        self._start_keyboard_listener()
        self._start_mouse_listener()

        # Start engine loop
        self.thread = threading.Thread(target=self._engine_loop, daemon=True)
        self.thread.start()

    # ============================================================
    # PROFILE MANAGEMENT
    # ============================================================

    def create_profile(self, name):
        profile = self.profile_store.create_profile(name)
        self.profiles.append(profile)
        return profile

    def rename_profile(self, profile, new_name):
        self.profile_store.rename_profile(profile, new_name)

    def delete_profile(self, profile):
        self.profile_store.delete_profile(profile)
        self.profiles.remove(profile)

    def get_profiles(self):
        return self.profiles

    def set_active_profile(self, profile):
        self.active_profile = profile
        self.macros = self._load_macros_for_profile(profile)

        # Rebuild runtime state for macros
        self._reset_runtime_state()

    def _load_macros_for_profile(self, profile):
        if not self.store:
            return profile.macros

        macros = []
        for filename in profile.macro_files:
            path = os.path.join("app", "storage", "macros", filename)
            if os.path.exists(path):
                macro = self.store.load_single_macro(path)
                macros.append(macro)
        return macros

    def _reset_runtime_state(self):
        self.toggles.clear()
        self.macro_state.clear()
        self.action_running.clear()
        self.toggle_latch.clear()
        self.mouse_toggle_latch.clear()
        self.action_from_key_latch.clear()

        for macro in self.macros:
            self._init_macro_runtime(macro)

    # ============================================================
    # INPUT LISTENERS
    # ============================================================

    def _start_keyboard_listener(self):
        def on_press(key):
            try:
                self.key_states.add(key.char)
            except Exception:
                self.key_states.add(str(key))

        def on_release(key):
            try:
                self.key_states.discard(key.char)
            except Exception:
                self.key_states.discard(str(key))

        listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        listener.daemon = True
        listener.start()

    def _start_mouse_listener(self):
        def on_click(x, y, button, pressed):
            if pressed:
                self.mouse_states.add(str(button))
            else:
                self.mouse_states.discard(str(button))

        listener = mouse.Listener(on_click=on_click)
        listener.daemon = True
        listener.start()

    # ============================================================
    # MACRO MANAGEMENT
    # ============================================================

    def register_macro(self, macro):
        """Public API used by UI."""
        self.active_profile.macros.append(macro)
        self.profile_store.add_macro_to_profile(self.active_profile, macro)

        self._init_macro_runtime(macro)

    def _init_macro_runtime(self, macro):
        self.toggles[macro] = False
        self.macro_state[macro] = {"active": False, "held_keys": set()}
        self.action_running[macro] = False
        macro._fire_once = False

    def set_macro_enabled(self, macro, enabled):
        macro.enabled = enabled
        if not enabled:
            self._cleanup_macro(macro)
            self.macro_state[macro]["active"] = False

    # ============================================================
    # ENGINE LOOP
    # ============================================================

    def _engine_loop(self):
        while self.running:
            for macro in list(self.macros):
                if not getattr(macro, "enabled", False):
                    continue

                cond = self._conditions_met(macro)
                state = self.macro_state.get(macro)
                if state is None:
                    continue

                # One-shot trigger
                if getattr(macro, "_fire_once", False):
                    self.action_running[macro] = True
                    self._execute_actions(macro, state)
                    self.action_running[macro] = False
                    macro._fire_once = False
                    continue

                # Continuous execution
                if cond:
                    self.action_running[macro] = True
                    self._execute_actions(macro, state)
                    self.action_running[macro] = False
                    state["active"] = True
                else:
                    if state["active"]:
                        self._cleanup_macro(macro)
                        state["active"] = False

            time.sleep(0.01)

    # ============================================================
    # CONDITION EVALUATION
    # ============================================================

    def _conditions_met(self, macro):
        if not hasattr(macro, "conditions"):
            return False

        for cond in macro.conditions:
            t = cond["type"]

            # always_on
            if t == "always_on":
                continue

            # while_key_down
            if t == "while_key_down":
                key = cond.get("key")
                if key not in self.key_states:
                    return False

            # toggle_with_key
            if t == "toggle_with_key":
                key = cond.get("key")
                pressed = key in self.key_states
                latch_key = (macro, key)
                latch = self.toggle_latch.get(latch_key, False)

                if pressed and not latch:
                    self.toggles[macro] = not self.toggles[macro]
                    self.toggle_latch[latch_key] = True

                    if not self.toggles[macro]:
                        if self.macro_state[macro]["active"]:
                            self._cleanup_macro(macro)
                            self.macro_state[macro]["active"] = False
                        return False

                elif not pressed and latch:
                    self.toggle_latch[latch_key] = False

                if not self.toggles[macro]:
                    return False

            # while_mouse_down
            if t == "while_mouse_down":
                btn = cond.get("button", "Button.left")
                if btn not in self.mouse_states:
                    return False

            # toggle_with_mouse
            if t == "toggle_with_mouse":
                btn = cond.get("button", "Button.left")
                pressed = btn in self.mouse_states
                latch_key = (macro, btn)
                latch = self.mouse_toggle_latch.get(latch_key, False)

                if pressed and not latch:
                    self.toggles[macro] = not self.toggles[macro]
                    self.mouse_toggle_latch[latch_key] = True
                elif not pressed and latch:
                    self.mouse_toggle_latch[latch_key] = False

                if not self.toggles[macro]:
                    return False

            # action_from_key
            if t == "action_from_key":
                key = cond.get("key")
                pressed = key in self.key_states

                latch_key = (macro, key)
                latch = self.action_from_key_latch.get(latch_key, False)

                if pressed and not latch:
                    self.action_from_key_latch[latch_key] = True

                    if cond.get("safe_mode", True) and self.action_running.get(macro, False):
                        self._cleanup_macro(macro)
                        self.action_running[macro] = False

                    macro._fire_once = True

                elif not pressed and latch:
                    self.action_from_key_latch[latch_key] = False

                return getattr(macro, "_fire_once", False)

        return True

    # ============================================================
    # ACTION EXECUTION
    # ============================================================

    def _execute_actions(self, macro, state):
        for step in macro.steps:
            t = step.step_type.value
            p = step.params

            if t == "key_down":
                key = p.get("key")
                if key:
                    self._press_key_down(key)
                    state["held_keys"].add(key)

            if t == "key_up":
                key = p.get("key")
                if key:
                    self._press_key_up(key)
                    state["held_keys"].discard(key)

            if t == "key_press":
                key = p.get("key")
                if key:
                    self._press_key_down(key)
                    time.sleep(0.01)
                    self._press_key_up(key)

            if t == "delay":
                ms = p.get("ms", 10)
                time.sleep(ms / 1000)

            if t == "mouse_click":
                btn = p.get("button", "left")
                self._mouse_click(btn)

            if t == "loop":
                while self._conditions_met(macro):
                    for inner_step in macro.steps:
                        inner_t = inner_step.step_type.value
                        inner_p = inner_step.params

                        if inner_t == "key_down":
                            key = inner_p.get("key")
                            if key:
                                self._press_key_down(key)
                                state["held_keys"].add(key)

                        if inner_t == "key_up":
                            key = inner_p.get("key")
                            if key:
                                self._press_key_up(key)
                                state["held_keys"].discard(key)

                        if inner_t == "key_press":
                            key = inner_p.get("key")
                            if key:
                                self._press_key_down(key)
                                time.sleep(0.01)
                                self._press_key_up(key)

                        if inner_t == "delay":
                            ms = inner_p.get("ms", 10)
                            time.sleep(ms / 1000)

                        if inner_t == "mouse_click":
                            btn = inner_p.get("button", "left")
                            self._mouse_click(btn)

                    time.sleep(0.01)
                return

    # ============================================================
    # CLEANUP
    # ============================================================

    def _cleanup_macro(self, macro):
        state = self.macro_state.get(macro)
        if not state:
            return

        for key in list(state["held_keys"]):
            self._press_key_up(key)
        state["held_keys"].clear()

    # ============================================================
    # LOW LEVEL INPUT
    # ============================================================

    def _press_key_down(self, key):
        try:
            self.keyboard_ctrl.press(key)
        except Exception:
            pass

    def _press_key_up(self, key):
        try:
            self.keyboard_ctrl.release(key)
        except Exception:
            pass

    def _mouse_click(self, button):
        btn = mouse.Button.left if button == "left" else mouse.Button.right
        self.mouse_ctrl.press(btn)
        self.mouse_ctrl.release(btn)
