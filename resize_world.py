import xml.etree.ElementTree as ET

file_path = 'worlds/mars_test_world.world'
try:
    tree = ET.parse(file_path)
    root = tree.getroot()
    world = root.find('world')
    
    # 1. Update cast_shadows to false
    for light in world.findall('light'):
        cast = light.find('cast_shadows')
        if cast is not None:
            cast.text = 'false'
            
    # 2. Change ground size
    for model in world.findall('model'):
        if model.get('name') == 'mars_ground':
            link = model.find('link')
            if link is not None:
                for geom_parent in ['collision', 'visual']:
                    gp = link.find(geom_parent)
                    if gp is not None:
                        geom = gp.find('geometry')
                        if geom is not None:
                            plane = geom.find('plane')
                            if plane is not None:
                                size = plane.find('size')
                                if size is not None:
                                    size.text = '60 60'
                                    
    # 3. Remove far away models
    to_remove = []
    for model in world.findall('model'):
        pose = model.find('pose')
        if pose is not None:
            parts = pose.text.strip().split()
            if len(parts) >= 2:
                try:
                    x = float(parts[0])
                    y = float(parts[1])
                    if abs(x) > 30 or abs(y) > 30:
                        to_remove.append(model)
                except:
                    pass
                    
    for m in to_remove:
        world.remove(m)
        
    tree.write(file_path, encoding='utf-8', xml_declaration=True)
    print(f'Done. Removed {len(to_remove)} distant models.')
except Exception as e:
    print('Error:', e)
