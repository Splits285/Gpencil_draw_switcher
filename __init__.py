bl_info = {
"name": "Grease Pencil material-brush bind-toggle-switcher (erase-switcher)",
"description": "Switch to a material and/or brush while a special gpencil.draw_switcher is held. Ideal for using holdout materials to erase strokes instead of erasing them by their vertices",
"author": "Splits285",
"version": (1, 0, 2),
"blender": (2, 8, 0),
"location": "Preferences > Keymaps > Grease Pencil Paint. Add an entry for gpencil.draw_switcher",
"warning": "Don\'t use X to clear text fields when changing Switch settings, blender lingers them unless you write exactly nothing, not even a space. Also \'ERASER\' as a key probably won't work well. More explanation on github (Documentation)",
"doc_url": "https://github.com/Splits285/Gpencil_draw_switcher",
"tracker_url": "https://github.com/Splits285/Gpencil_draw_switcher/issues/",
"category": "Grease Pencil",
}
import bpy

class KeymapEntry(bpy.types.PropertyGroup):
    #Class to store keymap entries inside
    idname: bpy.props.StringProperty()
    type: bpy.props.StringProperty()
    value: bpy.props.StringProperty()
    mode: bpy.props.StringProperty()
    
# Collection property to store all keymap entries
class KeymapEntriesP(bpy.types.PropertyGroup):
    keymap_entries: bpy.props.CollectionProperty(type=KeymapEntry)
    
class GPencilDrawSwitcherOperator(bpy.types.Operator):
    bl_idname = "gpencil.draw_switcher"
    bl_label = "GPencil Draw custom (eraser switching)"
    
    global keymap_entries
    global saved_mode
    #=================================================================================================
    #define a billion properties which will be fed into the switch handling or fed into the gpencil.draw
    #which gpencil.draw_custom invokes.
    #These are displayed for the addon user in their binding menu.

    #Self doesn't exist yet and is created by invoke!!!
    
#-------------------------------------------------------------X
    #access with self.CDO_DrawKey
    CDO_DrawKey: bpy.props.StringProperty(
        name="Draw button (Required)", #goes next to textbox ui element in the keymap binding properties in keymap preferences.
        description="Your pre-existing \'Grease Pencil Draw\' key as it is in keymaps, must be located in the Grease Pencil Stroke paint (Draw brush) section. This addon works by editing that keymap with the drawing mode (eraser/draw) calculated when this eraser is held and keeping that binding until eraser is released (pressed again in toggle mode.)\n\nValid mouse inputs look like: \n LEFTMOUSE\n RIGHTMOUSE\n MIDDLEMOUSE\n MOUSEBUTTON4\n MOUSEBUTTON5\n F12\n J \n\nIf you're setting a key input, it's just the key\'s name typed out.\n\nSearch blender event.type online if you don\'t know what your key is named",
        default='LEFTMOUSE',
    )
#------------------------------------------------------------X
    #access with self.CO_DrawVal
    CDO_DrawVal: bpy.props.EnumProperty(
        name="Draw Value (Required)", #goes next to textbox ui element in the keymap binding properties in keymap preferences.
        description="State your pre-existing \'Grease Pencil Draw\' keymap is activated in. If you don't know check your key in Grease Pencil Stroke Paint (Draw Brush)",
        items=[
            #PYTHON     DROPDOWNNAME    DESCRIPTION
            ('PRESS', "Press", "The normal key."),
            ('RELEASE', "Release", "Don\'t use this if you don\'t know how it works"),
            ('CLICK', "Eraser", "Don\'t use this if you don\'t know how it works"),
            ('DOUBLE_CLICK', "Eraser", "Don\'t use this if you don\'t know how it works"),
            ('CLICK_DRAG', "Eraser", "Don\'t use this if you don\'t know how it works"),
            ('NOTHING', "Nothing", "Don\'t use this if you don\'t know how it works, except you probably can\'t. Why is this an option in keybinds?"),
        ],
        default='PRESS',
    )
