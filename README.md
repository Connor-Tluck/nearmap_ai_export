# Internal Nearmap API Access Program

Sample Output From Program:

![alt text](
https://github.com/Connor-Tluck/nearmap_ai_export/blob/main/template_photo.png)



This code is modified form the Nearmaps doc page witten by Michael Bewley.

This is an internal program for Nearmap Solution Engineers to use to quickly access the AI API in order to quickly download AI feature packages.

Before running the script be sure to see the requirements file for required packages.

Upon running the script the user will be prompted to add an API Key as well as define the bounding box. The program will then be run in the console. Output file will be a geojson package that can be used in arcgis pro or other GIS software. The output file will be saved in the same location as the python program. Save the script in the location where you would like to see output files saved.


## Example Input for bounding box 

Formatting is important here. 

```bash
-111.8043139505859 40.56900731858258, 
-111.8042398578515 40.56369670105047, 
-111.7939411278105 40.56377981238411, 
-111.7940154106056 40.5691622974704, 
-111.8043139505859 40.56900731858258
```

## Example Input API Key

```bash
Simply use your key in unformatted text, you can copy and paste when asked.
``` 

## Installation

Clone the repository for use of the processing python script.

```bash
nearmap_ai_export.py
```

## Requirements

```python
see requirements file
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.


## License
[MIT](https://choosealicense.com/licenses/mit/)
