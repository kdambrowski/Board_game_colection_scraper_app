import json
import os
import re
import tkinter as tk
import tkinter.font as tkFont
from tkinter import filedialog
from tkinter import messagebox
from urllib.request import urlopen

import pandas as pd
from bs4 import BeautifulSoup as bs

from Settings import *


def pretty_print_nested_dict(dictionary):
    """Printing pretty dictionary in a nasted form.
    Args:
        dictionary (dict): The nested dictionary to be printed.
    """
    for main_key, sub_dict in dictionary.items():
        if isinstance(sub_dict, dict):
            print(f"{main_key}:")
            for key, value in sub_dict.items():
                print(f"\t{key}: {value}")
        else:
            print(f"{main_key}: {sub_dict}")


def get_page_soup(url, parser=HTML_PARSER):
    """Retrieves and parses the HTML content of a URL.
    Args:
        url (str): The URL to be fetched and parsed.
        parser (str, optional): The parser to be used for page analysis.
        Default: HTML_PARSER.
    Returns:
        BeautifulSoup: Parsed HTML content using the specified parser.
    """
    response = urlopen(url)
    url_content = response.read()
    return bs(url_content, parser)


def create_game_link_dict(url, base_page_adress, parser=HTML_PARSER):
    """Create a dictionary of game links from the provided URL and base URL.
    Args:
        url (str): The URL of the page containing game links.
        base_url (str): The base URL used to construct full game links.
    Returns:
        dict: A dictionary where keys are game names and
        values are their corresponding links.
    """
    soup = get_page_soup(url, parser)
    game_link_dict = dict()

    for tag in soup.find_all('td', class_="collection_objectname"):
        game_link_tag = tag.a
        href = game_link_tag['href']
        game_name = game_link_tag.text
        game_link_http = base_page_adress + href
        game_link_dict[game_name] = game_link_http

    return game_link_dict


def extract_avg_players_rating(game_stats_dict):
    """Extracts game statistics data about players rating.
    Args:
        stats (dict): A dictionary containing game statistics.
    Returns:
        dict: A dictionary containing extracted statistics data about
        average players rating (if available).
    """
    collected_stats = {}
    for item, value in game_stats_dict.items():
        if item == 'average':
            collected_stats[item + '_players_rating'] = value
    return collected_stats


def extract_min_max_players_data(item_data_dict):
    """Extracts player count data.
    Args:
        item_data (dict): A dictionary containing game data.
    Returns:
        dict: A dictionary containing extracted player count data (if available).
    """
    player_data = {}
    for item in ['minplayers', 'maxplayers']:
        if item in item_data_dict:
            player_data[item] = item_data_dict[item]
    return player_data


def extract_game_weight_data(polls_dict):
    """Extracts game weight data.
    Args:
        polls (dict): A dictionary containing poll results.
    Returns:
        dict: A dictionary containing extracted game weight data (if available).
    """
    weight_data = {}
    if 'boardgameweight' in polls_dict:
        weight_subdata = polls_dict['boardgameweight']
        if 'averageweight' in weight_subdata:
            weight_data['averageweight'] = weight_subdata['averageweight']
    return weight_data


def scrape_game_data(game_link, parser=HTML_PARSER):
    """Scrapes game data based on the provided link.
    Args:
        game_link (str): Link to the game page.
        parser (str, optional): Parser to be used for page analysis.
        Default: HTML_PARSER.
    Returns:
        dict: A dictionary containing the collected game data.
    """
    collected_data = {'link': game_link}
    game_bs = get_page_soup(game_link, parser)
    reg_compiler = re.compile(r'GEEK\.geekitemPreload')
    reg_searcher = r'GEEK\.geekitemPreload\s*=\s*({.*?});'
    # Find <script> tags containing data
    script_tags = game_bs.find_all('script', text=reg_compiler)

    for script_tag in script_tags:
        match = re.search(reg_searcher, script_tag.string)
        if match:
            geekitem_preload_text = match.group(1)
            geekitem_preload = json.loads(geekitem_preload_text)
            # Extract data from individual sections
            stats_data = extract_avg_players_rating(geekitem_preload['item']['stats'])
            players_data = extract_min_max_players_data(geekitem_preload['item'])
            weight_data = extract_game_weight_data(geekitem_preload['item']['polls'])
            collected_data.update(stats_data)
            collected_data.update(players_data)
            collected_data.update(weight_data)
    return collected_data