#-------------------------------------------------------------X
    #access with self.CDO_Toggle
    CDO_Toggle: bpy.props.BoolProperty(
        name="Toggle", #Don't switch back after draw_switcher activation ends, wait for next button.
        description="Don't switch bindings and or materials/brush back after gpencil.draw_switcher activation, wait for next activation",
        default=False,
    )
#---------------------------------------------------------------
    #access with self.CDO_Mode
    CDO_Mode: bpy.props.EnumProperty(
        name="Mode", #goes next to textbox ui element
        description="The mode you want this button to be in, assuming no Trigger/\'Switch to\' checks pass or are set. You'll want this in eraser if you are using this to replace your standard Eraser keymap",
        items=[
            #PYTHON     DROPDOWNNAME    DESCRIPTION
            ('DRAW', "Draw Freehand", "Draw normally"),
            ('DRAW_STRAIGHT', "Draw Straight Lines", "Who even uses this option? It seems bugged on normal gpencil.draw operation to force-use the first material in the objects' list for some reason..."),
            ('ERASER', "Eraser", "Erase Grease Pencil strokes")
        ],
        default='ERASER',
    )
#-------------------------------------------------------------
    #access with self.CDO_TriggerBrushName
    CDO_TriggerBrushName: bpy.props.StringProperty(
        name="TriggerBrush", #goes next to textbox ui element in the keymap binding properties in keymap preferences.
        description="Brush name which, if in use, will enable the brush/material-switcher. \nIf no brush is named here brush/material-switching will happen on every brush\n\n(Case-sensitive)",
        default='',
    )
#-------------------------------------------------------------
    #access with self.CDO_SwitchBrush
    CDO_SwitchBrush: bpy.props.StringProperty(
        name="Switch To Brush", #goes next to textbox ui element in the keymap binding properties in keymap preferences.
        description="Brush to switch to in addition to material switching. If unset or brush doesn't exist, current brush will stay\n\n(Case-sensitive)",
        default='',
    )
#---------------------------------------------------------------
    #access with self.CDO_MaterialName
    CDO_MaterialName: bpy.props.StringProperty(
        name="Switch To Material", #goes next to textbox ui element in the keymap binding properties in keymap preferences.
        description="Material to switch to while held. Does nothing if unset. Note if we find and switch to the matching material Draw mode will be forced on, ignoring your Mode setting.\n(What's the point of setting a material when you're just gonna erase? We won't switch to it if it doesn't exist...)\n\n(Case-sensitive)", 
        default='', #no sample text
    )
    #---------------------------------------------------------------
    #access with self.CDO_ForceThruPin
    CDO_ForceThruPin: bpy.props.BoolProperty(
        name="Switch even pinned brushes\' material", #goes next to textbox ui element
        description="Temporarily disable brush pinned-state while bind is held to allow material switching. This will happen to the \'Switch to brush\' if you set one and it's switched to",
        default=True,
    )

    #=================================================================================

    def invoke(self, context, event):
        try:
            print(bpy.app.driver_namespace['DontLeaveMeHanging'])
        except KeyError:
            bpy.app.driver_namespace['DontLeaveMeHanging'] = 0
 
        if bpy.app.driver_namespace['DontLeaveMeHanging'] == 0:
            #indent everything in invoke to here.
            #print("===================================================DOING")  
            #We use the driver namespace to store only transient data, cleared on shutdown.
            #I'd use scene data but if two people with this addon or just one person used the same session file and it saved with TogglerAwaiting 1 bad things will happeb
    
            if context.active_object.type == 'GPENCIL':
                #print("Active object is a Grease Pencil")
                
                #This comes in being given event.type [see event in the parenthesis?]r (the bind which activated it) 
                #and event.value (pressed or released?) It's also why this is invoke instead of execute.
                
                #The other needed part is .self which allows us to call self.CDO_whatever. Self as in this GPDrawSwitcherOperator class. I think.
    
                #print("OP Activator key name and op-invoking state:", event.type, event.value)
                
                #these are pretty much the only things we DON'T have to store in driverspace.
                #they die when the key is released, which should always happen and if not somehow, blender will kill it on shutdown
                global TRIGGERKEY
                TRIGGERKEY = event.type
                #global TRIGGERSTATE
                #TRIGGERSTATE = event.value
    
                #TRIGGERSTATE should usually be down. You're mad if you purposely bind this operator to be on release.
    
                SetMode = self.CDO_Mode #Base state set by the user.
