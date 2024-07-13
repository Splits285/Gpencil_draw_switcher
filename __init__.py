bl_info = {
"name": "Grease Pencil material-brush bind-toggle-switcher (erase-switcher)",
"description": "Switch to a material and/or brush while a special gpencil.draw_switcher is held. Ideal for using holdout materials to erase strokes instead of erasing them by their vertices",
"author": "Splits285",
"version": (0, 0, 5),
"blender": (2, 8, 0),
"location": "Preferences > keymap > Grease Pencil. Add an entry for gpencil.draw_switcher",
"warning": "Eraser binds probably won't work, unless you can bind the eraser with an actual button-hit (not selecting it.) Bind the eraser on your pen to a keystroke instead.",
"doc_url": "https://github.com/Splits285/Gpencil_draw_switcher",
"tracker_url": "https://github.com/Splits285/Gpencil_draw_switcher/issues/",
"category": "User Interface",
}
import bpy

class GPencilDrawSwitcherOperator(bpy.types.Operator):
    bl_idname = "gpencil.draw_switcher"
    bl_label = "GPencil Draw custom (eraser switching)"
    global STORED_BRUSH_NAME
    STORED_BRUSH_NAME = None
    #=================================================================================================
    #define a billion properties which will be fed into the switch handling or fed into the gpencil.draw
    #which gpencil.draw_custom invokes.
    #These are displayed for the end user in their binding menu.bpy.context.tool_settings.gpencil_paint.brush
    #---------------------------------------------------------------
    #access with self.CDO_Mode
    CDO_Mode: bpy.props.EnumProperty(
        name="Mode", #goes next to textbox ui element
        description="Select an option",
        items=[
            #PYTHON     DROPDOWNNAME    DESCRIPTION
            ('DRAW', "Draw Freehand", "Description for Option 1"),
            ('DRAW_STRAIGHT', "Draw Straight Lines", "Who even uses this option?"),
            ('ERASER', "Eraser", "Erase Grease Pencil strokes.")
        ],
        default='ERASER',
    )
    #---------------------------------------------------------------
    #access with self.CDO_WaitForInput
    CDO_WaitForInput: bpy.props.BoolProperty(
        name="Wait For Input", #goes next to textbox ui element
        description="Wait for impact before starting to draw the stroke. You probably want this for the eraser binds, since you hold eraser binds before touching the draw surface.",
        default=True,
        update=lambda self, context: update_global_variable(self)
    )
    #-------------------------------------------------------------
    #access with self.CDO_TriggerBrushName
    CDO_TriggerBrushName: bpy.props.StringProperty(
        name="TriggerBrush", #goes next to textbox ui element in the keymap binding properties in keymap preferences.
        description="Brush name which, if in use, will enable the brush/material-switcher. \nIf no brush is named here brush/material-switching will happen on every brush",
        default='',
    )
    #-------------------------------------------------------------
    #access with self.CDO_SwitchBrush
    CDO_SwitchBrush: bpy.props.StringProperty(
        name="Switch To Brush", #goes next to textbox ui element in the keymap binding properties in keymap preferences.
        description="Case-sensitive brush to switch to in addition to material switching. If unset or brush doesn't exist, current brush will stay",
        default='',
    )
    #---------------------------------------------------------------
    #access with self.CDO_MaterialName
    CDO_MaterialName: bpy.props.StringProperty(
        name="Switch To Material", #goes next to textbox ui element in the keymap binding properties in keymap preferences.
        description="Material to switch to while held. Does nothing if unset. Note if we find and switch to the matching material Draw mode will be forced on, ignoring your setting.\n(What's the point of setting a material when you're just gonna erase?)", 
        default='', #no sample text
    )
    #---------------------------------------------------------------
    #access with self.CDO_DisableStabilizer
    CDO_DisableStabilizer: bpy.props.BoolProperty(
        name="No Stabilizer", #goes next to textbox ui element
        description="Disable stabilizer. For some reason this always seems ignored, even in the real gpencil.draw().\n\nDon't worry, your stabilization hotkey will still work as normal. Just like the real gpencil.draw().",
        default=False,
    )
    #---------------------------------------------------------------
    #access with self.CDO_DisableFill
    CDO_DisableFill: bpy.props.BoolProperty(
        name="No Fill Areas", #goes next to textbox ui element
        description="Disable Fills being made by this bind.",
        default=False,
    )
    #---------------------------------------------------------------
    #access with self.CDO_GuideLastAngle
    CDO_GuideLastAngle: bpy.props.FloatProperty(
        name="Angle", #goes next to textbox ui element
        description="Angle, Speed guide angle",
        default=0.0,
        min=-10000,
        max=10000,
    )
    #---------------------------------------------------------------
    #access with self.CDO_DisableStraight
    CDO_DisableStraight: bpy.props.BoolProperty(
        name="No Straight Lines", #goes next to textbox ui element
        description="No Straight Lines, Disable key for straight lines",
        default=False,
    )

    #=================================================================================

    def invoke(self, context, event):

        if context.active_object.type == 'GPENCIL':
            #print("Active object is a Grease Pencil")
            
            #This comes in being given event.type [see event in the parenthesis?]r (the bind which activated it) 
            #and event.value (pressed or released?) It's also why this is invoke instead of execute.

            #print("OP Activator key name and op-invoking state:", event.type, event.value)
            
            global TRIGGERKEY
            TRIGGERKEY = event.type
            global TRIGGERSTATE
            TRIGGERSTATE = event.value

            #print('inv TRIGGERKEY:', TRIGGERKEY)

            #TRIGGERSTATE should usually be down. You're mad if you purposely bind this operator to be on release.
            #Don't blame me especially if you did something worse, like bind it to "Any".

            CheckBrush = self.CDO_TriggerBrushName
            TriggerBrushActive = 0
            SetMode = self.CDO_Mode #Base state set by the user.

            if CheckBrush == "" or bpy.context.tool_settings.gpencil_paint.brush.name == CheckBrush:
                #print("no specified trigger brush, OR WE'RE ON IT.")
                TriggerBrushActive = 1
                pass

            elif bpy.context.tool_settings.gpencil_paint.brush.name != CheckBrush:
                #We aren't on the trigger brush. The material/brush-switching Trigger brush.
                #TriggerBrushActive is 0 in this condition.
                #print(bpy.context.tool_settings.gpencil_paint.brush, CheckBrush)
                #print("Active brush doesn't trigger gpencil switchur.")
                #print(SetMode," NO CAP----")
                #print(TriggerBrushActive)
                pass

