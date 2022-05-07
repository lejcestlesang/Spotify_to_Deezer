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

4. WE ARE ALMOST THERE; the hardest part is already done. Now launch the algorithm

Unix/macOS terminal:  
```bash
cd public
python Deezer_main.py
```

Follow the instructions on the terminal, enter **y** to confirm and press return otherwise.

## ROADMAP

##### Q3 2022
1. Enable : Import Deezer Library
2. Enable : Upload Spotify Library
3. Enable : Download & Upload Qobuz Library

#### Q4 2022 
1. Create an UI with an application for Windows/Unix or a website
2. Accept Donations to support further developments

## LIMITATIONS

For now you will need to complete the .env file with your own data following the instructions below :
- [Deezer API](https://developers.deezer.com/guidelines/getting_started#setup)  
- [Spotify API](https://developer.spotify.com/dashboard/)  


## Resources

[Deezer API](https://developers.deezer.com/)  
[Spotify API](https://developer.spotify.com/documentation/web-api/)  
[Spotipy](https://spotipy.readthedocs.io/en/2.19.0/)  

## License

This project is licensed under the [MIT license](LICENSE).