#Togl----------------------------If toggling is active----------------------------------------
                if self.CDO_Toggle and bpy.app.driver_namespace['TogglerAwaiting']:
                    #print("Toggler's awaiting, skip all checks and keymap-building.")
                    
                    bpy.app.driver_namespace['TogglerAwaiting'] = bpy.app.driver_namespace['TogglerAwaiting'] + 1
                    #print("incremented ToggleAwaiting ",bpy.app.driver_namespace['TogglerAwaiting'])
                    
                    #I'm too stupid to set up more normal bools. 
    
                    if bpy.app.driver_namespace['TogglerAwaiting'] == 2:
                        bpy.app.driver_namespace['TogglerAwaiting'] = 0
                    #print("TogA=",bpy.app.driver_namespace['TogglerAwaiting'])
                        
                #If invoked and we're not on toggle mode or we're the first of 2 toggles (not the reciever, toggle isnt awaitingl)
                elif not self.CDO_Toggle or not bpy.app.driver_namespace['TogglerAwaiting']:
                    bpy.app.driver_namespace['TogglerAwaiting'] = 0
                    if self.CDO_Toggle:
                        bpy.app.driver_namespace['TogglerAwaiting'] = bpy.app.driver_namespace['TogglerAwaiting'] + 1
    
#Key1---------------------Find current drawing keys according to users' specified Draw button & Value. The real trick behind this whole addon.-----------------------------------------------
                
                    #print("Reached KBRemap section.")
                    #print("self.CDO_Mode", self.CDO_Mode)
        
                    # Get all keymap entries in the specified section
                    
                    global keymap_entries
                    #this actually works. Because we don't get to stop running when gpencil.draw doesn't feed our key back to us. If we didn't get it but the real button released, then it will trigger us again
                    #and we won't need to replace nothing, we'll just roll with what we have.

                    keymap_entries = []
                    for kmi_entry in bpy.context.window_manager.keyconfigs.user.keymaps['Grease Pencil Stroke Paint (Draw brush)'].keymap_items:
                        if (kmi_entry.idname == "gpencil.draw"
                            and kmi_entry.type == self.CDO_DrawKey
                            and kmi_entry.value == self.CDO_DrawVal
                            and not kmi_entry.properties.mode == 'ERASER'):
                            
                            
                            keymap_entries.append(kmi_entry)
                            global saved_mode
                            saved_mode = kmi_entry.properties.mode # Remember the state of properties.mode for each keymap entry
                            #print(f"on key with idname: {kmi_entry.idname}")
                            #print(f"savedmode: {saved_mode} on kmi_entry {kmi_entry}")
                            #print("not setting mode yet. We dont know what state to set it to")
                            
                    if self.CDO_DrawKey == "":
                        #print("Missing drawkey?!")
                        self.report({'ERROR'}, "No gpencil.draw keymap was specified!!! No re-keymapping attempted.")
                        #raise error here to user and do nothing
                        #we only act if keymap_entries has stuff to restore anyway
                        return {'FINISHED'}
                    
                    #This gets hit if the user lies to us and the keymap they specified doesn't exist (at least on draw mode)
                    if not keymap_entries and bpy.app.driver_namespace['DontLeaveMeHanging'] == 0:
                        self.report({'ERROR'}, "Error saving drawing keymaps. Likely the specified Draw keymap is nonexistent (or jammed in Eraser mode from a lingering mistake, so we missed it). No re-keymapping attempted.")
                        return {'FINISHED'}
    
                    
                    else: #Only continue if we got the key we need. 