def scrape_all_game_data(game_link_dict, parser=HTML_PARSER):
    """Scrape data for all games in the provided dictionary of game links.
    Args:
        game_link_dict (dict): A dictionary where keys are game names and values
        are their corresponding links.
        parser (str, optional): Parser to be used for page analysis.
        Default: HTML_PARSER.
    Returns:
        dict: A dictionary where keys are game names and values are dictionaries
        containing the collected game data.
    """
    game_data_dict = dict()
    for game_name, game_link in game_link_dict.items():
        collected_data = scrape_game_data(game_link, parser)
        game_data_dict[game_name] = collected_data
    return game_data_dict


def convert_objectcolumn_to_numeric(df):
    """Convert object-type columns in a DataFrame to numeric data types
    (float or int).
    Args:
            df (pandas.DataFrame): The DataFrame containing columns to be converted.
    Returns:
            None: The function modifies the input DataFrame in place by converting
            eligible columns to numeric types (float or int) and replacing values that
            cannot be converted with NaN.
    """
    for column in df.columns.tolist():
        if pd.to_numeric(df[column], errors='coerce').notna().all():
            df[column] = pd.to_numeric(df[column], errors='coerce')
    return df


def prepare_dataframe_from_dict(game_data_dict):
    """Prepares a DataFrame from a dictionary of game data.
    Args:
            game_data_dict (dict): A dictionary containing game data with
            game names as keys and data as values.
    Returns:
            pandas.DataFrame: A prepared DataFrame with game data, where
            game names are in the 'nazwa_gry' column.
    """
    df = pd.DataFrame.from_dict(game_data_dict, orient='index')
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'nazwa_gry'}, inplace=True)
    df = convert_objectcolumn_to_numeric(df)
    return df


def convert_and_replace_decimal_separator(df):
    """Converts all columns of a DataFrame to 'string' type
    and replaces dots with commas in numeric columns.
    This operation is necessary to usage DF in
    googlesheet as a numeric value.
    Args:
            param df: DataFrame whose columns need to be converted
            and where dots should be replaced with commas.
    Retuns:
            DataFrame after the conversion and replacement of decimal separators.
    """
    for column in df.columns.tolist():
        if pd.to_numeric(df[column], errors='coerce').notna().all():
            df[column] = df[column].astype('string')
            df[column] = df[column].apply(lambda x: x.replace('.', ','))
    return df


def run_scraper():
    """
    Perform web scraping based on user input, process the data, and save it to a CSV file.
    This function retrieves the user's BoardGameGeek (BGG) collection URL, performs web scraping to extract game data,
    and then processes the data. It saves the processed data to a CSV file with the chosen destination path and filename.
    """
    bgg_user_collection_url = bgg_user_collection_url_entry.get()
    csv_destination_path = csv_destination_path_var.get()
    csv_filename = csv_filename_var.get()

    game_link_dict = create_game_link_dict(bgg_user_collection_url, BASE_PAGE_ADDRESS)
    game_data_dict = scrape_all_game_data(game_link_dict)
    game_list_df = prepare_dataframe_from_dict(game_data_dict)
    game_list_df_for_sheet = convert_and_replace_decimal_separator(game_list_df)

    csv_path = os.path.join(csv_destination_path, csv_filename)
    game_list_df_for_sheet.to_csv(csv_path, index=False)

    messagebox.showinfo("Info", "Web scraping and data saving completed!")


