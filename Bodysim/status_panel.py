import bpy

current_status_panel = None
session = "NONE"
sim_loaded = False
editing = True
nameless = True
sim_saved = False
sim_name = "NONE"

class CurrentStatusPanel(bpy.types.Panel):
    """Panel that displays the sensors of a given simulation."""

    bl_label = "Current Status"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"

    global current_status_panel

    def draw(self, context):
        current_status_panel = self
        col_layout = self.layout.column()
        wrap(col_layout, "Load a session or create a new one.")

def reset_state():
    global sim_loaded, editing, nameless, sim_saved, sim_name
    sim_loaded = False
    editing = True
    nameless = True
    sim_saved = False
    sim_name = "NONE"

def draw_status_panel():
    bl_label = "Current Status"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"

    global current_status_panel

    def _draw_status_panel(self, context):
        col_layout = self.layout.column()
        text = "Loaded Session: "
        text += session

        wrap(col_layout, text)
        text=""
        if sim_loaded:
            if editing:
                col_layout = self.layout.column()
                text += "Current Simulation (Editable): "
                if nameless:
                    text += "nameless_sim."
                    wrap(col_layout, text)
                    col_layout = self.layout.column()
                    text = ""
                    text += "Either save or run the simulation to save simulation state."
                    wrap(col_layout, text)
                else:
                    text += sim_name
                    wrap(col_layout, text)
                    col_layout = self.layout.column()
                    text = ""
                    if(sim_saved):
                        text += "No changes made."
                    else:
                        text += "Changes have been made. Make sure to save simulation."
                    wrap(col_layout, text)

            else:
                text += "Current Simulation (Readonly): "
                text += sim_name
                wrap(col_layout, text)

    current_status_panel = type("CurrentStatusPanel", (bpy.types.Panel,),{
        "bl_label": bl_label,
        "bl_space_type": bl_space_type,
        "bl_region_type": bl_region_type,
        "draw": _draw_status_panel},)
    bpy.utils.register_class(current_status_panel)

def wrap(col,text,area="VIEW_3D",type="TOOLS",TabStr="    ",scaleY=0.55):
    """ Magical function that wraps long text in blender UI panels.
    Source: http://blenderartists.org/forum/showthread.php?243723.
    """
    aID=-1
    rID=-1
    newLine="\n"
    tab="\t"
    tabbing=False
    nLine=False
    col.scale_y=scaleY
    areas=bpy.context.screen.areas
    for i,a in enumerate(areas):
        if(a.type==area):
            aID=i
        reg=a.regions
        for ir,r in enumerate(reg):
            if(r.type==type):
                rID=ir
    if((aID>=0)and(rID>=0)):
        pWidth=areas[aID].regions[rID].width

        charWidth=7#approximate width of each character
        LineLength=int(pWidth/charWidth)
        LastSpace=LineLength#current position of last space character in text
        while LastSpace>0:
            splitPoint=LineLength#where to split the text
            if(splitPoint>len(text)):
                splitPoint=len(text)-1

            cr=text.find(newLine,0,len(text))

            if((cr>0) and (cr<=splitPoint)):
                nLine=True
                LastSpace=cr#Position of new line symbol, if found
            else:
                tabp=text.find("\t",0,splitPoint)
                if(tabp>=0):
                    text=text.replace(tab,"",1)
                    tabbing=True
                    nLine=False
                LastSpace=text.rfind(" ",0,splitPoint)#Position of last space character in text

            if((LastSpace==-1)or(len(text)<=LineLength)):#No more spaces found, or its the last line of text
                LastSpace=len(text)
            line=text[0:LastSpace]
            if(tabbing):
                line=TabStr+line
            col.label(line)
            if(nLine):
                tabbing=False
            text=text[LastSpace+1:len(text)]