#TriggerBrush----------------------------------------------------------------------------------------------------------------------------------------
                        TriggerBrushActive = False
            
                        if self.CDO_TriggerBrushName == "" or bpy.context.tool_settings.gpencil_paint.brush.name == self.CDO_TriggerBrushName:
                            #print("no specified trigger brush, OR WERE ON IT.")
                            TriggerBrushActive = True
                            pass
            
                        elif bpy.context.tool_settings.gpencil_paint.brush.name != self.CDO_TriggerBrushName:
                            #Got a brush, but it's not the right one, we aren't triggering
                            #TriggerBrushActive = 0
                            pass
                        else:
                            self.report({'ERROR'}, "Gpencil.draw switcher: Error checking brush or no brush is active")
                            #TriggerBrushActive = 0
                            pass
    
                        bpy.app.driver_namespace['STORED_BRUSH_NAME'] = None
                        bpy.app.driver_namespace['STORED_BRUSH_PINSTATE'] = 2
                        bpy.app.driver_namespace['STORED_MATERIAL_INDEX'] = -1
                        
                        if TriggerBrushActive:
            
#SB------------------If TriggerBrush Triggered... do switchbrush checks-----------------------
                            #print ("Tryin to change stuff, reached switchbrush section")
            
                            global BrushMissing
                            BrushMissing = True
                            
                            bpy.app.driver_namespace['STORED_BRUSH_NAME'] = ""
                            if self.CDO_SwitchBrush:
                                print("Switchbrush's name isn't empty.")
                                #Does the brush exist?
                                try:
                                    bpy.data.brushes[self.CDO_SwitchBrush]
                                    BrushMissing = False
                                except KeyError as e:
                                    self.report({'WARNING'}, "Couldn't find specified brush to switch to, staying in mode specified in gpencil.draw_switcher keymap")
                                    #Handle this, we'll just stay in user-set-mode.
                                    BrushMissing = True
                                    pass
                                    
                                
    
                                #switch to it since brushmissing is False
                                if BrushMissing == False:
                                    bpy.app.driver_namespace['STORED_BRUSH_NAME']= bpy.context.tool_settings.gpencil_paint.brush.name
                                    #print("Stored: ",bpy.app.driver_namespace['STORED_BRUSH_NAME']," as our stored brush")
                                    #print("we got the desired switchbrush @ ", bpy.data.brushes[self.CDO_SwitchBrush],", and we're gonna try switching to it.")
                                    context.tool_settings.gpencil_paint.brush = bpy.data.brushes[self.CDO_SwitchBrush]
            
#M--------------If triggerbrush triggered, Switch the material-------------------------------------------------------------------------------------------------
            
                            #print("Reached materials section.")
                            #Get the index of the self.CDO_MaterialName material by looping over the materials in the scene context. The reason we set the index instead of setting it by name is because setting it by name changes the name field of the active brush instead of switching the active brush to the one named by the user. 
                            #ForceThruPin is also a valid condition so that we preserve materials on normally pinned brushes.
    
                            if self.CDO_MaterialName != "":
                                bpy.app.driver_namespace['STORED_MATERIAL_INDEX'] = context.active_object.active_material_index
                                #print("Trying to switch materials, stored ",bpy.app.driver_namespace['STORED_MATERIAL_INDEX'])                                
                                for i, mat in enumerate(context.active_object.data.materials):
                                    #print("Enumerating materials @ 187")
                                    if mat.name == self.CDO_MaterialName:
                                        #switch to it!
                                        context.active_object.active_material_index = i
                                        break
                                        
                                #print(" step 1: setting mode to user mode, DRAW_STRAIGHT if not DRAW.")
                                #if specified material name....
                                if self.CDO_MaterialName != "":
                                    SetMode = "DRAW"
        
                                    if saved_mode != "DRAW": #why. draw_straight support.
                                        #print("saved_mode = ",saved_mode)
                                        SetMode = saved_mode
                                        #print(SetMode," is Setmode")
                
                                        #print(" switching to the material, step two.")
                            else:
                                bpy.app.driver_namespace['STORED_MATERIAL_INDEX'] = -1
                                if self.CDO_MaterialName != "": #if user specified a material but we didnt (-1) find it
                                    self.report({'WARNING'}, "Couldn't find specified material to switch to")
                            #print("setmode aft mat chex: ", SetMode)
