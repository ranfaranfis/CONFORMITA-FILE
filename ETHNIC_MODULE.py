bl_info = {
    "name": "IdentiRig GUI - Ethnicity & Gender",
    "author": "Ranfagni",
    "version": (1, 2),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > IDENTIRIG_GUI",
    "description": "Custom GUI for Ethnic and Gender Controls with collapsible sections",
    "category": "3D View"
}

import bpy

# === Property Group ===
class IdentirigGUIProps(bpy.types.PropertyGroup):
    # Foldouts
    show_ethnic: bpy.props.BoolProperty(name="Ethnic Base", default=True)
    show_caucasian: bpy.props.BoolProperty(name="Caucasian", default=True)
    show_african: bpy.props.BoolProperty(name="African", default=True)
    show_asian: bpy.props.BoolProperty(name="Asian", default=True)
    show_latino: bpy.props.BoolProperty(name="Latino", default=True)

    # Base ethnicity sliders
    asian: bpy.props.FloatProperty(name="Asian", default=0.0, min=0.0, max=1.0,
        update=lambda self, ctx: update_obj_location("GUI", "BASE", "ASIAN_BASE", self.asian))
    african: bpy.props.FloatProperty(name="African", default=0.0, min=0.0, max=1.0,
        update=lambda self, ctx: update_obj_location("GUI", "BASE", "AFRICAN_BASE", self.african))
    latino: bpy.props.FloatProperty(name="Latino", default=0.0, min=0.0, max=1.0,
        update=lambda self, ctx: update_obj_location("GUI", "BASE", "LATINO_BASE", self.latino))
    caucasian: bpy.props.FloatProperty(name="Caucasian", default=0.0, min=0.0, max=1.0,
        update=lambda self, ctx: update_obj_location("GUI", "BASE", "CAUCASIAN_BASE", self.caucasian))

    # Gender/Ethnicity sliders
    male_caucasian: bpy.props.FloatProperty(name="Male", default=0.0, min=0.0, max=1.0,
        update=lambda self, ctx: update_obj_location("GUI", "GENDER_ETHN", "MALE_CAUCASIAN_SLIDE", self.male_caucasian))
    female_caucasian: bpy.props.FloatProperty(name="Female", default=0.0, min=0.0, max=1.0,
        update=lambda self, ctx: update_obj_location("GUI", "GENDER_ETHN", "FEMALE_CAUCASIAN_SLIDE", self.female_caucasian))

    male_african: bpy.props.FloatProperty(name="Male", default=0.0, min=0.0, max=1.0,
        update=lambda self, ctx: update_obj_location("GUI", "GENDER_ETHN", "MALE_AFRICAN_SLIDE", self.male_african))
    female_african: bpy.props.FloatProperty(name="Female", default=0.0, min=0.0, max=1.0,
        update=lambda self, ctx: update_obj_location("GUI", "GENDER_ETHN", "FEMALE_AFRICAN_SLIDE", self.female_african))

    male_asian: bpy.props.FloatProperty(name="Male", default=0.0, min=0.0, max=1.0,
        update=lambda self, ctx: update_obj_location("GUI", "GENDER_ETHN", "MALE_ASIAN_SLIDE", self.male_asian))
    female_asian: bpy.props.FloatProperty(name="Female", default=0.0, min=0.0, max=1.0,
        update=lambda self, ctx: update_obj_location("GUI", "GENDER_ETHN", "FEMALE_ASIAN_SLIDE", self.female_asian))

    male_latino: bpy.props.FloatProperty(name="Male", default=0.0, min=0.0, max=1.0,
        update=lambda self, ctx: update_obj_location("GUI", "GENDER_ETHN", "MALE_LATINO_SLIDE", self.male_latino))
    female_latino: bpy.props.FloatProperty(name="Female", default=0.0, min=0.0, max=1.0,
        update=lambda self, ctx: update_obj_location("GUI", "GENDER_ETHN", "FEMALE_LATINO_SLIDE", self.female_latino))

# === Update Function ===
def update_obj_location(root_coll, sub_coll, obj_name, value):
    try:
        obj = bpy.data.collections[root_coll].children[sub_coll].objects[obj_name]
        obj.location.x = value
    except Exception as e:
        print(f"❌ Errore aggiornando {obj_name}: {e}")

# === Main Panel ===
class IDENTIRIG_PT_GUI_PANEL(bpy.types.Panel):
    bl_label = "ETHNICITY"
    bl_idname = "IDENTIRIG_PT_GUI_PANEL"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'IDENTIRIG_GUI'

    def draw(self, context):
        layout = self.layout
        props = context.scene.identirig_gui_props

        layout.label(text="🧬 ETHNIC BASE", icon="GROUP")
        box = layout.box()
        box.prop(props, "show_ethnic", icon="TRIA_DOWN" if props.show_ethnic else "TRIA_RIGHT", emboss=False)
        if props.show_ethnic:
            box.prop(props, "asian")
            box.prop(props, "african")
            box.prop(props, "latino")
            box.prop(props, "caucasian")

        layout.separator()
        layout.label(text="👥 GENDER CONTROLS", icon="MOD_ARMATURE")

        # Caucasian
        col = layout.box()
        col.prop(props, "show_caucasian", icon="TRIA_DOWN" if props.show_caucasian else "TRIA_RIGHT", emboss=False)
        if props.show_caucasian:
            col.prop(props, "male_caucasian")
            col.prop(props, "female_caucasian")

        # African
        col = layout.box()
        col.prop(props, "show_african", icon="TRIA_DOWN" if props.show_african else "TRIA_RIGHT", emboss=False)
        if props.show_african:
            col.prop(props, "male_african")
            col.prop(props, "female_african")

        # Asian
        col = layout.box()
        col.prop(props, "show_asian", icon="TRIA_DOWN" if props.show_asian else "TRIA_RIGHT", emboss=False)
        if props.show_asian:
            col.prop(props, "male_asian")
            col.prop(props, "female_asian")

        # Latino
        col = layout.box()
        col.prop(props, "show_latino", icon="TRIA_DOWN" if props.show_latino else "TRIA_RIGHT", emboss=False)
        if props.show_latino:
            col.prop(props, "male_latino")
            col.prop(props, "female_latino")

# === Register ===
classes = [
    IdentirigGUIProps,
    IDENTIRIG_PT_GUI_PANEL
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.identirig_gui_props = bpy.props.PointerProperty(type=IdentirigGUIProps)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.identirig_gui_props

if __name__ == "__main__":
    register()
