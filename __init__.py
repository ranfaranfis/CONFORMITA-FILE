bl_info = {
    "name": "IDENTILIBRARY",
    "author": "Tu",
    "version": (4, 2),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > IDENTIRIG_GUI",
    "description": "A FULL COMPLETE LIBRARY FOR IDENTIRIG",
    "category": "3D View"
}

import bpy
import json
import os
import ftplib

ftp_file_list = []
local_file_list = []
character_origin_frames = {}

TYPES = [
    ("HAIR", "Hair", ""),
    ("BEARD", "Beard", ""),
    ("EYEBROWS_GN", "Eyebrows", "")
]

# ----------------------
# DISPLACEMENT FUNCTIONS
# ----------------------
def get_displacement_data(obj):
    data = {"MICROSKIN": [], "WRINKLES": []}
    for mod in obj.modifiers:
        if mod.type == 'DISPLACE' and mod.texture and mod.texture.type == 'IMAGE':
            base_name = mod.name.split("_", 1)[-1] if "_" in mod.name else mod.name
            if "MicroSkin_" in mod.name:
                data["MICROSKIN"].append({
                    "name": base_name,
                    "region": mod.name.replace("MicroSkin_", ""),
                    "texture": mod.texture.image.filepath if mod.texture and mod.texture.image else "",
                    "strength": mod.strength,
                    "scale": getattr(mod.texture, "repeat_x", 1),
                    "coords": mod.texture_coords,
                })
            elif "Wrinkles_" in mod.name:
                data["WRINKLES"].append({
                    "name": base_name,
                    "region": mod.name.replace("Wrinkles_", ""),
                    "texture": mod.texture.image.filepath if mod.texture and mod.texture.image else "",
                    "strength": mod.strength,
                    "scale": getattr(mod.texture, "repeat_x", 1),
                    "coords": mod.texture_coords,
                })
    return data

def save_displacement_for_character(library_path, char_name, mesh_name="HEAD"):
    obj = bpy.data.objects.get(mesh_name)
    if not obj:
        print(f"[Displacement] Object '{mesh_name}' not found.")
        return
    disp_data = get_displacement_data(obj)
    disp_dir = os.path.join(library_path, "displacement")
    os.makedirs(disp_dir, exist_ok=True)
    json_path = os.path.join(disp_dir, f"{char_name}_displacement.json")
    with open(json_path, "w") as f:
        json.dump(disp_data, f, indent=4)
    print(f"[Displacement] Saved: {json_path}")

def load_displacement_json(library_path, char_name):
    disp_dir = os.path.join(library_path, "displacement")
    json_path = os.path.join(disp_dir, f"{char_name}_displacement.json")
    if not os.path.exists(json_path):
        return {}
    with open(json_path, "r") as f:
        return json.load(f)
    return {}

def apply_displacement_from_json(library_path, char_name, mesh_name="HEAD", set_keyframes=True, frame=None):
    obj = bpy.data.objects.get(mesh_name)
    if not obj:
        print(f"[Displacement] Object '{mesh_name}' not found.")
        return
    disp_data = load_displacement_json(library_path, char_name)
    if frame is None:
        frame = bpy.context.scene.frame_current
    for d_type in ["MICROSKIN", "WRINKLES"]:
        for disp in disp_data.get(d_type, []):
            base_name = disp["name"]
            mod_name = f"{char_name}_{base_name}"
            mod = obj.modifiers.get(mod_name)
            if not mod:
                mod = obj.modifiers.new(mod_name, 'DISPLACE')
                mod.texture_coords = disp.get("coords", "LOCAL")
                tex = bpy.data.textures.get(mod_name) or bpy.data.textures.new(mod_name, type='IMAGE')
                try:
                    tex.image = bpy.data.images.load(disp["texture"], check_existing=True)
                except Exception as e:
                    print(f"[Displacement] Could not load texture: {disp['texture']} ({e})")
                    continue
                tex.repeat_x = tex.repeat_y = disp.get("scale", 1)
                mod.texture = tex
                mod.vertex_group = f"{disp['region']}_DISPLACEMENT_TEX"
            mod.strength = disp["strength"]
            if set_keyframes:
                mod.keyframe_insert(data_path="strength", frame=frame)
    bpy.context.scene.frame_set(bpy.context.scene.frame_current)