def choose_destination_path():
    """
    Open a file dialog to choose the destination path for saving a CSV file.
    This function displays a file dialog that allows the user to select a destination path and filename for
    saving a CSV file. If a path is chosen, it updates the `csv_destination_path_var` and `csv_filename_var`
    variables with the selected path and filename, respectively."""
    chosen_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
    if chosen_path:
        csv_destination_path_var.set(os.path.dirname(chosen_path))
        csv_filename_var.set(os.path.basename(chosen_path))


def create_main_window():
    """
    Create and configure the main application window.
    This function creates the main application window using Tkinter, sets its title, and centers it on the screen.
    Args:
    None
    Returns:
    tk.Tk: The main application window.
    """
    root = tk.Tk()
    root.title("Web Scraper App")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - WINDOW_WIDTH) // 2
    y = (screen_height - WINDOW_HEIGHT) // 2
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
    return root


def create_user_collection_url_entry(root):
    """
    Create and configure the input field for the BoardGameGeek (BGG) User Collection URL.
    This function creates a label and an entry field for entering the BGG User Collection URL, configures the
    width of the entry field, and returns the entry field widget.
    Args:
    root (tk.Tk): The parent Tkinter window where the entry field will be placed.
    Returns:
    tk.Entry: The entry field widget for entering the BGG User Collection URL.
    """
    label = tk.Label(root, text="BGG User Collection URL:")
    label.pack()
    entry = tk.Entry(root)
    entry.config(width=50)
    entry.pack()
    return entry


def create_csv_destination_path_entry(root):
    """
    Create and configure the input field for the CSV destination path.
    This function creates a label, an entry field for entering the CSV destination path, and a StringVar to store the
    path. It also configures the width of the entry field and returns both the entry field widget and the StringVar.
    Args:
    root (tk.Tk): The parent Tkinter window where the entry field will be placed.
    Returns:
    tk.Entry: The entry field widget for entering the CSV destination path.
    tk.StringVar: The StringVar to store the CSV destination path.
    """
    label = tk.Label(root, text="CSV Destination Path:")
    label.pack(pady=(20, 0))
    var = tk.StringVar()
    entry = tk.Entry(root, textvariable=var)
    entry.config(width=50)
    entry.pack()
    return entry, var


def create_choose_path_button(root):
    """
    Create and configure a button for choosing the destination path.
    This function creates a button with the label "Choose Path" and associates it with the `choose_destination_path`
    function to handle the click event. It then packs the button in the specified Tkinter window.
    Args:
    root (tk.Tk): The parent Tkinter window where the button will be placed.
    """
    button = tk.Button(root, text="Choose Path", command=choose_destination_path)
    button.pack()


def create_run_button(root):
    """
    Create and configure a button for running the web scraper.
    This function creates a button labeled "Run Web Scraper" and associates it with the `run_scraper` function to handle
    the click event. It also configures the button's appearance, including padding, background color, text color, relief,
    and border width. Finally, it packs the button in the specified Tkinter window.
    Args:
    root (tk.Tk): The parent Tkinter window where the button will be placed.
    """
    button = tk.Button(root,
                       text="Run Web Scraper",
                       command=run_scraper,
                       padx=10,
                       pady=10,
                       bg="royal blue",
                       fg="white",
                       relief=tk.RAISED,
                       bd=3)
    button['font'] = tkFont.Font(weight="bold", size=12)
    button.pack(pady=20)


def create_web_scraper_app():
    """
        Create and run the web scraper application.
        This function creates the main application window, user interface elements, and starts the Tkinter main loop.
    """
    root = create_main_window()
    global bgg_user_collection_url_entry
    bgg_user_collection_url_entry = create_user_collection_url_entry(root)
    global csv_destination_path_var
    csv_destination_path_entry, csv_destination_path_var = create_csv_destination_path_entry(root)
    create_choose_path_button(root)
    global csv_filename_var
    csv_filename_var = tk.StringVar()
    bgg_user_collection_url_entry.config(width=50)
    csv_destination_path_entry.config(width=50)

    create_run_button(root)
    root.mainloop()
