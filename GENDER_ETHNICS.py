import bpy

def get_active_identirig_collections():
    rig_name = bpy.context.scene.get("identirig_active")
    rig_coll = bpy.data.collections.get(rig_name) if rig_name else None
    if not rig_coll:
        print("[IDENTIRIG][ETHNIC] ❌ Rig non trovato.")
        return None, None

    gui = next((c for c in rig_coll.children if c.name.startswith("GUI")), None)
    if not gui:
        print("[IDENTIRIG][ETHNIC] ❌ GUI non trovata.")
        return None, None

    base = next((c for c in gui.children if c.name.startswith("BASE")), None)
    if not base:
        print("[IDENTIRIG][ETHNIC] ❌ BASE non trovata.")
        return None, None

    return gui, base

def get_gender_collection():
    rig_name = bpy.context.scene.get("identirig_active")
    rig_coll = bpy.data.collections.get(rig_name) if rig_name else None
    if not rig_coll:
        return None

    gui = next((c for c in rig_coll.children if c.name.startswith("GUI")), None)
    if not gui:
        return None

    gender_ethn = next((c for c in gui.children if c.name.startswith("GENDER_ETHN")), None)
    if not gender_ethn:
        print("[IDENTIRIG][GENDER] ❌ GENDER_ETHN non trovata.")
        return None

    return gender_ethn

def update_ethnic_slider(self, context):
    gui, base = get_active_identirig_collections()
    gender_ethn = get_gender_collection()
    if not base:
        return

    # ETHNIC TARGETS
    ethnic_targets = {
        "asian": "ASIAN_BASE",
        "african": "AFRICAN_BASE",
        "caucasian": "CAUCASIAN_BASE",
        "latino": "LATINO_BASE",
    }

    for attr, prefix in ethnic_targets.items():
        value = getattr(self, attr, None)
        if value is None:
            continue

        for obj in base.all_objects:
            if obj.name.startswith(prefix):
                obj.location.x = value
                obj.location.y = value
                obj.location.z = value
                obj.keyframe_insert(data_path="location", index=0)
                obj.keyframe_insert(data_path="location", index=1)
                obj.keyframe_insert(data_path="location", index=2)
                print(f"[IDENTIRIG][ETHNIC] ✅ {obj.name}.location.xyz = ({value}, {value}, {value})")

    # GENDER TARGETS
    if not gender_ethn:
        return

    gender_targets = {
        "male_caucasian": "MALE_CAUCASIAN_SLIDE",
        "female_caucasian": "FEMALE_CAUCASIAN_SLIDE",
        "male_african": "MALE_AFRICAN_SLIDE",
        "female_african": "FEMALE_AFRICAN_SLIDE",
        "male_asian": "MALE_ASIAN_SLIDE",
        "female_asian": "FEMALE_ASIAN_SLIDE",
        "male_latino": "MALE_LATINO_SLIDE",
        "female_latino": "FEMALE_LATINO_SLIDE",
    }

    for attr, prefix in gender_targets.items():
        value = getattr(self, attr, None)
        if value is None:
            continue

        for obj in gender_ethn.all_objects:
            if obj.name.startswith(prefix):
                obj.location.x = value
                obj.keyframe_insert(data_path="location", index=0)
                print(f"[IDENTIRIG][GENDER] ✅ {obj.name}.location.x = {value}")

class ETHNIC_Module(bpy.types.Panel):
    bl_label = "ETHNIC & GENDER Module"
    bl_idname = "OBJECT_PT_ethnic_module"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'IDENTIRIG_GUI'

    def draw(self, context):
        layout = self.layout
        layout.label(text="🧬 Ethnic Base")
        layout.prop(context.scene, "asian", slider=True)
        layout.prop(context.scene, "african", slider=True)
        layout.prop(context.scene, "caucasian", slider=True)
        layout.prop(context.scene, "latino", slider=True)

        layout.separator()
        layout.label(text="👥 Gender Controls")
        layout.label(text="Caucasian")
        layout.prop(context.scene, "male_caucasian", slider=True)
        layout.prop(context.scene, "female_caucasian", slider=True)

        layout.label(text="African")
        layout.prop(context.scene, "male_african", slider=True)
        layout.prop(context.scene, "female_african", slider=True)

        layout.label(text="Asian")
        layout.prop(context.scene, "male_asian", slider=True)
        layout.prop(context.scene, "female_asian", slider=True)

        layout.label(text="Latino")
        layout.prop(context.scene, "male_latino", slider=True)
        layout.prop(context.scene, "female_latino", slider=True)

def register():
    bpy.utils.register_class(ETHNIC_Module)

    sliders = {
        "asian": "Asian",
        "african": "African",
        "caucasian": "Caucasian",
        "latino": "Latino",
        "male_caucasian": "Male Caucasian",
        "female_caucasian": "Female Caucasian",
        "male_african": "Male African",
        "female_african": "Female African",
        "male_asian": "Male Asian",
        "female_asian": "Female Asian",
        "male_latino": "Male Latino",
        "female_latino": "Female Latino",
    }

    for attr, label in sliders.items():
        setattr(bpy.types.Scene, attr, bpy.props.FloatProperty(
            name=label, default=0.0, min=0.0, max=1.0, update=update_ethnic_slider))

def unregister():
    bpy.utils.unregister_class(ETHNIC_Module)

    for attr in [
        "asian", "african", "caucasian", "latino",
        "male_caucasian", "female_caucasian",
        "male_african", "female_african",
        "male_asian", "female_asian",
        "male_latino", "female_latino",
    ]:
        delattr(bpy.types.Scene, attr)

if __name__ == "__main__":
    register()