def fadeout_displacements(personaggio, frame_origin, frame_morph_start, frame_morph_end, library_path, mesh_name="HEAD"):
    obj = bpy.data.objects.get(mesh_name)
    if not obj:
        return
    disp_data = load_displacement_json(library_path, personaggio)
    for d_type in ["MICROSKIN", "WRINKLES"]:
        for disp in disp_data.get(d_type, []):
            base_name = disp["name"]
            mod_name = f"{personaggio}_{base_name}"
            mod = obj.modifiers.get(mod_name)
            if not mod:
                mod = obj.modifiers.new(mod_name, 'DISPLACE')
                mod.texture_coords = disp.get("coords", "LOCAL")
                tex = bpy.data.textures.get(mod_name) or bpy.data.textures.new(mod_name, type='IMAGE')
                try:
                    tex.image = bpy.data.images.load(disp["texture"], check_existing=True)
                except Exception as e:
                    print(f"[Displacement] Could not load texture: {disp['texture']} ({e})")
                    continue
                tex.repeat_x = tex.repeat_y = disp.get("scale", 1)
                mod.texture = tex
                mod.vertex_group = f"{disp['region']}_DISPLACEMENT_TEX"
            # Chiavi: origine, morph_start, morph_end
            mod.strength = disp["strength"]
            mod.keyframe_insert(data_path="strength", frame=frame_origin)
            mod.strength = disp["strength"]
            mod.keyframe_insert(data_path="strength", frame=frame_morph_start)
            mod.strength = 0
            mod.keyframe_insert(data_path="strength", frame=frame_morph_end)
    bpy.context.scene.frame_set(bpy.context.scene.frame_current)

# --------------------
# GROOMING FUNCTIONS
# --------------------
def clear_grooming_collection():
    col = bpy.data.collections.get("GROOMING")
    if col:
        for obj in col.all_objects:
            bpy.data.objects.remove(obj, do_unlink=True)
        for c in col.children:
            col.children.unlink(c)

def key_geometry_nodes_inputs(obj, frame, value=None):
    if not obj.modifiers:
        return
    for mod in obj.modifiers:
        if mod.type == 'NODES' and mod.node_group:
            for node in mod.node_group.nodes:
                if "Density_Ctl" in node.name or "TrimLength_Ctl" in node.name:
                    input_socket = node.inputs[0]
                    if value is not None:
                        input_socket.default_value = value
                    input_socket.keyframe_insert("default_value", frame=frame)
                if node.name == "FHTG_SetHairCurveProfile":
                    if len(node.inputs) > 5:
                        if value is not None:
                            node.inputs[3].default_value = value
                            node.inputs[4].default_value = value
                            node.inputs[5].default_value = value
                        node.inputs[3].keyframe_insert("default_value", frame=frame)
                        node.inputs[4].keyframe_insert("default_value", frame=frame)
                        node.inputs[5].keyframe_insert("default_value", frame=frame)

def save_preset_data(filepath, obj_list):
    data = {}
    for obj in obj_list:
        if obj.type != 'CURVES':
            continue
        entry = {}
        for mod in obj.modifiers:
            if mod.type == 'NODES' and mod.node_group:
                for node in mod.node_group.nodes:
                    if "Density_Ctl" in node.name:
                        entry["grooming_default_density"] = node.inputs[0].default_value
                    elif "TrimLength_Ctl" in node.name:
                        entry["grooming_default_length"] = node.inputs[0].default_value
                    elif node.name == "FHTG_SetHairCurveProfile":
                        entry["grooming_default_shape"] = node.inputs[3].default_value
                        entry["grooming_default_size"] = node.inputs[4].default_value
                        entry["grooming_default_root"] = node.inputs[5].default_value
        data[obj.name] = entry
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

def load_preset_data(filepath):
    if not os.path.exists(filepath):
        return {}
    with open(filepath, 'r') as f:
        return json.load(f)

