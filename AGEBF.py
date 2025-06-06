bl_info = {
    "name": "IdentiRig GUI - Age and Bodyfat",
    "author": "Ranfagni",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > IDENTIRIG_GUI",
    "description": "Simple GUI for Age and Bodyfat controls",
    "category": "3D View"
}

import bpy

def get_age_bodyfat_collections():
    rig_name = bpy.context.scene.get("identirig_active")
    rig_coll = bpy.data.collections.get(rig_name) if rig_name else None
    if not rig_coll:
        print("[IDENTIRIG][AGEFAT] ❌ Rig non trovato.")
        return None, None, None

    gui = next((c for c in rig_coll.children if c.name.startswith("GUI")), None)
    if not gui:
        print("[IDENTIRIG][AGEFAT] ❌ GUI non trovata.")
        return None, None, None

    age = next((c for c in gui.children if c.name.startswith("AGE")), None)
    bf = next((c for c in gui.children if c.name.startswith("BF")), None)

    if not age:
        print("[IDENTIRIG][AGEFAT] ❌ AGE non trovata.")
    if not bf:
        print("[IDENTIRIG][AGEFAT] ❌ BF non trovata.")

    return gui, age, bf

def update_agefat_slider(self, context):
    _, age_coll, bf_coll = get_age_bodyfat_collections()

    # AGE
    if age_coll:
        age_targets = {
            "old": "OLD",
            "young": "YOUNG",
        }
        for attr, prefix in age_targets.items():
            value = getattr(self, attr, None)
            if value is None:
                continue
            for obj in age_coll.all_objects:
                if obj.name.startswith(prefix):
                    obj.location.x = value
                    obj.keyframe_insert(data_path="location", index=0)
                    print(f"[IDENTIRIG][AGE] ✅ {obj.name}.location.x = {value}")

    # BODYFAT
    if bf_coll:
        bf_targets = {
            "fat": "FAT",
            "slim": "SLIM",
            "flabby": "BF.001",  # questo nome va tenuto perché usato così nel file originale
        }
        for attr, prefix in bf_targets.items():
            value = getattr(self, attr, None)
            if value is None:
                continue
            for obj in bf_coll.all_objects:
                if obj.name.startswith(prefix):
                    obj.location.x = value
                    obj.keyframe_insert(data_path="location", index=0)
                    print(f"[IDENTIRIG][BODYFAT] ✅ {obj.name}.location.x = {value}")

class IDENTIRIG_PT_AGEFAT_PANEL(bpy.types.Panel):
    bl_label = "AGE / BODYFAT"
    bl_idname = "OBJECT_PT_agefat_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'IDENTIRIG_GUI'

    def draw(self, context):
        layout = self.layout
        props = context.scene

        layout.label(text="🕰️ AGE")
        layout.prop(props, "old", slider=True)
        layout.prop(props, "young", slider=True)

        layout.separator()
        layout.label(text="⚖️ BODYFAT")
        layout.prop(props, "fat", slider=True)
        layout.prop(props, "slim", slider=True)
        layout.prop(props, "flabby", slider=True)

def register():
    bpy.utils.register_class(IDENTIRIG_PT_AGEFAT_PANEL)

    bpy.types.Scene.old = bpy.props.FloatProperty(
        name="Old", default=0.0, min=0.0, max=1.0, update=update_agefat_slider)
    bpy.types.Scene.young = bpy.props.FloatProperty(
        name="Young", default=0.0, min=0.0, max=1.0, update=update_agefat_slider)

    bpy.types.Scene.fat = bpy.props.FloatProperty(
        name="Fat", default=0.0, min=0.0, max=1.0, update=update_agefat_slider)
    bpy.types.Scene.slim = bpy.props.FloatProperty(
        name="Slim", default=0.0, min=0.0, max=1.0, update=update_agefat_slider)
    bpy.types.Scene.flabby = bpy.props.FloatProperty(
        name="Flabby", default=0.0, min=0.0, max=1.0, update=update_agefat_slider)

def unregister():
    bpy.utils.unregister_class(IDENTIRIG_PT_AGEFAT_PANEL)

    del bpy.types.Scene.old
    del bpy.types.Scene.young
    del bpy.types.Scene.fat
    del bpy.types.Scene.slim
    del bpy.types.Scene.flabby

if __name__ == "__main__":
    register()
