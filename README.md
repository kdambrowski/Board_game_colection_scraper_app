# Board_game_colection_scraper_app
 
This Python-based web scraper application is designed to collect and process data from BGG (BoardGameGeek) user collection pages. It utilizes various functions and libraries to scrape data, manipulate it, and save it in a convenient format.

## Table of Contents
- [Overview](#overview)
- [Technologies](#technologies)
- [Features](#features)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Demo](#demo)
- [Contributions](#contributions)

## Overview

This application provides a framework for web scraping and data processing. It includes functions for:

- Fetching and parsing HTML content from URLs.
- Extracting specific data from web pages
  (BoardGame name, Link to BoardGame, Average players rating, min players, max players, game average weight).
- Converting and processing data.
- Creating a user-friendly graphical interface using Tkinter.

## Technologies

- Python
- Tkinter
- Beautiful Soup (bs4)
- urllib
- Regular Expressions (re)
- Pandas

## Features

### Data Scraping
- Fetching and parsing HTML content from web pages.
- Extracting data based on specific patterns or elements.

### Data Processing
- Converting object-type columns to numeric types.
- Preparing dataframes from dictionaries.
- Replacing decimal separators for compatibility.

### User Interface
- Creating a graphical user interface (GUI) for user interaction.
- Allowing users to input URLs and file paths.
- Initiating web scraping and data processing with the click of a button.

## Getting Started

To run this application, you need to have Python installed on your system. You can clone this repository and install the required libraries using pip:
Install the required libraries by running
```bash
 pip install -r requirements.txt
```

## Usage

1. Clone the repository to your local machine.

2. Install the required libraries as mentioned in the "Getting Started" section.

3. Customize the settings in the provided Python scripts according to your specific web scraping needs.
4. Run the project by command python
```bash
 python Main.py
```
5. Use the provided graphical user interface (GUI) to input URLs and file paths.

6. Click the "Run Web Scraper" button to initiate web scraping and data processing.

7. The processed data will be saved as a CSV file at the specified destination path, ready for further analysis or presentation.

## Demo
Click on this screen to see a video with a demo of how this app works.

[![Board_game_colection_scraper_app]([http://img.youtube.com/vi/ffNtDCFeqZA/0.jpg)](http://www.youtube.com/watch?v=ffNtDCFeqZA](https://youtu.be/wHLC_9bBoXI))

## Contributions

Contributions to this project are welcome. You can enhance the functionality, improve the user interface, or address any issues you encounter. Feel free to create pull requests and contribute to making this web scraper application even more versatile and user-friendly.