def key_and_zero_previous(character, type_, offset=10):
    if not character: return
    frame = bpy.context.scene.frame_current
    grooming = bpy.data.collections.get("GROOMING")
    if not grooming: return
    type_col = grooming.children.get(type_)
    if not type_col: return
    char_col = type_col.children.get(character)
    if not char_col: return
    bpy.context.scene.frame_set(frame - offset)
    gui = bpy.data.collections.get("GUI")
    if gui:
        for obj in gui.all_objects:
            if obj.type == 'MESH':
                for attr in ["location", "rotation_euler", "scale"]:
                    obj.keyframe_insert(data_path=attr, frame=frame - offset)
    for obj in char_col.all_objects:
        if obj.type == 'CURVES':
            key_geometry_nodes_inputs(obj, frame - offset)
    bpy.context.scene.frame_set(frame)
    for obj in char_col.all_objects:
        if obj.type == 'CURVES':
            key_geometry_nodes_inputs(obj, frame, value=0.0)

# -------------
# PREFERENCES/FTP
# -------------
class UnifiedLibraryPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    last_path: bpy.props.StringProperty(name="Last Used Library Path", subtype='DIR_PATH')
    def draw(self, context):
        self.layout.prop(self, "last_path")

def save_prefs_library_path(context):
    prefs = bpy.context.preferences.addons[__name__].preferences
    props = context.scene.unified_lib_props
    prefs.last_path = props.library_path

def load_prefs_library_path(context):
    prefs = bpy.context.preferences.addons[__name__].preferences
    if prefs.last_path:
        context.scene.unified_lib_props.library_path = prefs.last_path

def ftp_upload_dir(ftp, local_dir, remote_dir):
    if not os.path.isdir(local_dir):
        return
    try:
        ftp.mkd(remote_dir)
    except Exception:
        pass
    for item in os.listdir(local_dir):
        local_path = os.path.join(local_dir, item)
        remote_path = f"{remote_dir}/{item}"
        if os.path.isdir(local_path):
            ftp_upload_dir(ftp, local_path, remote_path)
        else:
            with open(local_path, 'rb') as f:
                try:
                    ftp.storbinary(f"STOR " + remote_path, f)
                except Exception as e:
                    print(f"[FTP UPLOAD ERROR] {e}")

class UNIFIEDLIB_OT_save_ftp(bpy.types.Operator):
    bl_idname = "unified_lib.save_ftp"
    bl_label = "Save to FTP"
    def execute(self, context):
        props = context.scene.unified_lib_props
        try:
            ftp = ftplib.FTP("ftp.workshops.homepc.it")
            ftp.login()
            ftp.cwd("FTP/LIBRARY")
            local_dir = props.library_path
            remote_dir = os.path.basename(local_dir)
            ftp_upload_dir(ftp, local_dir, remote_dir)
            ftp.quit()
        except Exception as e:
            self.report({'ERROR'}, f"FTP error: {e}")
            return {'CANCELLED'}
        self.report({'INFO'}, "Saved to FTP successfully.")
        return {'FINISHED'}

# -----------
# UI PROPERTY
# -----------
class UnifiedLibraryProps(bpy.types.PropertyGroup):
    library_path: bpy.props.StringProperty(name="Library Path", subtype='DIR_PATH')
    character_name: bpy.props.StringProperty(name="Character Name")
    chosen_type: bpy.props.EnumProperty(name="Grooming Type", items=TYPES, default="HAIR")
    ftp_selected_file: bpy.props.EnumProperty(name="FTP Characters", items=lambda self, context: ftp_file_list)
    local_selected_file: bpy.props.EnumProperty(name="Local Characters", items=lambda self, context: local_file_list)
    replace_grooming: bpy.props.BoolProperty(name="Replace Grooming", default=True)
    transition_frames: bpy.props.IntProperty(name="Transition Frames", default=10, min=0)
    do_morphing: bpy.props.BoolProperty(name="Morphing Transition", default=False)
    save_preset: bpy.props.BoolProperty(name="Save Preset", default=False)
    save_displacement: bpy.props.BoolProperty(name="Save Displacement", default=True)
    load_displacement: bpy.props.BoolProperty(name="Load Displacement", default=True)

def notify(msg):
    def draw(self, _context):
        self.layout.label(text=msg)
    bpy.context.window_manager.popup_menu(draw, title="INFO", icon='INFO')

