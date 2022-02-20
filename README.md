# DOG
Tools, Pre-Processing and Post-Processing layers for CATT Acoustic  

## Usage
Files are to be saved in the CATT project directory, next to /OUT  
Clone this repo to your CATT project folder and run the appropriate Python files  

### Python Files
Below details the functionality and type of each script  

#### sort.py
*Initial Post Processing, first to run after TUCT2 results saved*  

- finds and moves all .SIM impulse response files from the CATT /OUT folder into to DUMP folder. In TUCT2 use **Utilities > SxR save > Impulse Responses** and save all. *(requires that the impulse response output type is set to .SIM, not .WAV)
- loads the room configuration description from INS folder and creates appropriate folder structure in SORTED and STATS
- moves all required .SIM files from DUMP to appropriate folder in SORTED
- loads exported .txt statistics from OUT and exports clean .JSON statistics to appropriate folder in STATS. *(requires that TUCT2 is using **Sequence Processing** and autosaving options are enabled).*
