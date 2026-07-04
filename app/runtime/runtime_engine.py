import os
import time
import threading
from pynput import keyboard, mouse

from app.storage.profile_store import ProfileStore


class RuntimeEngine:
    def __init__(self, store=None):
        self.store = store
        self.profile_store = ProfileStore()

        # ----------------------------
        # PROFILES
        # ----------------------------
        profiles = self.profile_store.load_profiles()
        if not profiles:
            profiles = [self.profile_store.create_profile("Default")]

        self.profiles = profiles

        # Each profile only loads the macros listed in its own
        # macro_files, so macros never leak between profiles.
        if self.store:
            for profile in self.profiles:
                profile.macros = self.store.load_profile_macros(profile.macro_files)

        self.active_profile = profiles[0]
        self.macros = list(self.active_profile.macros)

        # ----------------------------
        # INPUT STATE
        # ----------------------------
        self.key_states = set()
        self.mouse_states = set()

        # ----------------------------
        # RUNTIME STATE (per macro)
        # ----------------------------
        self.toggles = {}
        self.macro_state = {}
        self.action_running = {}

        self.toggle_latch = {}
        self.mouse_toggle_latch = {}
        self.action_from_key_latch = {}

        # ----------------------------
        # CONTROL
        # ----------------------------
        self.running = True

        self.keyboard_ctrl = keyboard.Controller()
        self.mouse_ctrl = mouse.Controller()

        # init only once per macro
        for m in self.macros:
            self._init_macro(m)

        # listeners
        self._start_keyboard_listener()
        self._start_mouse_listener()

        # engine loop
        self.thread = threading.Thread(target=self._engine_loop, daemon=True)
        self.thread.start()

    # ============================================================
    # PROFILE MANAGEMENT
    # ============================================================

    def get_profiles(self):
        return self.profiles

    def set_active_profile(self, profile):
        self.active_profile = profile
        self.macros = list(profile.macros)

        # only init missing macros (NO FULL RESET)
        for m in self.macros:
            self._init_macro(m)

    # ============================================================
    # MACRO REGISTRATION (INCREMENTAL)
    # ============================================================

    def register_macro(self, macro):
        if macro not in self.macros:
            self.macros.append(macro)

        if macro not in self.active_profile.macros:
            self.active_profile.macros.append(macro)

        self.profile_store.add_macro_to_profile(self.active_profile, macro)

        self._init_macro(macro)

    def remove_macro(self, macro):
        if macro in self.macros:
            self.macros.remove(macro)

        if macro in self.active_profile.macros:
            self.active_profile.macros.remove(macro)

        self._cleanup_macro(macro)

        for d in [
            self.toggles,
            self.macro_state,
            self.action_running,
            self.toggle_latch,
            self.mouse_toggle_latch,
            self.action_from_key_latch,
        ]:
            d.pop(macro, None)

    def _init_macro(self, macro):
        if macro in self.macro_state:
            return

        self.toggles[macro] = False
        self.macro_state[macro] = {
            "active": False,
            "held_keys": set()
        }
        self.action_running[macro] = False
        macro._fire_once = False

    def ensure_macro(self, macro):
        if macro not in self.macros:
            self.macros.append(macro)
        self._init_macro(macro)

    # ============================================================
    # ENABLE / DISABLE
    # ============================================================

    def set_macro_enabled(self, macro, enabled):
        self.ensure_macro(macro)
        macro.enabled = enabled

        if not enabled:
            self._cleanup_macro(macro)
            state = self.macro_state.get(macro)
            if state:
                state["active"] = False

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

        keyboard.Listener(on_press=on_press, on_release=on_release, daemon=True).start()

    def _start_mouse_listener(self):
        def on_click(x, y, button, pressed):
            b = str(button)
            if pressed:
                self.mouse_states.add(b)
            else:
                self.mouse_states.discard(b)

        mouse.Listener(on_click=on_click, daemon=True).start()

    # ============================================================
    # ENGINE LOOP (OPTIMIZED)
    # ============================================================

    def _engine_loop(self):
        while self.running:
            macros = self.macros  # no copy needed unless you modify list during loop

            for macro in macros:
                if not getattr(macro, "enabled", False):
                    continue

                state = self.macro_state.get(macro)
                if state is None:
                    self._init_macro(macro)
                    state = self.macro_state[macro]

                cond = self._conditions_met(macro)

                if getattr(macro, "_fire_once", False):
                    self._run_actions(macro, state)
                    macro._fire_once = False
                    continue

                if cond:
                    state["active"] = True
                    self._run_actions(macro, state)
                else:
                    if state["active"]:
                        self._cleanup_macro(macro)
                        state["active"] = False

            time.sleep(0.005)

    # ============================================================
    # CONDITIONS
    # ============================================================

    def _conditions_met(self, macro):
        if not hasattr(macro, "conditions"):
            return False

        for cond in macro.conditions:
            t = cond["type"]

            if t == "always_on":
                continue

            if t == "while_key_down":
                if cond.get("key") not in self.key_states:
                    return False

            if t == "toggle_with_key":
                key = cond.get("key")
                if not key:
                    continue

                latch = self.toggle_latch.setdefault(macro, False)

                if key in self.key_states and not latch:
                    self.toggles[macro] = not self.toggles.get(macro, False)
                    self.toggle_latch[macro] = True
                elif key not in self.key_states:
                    self.toggle_latch[macro] = False

                if not self.toggles.get(macro, False):
                    return False

            if t == "mouse_button":
                if str(cond.get("button")) not in self.mouse_states:
                    return False

            if t == "action_from_key":
                key = cond.get("key")
                if not key:
                    continue

                latch = self.action_from_key_latch.setdefault(macro, False)

                if key in self.key_states and not latch:
                    macro._fire_once = True
                    self.action_from_key_latch[macro] = True
                elif key not in self.key_states:
                    self.action_from_key_latch[macro] = False

        return True

    # ============================================================
    # ACTIONS
    # ============================================================

    def _run_actions(self, macro, state):
        if not hasattr(macro, "steps"):
            return

        for step in macro.steps:
            t = step.get("type")
            p = step.get("params", {})

            if t == "press_key":
                k = p.get("key")
                if k:
                    self.keyboard_ctrl.press(k)
                    state["held_keys"].add(k)

            elif t == "release_key":
                k = p.get("key")
                if k:
                    self.keyboard_ctrl.release(k)
                    state["held_keys"].discard(k)

            elif t == "delay":
                time.sleep(p.get("ms", 10) / 1000)

            elif t == "mouse_click":
                btn = mouse.Button.left if p.get("button") == "left" else mouse.Button.right
                self.mouse_ctrl.press(btn)
                self.mouse_ctrl.release(btn)

    # ============================================================
    # CLEANUP
    # ============================================================

    def _cleanup_macro(self, macro):
        state = self.macro_state.get(macro)
        if not state:
            return

        for k in list(state["held_keys"]):
            try:
                self.keyboard_ctrl.release(k)
            except:
                pass

        state["held_keys"].clear()