def refresh_ftp_list():
    global ftp_file_list
    try:
        ftp = ftplib.FTP("ftp.workshops.homepc.it")
        ftp.login()
        ftp.cwd("FTP/LIBRARY")
        files = ftp.nlst()
        ftp.quit()
        ftp_file_list.clear()
        ftp_file_list.extend([(f, f, "") for f in files if f.endswith('.json')])
    except Exception as e:
        print(f"[FTP ERROR] {e}")

def refresh_local_list(path):
    global local_file_list
    if not os.path.isdir(path): return
    files = [f for f in os.listdir(path) if f.endswith('_gui.json')]
    local_file_list.clear()
    local_file_list.extend([(f.replace('_gui.json', ''), f.replace('_gui.json', ''), "") for f in files])

# -------------
# FULL SAVE/LOAD
# -------------
def save_full_library(context):
    props = context.scene.unified_lib_props
    char, type_ = props.character_name, props.chosen_type
    gui = bpy.data.collections.get("GUI")
    gui_data = {}
    if gui:
        for o in gui.all_objects:
            if o.type == 'MESH':
                gui_data[o.name] = {"location": list(o.location)}
    gui_path = os.path.join(props.library_path, f"{char}_gui.json")
    with open(gui_path, 'w') as f:
        json.dump(gui_data, f, indent=4)
    preset_dir = os.path.join(props.library_path, type_, char)
    os.makedirs(preset_dir, exist_ok=True)
    blend_path = os.path.join(preset_dir, f"{char}.blend")
    json_path = os.path.join(preset_dir, f"{char}.json")
    preset_path = os.path.join(preset_dir, f"preset.json")
    grooming = bpy.data.collections.get("GROOMING")
    if grooming:
        objs = [o for o in grooming.all_objects if o.type in {"CURVES", "MESH"}]
        curves = [o for o in objs if o.type == "CURVES"]
        surfaces = [o for o in objs if o.type == "MESH"]
        node_groups = []
        for o in curves:
            for m in o.modifiers:
                if m.type == 'NODES' and m.node_group and m.node_group not in node_groups:
                    node_groups.append(m.node_group)
        bpy.data.libraries.write(blend_path, set(objs + [o.data for o in objs] + node_groups), path_remap='RELATIVE')
        with open(json_path, 'w') as f:
            json.dump({"curves": [o.name for o in curves], "surfaces": [o.name for o in surfaces]}, f, indent=4)
        if props.save_preset:
            save_preset_data(preset_path, curves)