#P---------------If triggerbrush triggered, Switch pin state off if the keymap (self.CDO_ForceThruPin) told us to-------------------------------------------------------
                            
                            #Switch it off if ForceThruPin is true.
                            #print("Reached Pin section.")
                            bpy.app.driver_namespace['STORED_BRUSH_PINSTATE'] = 2
                            if self.CDO_ForceThruPin and bpy.app.driver_namespace['STORED_MATERIAL_INDEX'] != -1:
                                #print("stored matindex ",bpy.app.driver_namespace['STORED_MATERIAL_INDEX'])
                                #if brush pin...
                                if bpy.context.tool_settings.gpencil_paint.brush.gpencil_settings.use_material_pin:
                                    #Store pinstate...
                                    #print("storing pinstate 1 because UMP =.... ", bpy.context.tool_settings.gpencil_paint.brush.gpencil_settings.use_material_pin)
                                    bpy.app.driver_namespace['STORED_BRUSH_PINSTATE'] = 1
                                    #print("FORCETHRU: ", self.CDO_ForceThruPin)
                                    #...and turn it off. So we can draw.
                                    #print("Trying to toggle pin on brush")
                                    bpy.context.tool_settings.gpencil_paint.brush.gpencil_settings.use_material_pin = False
                            else:
                                bpy.app.driver_namespace['STORED_BRUSH_PINSTATE'] = 2
                            #print("Stored Pinstate: ", bpy.app.driver_namespace['STORED_BRUSH_PINSTATE'])
#Key2----------------------------Set the key entry to what we want. Finally.---------------------------------------------------------------------------------------
                            #If triggerbrush indent level
                        #If active gpencil indent level
                        
                        if keymap_entries:
                            for i in keymap_entries:
                                #print("setmode in key2: ", SetMode)
                                i.properties.mode = SetMode # Set mode to correct state as determined by the brush/material checks for each keymap entry
                                #print(f"Set Mode {SetMode} on keymap_entries entry {i}")
                                
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------                    
            else: #Corresponds to 'IF GPENCIL OBJECT'
                #print("Active object is not a Grease Pencil")
                pass

            #All checks/switching/Remapping is done. Run the modal and mark it as going. It will listen for the TRIGGERKEY (key user bound to this op)
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            #Previous modal is still running. Don't leave it hanging by spawning more.
            print("Previouse GPDrawSwitcher modal still running, no checks attempted, hit your keymap for the switcher again.")
            return {'FINISHED'}