#-----------If checkbrush is specified and active... do switchbrush checks-----------------------
            bruname = self.CDO_SwitchBrush
            #if brush is specified.... confirm it exists or switch the mode back.
            if bruname != "":
                #print("Switchbrush's name isn't empty.")
                #Does the brush exist?
                try:
                    bpy.data.brushes[bruname]
                except KeyError as e:
                    #print("Error: Brush not found, user-set state save us!!!!!!!!!")
                    #Handle this, we'll just stay in user-set-mode.
                    pass

            if TriggerBrushActive == 1:
                #print ("No Triggerbrush OR we're on it. The check passed, we should set draw mode and try to change stuff")
#~~~~~~~
                #print(bpy.context.tool_settings.gpencil_paint.brush.name," is the active brush. gonna try to store it")
                #context.scene.stored_brush_name does not exist normally and is declared in the register() function at the bottom.
                if bruname != "":
                    global STORED_BRUSH_NAME
                    STORED_BRUSH_NAME = bpy.context.tool_settings.gpencil_paint.brush.name
                        
                    #print("Stored: ",STORED_BRUSH_NAME,"")
                    #print("we got the desired switchbrush @ ", bpy.data.brushes[bruname],", and we're gonna try switching to it.")
                    #print("trigger brush is specified and we're trying to switch to it @L161")
                    #switch to it#
                    context.tool_settings.gpencil_paint.brush = bpy.data.brushes[bruname]    
