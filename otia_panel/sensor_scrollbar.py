import bpy
import random
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Define the mock data item
class MockDataItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name")
    value: bpy.props.FloatProperty(name="Value")

# Define the custom UI List
class OTIA_UL_MockDataList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=item.name)
        layout.label(text=str(item.value))

# Register and add mock data
def register_mock_data():
    bpy.utils.register_class(MockDataItem)
    bpy.utils.register_class(OTIA_UL_MockDataList)

    bpy.types.Scene.mock_data_collection = bpy.props.CollectionProperty(type=MockDataItem)
    bpy.types.Scene.mock_data_index = bpy.props.IntProperty(name="Index")

    # Add some random mock data if the collection is empty
    if not bpy.context.scene.mock_data_collection:
        for i in range(50):
            item = bpy.context.scene.mock_data_collection.add()
            item.name = f"Item {i+1}"
            item.value = random.random() * 100

def unregister_mock_data():
    bpy.utils.unregister_class(MockDataItem)
    bpy.utils.unregister_class(OTIA_UL_MockDataList)

    del bpy.types.Scene.mock_data_collection
    del bpy.types.Scene.mock_data_index
