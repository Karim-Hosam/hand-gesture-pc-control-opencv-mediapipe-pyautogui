import os
import cv2

def load_assets(folder_path):
    """Load and categorize all UI asset images from the given folder."""
    myList = os.listdir(folder_path)
    
    assets = {
        'ModesList_img': [],
        'ModesList_txt': [],
        'Before': [],
        'After': [],
        'ColorsList_img': [],
        'ColorsList_txt': [],
        'Eraser': [],
        # 'ZoomIt_Logo': [],
    }
    
    # Categorize loaded images into their respective UI lists
    for imPath in myList:
        image = cv2.imread(f'{folder_path}/{imPath}', cv2.IMREAD_UNCHANGED)
        
        if imPath == "Off Mode.png":
            off_mode_img = image
            off_mode_txt = "Off Mode" 
            
        elif "Mode" in imPath:
            assets['ModesList_img'].append(image)
            assets['ModesList_txt'].append(imPath.split(".")[0])
        
        elif "Color" in imPath:
            assets['ColorsList_img'].append(image)
            assets['ColorsList_txt'].append(imPath.split(" Color")[0])
            
        elif imPath == "Eraser.png":
            assets['Eraser'].append(image)
            
        elif imPath == "Before.png":
            assets['Before'].append(image)
            
        elif imPath == "After.png":
            assets['After'].append(image)
            
        # elif imPath == "ZoomIt_Logo.png":
        #     assets['ZoomIt_Logo'].append(image)

    assets['ModesList_img'].append(off_mode_img)
    assets['ModesList_txt'].append(off_mode_txt)
    
    return assets
