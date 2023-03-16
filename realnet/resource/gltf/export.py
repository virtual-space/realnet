from pygltflib import GLTF2, Scene, Mesh, Primitive, Node, Buffer, BufferView, Accessor, ELEMENT_ARRAY_BUFFER, ARRAY_BUFFER, SCALAR, UNSIGNED_SHORT, FLOAT, VEC3
import numpy as np
import trimesh
import trimesh.transformations as tf
import json
import base64
from PIL import Image, ImageDraw, ImageFont

def get_item_nodes(item, gltf):
    node = Node()

    mesh = get_item_mesh(item,gltf)
    size = len(gltf.meshes)
    gltf.meshes.append(mesh)
    node.mesh = size
    return node

def get_item_tmat(item):
    return [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]

def get_text_mesh(text):
    # Create a Pillow image object with the text "Hello, World!"
    font = ImageFont.truetype("arial.ttf", 36)
    size = font.getsize(text)
    image = Image.new("L", size, 255)
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), text, font=font, fill=0)

    # Convert the image to a 2D mesh
    mesh = trimesh.creation.annulus(inner_radius=0, outer_radius=size[0]/2.0, segments=64, r_min=0, r_max=size[0]/2.0, height=10.0)
    for i, face in enumerate(mesh.faces):
        face_uv = mesh.vertices[face] / float(size[0])
        # mesh.visual.uv[i] = face_uv[:, :2]
        mesh.visual.face_colors[i] = [255, 255, 255, 255]  # white

    # Extrude the mesh to create a 3D mesh
    return mesh
    # Visualize the mesh
    extruded_mesh.show()

def import_json(tgltf, buffers, scene, gltf):
    nodes = []
    buffer_count = len(gltf.buffers)
    node_count = len(gltf.nodes)
    mesh_count = len(gltf.meshes)
    buffer_view_count = len(gltf.bufferViews)
    
    if tgltf:
        for bufferView in tgltf['bufferViews']:
            bv = BufferView()
            
            if 'buffer' in bufferView:
                bv.buffer = int(bufferView['buffer']) + buffer_count

            if 'byteOffset' in bufferView:
                bv.byteOffset = bufferView['byteOffset']

            if 'byteLength' in bufferView:
                bv.byteLength = bufferView['byteLength']

            gltf.bufferViews.append(bv)

        for asset in tgltf['asset']:
            pass

        for accessor in tgltf['accessors']:
            bv = Accessor()

            if 'bufferView' in accessor:
                bv.bufferView = int(accessor['bufferView']) + buffer_count

            if 'componentType' in accessor:
                bv.componentType = accessor['componentType']

            if 'count' in accessor:
                bv.count = accessor['count']

            if 'max' in accessor:
                bv.max = accessor['max']

            if 'min' in accessor:
                bv.min = accessor['min']

            if 'type' in accessor:
                bv.type = accessor['type']

            if 'byteOffset' in accessor:
                bv.byteOffset = accessor['byteOffset']

            if 'normalized' in accessor:
                bv.normalized = accessor['normalized']
            
            gltf.accessors.append(bv)

        for buffer in tgltf['buffers']:
            b = Buffer()

            if 'byteLength' in buffer:
                b.byteLength = int(buffer['byteLength'])

            if 'uri' in buffer:
                b.uri = 'data:application/octet-stream;base64,' + base64.b64encode(buffers[buffer['uri']]).decode()

            gltf.buffers.append(b)

        for mesh in tgltf['meshes']:
            m = Mesh()

            if 'name' in mesh:
                m.name = mesh['name']
            
            if 'primitives' in mesh:
                for primitive in mesh['primitives']:
                    p = Primitive()

                    if 'indices' in primitive:
                        p.indices = int(primitive['indices']) + buffer_view_count
                    
                    if 'mode' in primitive:
                        p.mode = primitive['mode']
                    
                    if 'attributes' in primitive:
                        for k,v in primitive['attributes'].items():
                            if k == 'POSITION':
                                p.attributes.POSITION = v + buffer_view_count
                            elif k == 'COLOR_0':
                                p.attributes.COLOR_0 = v + buffer_view_count
                            else:
                                pass
                    
                    m.primitives.append(p)

            gltf.meshes.append(m)

        for node in tgltf['nodes']:
            n = Node()

            if 'matrix' in node:
                n.matrix = node['matrix']
            else:
                bbox_size = [5, 5, 5]
                n.translation =  [d for d in np.random.uniform(low=-np.array(bbox_size)/2, high=np.array(bbox_size)/2)]

            if 'name' in node:
                n.name = node['name']

            if 'children' in node:
                n.children = [c + node_count for c in node['children']]

            if 'mesh' in node:
                n.mesh = int(node['mesh']) + mesh_count

            gltf.nodes.append(n)
        
        for scn in tgltf['scenes']:
            if 'nodes' in scn:
                for node in scn['nodes']:
                    nodes.append(int(node) + node_count)
    
    return nodes

def render_item(module, scene, item, gltf):
    nodes = []
    buffers = dict()
    tgltf = {}
    #1. Check if attributes have model if yes load from there if not
    if 'model' in item.attributes:
        tgltf = item.attributes['model']
    #2. Check if items have index.gltf file and if yes load from there if not
    else:
        files = [i for i in item.items if i.name == 'index.gltf']
        if files:
            # here we need to get the gltf data of the item
            tgltf = json.loads(module.get_data(files[0].id))
        else:
    #3. Render as sphere
            tscene = trimesh.Scene()
            geom = trimesh.creation.icosphere(radius=0.25)
            # geom = get_text_mesh(item.name)
            geom.visual.face_colors = np.random.uniform(
                0, 1, (len(geom.faces), 3))
            transform = tf.translation_matrix([0.1, -0.1, 0.1 / 2])
            tscene.add_geometry(geom, transform=transform)
            res = trimesh.exchange.gltf.export_gltf(tscene)

            for file, data in res.items():
                if file.endswith('.gltf'):
                    tgltf = json.loads(data)
                elif file.endswith('.bin'):
                    buffers[file] = data

    return import_json(tgltf, buffers, scene, gltf)




def build_gltf_from_items(module, items):
    gltf = GLTF2()
    scene = Scene()
    gltf.scenes.append(scene)
    for item in items:
        nodes = render_item(module, scene, item, gltf)
        for node in nodes:
            scene.nodes.append(node)

    gltf.save('triangle.gltf')
    return gltf