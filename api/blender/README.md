# VirtualFit Blender

This is the Blender script for the VirtualFit project. It adds a SMPLX-generated mesh to a Blender scene and fits a garment to it.

## Usage

To use the script, run the following command in the terminal:

```bash
blender --python main.py -- --gender <gender> --obj <path_to_obj> --garment <path_to_garment_blend_file> --output <path_to_output_folder>
```

Replace `<gender>` with the gender of the avatar (e.g., "male" or "female"), `<path_to_obj>` with the path to the generated .obj file of the avatar,`<path_to_garment_blend_file>` with the path to the .blend file of the garment and `<path_to_output_folder>` with the path to the output folder.