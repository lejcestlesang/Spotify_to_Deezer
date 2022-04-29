# From Spotify to Deezer

If you are searching a way to transfer your Music library from Spotify to Deezer you are in the right place.   
Follow through the instructions and you might have it done faster than you might think.  

*This project is still under construction. Feel free to raise issue if needed.*  

## Prerequisites

- [python](https://www.python.org/downloads/)
- [pypi](https://pip.pypa.io/en/stable/installation/)


## Usage

1. Create a new folder (replace yournewfolder by the name of your choice in the following command lines).  
Unix/macOS terminal:  
```bash
mkdir yournewfolder
```
Windows PowerShell:
```bash
New-Item -Path .\yournewfolder -ItemType Directory
```

2. Now download the respository in this folder. If git is installed use the following commands if not use this [link](https://github.com/lejcestlesang/Spotify_to_Deezer)  

Unix/macOS terminal:  
```bash
cd yournewfolder
git clone https://github.com/lejcestlesang/Spotify_to_Deezer.git
```
Windows PowerShell:
```bash
cd yournewfolder
git clone https://github.com/lejcestlesang/Spotify_to_Deezer.git $HOME
```

3. Install the dependencies. 

Unix/macOS terminal:  
```bash
python -m pip install -r requirements.txt
```
Windows PowerShell:
```bash
py -m pip install -r requirements.txt
```

4. WE ARE ALMOST THERE; the hardest part is already done. now launch the following command  

Unix/macOS terminal:  
```bash
python Deezer_main.py
```

Follow the instructions on the terminal, enter **y** to confirm and press return otherwise.

## Linting


## Resources

[Deezer API](https://developers.deezer.com/)
[Spotify API](https://developer.spotify.com/documentation/web-api/)
[Sptipy](https://spotipy.readthedocs.io/en/2.19.0/)

## License

This project is licensed under the [MIT license](LICENSE).