#================================================================================

    def modal(self, context, event):
        bpy.app.driver_namespace['DontLeaveMeHanging'] = 1
        #This is running constantly until the user releases the button (or presses it again in toggle mode.)

        #It seems impossible that a held gpencil.draw would feed TRIGGERKEYS back to us, so we'll just keep running 
        #like normal eraser does if you are erasing and stop holding eraser button before lifting pen. 
        #With normal eraser you have to hit again to stop the now endlessly-held eraser, and we will act much the same.
        
        #Oh my god. We can listen for when gpencil.draw ENDS NOW. WE ARE IN CONTROL. FINALLY.


        #If 'eraser key', really activator key, is hit again in any way.
        if event.type == TRIGGERKEY or event.type == 'ESC':

            #print(self.CDO_DrawKey, "drawkey...")
            #print(TRIGGERKEY," TRIGGERKEY achieved.")
            #print("\n")
            #print("Material ",bpy.app.driver_namespace['STORED_MATERIAL_INDEX'])
            #print("StoredBru", bpy.app.driver_namespace['STORED_BRUSH_NAME'])
            #print("PinState", bpy.app.driver_namespace['STORED_BRUSH_PINSTATE'])
            #print("\n")

            if not self.CDO_Toggle or not bpy.app.driver_namespace['TogglerAwaiting']: #if togglerawaiting is 0
                if keymap_entries:
                    #print ("got some keymap entries, we need to restore it.")
                    for i, kmi_entry in enumerate(keymap_entries):
                
                        #print("---- saved_mode = ",saved_mode)
                        kmi_entry.properties.mode = saved_mode
                        #print(f"Keymap {i}: Restored ({saved_mode})")

                        if bpy.app.driver_namespace['TogglerAwaiting'] == 2 and self.CDO_Toggle:
                            #If togglemode's on its second go, reset the number.
                            bpy.app.driver_namespace['TogglerAwaiting'] = 0
                

                else:
                    #print("No keymaps to restore.")
                    self.report({'ERROR'}, "Couldn't restore keymaps for some reason, even though the saving function reported a success and let the modal run (which spewed this warning after finding no keymaps)")

                #restore the material
                if bpy.app.driver_namespace['STORED_MATERIAL_INDEX'] != -1:
                    if context.active_object.active_material_index != bpy.app.driver_namespace['STORED_MATERIAL_INDEX']:
                        context.active_object.active_material_index = bpy.app.driver_namespace['STORED_MATERIAL_INDEX']
                
                else:
                    #print("Material index is -1, so either nothing was specified, or nothing was given to restore.")
                    #print("bpy.app.driver_namespace['STORED_MATERIAL_INDEX']=",bpy.app.driver_namespace['STORED_MATERIAL_INDEX'])
                    pass

                #restore the brush pinstate. This needs to be middle since we just did or didn't switch the material to fix it before we potentially leave the brush in the next block.
                if bpy.app.driver_namespace['STORED_BRUSH_PINSTATE'] != 2:
                    #print("restoring brush pinstate ", bpy.app.driver_namespace['STORED_BRUSH_PINSTATE'])
                    bpy.context.tool_settings.gpencil_paint.brush.gpencil_settings.use_material_pin = bpy.app.driver_namespace['STORED_BRUSH_PINSTATE']
            
            
                #restore the brush to the one stored by SwitchBrush's checks
                if bpy.app.driver_namespace['STORED_BRUSH_NAME']:
                    context.tool_settings.gpencil_paint.brush = bpy.data.brushes.get(bpy.app.driver_namespace['STORED_BRUSH_NAME'])

            if event.type == 'ESC':
                print("Cancelling gp draw switcher")
                bpy.app.driver_namespace['DontLeaveMeHanging'] = 0
                return {'CANCELLED'}
                
            else:
                #print("Finishing=============================.\n\n\n\n")
                bpy.app.driver_namespace['DontLeaveMeHanging'] = 0
                return {'FINISHED'}
                
        else:
            #print(f"{TRIGGERKEY} is still held...") #This should spam every time youre moving the mouse or pen while testing if this print is uncommented   
            return {'PASS_THROUGH'}

def register():
    bpy.utils.register_class(GPencilDrawSwitcherOperator)
    bpy.utils.register_class(KeymapEntry)
    bpy.utils.register_class(KeymapEntriesP)
    
    #Even if saved, these will be cleared automatically at drawtime if blender restarts, but I'm still not sure how to store them in driverspace.
    bpy.types.Scene.keymap_entries = bpy.props.PointerProperty(type=KeymapEntriesP)

    bpy.app.driver_namespace['TogglerAwaiting'] = 0
    bpy.app.driver_namespace['DontLeaveMeHanging'] = 0

def unregister():
    del bpy.app.driver_namespace['TogglerAwaiting']
    del bpy.app.driver_namespace['DontLeaveMeHanging']
    bpy.utils.unregister_class(GPencilDrawSwitcherOperator)
    bpy.utils.unregister_class(KeymapEntry)
    bpy.utils.unregister_class(KeymapEntriesP)

if __name__ == "__main__":
    register()
