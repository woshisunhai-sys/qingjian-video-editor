#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Static validation for an AI drama first-frame run plan.
No API calls or actual media generation. Run from skill root:
    python scripts/validate_run_plan.py examples/example_run_plan.json
Optional:
    python scripts/validate_run_plan.py path/to/run_plan.json --check-files --assets-root /path/to/project
"""
import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

SHOT_STATUSES = {"planned", "blocked", "ready", "submitted", "accepted",
                 "trim", "retry_i2va", "skipped", "manual_review"}
GLOBAL_STATUSES = {"planned", "ready", "failed", "blocked"}
FORBIDDEN = {
    "position_reference_image", "shot_position_reference_image",
    "position_map_image", "position_guide_image", "location_reference_image",
    "shot_position_image", "last_frame_image", "end_frame_image",
    "per_shot_global_image"
}

def fail(errors, msg):
    errors.append(str(msg))

def is_number(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)

def is_path(x):
    return isinstance(x, str) and bool(x.strip())

def index_objects(items, name, errors):
    if not isinstance(items, list):
        fail(errors, f"{name}: must be an array")
        return {}
    out = {}
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            fail(errors, f"{name}[{i}]: must be object")
            continue
        key = item.get("id")
        if not isinstance(key, str) or not key.strip():
            fail(errors, f"{name}[{i}]: id missing")
        elif key in out:
            fail(errors, f"{name}[{i}]: duplicate id {key}")
        else:
            out[key] = item
    return out

def check_path(path_value, label, errors, check_files, root):
    if path_value is None:
        return
    if not is_path(path_value):
        fail(errors, f"{label}: must be a nonempty path/URI or null")
        return
    if not check_files:
        return
    parsed = urlparse(path_value)
    # Only local paths can be checked here. Asset URIs must be verified by the client.
    if parsed.scheme and parsed.scheme not in {"file"}:
        return
    path = Path(parsed.path if parsed.scheme == "file" else path_value)
    base = root.resolve()
    full = (path if path.is_absolute() else base / path).resolve()
    if not path.is_absolute() and not full.is_relative_to(base):
        fail(errors, f"{label}: path escapes the assets root")
    elif not full.is_file():
        fail(errors, f"{label}: file not found: {full}")

def check(data, check_files=False, root=None):
    errors, warnings = [], []
    root = root or Path(".")
    if not isinstance(data, dict):
        return ["root must be an object"], warnings
    if data.get("schema_version") != "1.0":
        fail(errors, "schema_version must be '1.0'")
    if not is_path(data.get("episode_id")):
        fail(errors, "episode_id is required")
    config = data.get("config")
    if not isinstance(config, dict):
        fail(errors, "config must be object")
        config = {}
    if config.get("video_mode") != "I2VA":
        fail(errors, "config.video_mode must be I2VA")
    if not isinstance(config.get("allow_fl2va_fallback"), bool):
        fail(errors, "config.allow_fl2va_fallback must be boolean")
    retries = config.get("max_video_retries")
    if not isinstance(retries, int) or isinstance(retries, bool) or retries < 0:
        fail(errors, "config.max_video_retries must be integer >= 0")
        retries = 0
    concurrency = config.get("max_parallel_video_jobs")
    if not isinstance(concurrency, int) or isinstance(concurrency, bool) or concurrency < 1:
        fail(errors, "config.max_parallel_video_jobs must be integer >= 1")

    scenes = index_objects(data.get("scenes"), "scenes", errors)
    states = index_objects(data.get("global_states"), "global_states", errors)
    shots = index_objects(data.get("shots"), "shots", errors)

    for sid, scene in scenes.items():
        check_path(scene.get("scene_reference_image"), f"scene {sid} scene_reference_image",
                   errors, check_files, root)
        if not is_path(scene.get("scene_reference_image")):
            fail(errors, f"scene {sid}: scene_reference_image required")
        for field in ("character_reference_images", "prop_reference_images"):
            obj = scene.get(field, {})
            if not isinstance(obj, dict):
                fail(errors, f"scene {sid}: {field} must be object")
                continue
            for asset_id, paths in obj.items():
                if not isinstance(paths, list) or not paths:
                    fail(errors, f"scene {sid}: {field}[{asset_id}] must be nonempty array")
                    continue
                for j, path in enumerate(paths):
                    check_path(path, f"scene {sid} {field}[{asset_id}][{j}]",
                               errors, check_files, root)

    for state_id, state in states.items():
        scene_id = state.get("scene_id")
        parent_id = state.get("parent_state_id")
        if scene_id not in scenes:
            fail(errors, f"state {state_id}: unknown scene {scene_id!r}")
        if not (parent_id is None or isinstance(parent_id, str)):
            fail(errors, f"state {state_id}: invalid parent_state_id")
        elif parent_id is not None:
            if parent_id not in states:
                fail(errors, f"state {state_id}: unknown parent {parent_id!r}")
            elif states[parent_id].get("scene_id") != scene_id:
                fail(errors, f"state {state_id}: parent belongs to another scene")
            elif parent_id == state_id:
                fail(errors, f"state {state_id}: cannot parent itself")
        layout = state.get("editor_layout")
        if not isinstance(layout, dict) or not layout:
            fail(errors, f"state {state_id}: editor_layout must be nonempty object")
        status = state.get("status")
        if status not in GLOBAL_STATUSES:
            fail(errors, f"state {state_id}: illegal status {status!r}")
        path = state.get("global_reference_image")
        check_path(path, f"state {state_id} global_reference_image",
                   errors, check_files, root)
        if status == "ready" and not is_path(path):
            fail(errors, f"state {state_id}: ready requires real global_reference_image")
        if not is_path(state.get("change_reason")):
            fail(errors, f"state {state_id}: change_reason required")

    for sid in states:
        seen, cur = set(), sid
        while cur in states:
            if cur in seen:
                fail(errors, f"state parent cycle detected at {sid}")
                break
            seen.add(cur)
            cur = states[cur].get("parent_state_id")

    previous_out = {}
    valid_dependencies = set(shots) | {"global:"+x for x in states}
    graph = {}
    for sid, shot in shots.items():
        prefix = f"shot {sid}"
        scene = shot.get("scene_id")
        before, after = shot.get("global_state_in"), shot.get("global_state_out")
        if scene not in scenes:
            fail(errors, f"{prefix}: unknown scene {scene!r}")
        for key, state_id in (("in", before), ("out", after)):
            if state_id not in states:
                fail(errors, f"{prefix}: unknown global_state_{key} {state_id!r}")
            elif states[state_id].get("scene_id") != scene:
                fail(errors, f"{prefix}: global_state_{key} belongs to another scene")
        if before in states and after in states and before != after:
            if states[after].get("parent_state_id") != before:
                fail(errors, f"{prefix}: transition must be direct child of {before}")
        if scene in previous_out and previous_out[scene] != before:
            fail(errors, f"{prefix}: continuity mismatch; previous state "
                         f"{previous_out[scene]} but current start {before}")
        if scene in scenes and after in states:
            previous_out[scene] = after
        for key in FORBIDDEN:
            if key in shot:
                fail(errors, f"{prefix}: forbidden per-shot position image field {key}")

        if not is_path(shot.get("source_shot_id")):
            fail(errors, f"{prefix}: source_shot_id required")
        for key in ("camera", "start_state", "main_action", "end_state",
                    "first_frame_prompt", "h3_prompt"):
            if not is_path(shot.get(key)):
                fail(errors, f"{prefix}: {key} must be nonempty text")
        duration = shot.get("generation_duration_seconds")
        cut = shot.get("target_cut_seconds")
        if not isinstance(duration, int) or isinstance(duration, bool) or duration <= 0:
            fail(errors, f"{prefix}: generation_duration_seconds must be positive integer")
        elif not 4 <= duration <= 15:
            warnings.append(f"{prefix}: {duration}s outside typical H3 4-15s; verify provider")
        if not is_number(cut) or cut <= 0:
            fail(errors, f"{prefix}: target_cut_seconds must be positive number")
        elif isinstance(duration, int) and cut > duration:
            fail(errors, f"{prefix}: target_cut_seconds exceeds generation duration")

        status = shot.get("status")
        if status not in SHOT_STATUSES:
            fail(errors, f"{prefix}: illegal status {status!r}")
        mode = shot.get("video_mode")
        if mode != "I2VA":
            if not (mode == "FL2VA" and config.get("allow_fl2va_fallback") is True
                    and shot.get("retry_count", 0) > 0
                    and is_path(shot.get("failure_reason"))):
                fail(errors, f"{prefix}: only I2VA permitted unless explicit failed I2VA fallback")
        first = shot.get("first_frame_image")
        video = shot.get("video_file")
        check_path(first, f"{prefix} first_frame_image", errors, check_files, root)
        check_path(video, f"{prefix} video_file", errors, check_files, root)
        if status in ("ready", "submitted", "accepted", "trim") and not is_path(first):
            fail(errors, f"{prefix}: {status} requires first_frame_image")
        if status in ("submitted", "accepted", "trim") and not is_path(shot.get("task_id")):
            # completed media may have been imported; require traceability in this plan.
            fail(errors, f"{prefix}: {status} requires real task_id")
        if status in ("accepted", "trim") and not is_path(video):
            fail(errors, f"{prefix}: {status} requires video_file")
        if status == "skipped":
            if not is_path(shot.get("failure_reason")):
                fail(errors, f"{prefix}: skipped requires failure_reason")
            if before != after and not is_path(shot.get("continuity_warning")):
                fail(errors, f"{prefix}: skipped transition requires continuity_warning")
        retry_count = shot.get("retry_count", 0)
        if not isinstance(retry_count, int) or isinstance(retry_count, bool) or retry_count < 0:
            fail(errors, f"{prefix}: retry_count must be nonnegative integer")
        elif retry_count > retries:
            warnings.append(f"{prefix}: retry_count exceeds configured automatic retry limit")

        deps = shot.get("dependencies", [])
        if not isinstance(deps, list):
            fail(errors, f"{prefix}: dependencies must be an array")
            deps = []
        graph[sid] = []
        if "global:"+str(before) not in deps:
            warnings.append(f"{prefix}: add dependency global:{before}")
        for dep in deps:
            if not isinstance(dep, str):
                fail(errors, f"{prefix}: dependency must be a string")
            elif dep not in valid_dependencies:
                fail(errors, f"{prefix}: unknown dependency {dep}")
            elif dep == sid:
                fail(errors, f"{prefix}: self dependency")
            elif not dep.startswith("global:"):
                graph[sid].append(dep)

    visited, active = set(), set()
    def visit(node):
        if node in active:
            fail(errors, f"task dependency cycle at {node}")
            return
        if node in visited:
            return
        visited.add(node)
        active.add(node)
        for dest in graph.get(node, []):
            visit(dest)
        active.remove(node)
    for sid in graph:
        visit(sid)
    return errors, warnings

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_plan", type=Path)
    parser.add_argument("--check-files", action="store_true",
                        help="check that local asset/media files really exist")
    parser.add_argument("--assets-root", type=Path, default=None,
                        help="base directory for relative file paths; defaults to run plan directory")
    args = parser.parse_args()
    try:
        data = json.loads(args.run_plan.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        print("INVALID: unable to read run plan:", exc)
        return 2
    root = args.assets_root or args.run_plan.parent
    errors, warnings = check(data, check_files=args.check_files, root=root)
    for msg in warnings:
        print("WARN:", msg)
    for msg in errors:
        print("ERROR:", msg)
    if errors:
        print(f"INVALID: {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    print(f"VALID: {len(data.get('global_states', []))} state(s), "
          f"{len(data.get('shots', []))} shot(s), {len(warnings)} warning(s)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