#-----------------------------------------------------------------------------

                #context.scene.stored_material_index does not exist normally and is created in the register() function at the bottom.
                context.scene.stored_material_index = context.active_object.active_material_index
                #Get the index of the self.CDO_MaterialName material by looping over the materials in the scene context. The reason we set the index instead of setting it by name is because setting it by name changes the name field of the active brush instead of switching the active brush to the one named by the user. 
                if self.CDO_MaterialName != "":
                    for i, mat in enumerate(context.active_object.data.materials):
                        #print("Enumerating materials @ 187")
                        if mat.name == self.CDO_MaterialName:
                            #switch to it!
                            #print("switching to draw mode")
                            SetMode = "DRAW"
                            #print("switching to the material, step one.")
                            context.active_object.active_material_index = i
                            break

                else: ##if TriggerBrushActive == 0 and materialname is also unspecified. Brush switching is irrelephant here.:
                    pass
                    
        else:
            #print("Active object is not a Grease Pencil")
            pass

        #print("==============================")
        #print("Mode",self.CDO_Mode)
        #print("TriggerBrushName",self.CDO_TriggerBrushName)
        #print("SwitchBrushName",self.CDO_SwitchBrush)
        #print("MaterialName",self.CDO_MaterialName)
        #print("WaitForInput",self.CDO_WaitForInput)
        #print("DisableStabilizer",self.CDO_DisableStabilizer)
        #print("DisableStraight",self.CDO_DisableStraight)
        #print("CDO_GuideLastAngle",self.CDO_GuideLastAngle)
        #print("==============================")

        #Call the damn draw function. Finally.
        #Seriously, Why, blender!!!!! Why don't you have any information about gpencil.draw ending?! it's not an instant function, strokes can go on for minutes!

        bpy.ops.gpencil.draw(
            'INVOKE_DEFAULT',
            mode=              SetMode,
            wait_for_input=    self.CDO_WaitForInput,
            #For some reason when you pass stabilizer to gpencil.draw it just listens to whatever it had before.
            disable_stabilizer=self.CDO_DisableStabilizer,
            disable_straight=self.CDO_DisableStraight,
            disable_fill=self.CDO_DisableFill,
            guide_last_angle=self.CDO_GuideLastAngle,
        )
        
        #By default gpencil.draw waits for mouse input to start going which is really bad.
        #It's only helpful if you somehow have a convenient way to invoke the operator
        #before your pen touches (click-holds till lifting) a drawing surface. There is exactly 1 single 
        #case where you would want to use that wait, which is for erasing as you hold the eraser
        #before you start erasing.
        #
        
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

#================================================================================

    def modal(self, context, event):
        if event.type == TRIGGERKEY and event.value != TRIGGERSTATE:
            #print(TRIGGERKEY, "opposite event.value achieved (raised probably)")
            
            #restore the material
            if context.active_object.active_material_index != context.scene.stored_material_index:
                context.active_object.active_material_index = context.scene.stored_material_index
            #print("restored material#: ",context.scene.stored_material_index)
            
            #restore the brush name
            if STORED_BRUSH_NAME is not None:
                #print("stored_brush_name is not none, its ",STORED_BRUSH_NAME)
                #print("Restoring!")
                context.tool_settings.gpencil_paint.brush = bpy.data.brushes.get(STORED_BRUSH_NAME)
            return {'FINISHED'}
        return {'PASS_THROUGH'}

def register():
    bpy.utils.register_class(GPencilDrawSwitcherOperator)

    bpy.types.Scene.stored_material_index = bpy.props.IntProperty()
    #https://docs.blender.org/api/current/bpy.props.html#bpy.props.PointerProperty
    #https://docs.blender.org/api/current/bpy.types.Brush.html#bpy.types.Brush
def unregister():
    bpy.utils.unregister_class(GPencilDrawSwitcherOperator)

    del bpy.types.Scene.stored_material_index

if __name__ == "__main__":
    register()