def load_full_library(context):
    props = context.scene.unified_lib_props
    char, type_ = props.character_name, props.chosen_type
    offset = props.transition_frames
    morphing = props.do_morphing
    frame = bpy.context.scene.frame_current
    gui_path = os.path.join(props.library_path, f"{char}_gui.json")
    preset_dir = os.path.join(props.library_path, type_, char)
    blend_path = os.path.join(preset_dir, f"{char}.blend")
    json_path = os.path.join(preset_dir, f"{char}.json")
    preset_path = os.path.join(preset_dir, "preset.json")
    preset_data = load_preset_data(preset_path)
    if morphing:
        for prev_char, frame_origin in character_origin_frames.items():
            if prev_char != char:
                fadeout_displacements(
                    prev_char,
                    frame_origin,
                    frame - offset,
                    frame,
                    props.library_path
                )
    if props.replace_grooming:
        clear_grooming_collection()
    if os.path.exists(gui_path):
        with open(gui_path, 'r') as f:
            data = json.load(f)
        for name, info in data.items():
            o = bpy.data.objects.get(name)
            if o:
                o.location = info["location"]
                o.keyframe_insert(data_path="location", frame=frame)
    if os.path.exists(blend_path) and os.path.exists(json_path):
        with open(json_path, 'r') as f:
            data = json.load(f)
        obj_names = data.get("curves", []) + data.get("surfaces", [])
        with bpy.data.libraries.load(blend_path, link=False) as (from_, to_):
            to_.objects = [n for n in obj_names if n in from_.objects]
            to_.node_groups = from_.node_groups
        grooming = bpy.data.collections.get("GROOMING") or bpy.data.collections.new("GROOMING")
        if grooming.name not in bpy.context.scene.collection.children:
            bpy.context.scene.collection.children.link(grooming)
        type_col = bpy.data.collections.get(type_) or bpy.data.collections.new(type_)
        if type_col.name not in grooming.children:
            grooming.children.link(type_col)
        char_col = bpy.data.collections.new(char)
        type_col.children.link(char_col)
        for o in to_.objects:
            if o:
                bpy.context.scene.collection.objects.link(o)
                char_col.objects.link(o)
                if o.type == 'MESH':
                    o.hide_viewport = True
                    o.hide_render = True
        head_obj = bpy.data.objects.get("HEAD")
        if head_obj:
            base_names = ["IDENTIRIG_BaseBeard", "IDENTIRIG_BaseHairCut", "IDENTIRIG_EyebrowBase"]
            for obj in char_col.all_objects:
                if obj.type == 'MESH' and any(base in obj.name for base in base_names):
                    for mod in obj.modifiers:
                        if hasattr(mod, "target"):
                            mod.target = head_obj
                        if hasattr(mod, "origin"):
                            mod.origin = head_obj
        bpy.context.scene.frame_set(frame - offset)
        for obj in char_col.all_objects:
            if obj.type == 'CURVES':
                key_geometry_nodes_inputs(obj, frame - offset, value=0.0)
        bpy.context.scene.frame_set(frame)
        for obj in char_col.all_objects:
            if obj.type == 'CURVES':
                defaults = preset_data.get(obj.name, {})
                for mod in obj.modifiers:
                    if mod.type == 'NODES' and mod.node_group:
                        nodes = mod.node_group.nodes
                        if "Density_Ctl" in nodes:
                            v = defaults.get("grooming_default_density", 1.0)
                            nodes["Density_Ctl"].inputs[0].default_value = v
                            nodes["Density_Ctl"].inputs[0].keyframe_insert("default_value", frame=frame)
                        if "TrimLength_Ctl" in nodes:
                            v = defaults.get("grooming_default_length", 1.0)
                            nodes["TrimLength_Ctl"].inputs[0].default_value = v
                            nodes["TrimLength_Ctl"].inputs[0].keyframe_insert("default_value", frame=frame)
                        if "FHTG_SetHairCurveProfile" in nodes:
                            p = nodes["FHTG_SetHairCurveProfile"]
                            p.inputs[3].default_value = defaults.get("grooming_default_shape", 0.3)
                            p.inputs[4].default_value = defaults.get("grooming_default_size", 0.3)
                            p.inputs[5].default_value = defaults.get("grooming_default_root", 0.3)
                            p.inputs[3].keyframe_insert("default_value", frame=frame)
                            p.inputs[4].keyframe_insert("default_value", frame=frame)
                            p.inputs[5].keyframe_insert("default_value", frame=frame)
    # Sempre: chiavi displacement (fade-in per nuovo personaggio)
    apply_displacement_from_json(props.library_path, char, set_keyframes=True, frame=frame)
    if char not in character_origin_frames:
        character_origin_frames[char] = frame

# -------------
# PANEL & OPS
# -------------
class UNIFIEDLIB_OT_save(bpy.types.Operator):
    bl_idname = "unified_lib.save"
    bl_label = "Save Character"
    def execute(self, context):
        global character_origin_frames
        props = context.scene.unified_lib_props
        save_prefs_library_path(context)
        char = props.character_name
        frame_now = bpy.context.scene.frame_current
        if char not in character_origin_frames:
            character_origin_frames[char] = frame_now
        if props.save_displacement:
            save_displacement_for_character(props.library_path, char)
        save_full_library(context)
        notify("Saved successfully.")
        return {'FINISHED'}

class UNIFIEDLIB_OT_load(bpy.types.Operator):
    bl_idname = "unified_lib.load"
    bl_label = "Load Character"
    def execute(self, context):
        global previous_character
        global character_origin_frames
        props = context.scene.unified_lib_props
        char = props.character_name
        frame_now = bpy.context.scene.frame_current
        offset = props.transition_frames
        morphing = props.do_morphing

        # morph grooming/GUI fadeout (solo previous_character)
        if morphing and previous_character and previous_character != char:
            key_and_zero_previous(previous_character, props.chosen_type, offset)

        # morph displacement multipersonaggio fadeout
        if morphing and len(character_origin_frames) > 0:
            for prev_char, frame_origin in character_origin_frames.items():
                if prev_char != char:
                    fadeout_displacements(
                        prev_char,
                        frame_origin,
                        frame_now - offset,
                        frame_now,
                        props.library_path
                    )

        # carica libreria (curves, mesh, blend, preset ecc)
        load_full_library(context)

        # applica displacement fadein nuovo personaggio con keyframe
        apply_displacement_from_json(props.library_path, char, set_keyframes=True, frame=frame_now)

        # aggiorna memoria frame origine personaggio
        if char not in character_origin_frames:
            character_origin_frames[char] = frame_now

        previous_character = char

        notify("Loaded successfully.")
        return {'FINISHED'}


