# Bone Generator

> Requires blender 2.91

## Install

1. Download this repository as a zip.
2. Open Blender.
3. Go to Edit > Preferences > Add-ons.
4. Click on "install..." an look for either the ".zip".

![basic_install](https://raw.githubusercontent.com/Pullusb/How_to_install_Blender_addons/master/imgs/basic_install.png)

5. Go to TESTING section
5. And click on the enable checkbox.

![activate_addon](https://raw.githubusercontent.com/Pullusb/How_to_install_Blender_addons/master/imgs/activate_addon.png)

### Note

Remember to check that your python executable is the same as blender.
```python
import sys
print(sys.executable)
```
Write this in Blender Scripting Console and your Python Console.

To install python requirements, I needed to use `sudo` prefix. 

## Development

After Installing the addon :
1. Go to where the addon is installed :
    - Windows : **a path that looks like** `C:\Users\<username>\AppData\Roaming\Blender Foundation\Blender\2.91\scripts\addons`
    - Linux : `~/.config/blender/2.91/scripts/addons`
2. Edit the code.
3. When you return to Blender, you need to reload the scripts. The easiest is to F3 and search for "Reload scripts".

## References

- We use a [Blender addon template](https://github.com/eliemichel/AdvancedBlenderAddon) provided by [eliemichel](https://github.com/eliemichel/)
- The install image comes from [Pullusb/How_to_install_Blender_addons](https://github.com/Pullusb/How_to_install_Blender_addons)

- [Vertex Color](https://blender.stackexchange.com/questions/909/how-can-i-set-and-get-the-vertex-color-property)