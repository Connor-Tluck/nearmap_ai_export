# Internal Nearmap API Access Program

Sample Output From Program:

![alt text](
https://github.com/Connor-Tluck/nearmap_ai_export/blob/main/template_photo.png)



This code is modified form the Nearmaps doc page witten by Michael Bewley.

This is an internal program for Nearmap Solution Engineers to use to quickly access the AI API in order to quickly download AI feature packages.

Before running the script be sure to see the requirements file for required packages.

Upon running the script the user will be prompted to complete 4 steps. 

1. Enter an active Nearmap API key
2. Select a geojson file (2d or 3d)
3. Select output file location (best practice is to create an empty folder)
4. Coordinate System (for now simply hit enter to choose default)

Output files will be geojson and json for all AI features avaiable. These will be parsed by feature type as well as one file that contains all possible AI features. A png map will also be added to the folder plotting the returned results. 


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