class UNIFIEDLIB_OT_refresh_local(bpy.types.Operator):
    bl_idname = "unified_lib.refresh_local"
    bl_label = "Refresh Local"
    def execute(self, context):
        refresh_local_list(context.scene.unified_lib_props.library_path)
        return {'FINISHED'}

class UNIFIEDLIB_OT_refresh_ftp(bpy.types.Operator):
    bl_idname = "unified_lib.refresh_ftp"
    bl_label = "Refresh FTP"
    def execute(self, context):
        refresh_ftp_list()
        return {'FINISHED'}

class UNIFIEDLIB_OT_set_from_local(bpy.types.Operator):
    bl_idname = "unified_lib.set_from_local"
    bl_label = "Load Local Character"
    def execute(self, context):
        p = context.scene.unified_lib_props
        p.character_name = p.local_selected_file
        bpy.ops.unified_lib.load()
        return {'FINISHED'}

class UNIFIEDLIB_OT_set_from_ftp(bpy.types.Operator):
    bl_idname = "unified_lib.set_from_ftp"
    bl_label = "Load FTP Character"
    def execute(self, context):
        p = context.scene.unified_lib_props
        p.character_name = p.ftp_selected_file.replace("_gui.json", "")
        local_path = os.path.join(p.library_path, p.ftp_selected_file)
        try:
            ftp = ftplib.FTP("ftp.workshops.homepc.it")
            ftp.login()
            ftp.cwd("FTP/LIBRARY")
            with open(local_path, 'wb') as f:
                ftp.retrbinary(f"RETR " + p.ftp_selected_file, f.write)
            ftp.quit()
        except Exception as e:
            self.report({'ERROR'}, f"FTP error: {e}")
            return {'CANCELLED'}
        bpy.ops.unified_lib.load()
        return {'FINISHED'}

class UNIFIEDLIB_PT_panel(bpy.types.Panel):
    bl_label = "Identirig Grooming Library"
    bl_idname = "UNIFIEDLIB_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "IDENTIRIG_GUI"

    def draw(self, context):
        p = context.scene.unified_lib_props
        l = self.layout
        l.prop(p, "library_path")
        l.prop(p, "character_name")
        l.prop(p, "chosen_type")
        l.prop(p, "replace_grooming")
        l.prop(p, "transition_frames")
        l.prop(p, "do_morphing")
        l.prop(p, "save_preset")
        l.prop(p, "save_displacement")
        l.prop(p, "load_displacement")
        l.operator("unified_lib.save")
        l.operator("unified_lib.load")
        l.operator("unified_lib.save_ftp", icon="EXPORT")
        l.separator()
        l.label(text="Local Characters")
        l.operator("unified_lib.refresh_local")
        l.prop(p, "local_selected_file")
        l.operator("unified_lib.set_from_local")
        l.separator()
        l.label(text="FTP Characters")
        l.operator("unified_lib.refresh_ftp")
        l.prop(p, "ftp_selected_file")
        l.operator("unified_lib.set_from_ftp")

classes = [
    UnifiedLibraryPreferences,
    UnifiedLibraryProps,
    UNIFIEDLIB_OT_save,
    UNIFIEDLIB_OT_load,
    UNIFIEDLIB_OT_save_ftp,
    UNIFIEDLIB_OT_refresh_local,
    UNIFIEDLIB_OT_refresh_ftp,
    UNIFIEDLIB_OT_set_from_local,
    UNIFIEDLIB_OT_set_from_ftp,
    UNIFIEDLIB_PT_panel
]

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Scene.unified_lib_props = bpy.props.PointerProperty(type=UnifiedLibraryProps)

def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
    del bpy.types.Scene.unified_lib_props

if __name__ == "__main__":
    register()
