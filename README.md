# RosettaBot
Python script that grants hours and validates exercices of the Rosetta website

# Installation

Simple just clone or downloads the file and then install the dependencies with:

```bash
pip install -r requierements.txt
```

# Usage

Before running the script you need to get some data:
- Open [Rosetta](https://login.rosettastone.com/#/launchpad) or [Rosetta](https://login.rosettastone.com/) if you are not logged.
- Open your web inspector (F12) and go into the Network section.
- On resetta click on the button with the "Foundations" text (where your lessons are).
- Wait until the page is fully loaded.
- In the web inspector enter "start" in the filter bar (take care of searching among all ressources).
- You must then have only one request. If multiple are present pick the last one (or if you are not confident, redo all the steps).
- Then right click on the request and select Copy -> copy as curl. If you are on windows choose copy as curl (bash).
- Then paste it into a file, let's name it **rosetta_meta**.

Now you can run the script. You have two choices
- Grant only hours
- Grant a whole exercice

## Grant only hours

Simple, just run the script with:

```bash
python rosetta.py -f rosetta_meta -t hours
```

Where:
- **rosetta_meta** is the file containing the curl command
- hours a float value for the number of hours you want (cannot be negative).

## Grant a whole exercices

**Warning: In order to validate an exercice, you need to have been registered on this exercice.
First you need to start the exercice, then ignore all the sub questions and launch the command below.
Sometimes they are a lot of sub quesrions and rosetta will say sommething like "you failed too much" don't worry, just launch the scrimt it will calidare all the subquestions you have ignored and you can then redo.**

Simple, just run the script with:

```bash
python rosetta.py -f rosetta_meta -u unitIndex -l lessonIndex -e exerciceIndex -v True
```

Where:
- rosetta_meta is the file containing the curl command
- unitIndex: the index of the unit (default 0)
- lessonIndex: the index of the lesson (default 0)
- exerciceIndex: the index of the exercice (default 0)

