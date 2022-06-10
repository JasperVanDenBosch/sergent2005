# EEGManyLabs - Sergent 2005
Code for the stimulation and analysis of the EEGManyLabs project for the replication of the 2005 publication *Timing of the brain events underlying access to consciousness during the attentional blink* by Claire Sergent, Sylvain Baillet and Stanislas Dehaene.


## Microsoft Windows
Tested on Windows 10. Largely adapted from [this VS Code tutorial](https://code.visualstudio.com/docs/python/python-tutorial).

1. Make sure you have [Powershell](https://docs.microsoft.com/en-us/powershell/scripting/overview?view=powershell-7.2) installed
2. Scroll down [this page](https://www.python.org/downloads/windows/) and look for *"Python 3.8.10, Windows embeddable package (64-bit)"*. It's important to get this specific version. Download and install.
3. Download the experiment code (this repository) and unzip in a location you prefer.
4. Start powershell as Administrator (right-click powershell in the start menu)
5. Execute the command `set-executionpolicy remotesigned`. Now exit and restart Powershell.

The following steps are all commands to be executed in Powershell

6. You should be able to run `py -3 --version` and it should answer *python 3.8.10*

7. Navigate to the unzipped code directory (e.g. `cd MyProjects\eegmanylabs-sergent2005`)
8. Create a *Virtual Environment* for our project. This is a directory that will store the required Python packages for our project, without interfering with other projects on your computer. In powershell, execute `py -3 -m venv env`. You should then see a directory `env` in the project directory.
9. Activate the Virtual Environment with the command `env\scripts\activate`. The word `(env)` should now appear in front of the terminal prompt. Test that this worked by executing `Get-Command python`. It should print a path to the python program inside the project directory.
10. Install Psychopy by executing `pip install psychopy==2021.1.4`. This may take up to 10 minutes.

To start the script
1. Open powershell.
2. Navigate to the project directory.
3. Activate the virtual environment: `env\scripts\activate`
4. Start the script: `python main.py`
